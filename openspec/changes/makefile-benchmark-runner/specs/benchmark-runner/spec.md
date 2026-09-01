## Purpose

Точка входа для полного прогона distroless-бенчмарка: сборка матрицы, smoke, Grype и отчёт через Makefile без project bash-скриптов.

## ADDED Requirements

### Requirement: Makefile is the benchmark entrypoint
Оператор MUST запускать полный прогон эксперимента через Makefile (корневой `Makefile`). Документация MUST указывать Make-команды, а не `scripts/*.sh`.

#### Scenario: Full run via make
- **WHEN** оператор выполняет документированную Make-команду полного прогона
- **THEN** выполняется матрица build → smoke → size → Grype → обновление `reports/latest.md`

### Requirement: No standalone bash driver scripts
В репозитории MUST NOT оставаться standalone shell-скриптов оркестрации бенчмарка (в частности `scripts/benchmark.sh`). Логика прогона MUST жить в Makefile и/или Python под `scripts/`.

#### Scenario: benchmark.sh removed
- **WHEN** change применён
- **THEN** файла `scripts/benchmark.sh` нет, а прогон доступен через Make

### Requirement: Report regeneration target
Makefile MUST предоставлять цель пересборки отчёта из существующих `reports/raw` без обязательного полного rebuild образов.

#### Scenario: Report-only make target
- **WHEN** оператор вызывает цель пересборки отчёта при наличии raw JSON
- **THEN** обновляется `reports/latest.md` без требования успешного docker build всей матрицы
