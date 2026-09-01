## Why

Сейчас Java-образы тащат полный JRE (`eclipse-temurin:21-jre` / `gcr.io/distroless/java21-debian12`), хотя Spring Boot health-сервису нужна лишь часть JDK-модулей. `jlink` позволяет собрать урезанный runtime и измерить, насколько это уменьшает размер образа в том же эксперименте baseline vs distroless.

## What Changes

- **BREAKING** для Java runtime: оба варианта (`Dockerfile.baseline`, `Dockerfile.distroless`) MUST собирать custom JRE через `jlink` (модули по `jdeps`/курированному списку) и запускать fat jar на этом runtime, а не на полном Temurin JRE / Distroless Java21.
- Quality-gate (Spotless + tests) и приложение Spring Boot остаются; меняется только этап runtime-сборки и финальный базовый слой под custom JRE.
- После смены образов — повторный прогон бенчмарка (size + Grype + smoke), чтобы отчёт отразил влияние jlink на размер (и при необходимости на CVE).

## Capabilities

### New Capabilities

<!-- нет -->

### Modified Capabilities

- `sample-apps`: Java baseline и distroless MUST использовать jlink custom runtime вместо полного JRE / `distroless/java21`.

## Impact

- `apps/java/Dockerfile.baseline`, `apps/java/Dockerfile.distroless` (и при необходимости общий build-stage / скрипт jlink).
- Сравнение размеров в `reports/latest.md` после `make bench` / `make report` станет относиться к jlink-образам (старые цифры полного JRE устареют).
- Smoke `/health` и матрица языков без изменений по составу вариантов (по-прежнему два Java-образа: baseline и distroless).
