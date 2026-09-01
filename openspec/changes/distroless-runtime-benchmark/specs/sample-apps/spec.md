## Purpose

Минимальные HTTP-приложения на Java, Node.js, Python и Go с вариантами runtime-образов (baseline и distroless; для Node — dynamic и static) для сравнительного эксперимента.

## ADDED Requirements

### Requirement: Sample HTTP apps per language
Репозиторий MUST содержать по одному минимальному HTTP-приложению для Java, Node.js, Python и Go. Каждое приложение MUST отвечать на health/root-запрос успешным HTTP-ответом с телом, достаточным для проверки работоспособности контейнера.

#### Scenario: Health check succeeds for each app
- **WHEN** приложение языка запущено в контейнере и клиент выполняет HTTP GET на согласованный endpoint (например `/` или `/health`)
- **THEN** ответ имеет статус 2xx и непустое тело

### Requirement: Baseline and distroless image variants
Для каждого языка система MUST предоставлять как минимум два собираемых runtime-образа: baseline (официальный slim/alpine language-образ) и distroless (Google Distroless или эквивалент без полноценной ОС-оболочки). Образы MUST собираться воспроизводимо из исходников репозитория (Dockerfile / build-скрипт).

#### Scenario: Both variants build for a language
- **WHEN** оператор запускает сборку baseline- и distroless-образов для выбранного языка
- **THEN** оба образа успешно собираются и помечены различимыми тегами

### Requirement: Node.js dynamic and static distroless variants
Для Node.js система MUST предоставлять два distroless-варианта: **dynamic** (Node runtime + зависимости приложения) и **static** (один исполняемый артефакт без отдельного Node runtime в образе). Оба варианта MUST успешно обслуживать тот же HTTP endpoint, что и baseline.

#### Scenario: Dynamic Node distroless serves traffic
- **WHEN** собран и запущен Node dynamic distroless-образ
- **THEN** HTTP health/root endpoint отвечает статусом 2xx

#### Scenario: Static Node distroless serves traffic
- **WHEN** собран и запущен Node static distroless-образ
- **THEN** HTTP health/root endpoint отвечает статусом 2xx и в runtime-образе отсутствует полноценный системный Node-интерпретатор как отдельный пакет/слой приложения (исполняется единый бинарь)

### Requirement: Documented image matrix
Система MUST документировать матрицу образов: язык, вариант (baseline / distroless / node-dynamic / node-static), тег образа и базовый runtime-образ.

#### Scenario: Matrix lists all expected variants
- **WHEN** оператор открывает документацию матрицы образов
- **THEN** в ней перечислены все варианты для Java, Python, Go (baseline + distroless) и для Node.js (baseline + dynamic distroless + static distroless)
