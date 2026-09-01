## Why

Сейчас оба Java-образа уже на jlink, поэтому в отчёте нельзя отделить вклад **distroless** от вклада **jlink** в размер (и непонятно, снижает ли jlink CVE). Нужна визуализация 2×2: full JRE vs jlink × baseline vs distroless — чтобы показать, что уменьшают и переход на distroless, и урезание runtime через jlink; параллельно измерить CVE по всем четырём вариантам.

## What Changes

- **BREAKING** для Java-матрицы: четыре runtime-варианта вместо двух:
  1. `baseline` — полный JRE (`eclipse-temurin:21-jre`)
  2. `distroless` — полный Distroless Java21
  3. `baseline-jlink` — jlink custom JRE на **той же** OS-базе Temurin JRE (замена `/opt/java/openjdk`, не Debian slim)
  4. `distroless-jlink` — jlink custom JRE на distroless cc/base
- В отчёте — секция **Java: full JRE vs jlink** (размер + CVE) в формате 2×2 / четырёх колонок, с явными дельтами (полный→distroless, полный→jlink, комбинированный эффект).
- Бенчмарк (`make bench`) собирает, smoke и Grype для всех четырёх; README обновляет матрицу.
- Общая языковая таблица размера: для Java comparable pair = `baseline-jlink` vs `distroless-jlink` (как «текущий лучший» стек); full-варианты видны в Java-секции (не дублировать вводящие в заблуждение колонки jlink=Totals).
- Ответ на CVE: не утверждать заранее — **измерить** и показать в той же 2×2; в notes — что jlink *может* убрать CVE модулей JDK, но не CVE fat jar / не обязан обнулить OS CVE.

## Capabilities

### New Capabilities

- `metrics-report`: секция отчёта Java 2×2 (full vs jlink × baseline vs distroless) для размера и CVE.

### Modified Capabilities

- `sample-apps`: Java MUST иметь четыре сопоставимых runtime-образа (full baseline/distroless + jlink baseline/distroless).

## Impact

- `apps/java/Dockerfile.*` (вернуть full; сохранить/переименовать jlink)
- `scripts/benchmark.py`, `regenerate_cve_breakdown.py` (MATRIX)
- `scripts/render_benchmark_report.py` (Java-секция; убрать дублирующие jlink=Total колонки из общего Size)
- `README.md`, `reports/latest.md` после `make bench`
