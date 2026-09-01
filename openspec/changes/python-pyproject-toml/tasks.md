## 1. Packaging

- [x] 1.1 Добавить `apps/python/pyproject.toml` (runtime deps + optional `dev`, setuptools)
- [x] 1.2 Обновить `Dockerfile.baseline` и `Dockerfile.distroless` на `pip install` из pyproject
- [x] 1.3 Удалить `requirements.txt` и `requirements-dev.txt`

## 2. Проверка

- [x] 2.1 Собрать Python baseline и distroless; убедиться quality (ruff/pytest) и smoke `/health`
