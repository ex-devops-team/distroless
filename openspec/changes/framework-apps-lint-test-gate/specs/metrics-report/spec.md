## Purpose

Собрать сопоставимый отчёт размера и CVE для обновлённой матрицы framework-apps, включая Express dynamic и nginx static, с учётом distro lineage.

## ADDED Requirements

### Requirement: Image size measurement
Система MUST измерять локальный размер каждого собранного образа матрицы в байтах и привязывать результат к тегу образа.

#### Scenario: Size recorded for each image
- **WHEN** оператор запускает замер размера для собранного образа
- **THEN** в результатах есть идентификатор образа и размер в байтах

### Requirement: Vulnerability scan with Grype
Система MUST сканировать каждый собранный образ Grype и фиксировать CRITICAL/HIGH/MEDIUM/LOW, а также версию Grype/DB в метаданных прогона.

#### Scenario: CVE counts by severity
- **WHEN** оператор запускает Grype для образа матрицы
- **THEN** в результатах есть счётчики как минимум CRITICAL и HIGH

### Requirement: Comparative report for framework matrix
Система MUST формировать markdown-отчёт по полной матрице framework-вариантов: язык, вариант, distro lineage, размер, CVE, smoke, comparable pair. Отчёт MUST обновляться командой прогона.

#### Scenario: Report covers Express and nginx variants
- **WHEN** выполнен полный прогон после успешной сборки
- **THEN** отчёт содержит строки для Node Express dynamic и nginx static наряду с Java/Python/Go

### Requirement: Smoke validation before successful metrics
Образы, не прошедшие smoke, MUST NOT попадать в отчёт как успешные измерения (допускается явная пометка failure).

#### Scenario: Failed smoke excludes success row
- **WHEN** smoke HTTP-check падает
- **THEN** итоговый отчёт не представляет образ как валидное успешное измерение без указания failure
