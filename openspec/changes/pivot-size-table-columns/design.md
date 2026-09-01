## Context

Сейчас `render_benchmark_report.py` печатает Size как стек: 5 строк Slice × язык. Эвристика уже зафиксирована: Application = dist size, OS base = max(0, base−dist), OS dist = 0. CVE-таблица стековая и в этом change не меняется. См. proposal.md — Why.

## Goals / Non-Goals

**Goals:**
- Пивот Size: 1 строка / язык, Slice → колонки.
- Явное пояснение «почему OS distroless = 0» у таблицы и в notes/README.
- Пересборка отчёта из raw (`make report`) без полного bench, если raw уже есть.

**Non-Goals:**
- Пивот CVE-таблицы.
- Слойный анализ размера (dive/buildkit) или смена эвристики чисел.
- Изменение matrix/smoke/Grype.

## Decisions

### 1. Только Size пивотится
**Выбор:** CVE остаётся стековой (severity × Slice).  
**Альтернатива:** пивотить обе — шире scope, CVE-severity плохо ложатся в одну строку (Crit/High/Med/Low × 5 срезов).  
**Почему:** запрос про таблицу размеров.

### 2. Порядок колонок
`Language | jlink baseline | jlink distroless | OS baseline | OS distroless | Application | Total baseline | Total distroless | Notes` — jlink-колонки = вес соответствующих Java-образов с custom JRE (MB); для остальных языков `—`.

### 3. Пояснение OS distroless = 0
**Выбор:** короткий абзац сразу под заголовком Size (до таблицы) + строка в Interpretation notes; README синхронизировать.  
**Формулировка (смысл):** эвристика относит весь `size(distroless)` к Application, поэтому колонка OS distroless всегда 0; в distroless всё ещё могут быть OS-пакеты и OS CVE — смотрите CVE-таблицу.

### 4. Notes
Одна ячейка Notes на язык (как раньше notes на первой строке стека), не дублировать по колонкам.

## Risks / Trade-offs

- [Широкая markdown-таблица на узких экранах] → Mitigation: порядок колонок фиксирован; MB с одним знаком после запятой как сейчас.
- [Путаница «0 размера ОС» vs «0 CVE ОС»] → Mitigation: явный disclaimer у Size; Interpretation notes уже частично говорит об этом — усилить.
- [Старые report-*.md в git] → Mitigation: новые отчёты через `make report`; старые артефакты не трогать.

## Migration Plan

1. Обновить `render_benchmark_report.py`.
2. `make report` → `reports/latest.md`.
3. Обновить README.
4. Rollback: вернуть стековый цикл строк в рендерере.

## Open Questions

Нет.
