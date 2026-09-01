## Purpose

Зафиксировать framework-based sample HTTP-приложения и варианты runtime-образов для сопоставимого distroless-эксперимента с реальными зависимостями.

## ADDED Requirements

### Requirement: Framework-based sample apps
Репозиторий MUST содержать sample HTTP-приложения: Java на Spring Boot, Node.js dynamic на Express, Python на FastAPI, Go на веб-фреймворке того же класса (Gin или эквивалент). Каждое приложение MUST отвечать на `GET /health` статусом 2xx и непустым телом.

#### Scenario: Health endpoint works for each framework app
- **WHEN** приложение языка запущено и клиент выполняет `GET /health`
- **THEN** ответ имеет статус 2xx и непустое тело

### Requirement: Node dynamic Express and static nginx variants
Для Node.js система MUST предоставлять dynamic-вариант на Express и static-вариант, где статика отдаётся через nginx. Оба варианта MUST быть представлены в матрице образов (baseline и distroless-совместимый runtime там, где применимо) и успешно проходить smoke `/health` или согласованный static health endpoint.

#### Scenario: Express dynamic serves health
- **WHEN** собран и запущен Node Express-образ
- **THEN** `GET /health` возвращает 2xx

#### Scenario: Nginx static serves content
- **WHEN** собран и запущен nginx static-образ
- **THEN** согласованный health/static endpoint отвечает статусом 2xx

### Requirement: Baseline and distroless image variants with aligned distro lineage
Для каждого языка система MUST предоставлять baseline и distroless (или distroless-совместимый) runtime-варианты на согласованной OS-линейке (Debian-first). Образы MUST собираться из Dockerfile/build-скриптов репозитория.

#### Scenario: Pair builds for a language
- **WHEN** оператор собирает baseline и distroless варианты языка
- **THEN** оба образа успешно собираются с различимыми тегами

### Requirement: Documented image matrix
Система MUST документировать матрицу: язык, вариант, тег образа, базовый runtime, distro lineage.

#### Scenario: Matrix includes framework variants
- **WHEN** оператор открывает матрицу образов
- **THEN** в ней есть Spring Boot, Express dynamic, nginx static, FastAPI и Go framework варианты с lineage
