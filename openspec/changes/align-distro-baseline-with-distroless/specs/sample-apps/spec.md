## MODIFIED Requirements

### Requirement: Baseline and distroless image variants
Для каждого языка система MUST предоставлять как минимум два собираемых runtime-образа: baseline и distroless. Для каждой baseline/distroless пары система MUST использовать согласованную OS-линейку (предпочтительно Debian 12 в рамках текущего эксперимента). Образы MUST собираться воспроизводимо из исходников репозитория (Dockerfile / build-скрипт).

#### Scenario: Both variants build for a language
- **WHEN** оператор запускает сборку baseline- и distroless-образов для выбранного языка
- **THEN** оба образа успешно собираются и помечены различимыми тегами

#### Scenario: Pair metadata includes distro lineage
- **WHEN** оператор просматривает матрицу образов
- **THEN** для baseline/distroless пары явно указана OS-линейка, подтверждающая сопоставимость сравнения

### Requirement: Documented image matrix
Система MUST документировать матрицу образов: язык, вариант (baseline / distroless / node-dynamic / node-static), тег образа, базовый runtime-образ и distro lineage.

#### Scenario: Matrix lists all expected variants
- **WHEN** оператор открывает документацию матрицы образов
- **THEN** в ней перечислены все варианты для Java, Python, Go (baseline + distroless) и для Node.js (baseline + dynamic distroless + static distroless) с полем distro lineage
