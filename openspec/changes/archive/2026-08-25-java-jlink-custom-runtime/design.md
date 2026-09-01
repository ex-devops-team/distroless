## Context

Сейчас Java baseline = `eclipse-temurin:21-jre` + fat jar; distroless = `gcr.io/distroless/java21-debian12:nonroot` + jar. Quality/build на `maven:3.9.9-eclipse-temurin-21`. Мотивация — см. proposal.md. Матрица остаётся: два варианта Java (baseline / distroless).

## Goals / Non-Goals

**Goals:**
- Собрать минимальный JRE 21 через `jlink` под зависимости Spring Boot fat jar.
- Подставить этот JRE в оба финальных образа и измерить размер/CVE тем же бенчмарком.
- Сохранить quality-gate и smoke `/health`.

**Non-Goals:**
- GraalVM native-image / CDS / отдельные матричные строки «до/после jlink».
- Смена версии Java или отказ от Spring Boot.
- Оптимизация размера самого fat jar (layertools и т.п.) как отдельная цель.

## Decisions

### 1. Заменить оба варианта, не добавлять третий
**Выбор:** обновить `Dockerfile.baseline` и `Dockerfile.distroless`, чтобы отчёт сразу сравнивал jlink-baseline vs jlink-distroless.  
**Альтернативы:** третий вариант `java:jlink` рядом со старыми — расширяет матрицу и размывает stacked-отчёт.  
**Почему:** цель — увидеть влияние jlink на размер в текущем эксперименте, не плодить ряды.

### 2. Общий jlink-stage в multi-stage Dockerfile
**Выбор:** после `mvn package` — stage на JDK 21 с `jdeps` (или курируемым `--add-modules`) + `jlink --strip-debug --no-man-pages --no-header-files --compress=2` → `/jre`; runtime копирует `/jre` + jar.  
**Альтернативы:** фиксированный список модулей без jdeps; jlink только в baseline.  
**Почему:** один pipeline для обоих образов; при падении старта можно расширить модули без смены архитектуры.

### 3. Базовые слои после jlink
**Выбор:**
- baseline: `debian:bookworm-slim` (или близкий Debian 12 slim) + COPY jre + jar, `PATH`/`JAVA_HOME` на custom JRE, non-root user.
- distroless: `gcr.io/distroless/cc-debian12:nonroot` (или `base-debian12`) + COPY jre + jar и явный entrypoint на `/jre/bin/java -jar ...` (не `java21` image).

**Альтернативы:** оставить `distroless/java21` и только «сжать» поверх — не даёт настоящего выигрыша от jlink.  
**Почему:** размер runtime тогда определяется custom JRE + OS-слой, а не готовым Distroless Java.

### 4. Модули
**Выбор:** сначала `jdeps --ignore-missing-deps --print-module-deps` по jar (с учётом Spring Boot layout); при необходимости добавить `jdk.unsupported`, `java.management` и др. вручную.  
**Альтернатива:** сразу широкий набор «на всякий случай» — проще старт, меньше экономия размера.  
**Почему:** эксперимент про «убрать лишнее»; узкий набор → сильнее сигнал по размеру, с запасным ручным дополнением.

## Risks / Trade-offs

- [Spring Boot + reflection / dynamic modules] → Mitigation: smoke `/health` после сборки; расширить `--add-modules` при `Error: module ... not found`.
- [glibc/libstdc++ для HotSpot на distroless/static] → Mitigation: предпочесть `cc-debian12` / `base-debian12`, не `static`, если нужен динамический linker.
- [Сравнение с прошлым `reports/latest.md`] → Mitigation: в notes отчёта/коммите указать, что Java-цифры теперь jlink; старый полный JRE не в матрице.
- [Разный размер jre в двух Dockerfiles из-за дрейфа команд] → Mitigation: общий stage или идентичный RUN jlink в обоих файлах.

## Migration Plan

1. Обновить Java Dockerfiles (quality/build без изменений по смыслу).
2. Локально собрать оба образа, проверить `/health`.
3. `make bench` / `make report` — новый размер и CVE.
4. Rollback: вернуть `FROM eclipse-temurin:21-jre` и `FROM gcr.io/distroless/java21-debian12:nonroot`.

## Open Questions

- Точный минимальный список модулей после первого `jdeps` — уточняется при apply, на спеку не влияет.
