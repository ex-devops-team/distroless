## Purpose

Сделать сравнение baseline и distroless воспроизводимым и методологически честным за счёт выравнивания OS-линейки в парных образах по каждому языку.

## ADDED Requirements

### Requirement: Baseline and distroless use aligned distro lineage
Для каждого языка система MUST определять парное сравнение baseline vs distroless в рамках одной distro-линейки (например, Debian 12 vs Debian 12). Смешивание Ubuntu и Debian в одной паре MUST NOT использоваться как основной сравнительный результат.

#### Scenario: Pair is accepted when lineage matches
- **WHEN** оператор запускает benchmark для языка из матрицы
- **THEN** baseline и distroless строки для этой пары используют одну и ту же OS-линейку и считаются валидным сравнением

#### Scenario: Pair is marked invalid when lineage differs
- **WHEN** baseline и distroless для языка построены на разных distro-семействах
- **THEN** система помечает пару как несопоставимую и не интерпретирует её как финальный baseline-vs-distroless вывод

### Requirement: Preferred baseline for current experiment is Debian
Для текущего эксперимента система MUST использовать Debian-линейку как предпочтительную базу для baseline-образов там, где это возможно, чтобы она соответствовала distroless Debian 12 runtime.

#### Scenario: Baseline image selection follows Debian preference
- **WHEN** оператор обновляет матрицу образов
- **THEN** baseline-теги выбираются из Debian-вариантов и документируются вместе с distroless-парой
