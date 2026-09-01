## Why

Текущие таблицы показывают CVE и размер по вариантам образа (строка = image), из‑за чего трудно сразу увидеть вклад ОС vs приложения и сравнить «сколько всего» у baseline и distroless. Нужен стековый формат по языку: OS baseline, OS distroless, приложение, итог baseline, итог distroless — и то же для размера.

## What Changes

- Заменить (как основной вид) широкую таблицу OS Crit/App Crit по вариантам на **стековые строки на язык**:
  - ЯП OS baseline
  - ЯП OS distroless
  - ЯП приложение
  - ЯП итого baseline (OS baseline + приложение)
  - ЯП итого distroless (OS distroless + приложение)
- Добавить **аналогичную таблицу размера** образа (OS vs приложение vs итоги).
- Сохранить классификацию Grype os/app/unknown; failed-smoke по-прежнему не как успешные измерения.
- Пересобрать `reports/latest.md` из существующих raw JSON (полный rebuild не обязателен).

## Capabilities

### New Capabilities

### Modified Capabilities
- `cve-os-app-breakdown`: таблица CVE — стек OS/приложение/итоги на язык, а не колонки OS+App в одной строке варианта.
- `metrics-report`: таблица размера в том же стековом разрезе; матрица образов остаётся служебной (smoke, tag, lineage).

## Impact

- Генератор markdown в `scripts/render_benchmark_report.py` (и вызов из `benchmark.sh`).
- README: пояснение строк стека и эвристики размера.
- Raw JSON: при необходимости явные поля итогов/эвристики размера; CVE breakdown уже есть.
- Содержимое `reports/latest.md`.
