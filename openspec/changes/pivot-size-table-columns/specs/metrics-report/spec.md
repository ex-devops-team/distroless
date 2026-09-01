## Purpose

Markdown-отчёт бенчмарка размера и CVE: таблицы и пояснения эвристик, чтобы сравнивать baseline vs distroless по языкам.

## ADDED Requirements

### Requirement: Pivoted size table by language
Markdown-отчёт MUST содержать таблицу размера, где **каждая строка — язык** (сопоставимая пара с успешным smoke), а **колонки — срезы Slice**:

| Колонка | Значение |
|---------|----------|
| jlink baseline | вес Java-образа baseline с jlink custom JRE (MB); иначе `—` |
| jlink distroless | вес Java-образа distroless с jlink custom JRE (MB); иначе `—` |
| OS baseline | `max(0, size(baseline) − size(distroless))` |
| OS distroless | `0` (по эвристике: весь измеренный size(distroless) отнесён к Application) |
| Application | `size(distroless)` |
| Total baseline | измеренный docker Size baseline |
| Total distroless | измеренный docker Size distroless |
| Notes | примечания пары (если есть) |

Эвристика MUST быть подписана непосредственно у таблицы размера. Пояснение MUST явно говорить: **OS distroless = 0 не означает отсутствие ОС/пакетов в образе** и **не равно нулю OS CVE**; это следствие модели «Application ≈ полный размер distroless», а не слойного анализа. Total baseline / Total distroless MUST совпадать с `size_bytes` успешных образов. Failed-smoke языки MUST NOT появляться как успешные строки этой таблицы. Если size(distroless) > size(baseline), OS baseline MUST быть 0, а факт MUST быть в Notes.

#### Scenario: One size row per language with slice columns
- **WHEN** построена таблица размера для успешных пар
- **THEN** для каждого языка одна строка и колонки jlink baseline, jlink distroless, OS baseline, OS distroless, Application, Total baseline, Total distroless (и Notes)

#### Scenario: Report explains zero OS distroless size
- **WHEN** оператор читает секцию размера в `reports/latest.md`
- **THEN** рядом с таблицей есть текст, что OS distroless size = 0 по эвристике и что это не то же самое, что OS CVE в distroless

#### Scenario: Size totals match docker inspect
- **WHEN** построена пивот-таблица размера
- **THEN** Total baseline и Total distroless равны `size_bytes` соответствующих успешных образов
