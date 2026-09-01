# Distroless runtime benchmark report

- **UTC:** 2026-09-01T10:31:48Z
- **Run ID:** `20260901T103148Z`
- **Platform:** `linux/amd64`
- **Size metric:** docker local Size (bytes from docker image inspect)
- **Grype:** Application:         grype Version:             0.118.0

## Size: OS vs application (heuristic)

Не слойный анализ (не разбор Docker-слоёв). Формулы: Application ≈ size(distroless); OS baseline ≈ max(0, baseline−distroless); **OS distroless = 0** — весь измеренный size(distroless) отнесён к Application. Это **не** значит, что в distroless нет ОС/пакетов, и **не** равно нулю OS CVE (см. CVE-таблицу). Для Java comparable pair = **baseline-jlink** vs **distroless-jlink** (full JRE — в секции 2×2).

| Language | OS baseline | OS distroless | Application | Total baseline | Total distroless | Notes |
|----------|-------------|---------------|-------------|----------------|------------------|-------|
| go | 26.2 | 0.0 | 3.5 | 29.8 | 3.5 |  |
| python | 31.8 | 0.0 | 29.6 | 61.3 | 29.6 |  |
| java | 21.5 | 0.0 | 64.7 | 86.2 | 64.7 | comparable pair = baseline-jlink vs distroless-jlink; full JRE — в секции Java 2×2 |
| nodejs | 27.1 | 0.0 | 50.8 | 77.9 | 50.8 |  |
| nginx | 66.3 | 0.0 | 2.8 | 69.0 | 2.8 | nginx vs Go file server — Application/size distroless другой бинарь |

## Java: full JRE vs jlink (2×2)

Отделяем вклад **distroless** (OS-база) и **jlink** (урезанный JRE). Строки — класс OS-базы; колонки — полный JRE vs jlink.

### Size (MB)

| | full JRE | jlink | Δ full→jlink |
|---|----------|-------|--------------|
| baseline | 98.7 | 86.2 | -12.5 |
| distroless | 78.0 | 64.7 | -13.3 |
| Δ baseline→distroless | -20.7 | -21.5 |  |

- Комбо (full baseline → jlink distroless): -34.0 MB

### CVE (Crit/High/Med/Low) и OS/app totals

| | full JRE | jlink |
|---|----------|-------|
| baseline C/H/M/L | 11/44/94/82 | 11/44/94/82 |
| distroless C/H/M/L | 5/40/65/41 | 5/26/32/27 |
| baseline OS/app/total | os=191 app=66 total=257 | os=191 app=66 total=257 |
| distroless OS/app/total | os=91 app=66 total=157 | os=29 app=66 total=95 |

- jlink *может* убрать CVE неиспользуемых модулей JDK; CVE fat jar (app) обычно те же; OS CVE: baseline full и baseline-jlink делят Temurin OS (сравниваем jlink); distroless full = java21, distroless-jlink = cc — OS разный; CVE fat jar обычно те же.


## Java: fat jar vs layered (jlink + distroless)

Spring Boot layer groups + Docker layers на `distroless-jlink`. Цель — shared dependencies между apps (registry / node cache / pull-дельта).

### Layer groups (из fat jar via layertools)

| Group | MB |
|-------|----|
| dependencies | 19.5 |
| spring-boot-loader | 0.4 |
| snapshot-dependencies | 0.0 |
| application | 0.005 |
| **sum groups** | 19.9 |

### Image size fat vs layered

| Variant | Image | MB |
|---------|-------|----|
| fat | `distroless-bench/java:distroless-jlink` | 64.7 |
| layered | `distroless-bench/java:distroless-jlink-layered` | 64.7 |

### Shared Docker layers (java vs java2 layered)

- Shared RootFS prefix: **23** / 24 vs 24 layers
- Digests расходятся после общего префикса (ожидаемо на application); общий prefix включает base/jre/dependencies при совпадении байтов.

### Registry footprint model (2 apps)

| Model | MB |
|-------|----|
| 2 × fat | 129.4 |
| 2 × layered (naive, no share) | 129.4 |
| layered shared model (1×shared + 2×app group) | 64.7 |

- shared_runtime_approx = size(layered java) − application group; two_layered_with_shared_model = shared_runtime + 2×application; assumes identical shared layers between apps (see rootfs_compare).
- Δ vs 2×fat (model): 64.8 MB (экономия)

### time-to-healthy (median)

- fat: **5.3** s; layered: **5.243** s (N=3, шум Docker Desktop возможен).
- wall clock docker run → HTTP 200 /health; noisy on Docker Desktop

## CVE: OS vs application

Только успешные smoke. OS = пакеты дистрибутива; Application = language ecosystem / binary приложения; Unknown = не классифицировано (входит в Total). Для Java — пара jlink (см. также секцию 2×2).

| Language | Slice | Crit | High | Med | Low | Unknown |
|----------|-------|------|------|-----|-----|---------|
| go | OS baseline | 7 | 17 | 63 | 66 | — |
| go | OS distroless | 0 | 0 | 0 | 0 | — |
| go | Application | 2 | 15 | 11 | 1 | — |
| go | Total baseline | 9 | 32 | 74 | 67 | 0 |
| go | Total distroless | 2 | 15 | 11 | 1 | 0 |
| python | OS baseline | 8 | 29 | 83 | 91 | — |
| python | OS distroless | 3 | 56 | 107 | 74 | — |
| python | Application (baseline) | 0 | 5 | 8 | 2 | — |
| python | Application (distroless) | 0 | 3 | 3 | 1 | — |
| python | Total baseline | 8 | 34 | 91 | 93 | 0 |
| python | Total distroless | 3 | 59 | 110 | 75 | 0 |
| java | OS baseline | 7 | 23 | 67 | 68 | — |
| java | OS distroless | 1 | 5 | 5 | 13 | — |
| java | Application | 4 | 21 | 27 | 14 | — |
| java | Total baseline | 11 | 44 | 94 | 82 | 0 |
| java | Total distroless | 5 | 26 | 32 | 27 | 0 |
| nodejs | OS baseline | 9 | 43 | 86 | 73 | — |
| nodejs | OS distroless | 3 | 20 | 8 | 14 | — |
| nodejs | Application (baseline) | 3 | 37 | 15 | 3 | — |
| nodejs | Application (distroless) | 0 | 7 | 11 | 7 | — |
| nodejs | Total baseline | 12 | 80 | 101 | 76 | 0 |
| nodejs | Total distroless | 3 | 27 | 19 | 21 | 0 |
| nginx | OS baseline | 31 | 155 | 185 | 147 | — |
| nginx | OS distroless | 0 | 0 | 0 | 0 | — |
| nginx | Application (baseline) | 0 | 0 | 0 | 0 | — |
| nginx | Application (distroless) | 2 | 13 | 9 | 1 | — |
| nginx | Total baseline | 31 | 155 | 185 | 147 | 0 |
| nginx | Total distroless | 2 | 13 | 9 | 1 | 0 |

## Matrix (smoke / tags)

| Language | Variant | Distro | Comparable pair | Image | Smoke | Notes |
|----------|---------|--------|-----------------|-------|-------|-------|
| go | baseline | debian12 | true | `distroless-bench/go:baseline` | ok |  |
| go | distroless | debian12 | true | `distroless-bench/go:distroless` | ok |  |
| python | baseline | debian12 | true | `distroless-bench/python:baseline` | ok |  |
| python | distroless | debian12 | true | `distroless-bench/python:distroless` | ok |  |
| java | baseline | debian12 | 2×2 only | `distroless-bench/java:baseline` | ok | full JRE (не jlink) |
| java | distroless | debian12 | 2×2 only | `distroless-bench/java:distroless` | ok | full JRE (не jlink) |
| java | baseline-jlink | debian12 | true | `distroless-bench/java:baseline-jlink` | ok | jlink custom JRE |
| java | distroless-jlink | debian12 | true | `distroless-bench/java:distroless-jlink` | ok | jlink custom JRE |
| java | distroless-jlink-layered | debian12 | layered | `distroless-bench/java:distroless-jlink-layered` | ok | Spring Boot layers + jlink |
| java2 | distroless-jlink | debian12 | fat pair | `distroless-bench/java2:distroless-jlink` | ok | second app for shared-layer experiment |
| java2 | distroless-jlink-layered | debian12 | layered | `distroless-bench/java2:distroless-jlink-layered` | ok | second app for shared-layer experiment |
| nodejs | baseline | debian12 | true | `distroless-bench/nodejs:baseline` | ok |  |
| nodejs | distroless-dynamic | debian12 | true | `distroless-bench/nodejs:distroless-dynamic` | ok |  |
| nginx | baseline | debian12 | true | `distroless-bench/nginx:baseline` | ok |  |
| nginx | distroless | debian12 | true | `distroless-bench/nginx:distroless` | ok | Go file server, not nginx |

## Interpretation notes

- Все baseline/distroless пары сопоставимы по distro lineage (Comparable pair = true).
- Node.js: baseline vs distroless-dynamic = Express. nginx — baseline nginx vs distroless Go file server (Application несопоставим).
- Java: в общей таблице — baseline-jlink vs distroless-jlink; full Temurin / distroless java21 — только в секции Java 2×2; fat vs layered / java2 — в секции layered.
- Quality toolchain (lint/test) выполняется в build stage и не входит в final runtime images.
- CVE Total = os + app + unknown того же образа. Таблица размера — эвристика (не слои): колонка OS distroless всегда 0, потому что весь size(distroless) в Application; OS CVE в distroless при этом может быть > 0.
- nginx: размер/CVE Application на стороне distroless относятся к static Go server.

## Failures / incomplete

_None — all matrix rows produced successful measurements._

## Raw artifacts

- Meta: `meta-20260901T103148Z.json`
- `result-go-baseline-20260901T103148Z.json`
- `result-go-distroless-20260901T103148Z.json`
- `result-python-baseline-20260901T103148Z.json`
- `result-python-distroless-20260901T103148Z.json`
- `result-java-baseline-20260901T103148Z.json`
- `result-java-distroless-20260901T103148Z.json`
- `result-java-baseline-jlink-20260901T103148Z.json`
- `result-java-distroless-jlink-20260901T103148Z.json`
- `result-java-distroless-jlink-layered-20260901T103148Z.json`
- `result-java2-distroless-jlink-20260901T103148Z.json`
- `result-java2-distroless-jlink-layered-20260901T103148Z.json`
- `result-nodejs-baseline-20260901T103148Z.json`
- `result-nodejs-distroless-dynamic-20260901T103148Z.json`
- `result-nginx-baseline-20260901T103148Z.json`
- `result-nginx-distroless-20260901T103148Z.json`
