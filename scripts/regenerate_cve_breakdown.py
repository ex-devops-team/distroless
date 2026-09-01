#!/usr/bin/env python3
"""Recompute OS/app CVE breakdown from saved Grype JSON and rewrite the report."""

from __future__ import annotations

import json
import sys
from pathlib import Path

from grype_breakdown import aggregate
from render_benchmark_report import render

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "reports" / "raw"
REPORTS = ROOT / "reports"


MATRIX_ORDER = [
    "go-baseline",
    "go-distroless",
    "python-baseline",
    "python-distroless",
    "java-baseline",
    "java-distroless",
    "java-baseline-jlink",
    "java-distroless-jlink",
    "java-distroless-jlink-layered",
    "java2-distroless-jlink",
    "java2-distroless-jlink-layered",
    "nodejs-baseline",
    "nodejs-distroless-dynamic",
    "nginx-baseline",
    "nginx-distroless",
]


def ordered_results(run_id: str) -> list[Path]:
    found = {p.name: p for p in RAW.glob(f"result-*-{run_id}.json")}
    ordered = []
    for key in MATRIX_ORDER:
        name = f"result-{key}-{run_id}.json"
        if name in found:
            ordered.append(found.pop(name))
    ordered.extend(sorted(found.values(), key=lambda p: p.name))
    return ordered


def latest_run_id() -> str:
    metas = sorted(RAW.glob("meta-*.json"))
    if not metas:
        raise SystemExit("no meta-*.json in reports/raw")
    return json.loads(metas[-1].read_text(encoding="utf-8"))["run_id"]


def main() -> None:
    run_id = sys.argv[1] if len(sys.argv) > 1 else latest_run_id()
    meta_path = RAW / f"meta-{run_id}.json"
    if not meta_path.exists():
        raise SystemExit(f"missing {meta_path}")
    meta = json.loads(meta_path.read_text(encoding="utf-8"))
    result_paths = ordered_results(run_id)
    if not result_paths:
        raise SystemExit(f"no result-*-{run_id}.json")

    rows = []
    mismatches = []
    for result_path in result_paths:
        row = json.loads(result_path.read_text(encoding="utf-8"))
        safe = f"{row['language']}-{row['variant']}"
        scan_path = RAW / f"grype-{safe}-{run_id}.json"
        if row.get("success_measurement") and scan_path.exists():
            data = json.loads(scan_path.read_text(encoding="utf-8"))
            cve = aggregate(data.get("matches") or [])
            bd = cve["breakdown"]
            summed = bd["os"]["total"] + bd["app"]["total"] + bd["unknown"]["total"]
            if summed != cve["total_matches"]:
                mismatches.append((safe, summed, cve["total_matches"]))
            row["cve"] = cve
            result_path.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
            print(f"updated {result_path.name}: os={bd['os']['total']} app={bd['app']['total']} unknown={bd['unknown']['total']} total={cve['total_matches']}")
        elif row.get("success_measurement") and not scan_path.exists():
            raise SystemExit(f"missing scan {scan_path}")
        rows.append(row)

    if mismatches:
        raise SystemExit(f"os+app+unknown != total_matches: {mismatches}")

    layered = None
    layered_name = meta.get("java_layered_analysis")
    if layered_name:
        cand = RAW / layered_name
        if cand.is_file():
            layered = json.loads(cand.read_text(encoding="utf-8"))

    text = render(
        meta, rows, meta_path.name, [p.name for p in result_paths], layered
    )
    stamped = REPORTS / f"report-{run_id}.md"
    latest = REPORTS / "latest.md"
    stamped.write_text(text, encoding="utf-8")
    latest.write_text(text, encoding="utf-8")
    print("report →", stamped)
    print("report →", latest)


if __name__ == "__main__":
    main()
