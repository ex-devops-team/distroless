## Why

Fat jar смешивает общие Spring Boot-зависимости и код приложения в одном слое Docker — при многих сервисах registry и ноды тянут одни и те же мегабайты снова. Нужен эксперимент: разложить jar на слои (dependencies / loader / application), измерить доли размера и показать, что на стеке **jlink + distroless** общие слои можно переиспользовать между приложениями (registry, pull-дельта, потенциально быстрее старт на распакованных слоях).

## What Changes

- Включить **Spring Boot layered jars** для Java-приложения(ий) и собрать runtime-образ(ы) с отдельными Docker-слоями под стандартные layer groups + custom jlink на distroless (опора на существующий `distroless-jlink`).
- Добавить **второе** минимальное Spring Boot-приложение с теми же зависимостями, но другим application-кодом — чтобы измерить совпадение digest'ов общих слоёв и размер «только app» при двух образах.
- В отчёте — секция **Java: fat jar vs layered** (размеры слоёв; оценка shared vs app; сравнение pull-дельты / суммарного registry footprint для 2 apps); опционально time-to-healthy fat vs layered.
- Матрица бенчмарка / README: новые варианты (layered) без поломки существующей 2×2 full/jlink.
- Не утверждать заранее «всегда быстрее старт» — **измерить**; registry/cache выгоду вывести из размеров слоёв и digest equality.

## Capabilities

### New Capabilities

- `metrics-report`: секция отчёта по размерам Spring Boot layers, shared vs application, footprint двух приложений и (если измерено) time-to-healthy.

### Modified Capabilities

- `sample-apps`: Java MUST поддерживать layered jar + Docker layering на jlink/distroless и второе sample-приложение для демонстрации общего dependency-слоя.

## Impact

- `apps/java/` (pom layered, Dockerfile layered), новое `apps/java-app2/` (или sibling module)
- `scripts/benchmark.py`, `render_benchmark_report.py`, возможно helper для layer sizes / digests
- `README.md`, `reports/latest.md` после `make bench`
