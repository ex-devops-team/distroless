#!/usr/bin/env python3
"""Classify Grype matches as os / app / unknown and count by severity."""

from __future__ import annotations

import json
import sys
from pathlib import Path

OS_TYPES = {
    "deb",
    "dpkg",
    "rpm",
    "apk",
    "alpm",
    "portage",
    "linux-kernel",
}
APP_TYPES = {
    "java-archive",
    "python",
    "npm",
    "yarn",
    "pnpm",
    "go-module",
    "dotnet",
    "gem",
    "php-composer",
    "rust-crate",
}

OS_PATH_PREFIXES = ("/usr/", "/lib/", "/lib64/", "/bin/", "/sbin/", "/var/lib/dpkg")


def _severity(match: dict) -> str:
    sev = str((match.get("vulnerability") or {}).get("severity") or "UNKNOWN").upper()
    if sev == "NEGLIGIBLE":
        return "LOW"
    return sev


def _paths(artifact: dict) -> list[str]:
    locs = artifact.get("locations") or []
    return [str(loc.get("path") or "") for loc in locs]


def _is_os_path(path: str) -> bool:
    return path.startswith(OS_PATH_PREFIXES) or path in ("/usr", "/lib", "/lib64", "/bin", "/sbin")


def classify_artifact(artifact: dict) -> str:
    typ = str(artifact.get("type") or "").lower()
    if typ in OS_TYPES:
        return "os"
    if typ in APP_TYPES:
        return "app"
    if typ == "binary":
        paths = _paths(artifact)
        if any(_is_os_path(p) for p in paths):
            return "os"
        return "app"
    return "unknown"


def empty_sev() -> dict:
    return {"critical": 0, "high": 0, "medium": 0, "low": 0, "unknown": 0, "total": 0}


def bump(bucket: dict, sev: str) -> None:
    key = {
        "CRITICAL": "critical",
        "HIGH": "high",
        "MEDIUM": "medium",
        "LOW": "low",
    }.get(sev, "unknown")
    bucket[key] += 1
    bucket["total"] += 1


def aggregate(matches: list) -> dict:
    totals = empty_sev()
    breakdown = {"os": empty_sev(), "app": empty_sev(), "unknown": empty_sev()}
    for match in matches:
        sev = _severity(match)
        bump(totals, sev)
        klass = classify_artifact(match.get("artifact") or {})
        bump(breakdown[klass], sev)
    return {
        "critical": totals["critical"],
        "high": totals["high"],
        "medium": totals["medium"],
        "low": totals["low"],
        "unknown": totals["unknown"],
        "total_matches": len(matches),
        "breakdown": breakdown,
    }


def main() -> None:
    path = Path(sys.argv[1])
    data = json.loads(path.read_text(encoding="utf-8"))
    print(json.dumps(aggregate(data.get("matches") or []), separators=(",", ":")))


if __name__ == "__main__":
    main()
