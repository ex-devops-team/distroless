## Why

Python sample сейчас описывает зависимости в `requirements.txt` / `requirements-dev.txt`. Современный стандарт — `pyproject.toml` (PEP 621): один манифест для runtime и dev, проще сопровождать Docker quality/runtime stages.

## What Changes

- Заменить `apps/python/requirements.txt` и `requirements-dev.txt` на `apps/python/pyproject.toml` (runtime + optional `dev`).
- Обновить `Dockerfile.baseline` и `Dockerfile.distroless`: установка через `pip install` из `pyproject.toml` (prod / `.[dev]`).
- Удалить устаревшие requirements-файлы.
- Сохранить версии зависимостей (FastAPI, uvicorn, pytest, httpx, ruff) и Python 3.11 для distroless wheels.

## Capabilities

### New Capabilities

### Modified Capabilities
- `sample-apps`: Python FastAPI sample MUST объявлять зависимости в `pyproject.toml`, а не в `requirements*.txt`.

## Impact

- `apps/python/pyproject.toml`, Dockerfiles, возможно README (если упоминаются requirements).
- Quality gate и runtime install в образах.
- Повторный build Python baseline/distroless для проверки smoke.
