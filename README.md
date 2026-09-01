# Distroless runtime benchmark

Сравнение **размера** и **CVE** (Grype) для framework-based HTTP-сервисов: baseline (Debian) vs **distroless**.

## Стеки

| Язык | Framework / role | Lint | Tests |
|------|------------------|------|-------|
| Go | Gin | golangci-lint | `go test` |
| Python | FastAPI + uvicorn | Ruff | pytest |
| Java | Spring Boot 3 | Spotless | JUnit 5 |
| Node.js | Express (dynamic) | ESLint | `node --test` |
| Static | nginx (baseline) / tiny static server (distroless) | `nginx -t` / `go vet` | config/build checks |

## Quality gate

Lint и unit tests выполняются в **отдельном Docker stage** при сборке образа.  
Зависимости lint/test **не копируются** в финальный runtime-слой (только prod artifact + runtime deps).

Официального Google Distroless образа с nginx нет: для static distroless используется минимальный Go file server на `distroless/static-debian12` (та же роль: раздача статики + `/health`).

## Требования

- Docker (`linux/amd64`)
- Grype
- Make (GNU Make; на macOS при проблемах с BSD make — `brew install make` / `gmake`)
- Python 3
- curl
- Опционально локально: Go, Node 22+, Python 3.11, JDK 21, Maven

## Выравнивание baseline ↔ distroless (Debian-first)

Пары baseline/distroless целятся в **Debian 12 (bookworm)** и согласованные major/minor рантайма:

| Язык | Baseline runtime | Distroless runtime | Примечание |
|------|------------------|--------------------|------------|
| Go | `debian:bookworm-slim` | `static-debian12` | статический бинарь |
| Python | `python:3.11-slim-bookworm` | `python3-debian12` | 3.11 — лимит distroless |
| Java full | `debian:bookworm-slim` + Temurin 21 JRE (COPY) | `java21-debian12` | OS — Debian 12; JRE — Temurin 21 |
| Java jlink | `debian:bookworm-slim` + custom jlink JRE | `cc-debian12` + jlink | сопоставимая пара в отчёте |
| Node.js | `node:22.22.0-bookworm-slim` | `nodejs22-debian12` | pin minor под distroless |
| nginx | `nginx:1.27-bookworm` | Go static server | роль та же, бинарь другой |

## Быстрый старт

```bash
make          # полный прогон
make report   # пересобрать отчёт из reports/raw без rebuild
make help
```

Отчёт: `reports/latest.md`. Сырые JSON: `reports/raw/`.

## Матрица образов

| Язык | Variant | Image tag | Base runtime | distro_lineage |
|------|---------|-----------|--------------|----------------|
| Go | baseline | `distroless-bench/go:baseline` | `debian:bookworm-slim` | `debian12` |
| Go | distroless | `distroless-bench/go:distroless` | `gcr.io/distroless/static-debian12` | `debian12` |
| Python | baseline | `distroless-bench/python:baseline` | `python:3.11-slim-bookworm` | `debian12` |
| Python | distroless | `distroless-bench/python:distroless` | `gcr.io/distroless/python3-debian12` | `debian12` |
| Java | baseline | `distroless-bench/java:baseline` | `debian:bookworm-slim` + Temurin 21 JRE | `debian12` |
| Java | distroless | `distroless-bench/java:distroless` | `gcr.io/distroless/java21-debian12` | `debian12` |
| Java | baseline-jlink | `distroless-bench/java:baseline-jlink` | `debian:bookworm-slim` + jlink JRE 21 | `debian12` |
| Java | distroless-jlink | `distroless-bench/java:distroless-jlink` | `gcr.io/distroless/cc-debian12` + jlink JRE 21 | `debian12` |
| Java | distroless-jlink-layered | `distroless-bench/java:distroless-jlink-layered` | same + Spring Boot layered dirs | `debian12` |
| Java2 | distroless-jlink | `distroless-bench/java2:distroless-jlink` | same stack, другое app (`health2`) | `debian12` |
| Java2 | distroless-jlink-layered | `distroless-bench/java2:distroless-jlink-layered` | layered для сравнения shared deps | `debian12` |
| Node.js | baseline | `distroless-bench/nodejs:baseline` | `node:22.22.0-bookworm-slim` | `debian12` |
| Node.js | distroless-dynamic | `distroless-bench/nodejs:distroless-dynamic` | `gcr.io/distroless/nodejs22-debian12` | `debian12` |
| nginx | baseline | `distroless-bench/nginx:baseline` | `nginx:1.27-bookworm` | `debian12` |
| nginx | distroless | `distroless-bench/nginx:distroless` | `gcr.io/distroless/static-debian12` | `debian12` |

## CVE / размер: таблицы

В `reports/latest.md`:

**Размер** — одна строка на язык; колонки: OS baseline | OS distroless | Application | Total baseline | Total distroless | Notes.  
Для Java comparable pair = **baseline-jlink** vs **distroless-jlink**. Отдельная секция **Java 2×2** сравнивает full JRE vs jlink × baseline vs distroless (размер и CVE).  
Ещё одна секция — **fat jar vs layered** (jlink+distroless): размеры Spring Boot layer groups, shared layers java/java2, модель registry footprint, time-to-healthy.

Эвристика без слойного анализа: Application ≈ size(distroless), OS baseline ≈ max(0, baseline−distroless), **OS distroless = 0** (весь size(distroless) отнесён к Application). Это **не** значит «в образе нет ОС» и **не** равно нулю OS CVE.

**CVE** — стек на язык (строки Slice):

1. OS baseline  
2. OS distroless  
3. Application (одна строка, если app-CVE совпали; иначе две)  
4. Total baseline  
5. Total distroless  

OS / Application из Grype `artifact.type` (см. ниже). Total = os + app + unknown того же образа.

## CVE: классификация Grype

Grype matches классифицируются по `artifact.type` (и пути для `binary`):

| Класс | Правило |
|-------|---------|
| **os** | `deb` / `dpkg` / `rpm` / `apk` / `alpm` / `portage` / `linux-kernel`; `binary` с путём под `/usr`, `/lib`, `/bin`, `/sbin` |
| **app** | `java-archive`, `python`, `npm`, `yarn`, `go-module`, `dotnet`, `gem`; `binary` вне OS-путей (например `/health`, `/nodejs/bin/node`) |
| **unknown** | всё остальное (входит в Total; не смешивается с app) |

Стеки строятся только для пар с успешным smoke. `binary` с путём под `/usr`, `/lib`, `/bin` считается OS, иначе — app.

## Структура

```
apps/{go,python,java,nodejs,nginx}/
Makefile
scripts/{benchmark.py,grype_breakdown.py,render_benchmark_report.py,regenerate_cve_breakdown.py}
reports/
```
