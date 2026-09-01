## Context

Сейчас Java в матрице: full / jlink × baseline / distroless; comparable pair и «лучший» стек — `distroless-jlink` с одним fat jar в одном Docker-слое. См. proposal.md — Why. Spring Boot 3.4 уже в `apps/java`; layered jars — штатная фича `spring-boot-maven-plugin` + `jarmode=layertools`.

## Goals / Non-Goals

**Goals:**
- Измерить долю fat jar / Docker-слоёв: dependencies (+ loader) vs application.
- Показать переиспользование dependency-слоёв между двумя apps на **jlink + distroless**.
- Зафиксировать в отчёте оценку registry footprint и (по возможности) time-to-healthy.

**Non-Goals:**
- Прод-готовый multi-app monorepo / shared base image в registry CI.
- Менять существующую 2×2 full/jlink CVE-секцию (кроме ссылки «см. также»).
- GraalVM native-image; CDS/AppCDS как основной эксперимент.
- Утверждать экономию CVE от layering (слои не уменьшают jar CVE сами по себе).

## Decisions

### 1. Стек сравнения
Сравнивать **fat** `distroless-jlink` (уже есть) vs новый **`distroless-jlink-layered`** (тот же jlink на `cc-debian12`, jar извлечён layertools, `JarLauncher`). Baseline Temurin layered — опционально later; для тезиса cache/registry достаточно distroless+jlink.

**Альтернатива:** только анализ размеров внутри fat jar без Docker layers — отвергнуто: не доказывает digest reuse на нодах.

### 2. Layer groups
Стандарт Spring Boot: `dependencies`, `spring-boot-loader`, `snapshot-dependencies`, `application`. В Dockerfile копировать в этом порядке (application последним). Измерять `du` по extracted dirs + `docker history` / layer digests через `docker image inspect` / `crane`/`docker buildx imagetools` — что уже доступно локально без новых тяжёлых deps; предпочтительно digests из `RepoDigests`/rootfs layers inspect.

### 3. Второе приложение
`apps/java-health2/` (или `apps/java2/`): клон стека `spring-boot-starter-web` 3.4.1, другой `artifactId` и чуть другой JSON `/health` (например `"app":"health2"`), тот же Java 21. Одинаковые версии зависимостей → одинаковый `dependencies` layer content.

**Альтернатива:** Maven multi-module в одном `apps/java` — ок, но два независимых Docker context проще для MATRIX.

### 4. pom: enable layers
В обоих pom: `spring-boot-maven-plugin` → `<layers><enabled>true</enabled></layers>`. Fat-образ может продолжать копировать один jar (layers внутри jar не мешают); layered Dockerfile делает `extract` в build stage.

### 5. Метрики в отчёте
| Метрика | Как |
|---------|-----|
| Layer sizes MB | `du -sb` после extract; сверить с docker layer sizes |
| Shared digest | сравнить layer digests image1 vs image2 для dependencies (+ loader) |
| Registry footprint (модель) | `2 × size(fat)` vs `size(shared_layers) + size(app1) + size(app2)` (+ jre/base один раз) |
| time-to-healthy | опционально: wall clock от `docker run` до HTTP 200 (N≥3, median); если шум велик — пометить |

### 6. MATRIX
Добавить варианты: `java` / `distroless-jlink-layered`, `java2` / `distroless-jlink-layered` (и при необходимости fat для java2). Общая языковая Size-таблица: Java comparable pair не ломать (по-прежнему jlink pair); layered — только в новой секции.

## Risks / Trade-offs

- [Digest mismatch из-за timestamps/SNAPSHOT в dependencies] → Mitigation: release-версии Spring; reproducible где возможно; если mismatch — явно в отчёте.
- [Layered образ чуть больше fat из-за extract + loader layout] → Mitigation: сравнивать честно; тезис про cache/дельта, не обязательно меньший single image.
- [time-to-healthy шумный на Docker Desktop] → Mitigation: median, или skip с пометкой.
- [Рост времени `make bench`] → Mitigation: +2 образа приемлемо; cache BuildKit.
- [Main `sample-apps` spec ещё не synced с 2×2] → Mitigation: этот change только ADDED layered requirements; sync/archive порядка — отдельно.

## Migration Plan

1. Enable layers в pom; добавить java2; Dockerfile layered на базе distroless-jlink.
2. MATRIX + сбор метрик слоёв/digest + секция отчёта + README.
3. `make bench` → `reports/latest.md`.
4. Rollback: убрать новые варианты MATRIX и apps/java2; fat/jlink 2×2 остаётся.

## Open Questions

Нет — второй app и стек distroless-jlink зафиксированы выше.
