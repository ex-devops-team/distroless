## Context

См. `proposal.md`. Текущие apps — минимальные HTTP без фреймворков; Node static сейчас SEA. Нужен переход к репрезентативным стекам и quality-gate в multi-stage Docker build при сохранении Debian-first / distroless сравнения.

## Goals / Non-Goals

**Goals:**
- Заменить apps на Spring Boot / Express / FastAPI / Gin (или эквивалент).
- Node static = nginx + статические файлы (не SEA).
- Lint + unit tests в build stage; fail build on error.
- Исключить quality toolchain из final image.
- Сохранить возможность прогона `scripts/benchmark.sh` и lineage/comparable.

**Non-Goals:**
- Полноценный frontend SPA / BFF / auth / БД.
- Полный CI на GitHub Actions как обязательный deliverable (локальный docker build = источник истины).
- Сравнение всех возможных линтеров экосистемы.

## Decisions

### 1) Стек приложений
| Язык | Framework | Lint | Tests |
|------|-----------|------|-------|
| Java | Spring Boot 3.x (Web) | Spotless или Checkstyle | JUnit 5 |
| Node dynamic | Express | ESLint | Jest или node:test |
| Node static | nginx + статический `index`/`health` | n/a для app code; config lint опционально (`nginx -t` в build) | smoke/`nginx -t` как quality check |
| Python | FastAPI + uvicorn | Ruff | pytest |
| Go | Gin | golangci-lint | `go test` |

**Почему Gin:** распространённый аналог Express/FastAPI по уровню абстракции; легче держать тонкий `/health`.

### 2) Multi-stage layout (общий паттерн)
1. `deps` / `quality` — установка toolchain + lint + test (fail on error)
2. `build` — сборка runtime-артефакта без копирования test/lint deps в output
3. `runtime` — baseline или distroless; только artifact + runtime deps

Для Node Express: `npm ci` с prod отдельно от `npm ci` including dev в quality stage.  
Для Python: `pip install` prod requirements в runtime layer; `requirements-dev.txt` только в quality.  
Для Java: Maven/Gradle `test` + `verify` в builder; final копирует fat jar.  
Для Go: `golangci-lint` + `go test` в builder; final — static binary в distroless/static.

### 3) Nginx static
- Baseline: `nginx:1.x-bookworm` (Debian-aligned) + конфиг с `/health`.
- Distroless-совместимый вариант: по возможности `gcr.io/distroless`-friendly nginx binary / distroless static file server; если полноценный nginx-distroless недоступен — зафиксировать ограничение и использовать минимальный Debian nginx как «near-distroless» только с пометкой, либо `nginx-unprivileged` на bookworm-slim как baseline pair и отдельный static binary на distroless/static.
- Предпочтительное решение для эксперимента: baseline `nginx:bookworm` / distroless = статически собранный tiny static server **или** nginx из distroless ecosystem; выбрать на apply по доступности образов и задокументировать.

### 4) Проверка «toolchain не в final»
- Для Go/Java/Node/Python: отсутствие test runners в слое (проверка через `docker run` + `which`/отсутствие путей, или dive/trivy fs — достаточно документированной проверки `docker history`/`docker run --rm image sh -c` где shell есть; для distroless — отсутствие файлов toolchain по известным путям или сравнение размера/слоёв copy).
- Практичный критерий apply: quality stage не `COPY`ится в final; prod lockfile/requirements без dev.

### 5) Матрица benchmark
Сохранить теги `distroless-bench/<lang>:<variant>`, обновить README; Node SEA удалить из матрицы.

## Risks / Trade-offs

- [Nginx + distroless сложнее Express] → Зафиксировать выбранный pair в README; при блокере — comparable=false с пояснением.
- [Spring Boot сильно увеличит размер/CVE] → Это цель эксперимента; не оптимизировать prematurely.
- [golangci-lint version pin] → Пинить версию в Dockerfile builder.
- [Долгая сборка] → Кэш Docker layers для deps/quality.

## Migration Plan

1. Заменить исходники apps по языкам.
2. Переписать Dockerfiles под quality→build→runtime.
3. Обновить матрицу/README/benchmark.
4. Прогнать benchmark; сравнить с предыдущим «пустым» прогоном как baseline эксперимента v2.

## Open Questions

- Точный distroless-партнёр для nginx (официальный distroless nginx vs static file binary) — решить на apply по доступным образам без смены specs.
