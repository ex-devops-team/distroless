## ADDED Requirements

### Requirement: Python dependencies via pyproject.toml
Python FastAPI sample MUST объявлять runtime-зависимости в `apps/python/pyproject.toml` (PEP 621). Dev-зависимости для lint/tests MUST быть отделены (например optional-dependencies `dev`) и MUST NOT попадать в финальный runtime-образ. Файлы `requirements.txt` / `requirements-dev.txt` MUST NOT использоваться как источник зависимостей приложения.

#### Scenario: Runtime installs from pyproject
- **WHEN** собирается Python baseline или distroless runtime stage
- **THEN** зависимости устанавливаются из `pyproject.toml` без `requirements.txt`

#### Scenario: Quality uses pyproject dev extras
- **WHEN** выполняется quality stage Python-образа
- **THEN** lint/test зависимости берутся из `pyproject.toml` (dev extras), а не из `requirements-dev.txt`

#### Scenario: No requirements files remain
- **WHEN** change применён
- **THEN** в `apps/python/` нет `requirements.txt` и `requirements-dev.txt`
