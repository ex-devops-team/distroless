## Why

Минимальные sample-apps без зависимостей — хороший старт, но малорепрезентативны для реальных runtime-образов. Нужен следующий шаг эксперимента: типовые фреймворки (Spring Boot, Express, FastAPI, аналог на Go) плюс обязательные lint/unit-test на этапе сборки без попадания toolchain в финальный контейнер.

## What Changes

- **BREAKING** для sample-apps: заменить минимальные приложения на framework-based сервисы с реальными runtime-зависимостями.
- Java → Spring Boot с `/health` и юнит-тестами + линтер (Checkstyle/Spotless или аналог).
- Node.js dynamic → Express; Node.js static → раздача статики через **nginx** (вместо SEA).
- Python → FastAPI (+ uvicorn) с тестами и линтером (ruff/pytest).
- Go → веб-фреймворк того же класса (Gin) с тестами и линтером (golangci-lint / go test).
- Добавить gate в multi-stage build: lint и unit tests MUST выполняться при сборке образа; зависимости линтов/тестов MUST NOT попадать в финальный runtime-слой.
- Обновить матрицу образов/документацию и прогон benchmark под новые варианты (включая nginx static).

## Capabilities

### New Capabilities
- `build-quality-gate`: lint и unit tests как обязательный шаг сборки образа; исключение toolchain из финального контейнера.
- `sample-apps`: framework-based HTTP-приложения и варианты образов (baseline/distroless; Node dynamic Express и static nginx).
- `metrics-report`: сравнительный отчёт размера/CVE с учётом обновлённой матрицы (в т.ч. nginx static).

### Modified Capabilities

## Impact

- Полная переработка `apps/{java,nodejs,python,go}/` (зависимости, тесты, линтеры, Dockerfiles).
- Изменение Node static: SEA → nginx; возможны новые базовые образы для nginx (Debian-aligned).
- Удлинение времени сборки образов из-за lint/test stage.
- Рост размера baseline/distroless образов относительно текущего «почти пустого» старта — это ожидаемый эффект эксперимента.
