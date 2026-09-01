## 1. Генератор отчёта

- [x] 1.1 Стековая таблица CVE: OS baseline / OS distroless / Application (одна или две строки) / Total baseline / Total distroless
- [x] 1.2 Стековая таблица размера по эвристике (OS baseline = max(0, base−dist), OS distroless = 0, Application = distroless, totals = inspect)
- [x] 1.3 Служебная матрица без дублирования CVE/size колонок; failed-smoke не в стеках; Notes для nginx и unknown

## 2. Документация и прогон

- [x] 2.1 README: стековые строки и что эвристика размера ≠ CVE OS
- [x] 2.2 Пересобрать `reports/latest.md` из существующих raw JSON
- [x] 2.3 Проверить: CVE totals = os+app+unknown; size totals = size_bytes
