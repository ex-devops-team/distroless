## ADDED Requirements

### Requirement: Stacked size table OS vs application
Markdown-отчёт MUST содержать стековую таблицу размера на каждый язык (сопоставимая пара) со строками:

1. OS baseline — эвристика: `max(0, size(baseline) − size(distroless))`
2. OS distroless — эвристика: `0` (весь измеренный размер distroless относится к срезу Application)
3. Application — `size(distroless)` (прокси «приложение + runtime без жирной ОС»)
4. Total baseline — измеренный docker Size baseline
5. Total distroless — измеренный docker Size distroless

Эвристика MUST быть подписана в отчёте: это не слойный анализ, итоги MUST совпадать с измеренными размерами. Failed-smoke образы MUST NOT входить как успешные строки. Если distroless больше baseline, OS baseline MUST быть 0, а расхождение MUST быть в Notes.

#### Scenario: Stacked size rows per language
- **WHEN** обе стороны пары имеют успешный smoke и измеренный размер
- **THEN** в отчёте для языка есть строки OS baseline, OS distroless, Application и два итога размера

#### Scenario: Size totals match docker inspect
- **WHEN** построен стек размера
- **THEN** Total baseline и Total distroless равны `size_bytes` соответствующих успешных образов

## MODIFIED Requirements

### Requirement: Comparative report for framework matrix
Система MUST формировать markdown-отчёт по полной матрице framework-вариантов. **Основные** таблицы интерпретации MUST быть стековыми (CVE OS/приложение/итоги и размер OS/приложение/итоги). Служебная матрица MUST сохранять язык, вариант, distro lineage, image tag, smoke и comparable pair. Отчёт MUST обновляться командой прогона или пересборкой из raw JSON.

#### Scenario: Report covers Express and nginx variants
- **WHEN** выполнен полный прогон после успешной сборки
- **THEN** отчёт содержит стеки (и служебные строки матрицы) для Node Express dynamic и nginx static наряду с Java/Python/Go

#### Scenario: Stacked tables are primary
- **WHEN** оператор открывает `reports/latest.md` после успешного прогона
- **THEN** стековые таблицы CVE и размера присутствуют как основной разрез OS vs приложение, а не только широкая таблица вариант×OS/App колонки
