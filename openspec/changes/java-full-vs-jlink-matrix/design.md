## Context

Сейчас `Dockerfile.baseline` / `Dockerfile.distroless` уже только jlink; колонки «jlink *» в Size дублируют Totals. См. proposal.md — Why. Change `pivot-size-table-columns` дал пивот Size; этот change добавляет честную 2×2 для Java.

## Goals / Non-Goals

**Goals:**
- Четыре образа + измерения size/CVE/smoke.
- Секция отчёта 2×2 (размер и CVE) с читаемыми дельтами.
- Убрать вводящие в заблуждение jlink-колонки из общего Size.
- Зафиксировать empirically, меняет ли jlink CVE (без заранее «да/нет» в тексте отчёта как догму — только цифры + краткая интерпретация).

**Non-Goals:**
- GraalVM native-image; пятый вариант.
- Пивот CVE для всех языков.
- Слойный анализ размера.

## Decisions

### 1. Имена вариантов и файлов
| Variant | Dockerfile | Image tag | Runtime |
|---------|------------|-----------|---------|
| baseline | `Dockerfile.baseline` | `java:baseline` | `eclipse-temurin:21-jre` |
| distroless | `Dockerfile.distroless` | `java:distroless` | `gcr.io/distroless/java21-debian12:nonroot` |
| baseline-jlink | `Dockerfile.baseline-jlink` | `java:baseline-jlink` | `eclipse-temurin:21-jre` OS + jlink (не bookworm-slim) |
| distroless-jlink | `Dockerfile.distroless-jlink` | `java:distroless-jlink` | текущий cc+jlink |

Переименовать нынешние jlink Dockerfiles → `*-jlink`; восстановить full в `baseline`/`distroless`.

### 2. Comparable pair в общей таблице
Java в пивот Size / стек CVE: **baseline-jlink** vs **distroless-jlink** (современный «сжатый» стек). Full-пара — только в секции 2×2.

### 3. Форма секции Java 2×2
Две маленькие markdown-таблицы (Size MB; CVE Critical/High/Med/Low/Total или OS|App|Total). Строки: baseline / distroless; колонки: full JRE / jlink. Опционально строка Δ под таблицей size.

### 4. CVE и jlink (ожидание для notes, не спека)
- **Может уменьшить:** CVE в отрезанных модулях JDK (меньше файлов/пакетов JRE в образе).
- **Не уменьшает само по себе:** CVE в Spring fat jar (`java-archive`).
- **OS CVE:** baseline full vs baseline-jlink — одна Temurin OS (честный эффект jlink); distroless full (`java21`) vs distroless-jlink (`cc`) — разные OS-базы, сравнивать осторожно; в notes отчёта это отразить.
Итог — числа из Grype в 2×2.

### 5. MATRIX / regenerate
Добавить две строки в `benchmark.py` и `MATRIX_ORDER` в regenerate; `successful_pairs` для java брать `baseline-jlink`+`distroless-jlink` (или baseline+distroless-jlink aliases).

## Risks / Trade-offs

- [Дольше `make bench` (+2 Java build/grype)] → Mitigation: приемлемо для эксперимента.
- [Путаница имён baseline vs baseline-jlink] → Mitigation: README + заголовок секции 2×2.
- [Quality stage дважды×4] → Mitigation: BuildKit cache; при желании общий quality — later, не блокер.
- [pivot change ещё не archived] → Mitigation: этот change правит те же файлы отчёта; применять после/вместо дублирующих jlink-колонок.

## Migration Plan

1. Rename current Dockerfiles to `*-jlink`; add full `baseline`/`distroless`.
2. Update MATRIX + render + README.
3. `make bench` → новый `reports/latest.md`.
4. Rollback: удалить full / вернуть только jlink как baseline/distroless.

## Open Questions

Нет — CVE-ответ даёт прогон, не заранее.
