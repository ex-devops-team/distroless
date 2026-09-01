#!/usr/bin/env python3
"""Measure Spring Boot layer group sizes and compare Docker layer digests."""

from __future__ import annotations

import json
import re
import secrets
import subprocess
import tempfile
from pathlib import Path


LAYER_GROUPS = (
    "dependencies",
    "spring-boot-loader",
    "snapshot-dependencies",
    "application",
)


def _run(cmd: list[str], check: bool = False) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, capture_output=True, text=True, check=check)


def rootfs_layers(image: str) -> list[str]:
    proc = _run(
        ["docker", "image", "inspect", "--format", "{{json .RootFS.Layers}}", image]
    )
    if proc.returncode != 0 or not proc.stdout.strip():
        return []
    try:
        return list(json.loads(proc.stdout.strip()))
    except json.JSONDecodeError:
        return []


def history_layer_sizes(image: str) -> list[dict]:
    """Created layers newest-first (docker history default), size in bytes."""
    proc = _run(
        [
            "docker",
            "history",
            "--no-trunc",
            "--format",
            "{{.Size}}\t{{.CreatedBy}}",
            image,
        ]
    )
    if proc.returncode != 0:
        return []
    out = []
    for line in proc.stdout.splitlines():
        if not line.strip() or "\t" not in line:
            continue
        size_s, created = line.split("\t", 1)
        out.append({"size_human": size_s.strip(), "created_by": created.strip()})
    return out


def parse_size_to_bytes(human: str) -> int | None:
    human = human.strip()
    if human in ("0B", "0", "<missing>"):
        return 0
    m = re.fullmatch(r"([0-9.]+)\s*([kKmMgG]?[bB])?", human.replace(" ", ""))
    if not m:
        return None
    n = float(m.group(1))
    unit = (m.group(2) or "B").upper()
    mult = {"B": 1, "KB": 1024, "MB": 1024**2, "GB": 1024**3}.get(unit, 1)
    return int(n * mult)


def layer_group_sizes_from_fat_image(fat_image: str, jar_path: str = "/app/app.jar") -> dict:
    """Extract layertools groups from fat jar inside image; return sizes in bytes."""
    name = f"layer-jar-{secrets.token_hex(4)}"
    create = _run(["docker", "create", "--name", name, fat_image])
    if create.returncode != 0:
        return {"error": create.stderr.strip() or "docker create failed"}
    try:
        with tempfile.TemporaryDirectory() as tmp:
            jar_host = Path(tmp) / "app.jar"
            cp = _run(["docker", "cp", f"{name}:{jar_path}", str(jar_host)])
            if cp.returncode != 0:
                return {"error": cp.stderr.strip() or "docker cp jar failed"}
            extract_dir = Path(tmp) / "extract"
            extract_dir.mkdir()
            extract = _run(
                [
                    "docker",
                    "run",
                    "--rm",
                    "-v",
                    f"{jar_host}:/app.jar:ro",
                    "-v",
                    f"{extract_dir}:/out",
                    "--workdir",
                    "/out",
                    "eclipse-temurin:21-jdk",
                    "bash",
                    "-c",
                    "java -Djarmode=layertools -jar /app.jar extract && du -sb "
                    + " ".join(LAYER_GROUPS),
                ]
            )
            if extract.returncode != 0:
                return {
                    "error": extract.stderr.strip()
                    or extract.stdout.strip()
                    or "layertools extract failed"
                }
            sizes: dict[str, int] = {}
            for line in extract.stdout.splitlines():
                parts = line.strip().split(maxsplit=1)
                if len(parts) != 2:
                    continue
                if not parts[0].isdigit():
                    continue
                name_g = Path(parts[1]).name
                if name_g in LAYER_GROUPS:
                    sizes[name_g] = int(parts[0])
            return {"groups_bytes": sizes, "groups_total_bytes": sum(sizes.values())}
    finally:
        _run(["docker", "rm", "-f", name])


def compare_rootfs(image_a: str, image_b: str) -> dict:
    a = rootfs_layers(image_a)
    b = rootfs_layers(image_b)
    shared_prefix = 0
    for i, (la, lb) in enumerate(zip(a, b)):
        if la != lb:
            break
        shared_prefix = i + 1
    shared = a[:shared_prefix]
    only_a = a[shared_prefix:]
    only_b = b[shared_prefix:]
    return {
        "image_a": image_a,
        "image_b": image_b,
        "layers_a": len(a),
        "layers_b": len(b),
        "shared_prefix_count": shared_prefix,
        "shared_layer_digests": shared,
        "diverged_a": only_a,
        "diverged_b": only_b,
        "dependencies_likely_shared": shared_prefix >= 2 and len(only_a) >= 1 and len(only_b) >= 1,
    }


def build_layered_analysis(
    *,
    fat_java: dict,
    layered_java: dict,
    fat_java2: dict | None,
    layered_java2: dict | None,
    time_to_healthy: dict | None,
) -> dict:
    """Assemble analysis payload for the report (sizes in bytes)."""
    out: dict = {
        "fat_image": fat_java.get("image"),
        "layered_image": layered_java.get("image"),
        "fat_size_bytes": fat_java.get("size_bytes"),
        "layered_size_bytes": layered_java.get("size_bytes"),
        "layer_groups": None,
        "rootfs_compare": None,
        "footprint": None,
        "time_to_healthy_sec": time_to_healthy,
    }

    if fat_java.get("success_measurement"):
        groups = layer_group_sizes_from_fat_image(fat_java["image"])
        out["layer_groups"] = groups

    if (
        layered_java.get("success_measurement")
        and layered_java2
        and layered_java2.get("success_measurement")
    ):
        out["rootfs_compare"] = compare_rootfs(
            layered_java["image"], layered_java2["image"]
        )

    fat_sz = fat_java.get("size_bytes")
    fat2_sz = fat_java2.get("size_bytes") if fat_java2 else None
    lay_sz = layered_java.get("size_bytes")
    lay2_sz = layered_java2.get("size_bytes") if layered_java2 else None
    groups = (out.get("layer_groups") or {}).get("groups_bytes") or {}
    deps = groups.get("dependencies", 0)
    loader = groups.get("spring-boot-loader", 0)
    snap = groups.get("snapshot-dependencies", 0)
    app = groups.get("application", 0)
    shared_app_layers = deps + loader + snap

    if isinstance(fat_sz, int) and isinstance(fat2_sz, int):
        two_fat = fat_sz + fat2_sz
    else:
        two_fat = None

    # Model: one shared base approximated as layered - application group,
    # plus two application groups (from extract sizes).
    if (
        isinstance(lay_sz, int)
        and isinstance(lay2_sz, int)
        and groups
        and app
    ):
        # shared ≈ layered_total - application (per image) ; then + 2*app
        shared_runtime = lay_sz - app
        two_layered_shared = shared_runtime + app + app
        out["footprint"] = {
            "two_fat_bytes": two_fat,
            "two_layered_with_shared_model_bytes": two_layered_shared,
            "naive_two_layered_bytes": lay_sz + lay2_sz,
            "shared_runtime_approx_bytes": shared_runtime,
            "application_group_bytes": app,
            "dependency_groups_bytes": shared_app_layers,
            "note": (
                "shared_runtime_approx = size(layered java) − application group; "
                "two_layered_with_shared_model = shared_runtime + 2×application; "
                "assumes identical shared layers between apps (see rootfs_compare)."
            ),
        }
    elif isinstance(fat_sz, int) and isinstance(fat2_sz, int):
        out["footprint"] = {"two_fat_bytes": two_fat}

    return out
