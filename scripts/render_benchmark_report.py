#!/usr/bin/env python3
"""Render markdown benchmark report from meta + result JSON files."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def mb(b) -> str:
    if b is None:
        return "—"
    return f"{b / (1024 * 1024):.1f}"


def mb_precise(b) -> str:
    """For tiny layer groups (application often << 0.1 MiB)."""
    if b is None:
        return "—"
    x = b / (1024 * 1024)
    if x > 0 and x < 0.05:
        return f"{x:.3f}"
    return f"{x:.1f}"


def pair_comparable_map(rows: list) -> dict:
    lineage: dict = {}
    for r in rows:
        lang = r["language"]
        v = r.get("variant")
        if lang == "java":
            if v == "baseline-jlink":
                lineage.setdefault(lang, {})["baseline"] = r.get("distro_lineage")
            if v == "distroless-jlink":
                lineage.setdefault(lang, {})["distroless"] = r.get("distro_lineage")
            continue
        if v in ("baseline", "distroless"):
            lineage.setdefault(lang, {})[v] = r.get("distro_lineage")
        if v == "distroless-dynamic":
            lineage.setdefault(lang, {})["distroless_pair"] = r.get("distro_lineage")
    comparable = {}
    for lang, pair in lineage.items():
        dist = pair.get("distroless") or pair.get("distroless_pair")
        comparable[lang] = bool(pair.get("baseline") and dist and pair["baseline"] == dist)
    return comparable


def language_order(rows: list) -> list[str]:
    order: list[str] = []
    for r in rows:
        if r["language"] not in order:
            order.append(r["language"])
    return order


def successful_pairs(rows: list) -> list[tuple[str, dict, dict]]:
    by_lang: dict = {}
    for r in rows:
        by_lang.setdefault(r["language"], {})[r["variant"]] = r
    pairs = []
    for lang in language_order(rows):
        variants = by_lang.get(lang) or {}
        if lang == "java":
            base = variants.get("baseline-jlink")
            dist = variants.get("distroless-jlink")
        else:
            base = variants.get("baseline")
            dist = variants.get("distroless") or variants.get("distroless-dynamic")
        if (
            base
            and dist
            and base.get("success_measurement")
            and dist.get("success_measurement")
        ):
            pairs.append((lang, base, dist))
    return pairs


def breakdown(row: dict) -> dict:
    return (row.get("cve") or {}).get("breakdown") or {}


def empty_sev() -> dict:
    return {"critical": 0, "high": 0, "medium": 0, "low": 0, "unknown": 0, "total": 0}


def bucket(row: dict, klass: str) -> dict:
    return breakdown(row).get(klass) or empty_sev()


def app_sev_tuple(row: dict) -> tuple:
    b = bucket(row, "app")
    return (b.get("critical", 0), b.get("high", 0), b.get("medium", 0), b.get("low", 0))


def total_sev(row: dict) -> dict:
    """os + app + unknown (classification) by severity; equals image totals."""
    os_b, app_b, unk_b = bucket(row, "os"), bucket(row, "app"), bucket(row, "unknown")
    out = {}
    for key in ("critical", "high", "medium", "low", "unknown"):
        out[key] = os_b.get(key, 0) + app_b.get(key, 0) + unk_b.get(key, 0)
    out["total"] = os_b.get("total", 0) + app_b.get("total", 0) + unk_b.get("total", 0)
    return out


def sev_cells(b: dict) -> tuple:
    return (
        b.get("critical", 0),
        b.get("high", 0),
        b.get("medium", 0),
        b.get("low", 0),
    )


def cve_row(lang: str, slice_name: str, b: dict, unknown_cell) -> str:
    c, h, m, l = sev_cells(b)
    return f"| {lang} | {slice_name} | {c} | {h} | {m} | {l} | {unknown_cell} |"


def pair_notes(lang: str, base: dict, dist: dict, pair_comparable: dict) -> list[str]:
    notes: list[str] = []
    if lang == "java":
        notes.append("comparable pair = baseline-jlink vs distroless-jlink; full JRE — в секции Java 2×2")
    if lang == "nginx":
        notes.append("nginx vs Go file server — Application/size distroless другой бинарь")
    if not pair_comparable.get(lang, False):
        notes.append("lineage mismatch")
    unk_b = bucket(base, "unknown").get("total", 0)
    unk_d = bucket(dist, "unknown").get("total", 0)
    if unk_b or unk_d:
        notes.append(f"unclassified CVE: baseline={unk_b}, distroless={unk_d}")
    base_sz = base.get("size_bytes")
    dist_sz = dist.get("size_bytes")
    if (
        isinstance(base_sz, int)
        and isinstance(dist_sz, int)
        and dist_sz > base_sz
    ):
        notes.append("distroless size > baseline; OS baseline size clamped to 0")
    return notes


def java_variants(rows: list) -> dict[str, dict]:
    return {
        r["variant"]: r
        for r in rows
        if r.get("language") == "java" and r.get("success_measurement")
    }


def fmt_cve_chml(row: dict | None) -> str:
    if not row:
        return "—"
    t = total_sev(row)
    c, h, m, l = sev_cells(t)
    return f"{c}/{h}/{m}/{l}"


def fmt_cve_os_app(row: dict | None) -> str:
    if not row:
        return "—"
    os_t = bucket(row, "os").get("total", 0)
    app_t = bucket(row, "app").get("total", 0)
    tot = total_sev(row).get("total", 0)
    return f"os={os_t} app={app_t} total={tot}"


def delta_mb(a, b) -> str:
    if not isinstance(a, int) or not isinstance(b, int):
        return "—"
    return f"{(b - a) / (1024 * 1024):+.1f}"


def render_java_2x2(rows: list) -> list[str]:
    jv = java_variants(rows)
    need = ("baseline", "distroless", "baseline-jlink", "distroless-jlink")
    if not all(k in jv for k in need):
        missing = [k for k in need if k not in jv]
        return [
            "",
            "## Java: full JRE vs jlink (2×2)",
            "",
            f"_Неполная матрица Java (нет: {', '.join(missing)})._",
            "",
        ]

    fb, fd = jv["baseline"], jv["distroless"]
    jb, jd = jv["baseline-jlink"], jv["distroless-jlink"]
    fb_sz, fd_sz = fb.get("size_bytes"), fd.get("size_bytes")
    jb_sz, jd_sz = jb.get("size_bytes"), jd.get("size_bytes")

    lines = [
        "",
        "## Java: full JRE vs jlink (2×2)",
        "",
        "Отделяем вклад **distroless** (OS-база) и **jlink** (урезанный JRE). "
        "Строки — класс OS-базы; колонки — полный JRE vs jlink.",
        "",
        "### Size (MB)",
        "",
        "| | full JRE | jlink | Δ full→jlink |",
        "|---|----------|-------|--------------|",
        f"| baseline | {mb(fb_sz)} | {mb(jb_sz)} | {delta_mb(fb_sz, jb_sz)} |",
        f"| distroless | {mb(fd_sz)} | {mb(jd_sz)} | {delta_mb(fd_sz, jd_sz)} |",
        f"| Δ baseline→distroless | {delta_mb(fb_sz, fd_sz)} | {delta_mb(jb_sz, jd_sz)} |  |",
        "",
        f"- Комбо (full baseline → jlink distroless): {delta_mb(fb_sz, jd_sz)} MB",
        "",
        "### CVE (Crit/High/Med/Low) и OS/app totals",
        "",
        "| | full JRE | jlink |",
        "|---|----------|-------|",
        f"| baseline C/H/M/L | {fmt_cve_chml(fb)} | {fmt_cve_chml(jb)} |",
        f"| distroless C/H/M/L | {fmt_cve_chml(fd)} | {fmt_cve_chml(jd)} |",
        f"| baseline OS/app/total | {fmt_cve_os_app(fb)} | {fmt_cve_os_app(jb)} |",
        f"| distroless OS/app/total | {fmt_cve_os_app(fd)} | {fmt_cve_os_app(jd)} |",
        "",
        "- jlink *может* убрать CVE неиспользуемых модулей JDK; CVE fat jar (app) обычно те же; "
        "OS CVE: baseline full и baseline-jlink делят Temurin OS (сравниваем jlink); "
        "distroless full = java21, distroless-jlink = cc — OS разный; "
        "CVE fat jar обычно те же.",
        "",
    ]
    return lines


def render_java_layered(layered: dict | None) -> list[str]:
    lines = [
        "",
        "## Java: fat jar vs layered (jlink + distroless)",
        "",
        "Spring Boot layer groups + Docker layers на `distroless-jlink`. "
        "Цель — shared dependencies между apps (registry / node cache / pull-дельта).",
        "",
    ]
    if not layered:
        lines += ["_Секция не построена (нет успешных fat/layered измерений)._", ""]
        return lines

    groups = (layered.get("layer_groups") or {}).get("groups_bytes") or {}
    lines += [
        "### Layer groups (из fat jar via layertools)",
        "",
        "| Group | MB |",
        "|-------|----|",
    ]
    if groups:
        for name in (
            "dependencies",
            "spring-boot-loader",
            "snapshot-dependencies",
            "application",
        ):
            if name in groups:
                lines.append(f"| {name} | {mb_precise(groups[name])} |")
        total = (layered.get("layer_groups") or {}).get("groups_total_bytes")
        if total is not None:
            lines.append(f"| **sum groups** | {mb_precise(total)} |")
    else:
        err = (layered.get("layer_groups") or {}).get("error") or "n/a"
        lines.append(f"| — | extract failed: {err} |")

    lines += [
        "",
        "### Image size fat vs layered",
        "",
        "| Variant | Image | MB |",
        "|---------|-------|----|",
        f"| fat | `{layered.get('fat_image')}` | {mb(layered.get('fat_size_bytes'))} |",
        f"| layered | `{layered.get('layered_image')}` | {mb(layered.get('layered_size_bytes'))} |",
        "",
    ]

    cmp_ = layered.get("rootfs_compare")
    lines += ["### Shared Docker layers (java vs java2 layered)", ""]
    if cmp_:
        shared_n = cmp_.get("shared_prefix_count", 0)
        lines.append(
            f"- Shared RootFS prefix: **{shared_n}** / "
            f"{cmp_.get('layers_a')} vs {cmp_.get('layers_b')} layers"
        )
        if cmp_.get("dependencies_likely_shared"):
            lines.append(
                "- Digests расходятся после общего префикса (ожидаемо на application); "
                "общий prefix включает base/jre/dependencies при совпадении байтов."
            )
        elif shared_n == 0:
            lines.append(
                "- Общих RootFS digest'ов с начала нет — jlink/base слои различаются "
                "(частый эффект разных jdeps/jlink сборок); смотри размеры groups выше."
            )
        else:
            lines.append(f"- Shared digests (prefix): `{cmp_.get('shared_layer_digests')}`")
    else:
        lines.append("- java2 layered не измерен — сравнение digests пропущено.")

    fp = layered.get("footprint") or {}
    lines += [
        "",
        "### Registry footprint model (2 apps)",
        "",
        "| Model | MB |",
        "|-------|----|",
        f"| 2 × fat | {mb(fp.get('two_fat_bytes'))} |",
        f"| 2 × layered (naive, no share) | {mb(fp.get('naive_two_layered_bytes'))} |",
        f"| layered shared model (1×shared + 2×app group) | "
        f"{mb(fp.get('two_layered_with_shared_model_bytes'))} |",
        "",
    ]
    if fp.get("note"):
        lines.append(f"- {fp['note']}")
    if isinstance(fp.get("two_fat_bytes"), int) and isinstance(
        fp.get("two_layered_with_shared_model_bytes"), int
    ):
        save = fp["two_fat_bytes"] - fp["two_layered_with_shared_model_bytes"]
        lines.append(f"- Δ vs 2×fat (model): {mb(save)} MB "
                     f"({'экономия' if save > 0 else 'без экономии / модель грубая'})")

    ttfb = layered.get("time_to_healthy_sec")
    lines += ["", "### time-to-healthy (median)", ""]
    if ttfb:
        fat_t = (ttfb.get("fat") or {}).get("median_sec")
        lay_t = (ttfb.get("layered") or {}).get("median_sec")
        lines.append(
            f"- fat: **{fat_t if fat_t is not None else '—'}** s; "
            f"layered: **{lay_t if lay_t is not None else '—'}** s "
            f"(N={(ttfb.get('fat') or {}).get('samples')}, "
            f"шум Docker Desktop возможен)."
        )
        note = (ttfb.get("fat") or {}).get("note")
        if note:
            lines.append(f"- {note}")
    else:
        lines.append("- Старт не измерялся.")

    lines.append("")
    return lines


def render(
    meta: dict,
    rows: list,
    meta_name: str,
    result_names: list[str],
    layered_analysis: dict | None = None,
) -> str:
    pair_comparable = pair_comparable_map(rows)
    pairs = successful_pairs(rows)
    lines = [
        "# Distroless runtime benchmark report",
        "",
        f"- **UTC:** {meta.get('timestamp_utc')}",
        f"- **Run ID:** `{meta.get('run_id')}`",
        f"- **Platform:** `{meta.get('platform')}`",
        f"- **Size metric:** {meta.get('size_metric')}",
        f"- **Grype:** {meta.get('grype_version_summary') or 'see raw meta'}",
        "",
        "## Size: OS vs application (heuristic)",
        "",
        "Не слойный анализ (не разбор Docker-слоёв). Формулы: Application ≈ size(distroless); "
        "OS baseline ≈ max(0, baseline−distroless); **OS distroless = 0** — весь измеренный "
        "size(distroless) отнесён к Application. Это **не** значит, что в distroless нет ОС/пакетов, "
        "и **не** равно нулю OS CVE (см. CVE-таблицу). "
        "Для Java comparable pair = **baseline-jlink** vs **distroless-jlink** (full JRE — в секции 2×2).",
        "",
        "| Language | OS baseline | OS distroless | Application | Total baseline | Total distroless | Notes |",
        "|----------|-------------|---------------|-------------|----------------|------------------|-------|",
    ]

    for lang, base, dist in pairs:
        notes = "; ".join(pair_notes(lang, base, dist, pair_comparable))
        base_sz = base.get("size_bytes")
        dist_sz = dist.get("size_bytes")
        if isinstance(base_sz, int) and isinstance(dist_sz, int):
            os_base = max(0, base_sz - dist_sz)
            os_dist = 0
            app_sz = dist_sz
        else:
            os_base = os_dist = app_sz = None
        lines.append(
            f"| {lang} | {mb(os_base)} | {mb(os_dist)} | {mb(app_sz)} | "
            f"{mb(base_sz if isinstance(base_sz, int) else None)} | "
            f"{mb(dist_sz if isinstance(dist_sz, int) else None)} | {notes} |"
        )

    lines += render_java_2x2(rows)
    lines += render_java_layered(layered_analysis)

    lines += [
        "## CVE: OS vs application",
        "",
        "Только успешные smoke. OS = пакеты дистрибутива; Application = language ecosystem / binary приложения; Unknown = не классифицировано (входит в Total). "
        "Для Java — пара jlink (см. также секцию 2×2).",
        "",
        "| Language | Slice | Crit | High | Med | Low | Unknown |",
        "|----------|-------|------|------|-----|-----|---------|",
    ]

    for lang, base, dist in pairs:
        os_b, os_d = bucket(base, "os"), bucket(dist, "os")
        app_b, app_d = bucket(base, "app"), bucket(dist, "app")
        tot_b, tot_d = total_sev(base), total_sev(dist)
        unk_b = bucket(base, "unknown").get("total", 0)
        unk_d = bucket(dist, "unknown").get("total", 0)

        lines.append(cve_row(lang, "OS baseline", os_b, "—"))
        lines.append(cve_row(lang, "OS distroless", os_d, "—"))
        if app_sev_tuple(base) == app_sev_tuple(dist):
            lines.append(cve_row(lang, "Application", app_b, "—"))
        else:
            lines.append(cve_row(lang, "Application (baseline)", app_b, "—"))
            lines.append(cve_row(lang, "Application (distroless)", app_d, "—"))
        lines.append(cve_row(lang, "Total baseline", tot_b, unk_b))
        lines.append(cve_row(lang, "Total distroless", tot_d, unk_d))

    lines += [
        "",
        "## Matrix (smoke / tags)",
        "",
        "| Language | Variant | Distro | Comparable pair | Image | Smoke | Notes |",
        "|----------|---------|--------|-----------------|-------|-------|-------|",
    ]

    for r in rows:
        smoke = "ok" if r.get("smoke_ok") else "FAIL"
        note = ""
        if not r.get("success_measurement"):
            note = r.get("error") or "not a successful measurement"
        comparable = "n/a"
        v = r.get("variant")
        if r["language"] == "java":
            if v in ("baseline-jlink", "distroless-jlink"):
                comparable = "true" if pair_comparable.get("java", False) else "false"
            elif v in ("baseline", "distroless"):
                comparable = "2×2 only"
                if not note:
                    note = "full JRE (не jlink)"
            elif v == "distroless-jlink-layered":
                comparable = "layered"
                if not note:
                    note = "Spring Boot layers + jlink"
            if v in ("baseline-jlink", "distroless-jlink") and not note:
                note = "jlink custom JRE"
        elif r["language"] == "java2":
            comparable = "layered" if "layered" in str(v) else "fat pair"
            if not note:
                note = "second app for shared-layer experiment"
        elif v in ("baseline", "distroless", "distroless-dynamic"):
            comparable = "true" if pair_comparable.get(r["language"], False) else "false"
            if comparable == "false" and not note:
                note = "lineage mismatch: not for final baseline-vs-distroless conclusion"
        if r["language"] == "nginx" and v in ("distroless",) and not note:
            note = "Go file server, not nginx"
        lines.append(
            f"| {r['language']} | {r['variant']} | {r.get('distro_lineage', '—')} | {comparable} | `{r['image']}` | {smoke} | {note} |"
        )

    lines += ["", "## Interpretation notes", ""]
    non_comparable = sorted([lang for lang, ok in pair_comparable.items() if not ok])
    if non_comparable:
        lines.append("- Baseline-vs-distroless выводы делайте только для языков с Comparable pair = true.")
        lines.append("- Несопоставимые пары: " + ", ".join(non_comparable))
    else:
        lines.append("- Все baseline/distroless пары сопоставимы по distro lineage (Comparable pair = true).")
    lines.append(
        "- Node.js: baseline vs distroless-dynamic = Express. nginx — baseline nginx vs distroless Go file server (Application несопоставим)."
    )
    lines.append(
        "- Java: в общей таблице — baseline-jlink vs distroless-jlink; full Temurin / distroless java21 — только в секции Java 2×2; "
        "fat vs layered / java2 — в секции layered."
    )
    lines.append("- Quality toolchain (lint/test) выполняется в build stage и не входит в final runtime images.")
    lines.append(
        "- CVE Total = os + app + unknown того же образа. Таблица размера — эвристика (не слои): "
        "колонка OS distroless всегда 0, потому что весь size(distroless) в Application; "
        "OS CVE в distroless при этом может быть > 0."
    )
    if any(lang == "nginx" for lang, _, _ in pairs):
        lines.append("- nginx: размер/CVE Application на стороне distroless относятся к static Go server.")

    lines += ["", "## Failures / incomplete", ""]
    fails = [r for r in rows if not r.get("success_measurement")]
    if not fails:
        lines.append("_None — all matrix rows produced successful measurements._")
    else:
        for r in fails:
            lines.append(f"- `{r['image']}`: {r.get('error') or 'unknown error'}")

    lines += ["", "## Raw artifacts", "", f"- Meta: `{meta_name}`"]
    for name in result_names:
        lines.append(f"- `{name}`")

    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--meta", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--latest", required=True)
    parser.add_argument("results", nargs="+")
    args = parser.parse_args()
    meta_path = Path(args.meta)
    meta = json.loads(meta_path.read_text(encoding="utf-8"))
    result_paths = [Path(p) for p in args.results]
    rows = [json.loads(p.read_text(encoding="utf-8")) for p in result_paths]
    layered = None
    layered_name = meta.get("java_layered_analysis")
    if layered_name:
        cand = meta_path.parent / layered_name
        if cand.is_file():
            layered = json.loads(cand.read_text(encoding="utf-8"))
    text = render(meta, rows, meta_path.name, [p.name for p in result_paths], layered)
    Path(args.out).write_text(text, encoding="utf-8")
    Path(args.latest).write_text(text, encoding="utf-8")
    print("report →", args.out)
    print("report →", args.latest)


if __name__ == "__main__":
    main()
