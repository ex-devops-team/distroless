## ADDED Requirements

### Requirement: Spring Boot layered jar for Java samples
Java sample-приложения, участвующие в эксперименте layered cache, MUST собираться как Spring Boot layered jar (layertools / `layers.idx`) так, чтобы зависимости и application-код попадали в разные layer groups.

#### Scenario: Layered jar extractable
- **WHEN** собирается jar primary Java health-приложения с layered конфигурацией
- **THEN** `java -Djarmode=layertools -jar … extract` (или эквивалент) выделяет как минимум группы dependencies и application

### Requirement: Distroless jlink image with Docker layering
Репозиторий MUST содержать runtime-образ(ы) Java на базе jlink + distroless (тот же класс, что `distroless-jlink`), где Spring Boot layer groups скопированы отдельными Docker-слоями (dependencies раньше application), с успешным smoke `GET /health`.

#### Scenario: Layered distroless-jlink smokes
- **WHEN** собирается layered вариант на jlink+distroless
- **THEN** контейнер отвечает на `GET /health` с 2xx и непустым телом

#### Scenario: Application layer is last among app layers
- **WHEN** инспектируется Dockerfile/сборка layered runtime
- **THEN** слой(и) с кодом приложения идут после слоёв dependencies / loader, чтобы изменение app не инвалидировало dependency-слои

### Requirement: Second Java app sharing dependency stack
Репозиторий MUST содержать второе минимальное Spring Boot-приложение с тем же набором runtime-зависимостей Spring Boot (тот же major stack), но отличимым application-кодом / artifactId, также собираемое layered и входящее в матрицу/прогон для сравнения digest'ов общих слоёв.

#### Scenario: Second app health and distinct app layer
- **WHEN** собраны layered-образы двух приложений
- **THEN** оба проходят smoke `/health`, а application-слой (или его digest) различается, при этом dependency-слои совпадают при одинаковых версиях зависимостей
