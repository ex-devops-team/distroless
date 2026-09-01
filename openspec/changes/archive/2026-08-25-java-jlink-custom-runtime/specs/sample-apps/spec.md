## ADDED Requirements

### Requirement: Java runtime via jlink custom JRE
Java baseline и distroless runtime-образы MUST запускать Spring Boot fat jar на custom JRE, собранном через `jlink` из JDK 21. Полный `eclipse-temurin:21-jre` и готовый `gcr.io/distroless/java21-debian12` MUST NOT быть финальным runtime Java-приложения. Набор модулей MUST быть достаточным для успешного старта приложения и ответа на `GET /health`.

#### Scenario: Baseline uses jlink JRE
- **WHEN** собирается Java baseline runtime image
- **THEN** в финальном образе есть custom JRE от `jlink`, а не полный Temurin JRE-образ как единственный runtime

#### Scenario: Distroless uses jlink JRE
- **WHEN** собирается Java distroless runtime image
- **THEN** в финальном образе есть тот же класс custom JRE от `jlink` на minimal/distroless base, а не `gcr.io/distroless/java21-*` как готовый полный Java runtime

#### Scenario: Health works on jlink runtime
- **WHEN** контейнер Java baseline или distroless запущен после сборки с jlink
- **THEN** `GET /health` возвращает 2xx и непустое тело
