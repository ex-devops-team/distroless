## Context

Репозиторий пустой с точки зрения приложений (есть только OpenSpec-скелет). Нужен небольшой, локально воспроизводимый эксперимент: sample-apps + Dockerfiles + скрипт замера. Мотивация — см. `proposal.md` (Why). Поведение — см. specs `sample-apps` и `metrics-report`.

Ограничения первого прогона: одна платформа (`linux/amd64`), минимальные зависимости приложений, без продакшен-оркестрации.

## Goals / Non-Goals

**Goals:**
- Единая матрица образов и один скрипт «собрать → smoke → size → scan → отчёт».
- Сопоставимые baseline vs distroless для Java / Python / Go; для Node — baseline + dynamic + static.
- Прозрачные допущения по базовым образам и сканеру, зафиксированные в README/отчёте.

**Non-Goals:**
- Оптимизация под минимально возможный размер «во что бы то ни стало» (например, GraalVM native-image как обязательный трек).
- Сравнение всех экосистемных альтернатив (Chainguard, Alpine-only matrix, multi-arch).
- Полный CI/CD и публикация образов в registry (достаточно локальной сборки).
- Нагрузочное/latency-тестирование — только smoke HTTP.

## Decisions

### 1. Структура репозитория
- `apps/{java,nodejs,python,go}/` — исходники минимальных HTTP-сервисов.
- `apps/<lang>/Dockerfile.*` или `docker/<lang>/` — варианты образов рядом с приложением.
- `scripts/benchmark.sh` (или аналог) — оркестрация прогона.
- `reports/` — генерируемый markdown-отчёт (не ручное редактирование как источник истины).

**Альтернатива:** monorepo с Bazel/ko — отвергнуто как избыточное для маленького эксперимента.

### 2. Baseline-образы
| Язык | Baseline (предпочтение) |
|------|-------------------------|
| Java | `eclipse-temurin:<LTS>-jre-jammy` (или `*-jre`) |
| Node.js | `node:<LTS>-slim` |
| Python | `python:<3.x>-slim` |
| Go | `golang` build → runtime `debian:bookworm-slim` **или** `alpine` — зафиксировать один и не смешивать в одном прогоне |

**Почему:** slim ближе к «типичному» корпоративному baseline, чем full; alpine отдельно не обязателен в v1.

### 3. Distroless-базы (Google)
| Язык | Distroless runtime |
|------|--------------------|
| Java | `gcr.io/distroless/java21-debian12` (или актуальный LTS-тег) |
| Node dynamic | `gcr.io/distroless/nodejs22-debian12` (или LTS) |
| Node static | `gcr.io/distroless/static-debian12` (или `cc` если нужны libc-зависимости бинаря) |
| Python | `gcr.io/distroless/python3-debian12` |
| Go | `gcr.io/distroless/static-debian12` при `CGO_ENABLED=0` |

Мультистейдж: builder = официальный SDK-образ, final = distroless/baseline.

### 4. Node.js: dynamic vs static
- **Dynamic:** `npm ci --omit=dev` → копирование app + `node_modules` в `distroless/nodejs*`, `CMD` через node entrypoint.
- **Static:** Node **SEA** (Single Executable Application) или эквивалент «один бинарь»: сборка blob + embed в node binary / tooling, результат копируется в `distroless/static*` (или `cc`, если бинарь динамически линкуется с libc). Цель — сравнить «Node как runtime в образе» vs «один исполняемый файл».

**Альтернативы:** `pkg`/`nexe` (устаревают/хрупки), Bun compile — можно упомянуть как follow-up, не в v1.

### 5. Приложения
Один endpoint `GET /health` → `200` + короткий JSON/text. Порт единый (например `8080`). Без БД, без auth, без фреймворков тяжёлее необходимого (для Java — простой embedded server; для Python — stdlib `http.server` или ultralight framework; Node — `http`; Go — `net/http`).

### 6. Метрики и сканер
- **Size:** `docker image inspect` / `docker images --format` → размер в байтах (локальный uncompressed-ish size Docker; в отчёте явно подписать «docker local size»).
- **CVE:** **Grype** (`grype <image> -o json`); агрегация CRITICAL/HIGH/MEDIUM/LOW по полям severity.
- В отчёт писать версию Grype (`grype version`), сведения о DB и дату прогона.
- Smoke: `docker run` + `curl`/`wget` с retries и timeout.

**Альтернатива:** Trivy — отвергнута по выбору эксперимента; сравнение сканеров между собой не входит в scope.

### 7. Отчёт
Markdown-таблица: Language | Variant | Image | Size (MB) | Crit | High | Med | Low | Smoke. Генерация из JSON intermediate-файлов в `reports/raw/`.

## Risks / Trade-offs

- [Разные CVE DB / версии Grype меняют цифры] → Фиксировать версию Grype и DB в README/отчёте; печатать timestamp прогона.
- [SEA для Node сложнее и платформозависим] → Держать static как отдельный Dockerfile; при блокере — зафиксировать failure в отчёте, не ломая остальные языки.
- [Python/Java distroless всё равно тянут runtime] → Ожидаемо; эксперимент показывает относительный выигрыш, не «ноль CVE».
- [Сравнение size «docker local» ≠ digest compressed] → Явно описать метрику в отчёте; не смешивать с `docker hub` compressed size без пометки.
- [Версии LTS базовых образов устареют] → Пинить minor/digest где практично; документировать выбранные теги в матрице.

## Migration Plan

Не применимо (greenfield). Откат = удаление `apps/`, `scripts/`, `reports/`.

## Open Questions

- Точные LTS-теги (Node 22 vs 20, Java 21 vs 17) — выбрать актуальные на момент реализации и зафиксировать в матрице.
- Нужен ли второй baseline на Alpine для тех же apps — отложено; не блокирует v1.
