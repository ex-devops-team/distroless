## Why

Стековая таблица размера (много строк Slice на один ЯП) мешает сравнивать срезы «глазами»: вклад OS/Application/Total размазан по вертикали. Нужен разворот: одна строка на язык, типы Slice — колонки. Параллельно в отчёте часто непонятно, почему **OS distroless = 0** при ненулевых OS CVE в distroless — это надо явно объяснить рядом с таблицей.

## What Changes

- **BREAKING** для читателей отчёта: таблица размера — **Language = строки**, **Slice = колонки** (OS baseline, OS distroless, Application, Total baseline, Total distroless; Notes).
- Эвристика чисел **без изменения**: Application ≈ size(distroless), OS baseline ≈ max(0, base−dist), OS distroless = **0 по определению эвристики** (не «в образе нет ОС»).
- Текст у таблицы / Interpretation notes MUST ясно объяснять, почему OS distroless size = 0 и что это ≠ CVE OS.
- Таблица CVE **не** пивотится в этом change (остаётся стековой).
- README: описание формата таблицы размера обновить под колонки Slice.

## Capabilities

### New Capabilities

- `metrics-report`: формат markdown-отчёта бенчмарка; пивот таблицы размера и пояснение эвристики OS distroless = 0.

### Modified Capabilities

<!-- нет -->

## Impact

- `scripts/render_benchmark_report.py` (секция Size)
- `make report` / `make bench` → новый вид `reports/latest.md`
- `README.md` (раздел про стековые/размерные таблицы)
