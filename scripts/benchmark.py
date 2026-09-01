#!/usr/bin/env python3
"""Distroless runtime benchmark: build → smoke → size → grype → report."""

from __future__ import annotations

import json
import os
import re
import secrets
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
ROOT = SCRIPTS.parent
sys.path.insert(0, str(SCRIPTS))

from grype_breakdown import aggregate  # noqa: E402
from java_layered_metrics import build_layered_analysis  # noqa: E402
from render_benchmark_report import render  # noqa: E402

RAW_DIR = ROOT / "reports" / "raw"
PLATFORM = os.environ.get("PLATFORM", "linux/amd64")
PORT = int(os.environ.get("PORT", "8080"))
SMOKE_RETRIES = int(os.environ.get("SMOKE_RETRIES", "30"))
SMOKE_SLEEP = float(os.environ.get("SMOKE_SLEEP", "1"))
TTFB_SAMPLES = int(os.environ.get("TTFB_SAMPLES", "3"))

EMPTY_CVE = {
    "critical": None,
    "high": None,
    "medium": None,
    "low": None,
    "unknown": None,
    "total_matches": None,
    "breakdown": None,
}

MATRIX = [
    ("go", "baseline", ROOT / "apps/go", "Dockerfile.baseline", "distroless-bench/go:baseline", "debian12"),
    ("go", "distroless", ROOT / "apps/go", "Dockerfile.distroless", "distroless-bench/go:distroless", "debian12"),
    ("python", "baseline", ROOT / "apps/python", "Dockerfile.baseline", "distroless-bench/python:baseline", "debian12"),
    ("python", "distroless", ROOT / "apps/python", "Dockerfile.distroless", "distroless-bench/python:distroless", "debian12"),
    ("java", "baseline", ROOT / "apps/java", "Dockerfile.baseline", "distroless-bench/java:baseline", "debian12"),
    ("java", "distroless", ROOT / "apps/java", "Dockerfile.distroless", "distroless-bench/java:distroless", "debian12"),
    (
        "java",
        "baseline-jlink",
        ROOT / "apps/java",
        "Dockerfile.baseline-jlink",
        "distroless-bench/java:baseline-jlink",
        "debian12",
    ),
    (
        "java",
        "distroless-jlink",
        ROOT / "apps/java",
        "Dockerfile.distroless-jlink",
        "distroless-bench/java:distroless-jlink",
        "debian12",
    ),
    (
        "java",
        "distroless-jlink-layered",
        ROOT / "apps/java",
        "Dockerfile.distroless-jlink-layered",
        "distroless-bench/java:distroless-jlink-layered",
        "debian12",
    ),
    (
        "java2",
        "distroless-jlink",
        ROOT / "apps/java2",
        "Dockerfile.distroless-jlink",
        "distroless-bench/java2:distroless-jlink",
        "debian12",
    ),
    (
        "java2",
        "distroless-jlink-layered",
        ROOT / "apps/java2",
        "Dockerfile.distroless-jlink-layered",
        "distroless-bench/java2:distroless-jlink-layered",
        "debian12",
    ),
    ("nodejs", "baseline", ROOT / "apps/nodejs", "Dockerfile.baseline", "distroless-bench/nodejs:baseline", "debian12"),
    (
        "nodejs",
        "distroless-dynamic",
        ROOT / "apps/nodejs",
        "Dockerfile.distroless-dynamic",
        "distroless-bench/nodejs:distroless-dynamic",
        "debian12",
    ),
    ("nginx", "baseline", ROOT / "apps/nginx", "Dockerfile.baseline", "distroless-bench/nginx:baseline", "debian12"),
    ("nginx", "distroless", ROOT / "apps/nginx", "Dockerfile.distroless", "distroless-bench/nginx:distroless", "debian12"),
]


def need(tool: str) -> None:
    if shutil.which(tool) is None:
        raise SystemExit(f"error: required tool not found: {tool}")


def run_capture(cmd: list[str], check: bool = False) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, capture_output=True, text=True, check=check)


def image_size_bytes(image: str) -> int | None:
    proc = run_capture(["docker", "image", "inspect", "--format", "{{.Size}}", image])
    if proc.returncode != 0:
        return None
    text = proc.stdout.strip()
    if re.fullmatch(r"[0-9]+", text):
        return int(text)
    return None


def smoke_http(image: str) -> bool:
    return smoke_http_timed(image) is not None


def smoke_http_timed(image: str) -> float | None:
    """Return seconds until /health=200, or None on failure."""
    name = f"bench-smoke-{os.getpid()}-{secrets.token_hex(3)}"
    run = subprocess.run(
        [
            "docker",
            "run",
            "-d",
            "--rm",
            "--platform",
            PLATFORM,
            "--name",
            name,
            "-p",
            f"127.0.0.1::{PORT}",
            image,
        ],
        capture_output=True,
        text=True,
    )
    if run.returncode != 0:
        return None

    try:
        port_proc = run_capture(["docker", "port", name, f"{PORT}/tcp"])
        host_port = port_proc.stdout.strip().rsplit(":", 1)[-1]
        t0 = time.perf_counter()
        for _ in range(SMOKE_RETRIES):
            curl = run_capture(
                [
                    "curl",
                    "-s",
                    "-o",
                    "/dev/null",
                    "-w",
                    "%{http_code}",
                    "--max-time",
                    "2",
                    f"http://127.0.0.1:{host_port}/health",
                ]
            )
            if curl.stdout.strip() == "200":
                return time.perf_counter() - t0
            time.sleep(SMOKE_SLEEP)
        return None
    finally:
        subprocess.run(["docker", "stop", name], capture_output=True, text=True)


def median(xs: list[float]) -> float | None:
    if not xs:
        return None
    s = sorted(xs)
    mid = len(s) // 2
    if len(s) % 2:
        return s[mid]
    return (s[mid - 1] + s[mid]) / 2


def time_to_healthy_median(image: str, samples: int = TTFB_SAMPLES) -> dict:
    times: list[float] = []
    for _ in range(samples):
        t = smoke_http_timed(image)
        if t is not None:
            times.append(t)
    return {
        "samples": samples,
        "ok_samples": len(times),
        "values_sec": [round(t, 3) for t in times],
        "median_sec": round(median(times), 3) if times else None,
        "note": "wall clock docker run → HTTP 200 /health; noisy on Docker Desktop",
    }


def grype_summary(raw: str) -> str:
    lines = [ln for ln in raw.splitlines() if ln.startswith(("Application:", "Version:"))]
    if lines:
        return " ".join(lines[:2])
    return raw.splitlines()[0] if raw.strip() else "see raw meta"


def write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def apply_comparable(result_paths: list[Path]) -> None:
    rows = [json.loads(p.read_text(encoding="utf-8")) for p in result_paths]
    lineage: dict = {}
    for r in rows:
        v = r.get("variant")
        if v in ("baseline", "distroless"):
            lineage.setdefault(r["language"], {})[v] = r.get("distro_lineage")
        if v == "distroless-dynamic":
            lineage.setdefault(r["language"], {})["distroless_pair"] = r.get("distro_lineage")
    pair_comparable = {}
    for lang, pair in lineage.items():
        dist = pair.get("distroless") or pair.get("distroless_pair")
        pair_comparable[lang] = bool(pair.get("baseline") and dist and pair["baseline"] == dist)
    for path, row in zip(result_paths, rows):
        if row.get("variant") in ("baseline", "distroless", "distroless-dynamic"):
            row["comparable"] = pair_comparable.get(row["language"], False)
        else:
            row["comparable"] = None
        write_json(path, row)


def main() -> None:
    for tool in ("docker", "grype", "python3", "curl"):
        need(tool)

    RAW_DIR.mkdir(parents=True, exist_ok=True)
    now = datetime.now(timezone.utc)
    timestamp = now.strftime("%Y-%m-%dT%H:%M:%SZ")
    run_id = now.strftime("%Y%m%dT%H%M%SZ")

    grype_version = run_capture(["grype", "version"]).stdout or ""
    db_status = run_capture(["grype", "db", "status"]).stdout or ""
    meta_file = RAW_DIR / f"meta-{run_id}.json"
    meta = {
        "timestamp_utc": timestamp,
        "run_id": run_id,
        "platform": PLATFORM,
        "grype_version_raw": grype_version,
        "grype_version_summary": grype_summary(grype_version),
        "grype_db_status_raw": db_status,
        "size_metric": "docker local Size (bytes from docker image inspect)",
    }
    write_json(meta_file, meta)
    print("meta →", meta_file)

    result_paths: list[Path] = []
    for language, variant, context, dockerfile, image, distro_lineage in MATRIX:
        safe_name = f"{language}-{variant}"
        result_file = RAW_DIR / f"result-{safe_name}-{run_id}.json"
        scan_file = RAW_DIR / f"grype-{safe_name}-{run_id}.json"

        print(f"\n==> {language}/{variant} → {image}")

        build_ok = False
        smoke_ok = False
        size_bytes: int | None = None
        cve = dict(EMPTY_CVE)
        error_msg = ""

        build = subprocess.run(
            [
                "docker",
                "build",
                "--platform",
                PLATFORM,
                "-f",
                str(context / dockerfile),
                "-t",
                image,
                str(context),
            ]
        )
        if build.returncode == 0:
            build_ok = True
        else:
            error_msg = "docker build failed"

        if build_ok:
            if smoke_http(image):
                smoke_ok = True
                size_bytes = image_size_bytes(image)
                with scan_file.open("w", encoding="utf-8") as fh:
                    scan = subprocess.run(
                        ["grype", image, "-o", "json"],
                        stdout=fh,
                        stderr=subprocess.PIPE,
                        text=True,
                    )
                if scan.returncode != 0:
                    error_msg = "grype scan failed"
                    smoke_ok = False
                    cve = dict(EMPTY_CVE)
                else:
                    data = json.loads(scan_file.read_text(encoding="utf-8"))
                    cve = aggregate(data.get("matches") or [])
            else:
                error_msg = "smoke HTTP /health failed"
                size_bytes = image_size_bytes(image)

        payload = {
            "language": language,
            "variant": variant,
            "image": image,
            "distro_lineage": distro_lineage,
            "dockerfile": dockerfile,
            "build_ok": build_ok,
            "smoke_ok": smoke_ok,
            "size_bytes": size_bytes,
            "cve": cve,
            "error": error_msg or None,
            "run_id": run_id,
            "success_measurement": build_ok and smoke_ok,
        }
        write_json(result_file, payload)
        print("result →", result_file)
        result_paths.append(result_file)

    apply_comparable(result_paths)

    rows = [json.loads(p.read_text(encoding="utf-8")) for p in result_paths]
    by = {(r["language"], r["variant"]): r for r in rows}
    layered_path = RAW_DIR / f"java-layered-{run_id}.json"
    layered_payload = None
    if by.get(("java", "distroless-jlink"), {}).get("success_measurement") and by.get(
        ("java", "distroless-jlink-layered"), {}
    ).get("success_measurement"):
        print("\n==> java layered metrics + time-to-healthy")
        ttfb = {
            "fat": time_to_healthy_median(by[("java", "distroless-jlink")]["image"]),
            "layered": time_to_healthy_median(
                by[("java", "distroless-jlink-layered")]["image"]
            ),
        }
        layered_payload = build_layered_analysis(
            fat_java=by[("java", "distroless-jlink")],
            layered_java=by[("java", "distroless-jlink-layered")],
            fat_java2=by.get(("java2", "distroless-jlink")),
            layered_java2=by.get(("java2", "distroless-jlink-layered")),
            time_to_healthy=ttfb,
        )
        write_json(layered_path, layered_payload)
        print("layered →", layered_path)
        meta["java_layered_analysis"] = layered_path.name
        write_json(meta_file, meta)

    report_ts = ROOT / "reports" / f"report-{run_id}.md"
    report_latest = ROOT / "reports" / "latest.md"
    text = render(
        meta,
        rows,
        meta_file.name,
        [p.name for p in result_paths],
        layered_analysis=layered_payload,
    )
    report_ts.write_text(text, encoding="utf-8")
    report_latest.write_text(text, encoding="utf-8")
    print("report →", report_ts)
    print("report →", report_latest)
    print("\nDone. See reports/latest.md")


if __name__ == "__main__":
    main()
