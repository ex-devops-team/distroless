## 1. Каркас и документация

- [x] 1.1 Обновить README: стеки (Spring Boot / Express / nginx / FastAPI / Gin), quality tools, правило multi-stage isolation
- [x] 1.2 Обновить матрицу образов (убрать SEA; добавить Express dynamic и nginx static) с `distro_lineage`

## 2. Java — Spring Boot

- [x] 2.1 Создать Spring Boot app с `GET /health`, JUnit-тестами и линтером (Spotless/Checkstyle)
- [x] 2.2 Dockerfile baseline/distroless: quality (lint+test) → build jar → runtime без test toolchain
- [x] 2.3 Проверить fail-on-test и отсутствие test deps в final образе

## 3. Node.js — Express + nginx

- [x] 3.1 Express app с `/health`, ESLint, unit tests; Dockerfile dynamic baseline/distroless с quality stage
- [x] 3.2 Nginx static вариант (конфиг + health), baseline + distroless-совместимый runtime по design
- [x] 3.3 Убедиться, что SEA/static Node binary больше не используется в матрице

## 4. Python — FastAPI

- [x] 4.1 FastAPI app с `/health`, Ruff, pytest
- [x] 4.2 Dockerfile baseline/distroless: quality → prod deps → runtime без requirements-dev

## 5. Go — Gin (или эквивалент)

- [x] 5.1 Gin app с `/health`, `go test`, golangci-lint
- [x] 5.2 Dockerfile baseline/distroless: quality → static binary → runtime без toolchain

## 6. Benchmark и верификация

- [x] 6.1 Обновить `scripts/benchmark.sh` под новую матрицу и comparable-пары (Express vs nginx как отдельные варианты)
- [x] 6.2 Прогнать полный benchmark и сохранить отчёт
- [x] 6.3 Зафиксировать в отчёте/README, что quality toolchain не входит в final images
