## 1. Layered jars и второе приложение

- [x] 1.1 Включить Spring Boot layers в `apps/java/pom.xml`
- [x] 1.2 Добавить `apps/java2` (тот же Spring Boot stack, другой `/health` payload / artifactId) с layers
- [x] 1.3 `Dockerfile.distroless-jlink-layered` для java: extract layertools → отдельные COPY → jlink на cc-debian12 + JarLauncher; smoke `/health`

## 2. Матрица и метрики

- [x] 2.1 Layered Dockerfile для java2; строки MATRIX (+ fat java2 при необходимости для fair footprint)
- [x] 2.2 Скрипт/хелпер: размеры layer groups + сравнение digests общих слоёв двух образов
- [x] 2.3 Опционально: median time-to-healthy fat vs layered (или явный skip в отчёте)

## 3. Отчёт и документация

- [x] 3.1 Секция в `render_benchmark_report.py`: fat vs layered sizes, shared vs app, footprint 2 apps
- [x] 3.2 Обновить README (новые варианты / цель эксперимента)

## 4. Прогон

- [x] 4.1 `make bench` — smoke OK; `reports/latest.md` с секцией layered + цифрами shared/app
