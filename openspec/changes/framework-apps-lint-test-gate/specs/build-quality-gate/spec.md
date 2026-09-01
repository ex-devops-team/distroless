## Purpose

Обеспечить обязательный прогон линтеров и юнит-тестов при сборке образов без включения toolchain и test-зависимостей в финальный runtime-контейнер.

## ADDED Requirements

### Requirement: Lint and unit tests run during image build
Сборка каждого application-образа MUST выполнять lint и unit tests в build-stage (или отдельном quality-stage) до публикации финального runtime-слоя. При падении lint или tests сборка образа MUST завершаться ошибкой.

#### Scenario: Failing test blocks image build
- **WHEN** unit test падает во время docker build
- **THEN** сборка образа завершается неуспехом и финальный тег не публикуется как успешный runtime

#### Scenario: Failing lint blocks image build
- **WHEN** линтер завершается с ошибкой во время docker build
- **THEN** сборка образа завершается неуспехом

### Requirement: Quality toolchain excluded from final image
Зависимости и инструменты, нужные только для lint/tests (devDependencies, test runners, linters, JDK annotation processors только для quality и т.п.), MUST NOT присутствовать в финальном runtime-образе. Финальный образ MUST содержать только runtime-артефакт приложения и необходимые runtime-зависимости.

#### Scenario: Final image has no test toolchain packages
- **WHEN** оператор инспектирует финальный runtime-образ (filesystem / package list / layer contents — согласованным способом в design)
- **THEN** в нём отсутствуют установленные lint/test toolchain пакеты из quality-stage

### Requirement: Documented quality tools per language
Для каждого языка система MUST документировать выбранные линтер и test runner, а также то, что они выполняются в build и не копируются в final stage.

#### Scenario: README lists quality tools
- **WHEN** оператор открывает документацию apps
- **THEN** для Java/Node/Python/Go указаны lint tool, test tool и multi-stage isolation rule
