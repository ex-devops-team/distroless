## Context

См. `proposal.md`. Сейчас единственный project bash — `scripts/benchmark.sh` (~280 строк): матрица, smoke, grype, запись result JSON, вызов `render_benchmark_report.py`. Python-хелперы уже есть.

## Goals / Non-Goals

**Goals:**
- Makefile как UX (`make bench`, `make report`, `make help`).
- Удалить `scripts/benchmark.sh`.
- Сохранить семантику прогона и формат raw/отчёта.

**Non-Goals:**
- Переписывать Dockerfiles / apps.
- Менять классификацию CVE или стековые таблицы.
- GNU Make-only магия без переносимости на BSD make — ориентир GNU Make (macOS: brew make / gmake при необходимости зафиксировать в README).

## Decisions

### 1) Make = тонкий вход, Python = оркестрация

Smoke с retries и записью JSON в чистом Make неудобны. Перенести логику `benchmark.sh` в `scripts/benchmark.py`; Makefile:

```makefile
.PHONY: bench report help
bench:
	python3 scripts/benchmark.py
report:
	python3 scripts/regenerate_cve_breakdown.py
help:
	@echo ...
```

Альтернатива «всё в Makefile recipes» отвергнута из‑за smoke-циклов.

### 2) Имена целей

- `make` / `make bench` — полный прогон (default).
- `make report` — пересборка из raw.
- `make help` — список целей.

### 3) Совместимость API

Переменные окружения как сейчас: `PLATFORM`, `PORT`, `SMOKE_RETRIES`, `SMOKE_SLEEP` — пробрасывать в Python.

### 4) Shell в recipes

Допускаются однострочные `/bin/sh` вызовы `python3 ...` в Makefile; standalone `.sh` файлов проекта не должно быть.

## Risks / Trade-offs

- [Пользователи зовут старый путь] → README + краткий note в удалённом месте не нужен; breaking в proposal.
- [BSD make на macOS] → документировать GNU Make при несовместимости.

## Migration Plan

1. Добавить `scripts/benchmark.py` (порт с `benchmark.sh`).
2. Добавить корневой `Makefile`.
3. Удалить `scripts/benchmark.sh`.
4. Обновить README.
5. Smoke-check: `make report` на существующих raw; опционально короткий `make bench` одной пары не требуется — полный bench по возможности.
