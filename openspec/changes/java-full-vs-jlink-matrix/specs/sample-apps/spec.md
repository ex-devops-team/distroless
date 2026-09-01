## MODIFIED Requirements

### Requirement: Java runtime via jlink custom JRE
Варианты `baseline-jlink` и `distroless-jlink` MUST запускать Spring Boot fat jar на custom JRE, собранном через `jlink` из JDK 21. Для этих двух вариантов полный `eclipse-temurin:21-jre` и готовый `gcr.io/distroless/java21-debian12` MUST NOT быть финальным runtime. Набор модулей MUST быть достаточным для успешного старта и ответа на `GET /health`.

#### Scenario: Baseline uses jlink JRE
- **WHEN** собирается Java `baseline-jlink` runtime image
- **THEN** в финальном образе есть custom JRE от `jlink`, а не полный Temurin JRE-образ как единственный runtime

#### Scenario: Distroless uses jlink JRE
- **WHEN** собирается Java `distroless-jlink` runtime image
- **THEN** в финальном образе есть custom JRE от `jlink` на minimal/distroless base, а не `gcr.io/distroless/java21-*` как готовый полный Java runtime

#### Scenario: Health works on jlink runtime
- **WHEN** контейнер `baseline-jlink` или `distroless-jlink` запущен
- **THEN** `GET /health` возвращает 2xx и непустое тело

## ADDED Requirements

### Requirement: Four Java runtime variants for comparison
Репозиторий MUST содержать четыре Java runtime-образа с успешным smoke `/health`:

1. `baseline` — полный JRE (`eclipse-temurin:21-jre` или эквивалент)
2. `distroless` — полный Distroless Java21 (`gcr.io/distroless/java21-debian12` или эквивалент)
3. `baseline-jlink` — jlink custom JRE на той же OS-базе, что и `baseline` (Temurin JRE layers + замена JRE на jlink)
4. `distroless-jlink` — jlink custom JRE на distroless cc/base debian12

Все четыре MUST входить в матрицу бенчмарка (build + smoke + size + Grype).

#### Scenario: Matrix lists four Java variants
- **WHEN** выполняется полный прогон бенчмарка
- **THEN** для Java измерены все четыре варианта с успешным smoke

#### Scenario: Full JRE variants are not jlink
- **WHEN** собираются `baseline` и `distroless` (без суффикса jlink)
- **THEN** runtime — полный JRE / Distroless Java21, а не только custom jlink JRE
