## 1. jlink runtime в Dockerfiles

- [x] 1.1 Добавить stage после Maven package: `jdeps` + `jlink` → custom JRE 21 (одинаковая логика для обоих образов)
- [x] 1.2 Обновить `Dockerfile.baseline`: runtime на Debian bookworm-slim + COPY jre/jar, entrypoint `java -jar`
- [x] 1.3 Обновить `Dockerfile.distroless`: runtime на `cc-debian12`/`base-debian12` nonroot + COPY jre/jar, явный entrypoint на custom `java` (без `distroless/java21`)

## 2. Проверка и отчёт

- [x] 2.1 Собрать оба Java-образа; quality-gate и smoke `GET /health` OK
- [x] 2.2 Прогнать бенчмарк/отчёт (`make bench` или эквивалент) и зафиксировать влияние jlink на размер (и CVE) в `reports/latest.md`
