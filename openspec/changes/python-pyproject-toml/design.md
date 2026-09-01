## Context

См. `proposal.md`. Сейчас `apps/python` ставит пакеты через `pip install -r requirements*.txt` в quality/runtime/build stages. Distroless остаётся на Python 3.11.

## Goals / Non-Goals

**Goals:**
- Единый `pyproject.toml` (runtime + `dev` extras).
- Dockerfiles без `requirements*.txt`.
- Quality toolchain только в quality stage.

**Non-Goals:**
- Poetry/uv lockfile как обязательный runtime (достаточно pip + pyproject).
- Менять версии FastAPI/uvicorn без нужды.
- Перенос ruff-конфига из `ruff.toml` (опционально позже).

## Decisions

### 1) PEP 621 + hatchling/setuptools minimal

```toml
[project]
name = "distroless-bench-python"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = ["fastapi==…", "uvicorn[standard]==…"]

[project.optional-dependencies]
dev = ["pytest==…", "httpx==…", "ruff==…"]

[build-system]
requires = ["setuptools>=61"]
build-backend = "setuptools.build_meta"
```

Пакет может быть «почти empty» (только metadata) — `main.py` остаётся скриптом; `pip install .` / `pip install ".[dev]"` ставит deps. Альтернатива: `pip install --no-deps` + list — отвергнута, нужен стандартный install.

Для distroless `--target=/deps`: `pip install --target=/deps .` (без editable).

### 2) Docker

Quality: `COPY pyproject.toml` (+ нужные src files для setuptools) → `pip install ".[dev]"` → copy tests → ruff/pytest.  
Runtime/build: `pip install .` или `pip install --target=/deps .`.

Если setuptools требует пакетный layout: добавить минимальный `[tool.setuptools]` `py-modules = []` / packages find, либо `package-dir` — зафиксировать при apply так, чтобы `pip install .` не падал без packaging `main` как module (main остаётся COPY отдельно как сейчас).

Практичный путь: `pip install --no-cache-dir ".[dev]"` с `pyproject.toml` где зависимости в `[project]`, и `TOOL.setuptools.packages.find` where = [] или use `pip install` with `--use-pep517` only deps via:

Actually the cleanest for a non-packaged app script:
```
pip install --no-cache-dir .
```
with setuptools and:
```
[tool.setuptools]
py-modules = []
```
Or include main as module. Current CMD is `uvicorn main:app` with main.py at /app — keep COPY main.py separate; pyproject only for dependency metadata.

`pip install .` with empty packages still installs project.dependencies. Good.

### 3) Delete requirements*.txt

После миграции удалить оба файла.

## Risks / Trade-offs

- [setuptools layout errors] → минимальный py-modules config, проверить оба Dockerfile.
- [3.11 vs 3.12] → сохранить разные FROM как сейчас.

## Migration Plan

1. Добавить `pyproject.toml`.
2. Обновить оба Dockerfile.
3. Удалить requirements*.txt.
4. `docker build` python baseline + distroless (или через make bench для python — достаточно ручной build+smoke).
