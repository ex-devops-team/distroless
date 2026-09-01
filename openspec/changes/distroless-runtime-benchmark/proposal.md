## Why

Нужно быстро и воспроизводимо сравнить, насколько distroless runtime уменьшает размер образов и количество CVE относительно «обычных» language-образов для Java, Node.js, Python и Go. Для Node.js важно отдельно увидеть разницу между динамическим runtime (Node + зависимости) и статически упакованным артефактом.

## What Changes

- Добавить минимальные sample-приложения (простой HTTP-сервис) на Java, Node.js, Python и Go.
- Для каждого языка собрать минимум два runtime-образа: baseline (официальный slim/alpine) и distroless.
- Для Node.js добавить два distroless-варианта: **dynamic** (Node runtime + `node_modules`) и **static** (single executable / SEA на distroless/static или эквивалент).
- Добавить воспроизводимый скрипт/пайплайн замера: размер образа и число уязвимостей (по severity) через сканер (**Grype**).
- Сформировать сводный отчёт (таблица markdown) с результатами эксперимента.

## Capabilities

### New Capabilities
- `sample-apps`: минимальные HTTP-приложения и Dockerfile-варианты (baseline / distroless; для Node — dynamic и static).
- `metrics-report`: сбор метрик размера образа и CVE, агрегация в сравнительный отчёт.

### Modified Capabilities

## Impact

- Новый код sample-приложений и Dockerfiles в репозитории (пока зелёный проект без приложений).
- Зависимости инструментов: Docker (buildx), Grype, языковые SDK для локальной/мультистейдж-сборки.
- Результат эксперимента — артефакт отчёта (markdown); CI опционален и не обязателен для первого прогона.
