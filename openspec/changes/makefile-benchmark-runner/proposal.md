## Why

Оркестрация эксперимента сейчас в `scripts/benchmark.sh`: длинный bash с smoke/build/scan плохо читается и расходится с уже существующими Python-хелперами. Нужен единый вход через Makefile и удаление project bash-скриптов.

## What Changes

- **BREAKING:** заменить `./scripts/benchmark.sh` на Makefile-таргеты (например `make` / `make bench`, `make report`).
- Удалить `scripts/benchmark.sh`; оркестрацию перенести в Python (вызываемый из Make), сохранив `grype_breakdown.py`, `render_benchmark_report.py`, `regenerate_cve_breakdown.py`.
- Обновить README: быстрый старт через `make`.
- Поведение прогона (матрица, smoke, Grype, стековый отчёт) без изменений по смыслу.

## Capabilities

### New Capabilities
- `benchmark-runner`: точка входа эксперимента — Makefile; без standalone `.sh` драйверов в репозитории.

### Modified Capabilities
- `metrics-report`: отчёт обновляется командами Make (полный прогон / пересборка из raw), а не bash-скриптом.

## Impact

- Новый `Makefile`, новый `scripts/benchmark.py` (или эквивалент), удаление `scripts/benchmark.sh`.
- README и упоминания в docs.
- Требования: `make`, `docker`, `grype`, `python3`, `curl` (как сейчас).
