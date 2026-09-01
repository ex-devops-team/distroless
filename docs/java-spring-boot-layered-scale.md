# Java: Spring Boot layered + jlink/distroless — масштаб, pull, старт, registry

Документ собирает выводы эксперимента в репозитории `distroless` и внешние референсы.
Измерения: `reports/latest.md` (секция **Java: fat jar vs layered**), OpenSpec change `java-spring-boot-layered-cache`.

Дата сводки: 2026-08-25.

---

## 1. Что измеряли

Стек: **jlink custom JRE** на `gcr.io/distroless/cc-debian12` + Spring Boot 3.4.

| Вариант | Суть |
|---------|------|
| fat | один `.jar` в образе (`distroless-jlink`) |
| layered | layertools extract → отдельные Docker-слои (`dependencies` → … → `application`) |
| java2 | второе приложение с тем же dependency stack, другим application-кодом |

### 1.1 Цифры прогона (локальный bench)

| Метрика | Значение |
|---------|----------|
| Layer `dependencies` | ~19.5 MB |
| Layer `spring-boot-loader` | ~0.4 MB |
| Layer `application` | ~5.5 KB (~0.005 MB) |
| Размер образа fat ≈ layered | ~64.7 MB |
| Shared RootFS digests java ↔ java2 | **23 / 24** слоёв |
| 2×fat | ~129.4 MB |
| Модель «1×shared + 2×app» | ~64.7 MB (Δ ≈ **−65 MB**) |
| time-to-healthy median (N=3) | fat **5.265** s, layered **5.242** s |

Вывод по app-слою в этом sample: код приложения **≪ 1%** объёма образа и jar-groups; почти всё — base/jlink + Spring dependencies.

Оговорка по старту: Δ ~0.02 s на фоне Docker Desktop — **шум**, не доказанный выигрыш.

---

## 2. Модель масштаба

Обозначения:

- \(S\) — shared (base + jlink + dependencies + loader), одинаковые digests между apps  
- \(A\) — слой `application`  
- \(N\) — число приложений с **одним** shared-стеком  

| Без шаринга (fat / naive layered) | С шарингом слоёв |
|-----------------------------------|------------------|
| \(N \cdot (S + A)\) | \(S + N \cdot A\) |

\[
\text{экономия storage} \approx (N - 1) \cdot S
\]

Важно:

- Рост **\(A\)** (больше кода) почти **не уменьшает** экономию — \(A\) платится \(N\) раз в обеих моделях.  
- Рост **\(S\)** (больше зависимостей) **увеличивает** экономию.  
- Шаринг работает только при **байт-идентичных** shared-слоях (один BOM / версии Spring). Разные стеки → несколько «семей» \(S\).

---

## 3. Сводная таблица (N = 800, идеал: один stack)

Оценка **времени pull**: \(\mathrm{t} \approx \mathrm{size} / \mathrm{bandwidth}\) (порядок величины; ниже — типичные DC-линки **1G / 10G+**, не «домашний» канал).

| Сценарий | \(S\) | \(A\) | Registry 800×fat | Registry + share | Экономия store | Pull cold (1 app) | Pull warm redeploy | Старт (ожидание) |
|----------|------|------|------------------|------------------|----------------|-------------------|--------------------|------------------|
| Как в bench | ~65 MB | ~5 KB | ~50.5 GiB | ~0.07 GiB | **~50.5 GiB** | ~65 MB | **~5 KB** | ≈ без Δ (наш median) |
| Боевой | 80 MB | 5 MB | ~66 GiB | ~4 GiB | **~62 GiB** | ~85 MB | **~5 MB** | небольшой выигрыш unpacked |
| Тяжелее | 120 MB | 20 MB | ~109 GiB | ~16 GiB | **~94 GiB** | ~140 MB | **~20 MB** | заметнее на большом jar |
| Ещё тяжелее | 150 MB | 50 MB | ~156 GiB | ~39 GiB | **~117 GiB** | ~200 MB | **~50 MB** | + CDS/AOT поверх layered |

Пересчёт pull во время на **1 GbE / 10 GbE** (line rate ≈ 125 / 1250 MB/s; реальный goodput часто ~70–90% — порядок тот же):

| Объём | 1 GbE (~125 MB/s) | 10 GbE (~1.25 GB/s) | 25 GbE (~3.1 GB/s) |
|-------|-------------------|---------------------|---------------------|
| Cold ~65 MB (bench \(S{+}A\)) | ~0.5 s | ~0.05 s | ~0.02 s |
| Cold ~200 MB (тяжёлый образ) | ~1.6 s | ~0.16 s | ~0.06 s |
| Warm ~5 MB (боевой \(A\)) | ~0.04 s | ~4 ms | ~2 ms |
| Warm ~50 MB (толстый \(A\)) | ~0.4 s | ~0.04 s | ~0.02 s |

На **10G+** одиночный pull уже мал рядом с JVM start (~секунды). Выигрыш layered там смещается к:

1. **Storage** registry — \((N-1)\cdot S\) (десятки GiB при N=800).  
2. **Массовый rollout** — сотни нод × полный \(S{+}A\) vs дельта \(A\) (шторм на registry/сеть).  
3. **Первый cold start на пустой ноде** всё ещё платит \(S{+}A\); дальше на этой ноде — в основном \(A\).

Главный смысл pull-оптимизации — **не качать \(S\) повторно**, а не «сжать» один образ.

Доля \(A\) в одном образе в «боевых» рядах таблицы — уже не ≪1%, а порядка **6–25%**; экономия на 800 apps при этом всё равно десятки–сотни GiB за счёт \((N-1)\cdot S\).

---

## 4. Время старта — референсы

| Утверждение | Источник |
|-------------|----------|
| Nested fat jar даёт **небольшой** overhead на старте; **exploded/unpacked** быстрее и рекомендуется в production; после старта runtime одинаковый | [Spring Boot — Efficient Deployments](https://docs.spring.io/spring-boot/reference/packaging/efficient.html) |
| Один слой с fat jar субоптимален для Docker; deps и application лучше разнести; unpacked «slightly faster» | [Spring Boot 2.7 — Container Images](https://docs.spring.io/spring-boot/docs/2.7.x/reference/html/container-images.html) |
| Layout после extract удобен для **CDS / AOT cache** | [Spring Boot — Dockerfiles](https://docs.spring.io/spring-boot/reference/packaging/container-images/dockerfiles.html) |
| Независимый замер: unpacked layered ≈ **−11%** vs fat jar; unpacked + **CDS** ≈ **−29%** | [Dominik Cebula — Startup comparison](https://blog.dominikcebula.com/optimizing-spring-boot-startup-time-a-comparative-analysis-of-jvm-and-native-image-configurations/) |
| Layered jars: кэш dependencies между сборками и сервисами | [springframework.guru — Why use Docker layers](https://springframework.guru/why-you-should-be-using-spring-boot-docker-layers/) |

**Практика:** заметный выигрыш старта ждать от **unpacked + CDS/AOT cache**, не от одного Docker layering. Наш bench (fat vs layered JarLauncher) старт не разделил.

---

## 5. Что такое CDS и AOT cache

Это **фичи JVM** (не Docker и не «Spring AOT processing» в смысле native hints). Цель одна: меньше работы при каждом cold start — не парсить/линковать одни и те же классы с нуля.

Связь с layered/unpacked: Spring рекомендует **сначала extract** jar (exploded layout), затем training run → файл кэша рядом с приложением. Nested fat jar для этого хуже подходит.

```
fat jar  →  extract (layertools / jarmode=tools)
                 ↓
         training run  →  *.jsa (CDS)  или  *.aot (AOT cache)
                 ↓
         prod start с -XX:SharedArchiveFile=…  или  -XX:AOTCache=…
```

### 5.1 CDS (Class Data Sharing) / AppCDS

**Идея:** JVM один раз загружает и обрабатывает классы, складывает их метаданные в архив (часто `*.jsa`). При следующих стартах архив **memory-map**’ится: классы не читаются и не парсятся заново с диска так же дорого.

| Термин | Смысл |
|--------|--------|
| **CDS** | Базовый механизм JDK: шаринг class metadata (исторически — в основном JDK-классы; default archive уже в дистрибутиве JDK) |
| **AppCDS** | Расширение: в архив попадают ещё **классы приложения и classpath** (Spring, ваши пакеты) |

**Типичный цикл (Spring Boot, JDK ≤ 24 / пока нет AOT cache):**

1. `java -Djarmode=tools -jar app.jar extract …`  
2. Training:  
   `java -XX:ArchiveClassesAtExit=application.jsa -Dspring.context.exit=onRefresh -jar …`  
3. Prod:  
   `java -XX:SharedArchiveFile=application.jsa -jar …`

**Что даёт:** быстрее старт, чуть меньше Metaspace при нескольких JVM на одной машине (read-only страницы шарятся).  
**Чего не даёт:** не убирает инициализацию Spring-контекста, рефлексию бинов, I/O к БД и т.п. — только «разогрев» загрузки классов.

Ориентир из внешних замеров: unpacked + CDS порядка **−30%** к cold start vs обычный fat jar ([Cebula](https://blog.dominikcebula.com/optimizing-spring-boot-startup-time-a-comparative-analysis-of-jvm-and-native-image-configurations/)).

Доки: [Oracle — Class Data Sharing](https://docs.oracle.com/en/java/javase/22/vm/class-data-sharing.html), [Spring Boot — Class Data Sharing](https://docs.spring.io/spring-boot/reference/packaging/class-data-sharing.html).

### 5.2 AOT cache (JVM, Project Leyden / JEP 483)

**Идея:** эволюция CDS. Кэш хранит не только «разобранные» классы, но и больше **ahead-of-time** состояния (загрузка/linking и дальше по мере зрелости Leyden), чтобы cold start был ближе к «уже подготовленной» JVM.

- Появляется в линии **JDK 24+**, Spring Boot рекомендует AOT cache на **Java 25+**, на более старых JDK — оставаться на CDS.  
- Файл кэша обычно `*.aot`, старт: `-XX:AOTCache=app.aot`.  
- Training run тоже на **extracted** приложении (как у CDS).

Упрощённо:

| | CDS / AppCDS | AOT cache (JVM) |
|--|--------------|-----------------|
| JDK | давно / AppCDS зрелый | 24+, предпочтительно 25+ |
| Файл | `*.jsa` | `*.aot` |
| Суть | шаринг class metadata | преемник CDS, глубже AOT-подготовка |
| Spring | поддерживает | рекомендует, если JDK позволяет |

Доки: [Spring Boot — AOT Cache](https://docs.spring.io/spring-boot/reference/packaging/aot-cache.html), [Spring Boot — CDS (с блоком AOT cache)](https://docs.spring.io/spring-boot/reference/packaging/class-data-sharing.html).

### 5.3 Не путать: Spring AOT processing ≠ JVM AOT cache

| | Spring AOT (Framework) | JVM AOT cache |
|--|------------------------|---------------|
| Кто | Spring (build-time) | HotSpot / Leyden |
| Что | генерирует код/hints, меньше рефлексии; путь к **GraalVM native-image** | кэш классов для **того же JVM** на следующих стартах |
| Артефакт | сгенерированные источники / `native-image` binary | `*.aot` рядом с app |
| Связь с layered | полезен отдельно | требует exploded layout, как CDS |

В таблице масштаба фраза «+ CDS/AOT» значит: **после** layered/unpacked включить JVM-кэш классов — это следующий рычаг старта, не замена шаринга Docker-слоёв.

### 5.4 Как это стыкуется с нашим экспериментом

| Слой оптимизации | Что ускоряет | Есть в нашем bench? |
|------------------|--------------|---------------------|
| Distroless + jlink | размер/CVE base+JRE | да (2×2) |
| Docker layered jars | pull / registry / cache на нодах | да |
| Unpacked (JarLauncher / extract) | чуть меньше overhead nested jar | layered = unpacked dirs |
| **CDS / AOT cache** | загрузка классов при cold start | **нет** (не включали) |
| GraalVM native | радикальный старт | out of scope |

Поэтому в документе «потенциальное время старта» для CDS/AOT — из доков и внешних бенчей, не из `make bench`.

---

## 6. Артефактное хранилище (Harbor / Nexus / Artifactory)

Для частного контура смотрим на **self-hosted OCI registry**: Harbor, Sonatype Nexus (Docker/OCI), JFrog Artifactory. Модель та же: слои по digest, повторная загрузка того же blob не нужна.

### 6.1 Два главных плюса layered при общем \(S\)

| Плюс | Что происходит | Зачем важно |
|------|----------------|-------------|
| **Push в основном \(A\)** | После того как base/jlink/dependencies уже лежат в registry, CI при выкладке app **не заливает \(S\) снова** — клиент делает mount/reuse существующих blob’ов и загружает новый слой application | Быстрее pipeline, меньше нагрузка на registry и канал CI→registry |
| **Экономия места за счёт дедупа слоёв** | На диске registry \(S\) хранится **один раз** на все apps с тем же digest; формула \(S + N\cdot A\) вместо \(N\cdot(S+A)\) | Меньше volume PVC/дисков бэкапов; при N=800 и \(S\sim65\)–150 MB — десятки GiB (см. §3) |

Без совпадения digests оба плюса схлопываются: каждый «уникальный» стек снова полный push и полный \(S\) на диске.

### 6.2 Как это выглядит на практике

```
1-й сервис (или общий base-image push):  upload S + A₁
2-й … N-й сервис (тот же BOM/jlink):     upload ≈ Aᵢ   (S уже в registry)
Хранилище:                               S + A₁ + … + Aₙ
```

Pull на нодах — симметрично: cold node тянет \(S{+}A\), дальше при том же \(S\) — дельта \(A\) (см. §3, 1G/10G).

### 6.3 Замечания по продуктам

| Система | Заметка |
|---------|---------|
| **Harbor** | OCI registry; blob storage content-addressable — одинаковые layers не дублируются внутри registry |
| **Nexus** | Docker/OCI hosted repo; экономия через те же digest’ы слоёв |
| **Artifactory** | Docker/OCI; дедуп blob’ов по checksum; плюс привычный push/pull из CI |
| Облачный ECR/GHCR | Та же OCI-логика; у ECR дополнительно cross-repo blob mounting (2026) — для **приватной** установки не обязательно, внутри одного Harbor/Nexus дедуп и так по digest |

Cloud-$/GB здесь вторичны: в on-prem важнее **диск registry**, **время CI push** и **шторм pull** при rollout.

Ограничение то же: шаринг только при **байт-идентичных** shared-слоях (наш bench: 23/24 RootFS между java и java2).

---

## 7. Практические выводы

1. В **Harbor / Nexus / Artifactory** при общем стеке: **push ≈ только \(A\)** + **дедуп \(S\) на диске registry** (\(S + N\cdot A\)).  
2. **Redeploy / warm node**: pull в основном \(A\); на 10G+ одиночный pull мал vs JVM start — ценнее массовый rollout и storage.  
3. **Старт** от layering alone — скромный; для старта — unpacked + **CDS** (JDK 21) или **AOT cache** (JDK 25+).  
4. **Больше deps** → больше экономия \((N-1)S\); **больше кода** → выше footprint, формула экономии от \(S\) та же.  
5. Нужна дисциплина BOM/версий, иначе digests разъедутся — и push снова полный, и дедупа нет.

---

## 8. Связанные артефакты в репо

| Путь | Назначение |
|------|------------|
| `reports/latest.md` | Актуальный bench-отчёт с секцией layered |
| `apps/java/`, `apps/java2/` | Sample-приложения и Dockerfile `*-layered` |
| `scripts/java_layered_metrics.py` | Размеры groups + сравнение RootFS digests |
| `openspec/changes/java-spring-boot-layered-cache/` | OpenSpec proposal / design / specs / tasks |

---

## 9. Список ссылок

1. https://docs.spring.io/spring-boot/reference/packaging/efficient.html  
2. https://docs.spring.io/spring-boot/docs/2.7.x/reference/html/container-images.html  
3. https://docs.spring.io/spring-boot/reference/packaging/container-images/dockerfiles.html  
4. https://docs.spring.io/spring-boot/reference/packaging/class-data-sharing.html  
5. https://docs.spring.io/spring-boot/reference/packaging/aot-cache.html  
6. https://docs.oracle.com/en/java/javase/22/vm/class-data-sharing.html  
7. https://blog.dominikcebula.com/optimizing-spring-boot-startup-time-a-comparative-analysis-of-jvm-and-native-image-configurations/  
8. https://springframework.guru/why-you-should-be-using-spring-boot-docker-layers/  
9. https://cloudburn.io/blog/amazon-ecr-pricing  
10. https://aws.amazon.com/about-aws/whats-new/2026/01/amazon-ecr-cross-repository-layer-sharing/  
