## MODIFIED Requirements

### Requirement: Comparative report for framework matrix
Система MUST формировать markdown-отчёт по полной матрице framework-вариантов. **Основные** таблицы интерпретации MUST быть стековыми (CVE OS/приложение/итоги и размер OS/приложение/итоги). Служебная матрица MUST сохранять язык, вариант, distro lineage, image tag, smoke и comparable pair. Отчёт MUST обновляться Make-командой полного прогона или Make-целью пересборки из raw JSON (не bash-скриптом).

#### Scenario: Report covers Express and nginx variants
- **WHEN** выполнен полный прогон после успешной сборки
- **THEN** отчёт содержит стеки (и служебные строки матрицы) для Node Express dynamic и nginx static наряду с Java/Python/Go

#### Scenario: Stacked tables are primary
- **WHEN** оператор открывает `reports/latest.md` после успешного прогона
- **THEN** стековые таблицы CVE и размера присутствуют как основной разрез OS vs приложение, а не только широкая таблица вариант×OS/App колонки

#### Scenario: Report refreshed via Make
- **WHEN** оператор запускает документированную Make-команду обновления отчёта
- **THEN** `reports/latest.md` перезаписывается актуальными результатами
