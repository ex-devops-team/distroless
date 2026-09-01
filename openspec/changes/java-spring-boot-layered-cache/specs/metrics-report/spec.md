## Purpose

Секция бенчмарк-отчёта про размеры Spring Boot Docker-слоёв (shared dependencies vs application), footprint нескольких приложений и опционально time-to-healthy для fat jar vs layered.

## ADDED Requirements

### Requirement: Java layered size section in report
Отчёт MUST содержать секцию про Java layered jars: размеры слоёв (как минимум dependencies / spring-boot-loader / application, плюс прочие группы если присутствуют), сравнение с fat-jar образом на том же jlink+distroless классе базы, и оценку shared vs application для сценария двух приложений с одинаковыми dependency-слоями.

#### Scenario: Layer sizes listed
- **WHEN** формируется отчёт после успешного прогона с layered Java-образами
- **THEN** в секции указаны размеры (MB) ключевых Spring Boot layer groups и total image size для fat vs layered

#### Scenario: Two-app shared footprint
- **WHEN** в прогоне есть два layered-приложения с совпадающими dependency-слоями
- **THEN** отчёт показывает, что digests общих слоёв совпадают (или явно фиксирует расхождение) и приводит оценку registry footprint: 2×fat vs (shared layers + 2×application)

### Requirement: Optional startup timing in layered section
Если бенчмарк измеряет time-to-healthy, отчёт MUST показать fat vs layered рядом с оговоркой о шуме измерения. Если измерение не выполнялось, секция MUST NOT выдумывать цифры старта.

#### Scenario: Timing present or omitted honestly
- **WHEN** отчёт рендерится
- **THEN** либо есть измеренные time-to-healthy для fat и layered, либо явно указано, что старт не измерялся
