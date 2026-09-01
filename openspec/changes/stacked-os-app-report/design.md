## Context

См. `proposal.md`. Сейчас `reports/latest.md` — матрица по вариантам плюс широкая таблица OS/App колонок. Классификация Grype os/app/unknown и `size_bytes` уже есть в raw JSON. Размер слоёв OS vs app сканер не даёт.

## Goals / Non-Goals

**Goals:**
- Стековые таблицы CVE и размера как основной вид отчёта.
- Итоги CVE = os+app+unknown того же образа; итоги размера = docker Size.
- Пересборка из `reports/raw` без полного rebuild.

**Non-Goals:**
- Слойный анализ (dive/syft) для «настоящего» OS-size.
- Смена классификации Grype.
- Менять матрицу приложений / Dockerfiles.

## Decisions

### 1) Пять строк на язык (CVE)

| Строка | Источник |
|--------|----------|
| OS baseline | `cve.breakdown.os` baseline |
| OS distroless | `cve.breakdown.os` distroless (для Node — `distroless-dynamic`) |
| Application | `cve.breakdown.app`; одна строка, если Crit/High/Med/Low совпали; иначе две |
| Total baseline | os+app+unknown baseline (должно совпасть с текущим TOTAL) |
| Total distroless | os+app+unknown distroless |

Альтернатива «всегда одна Application из distroless» отвергнута: у Java/Node `app` различается, итог перестал бы сходиться.

Unknown классификации: входит в Total; если > 0 — колонка или Notes, не смешивать с app.

### 2) Эвристика размера (не слои)

Нет OS/app size в inspect. Прокси:

- Application = size(distroless)
- OS distroless = 0
- OS baseline = max(0, size(baseline) − size(distroless))
- Totals = измеренные `size_bytes`

Это **другая модель**, чем CVE (у Java distroless OS CVE ≠ 0, но OS size эвристически 0). Подписать в README и notes отчёта.

Альтернатива (dive/syft) — out of scope.

### 3) Служебная матрица

Оставить компактную таблицу: Language, Variant, Image, Distro, Comparable, Smoke, Notes — без дублирования CVE/size колонок, чтобы не спорить с стеком.

### 4) nginx

Пара несопоставима по приложению (nginx vs Go file server). Стек всё равно строить, Notes: Application/size distroless — другой бинарь.

## Risks / Trade-offs

- [Эвристика размера путает с CVE OS] → Явная подпись «size heuristic, not layers».
- [distroless > baseline] → OS baseline = 0 + Notes.
- [App CVE различаются] → две строки Application, не подгонять одну цифру.

## Migration Plan

1. Обновить `render_benchmark_report.py`.
2. README: стек + эвристика размера.
3. `python3 scripts/regenerate_cve_breakdown.py` (или эквивалент) для `latest.md`.
