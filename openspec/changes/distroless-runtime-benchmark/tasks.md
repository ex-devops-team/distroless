## 1. Каркас репозитория

- [x] 1.1 Создать структуру `apps/{java,nodejs,python,go}/`, `scripts/`, `reports/` (+ `.gitignore` для raw/артефактов при необходимости)
- [x] 1.2 Добавить README с целью эксперимента, матрицей образов (заглушка тегов) и требованиями к инструментам (Docker, Grype)
- [x] 1.3 Зафиксировать выбранные LTS-теги базовых/distroless образов в матрице документации

## 2. Sample-приложения

- [x] 2.1 Реализовать минимальный HTTP `/health` на Go
- [x] 2.2 Реализовать минимальный HTTP `/health` на Python
- [x] 2.3 Реализовать минимальный HTTP `/health` на Node.js
- [x] 2.4 Реализовать минимальный HTTP `/health` на Java
- [x] 2.5 Убедиться, что локальный запуск каждого приложения отдаёт 2xx на `/health`

## 3. Dockerfiles: baseline и distroless

- [x] 3.1 Go: Dockerfile baseline + distroless (`static`, `CGO_ENABLED=0`)
- [x] 3.2 Python: Dockerfile baseline (slim) + distroless/python3
- [x] 3.3 Java: Dockerfile baseline (JRE slim) + distroless/java
- [x] 3.4 Node.js: Dockerfile baseline (node slim) + distroless **dynamic** (nodejs + app + node_modules)
- [x] 3.5 Node.js: Dockerfile distroless **static** (SEA / единый бинарь → static или cc)
- [x] 3.6 Проверить сборку всех образов матрицы и smoke HTTP для каждого успешного билда

## 4. Замер метрик и отчёт

- [x] 4.1 Скрипт/функция замера локального размера образа (байты → MB в отчёте)
- [x] 4.2 Скрипт сканирования Grype с агрегацией CRITICAL/HIGH/MEDIUM/LOW + версия Grype/DB в метаданных
- [x] 4.3 Smoke-check в прогоне: при failure не писать образ как успешное измерение
- [x] 4.4 Оркестратор `scripts/benchmark.sh` (или аналог): build → smoke → size → scan → raw JSON
- [x] 4.5 Генерация сравнительного markdown-отчёта в `reports/` по полной матрице
- [x] 4.6 Прогнать полный эксперимент один раз и сохранить отчёт с датой/версиями инструментов
