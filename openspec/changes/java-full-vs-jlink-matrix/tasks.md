## 1. Четыре Java Docker-образа

- [x] 1.1 Переименовать текущие jlink Dockerfiles в `Dockerfile.baseline-jlink` и `Dockerfile.distroless-jlink`
- [x] 1.2 Восстановить `Dockerfile.baseline` (Temurin 21 JRE) и `Dockerfile.distroless` (distroless java21)
- [x] 1.3 `baseline-jlink`: та же OS, что `baseline` (`eclipse-temurin:21-jre` + jlink вместо полного JRE), не `debian:bookworm-slim`

## 2. Матрица бенчмарка

- [x] 2.1 Добавить оба jlink-варианта в `benchmark.py` и `regenerate_cve_breakdown.py` (MATRIX_ORDER)
- [x] 2.2 Comparable pair для Java в отчёте: `baseline-jlink` vs `distroless-jlink`

## 3. Визуализация отчёта

- [x] 3.1 Секция Java 2×2: размер (full vs jlink × baseline vs distroless)
- [x] 3.2 Та же секция: CVE (totals и/или OS/app) + краткая note про возможное влияние jlink на CVE
- [x] 3.3 Убрать дублирующие колонки jlink из общей Size-таблицы; обновить README

## 4. Прогон

- [x] 4.1 `make bench` — четыре Java smoke OK; `reports/latest.md` с 2×2 size и CVE (после смены базы baseline-jlink)
