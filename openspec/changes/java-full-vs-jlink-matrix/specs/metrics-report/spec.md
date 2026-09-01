## Purpose

Markdown-отчёт бенчмарка: таблицы размера/CVE и Java-сравнение full JRE vs jlink, чтобы отделить вклад distroless от вклада урезанного runtime.

## ADDED Requirements

### Requirement: Java 2x2 size and CVE comparison
Отчёт MUST содержать отдельную секцию сравнения Java с четырьмя измеренными вариантами (только успешный smoke):

| | full JRE | jlink |
|---|----------|-------|
| baseline | size + CVE totals (и при необходимости OS/app) | size + CVE |
| distroless | size + CVE | size + CVE |

Секция MUST позволять увидеть:

1. эффект **distroless** при полном JRE (baseline full → distroless full);
2. эффект **jlink** при том же классе OS-базы (baseline full → baseline-jlink; distroless full → distroless-jlink);
3. комбинированный эффект (baseline full → distroless-jlink).

Числа MUST браться из docker Size и Grype того же прогона. Секция MUST кратко пояснять: jlink *может* снизить CVE за счёт удаления неиспользуемых модулей JDK, но не обязан; CVE приложения (fat jar) и OS зависят от состава образа — итог ONLY из измерений. Общая языковая Size-таблица MUST NOT дублировать jlink-колонки, равные Total для Java; comparable pair для Java в общей таблице = `baseline-jlink` vs `distroless-jlink`.

#### Scenario: Report shows four Java sizes
- **WHEN** все четыре Java-варианта успешно измерены
- **THEN** в секции Java 2×2 видны четыре размера (baseline/distroless × full/jlink)

#### Scenario: Report shows four Java CVE totals
- **WHEN** все четыре Java-варианта успешно просканированы Grype
- **THEN** в секции Java 2×2 видны CVE totals (или OS/app breakdown) для каждого из четырёх

#### Scenario: General size table uses jlink pair for Java
- **WHEN** строится общая пивот-таблица размера по языкам
- **THEN** для Java comparable pair — baseline-jlink и distroless-jlink, без колонок jlink=Total
