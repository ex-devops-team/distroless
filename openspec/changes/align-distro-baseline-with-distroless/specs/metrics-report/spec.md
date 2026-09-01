## MODIFIED Requirements

### Requirement: Vulnerability scan
Система MUST сканировать каждый собранный образ на известные уязвимости с помощью Grype и фиксировать количество находок как минимум по severity CRITICAL, HIGH, MEDIUM, LOW (и TOTAL при наличии). Версия Grype и идентификатор/дата vulnerability DB MUST быть зафиксированы в отчёте или метаданных прогона, чтобы результат был интерпретируем.

#### Scenario: CVE counts by severity
- **WHEN** оператор запускает сканирование уязвимостей Grype для образа из матрицы
- **THEN** в результатах появляются счётчики как минимум для CRITICAL и HIGH, связанные с идентификатором образа

### Requirement: Comparative report
Система MUST формировать сравнительный отчёт (markdown), где для каждой строки матрицы указаны: язык, вариант, distro lineage, размер, счётчики CVE по severity. Для каждой baseline/distroless пары отчёт MUST явно отмечать, является ли сравнение сопоставимым по OS-линейке.

#### Scenario: Report covers full matrix
- **WHEN** оператор выполняет полный прогон замера после успешной сборки всех вариантов
- **THEN** отчёт содержит строку для каждого варианта матрицы с полями distro lineage, размера и CVE

#### Scenario: Report flags non-comparable pair
- **WHEN** baseline/distroless пара построена на разных distro-семействах
- **THEN** отчёт помечает такую пару как несопоставимую для финальной интерпретации baseline-vs-distroless
