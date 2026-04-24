# SCE Core — обзор (RU)

## Что такое SCE Core

SCE Core — это вычислительный framework для изучения Constraint-Driven Stability (CDS)
в адаптивных системах, с прикладной decision-engine поверхностью для AI-агентов.

Он соединяет в одном цикле:
- выбор допустимого плана,
- объяснение, что именно несло решение,
- измерение надёжности по результату,
- эпизодическую память,
- адаптацию следующего выбора.

```text
Решить → Объяснить → Запомнить/Надёжность → Улучшить
```

SCE Core — не просто набор демо и не «чат-обёртка».
Это переиспользуемый CDS-oriented вычислительный и decision layer с inspectable API/graph/UI поверхностями.

---

## Что уже реализовано

В текущем репозитории уже есть:

- constrained selection (кандидаты, скоринг, ранжирование),
- decision backbone extraction (несущая структура решения),
- reliability tracking из prediction error,
- episodic memory (с опциональной PostgreSQL-персистентностью),
- adaptive reselection под влиянием памяти и надёжности,
- inspectable API: `/decide`, `/memory`, `/reliability`, `/graph`, `/ui`,
- три флагманских демо на одном движке: `supplier-risk`, `hypothesis`, `resource-stability`.

---

## Флагманские демо

### `supplier-risk` (product-facing)

Практический вход в систему:

```text
контекст поставщика → выбор плана → backbone-объяснение → сигнал надёжности → влияние памяти → улучшенный следующий выбор
```

### `hypothesis` (research-facing)

Исследовательский вход в тот же цикл:
- ранжирование конкурирующих гипотез,
- разделение decision-carrying evidence и dangling context,
- формирование следующих исследовательских шагов.

### `resource-stability` (scientific toy model)

Первый компактный научный сценарий:
- начальный неустойчивый режим «популяция-ресурсы»,
- детерминированный набор candidate regimes,
- ранжирование по stability under constraints,
- выбор устойчивого режима + список non-carrying режимов,
- следующие исследовательские шаги.

---

## Переиспользуемая API-поверхность

Базовые endpoints:

- `POST /decide`
- `GET /memory`
- `GET /reliability`
- `GET /graph`
- `GET /ui`

Поддерживающие showcase endpoints:

- `POST /ask`
- `GET /demo`
- `POST /demo`
- `POST /demo/explain`

Важно: `/memory` и `/reliability` отражают процесс-локальное состояние текущего API-процесса.

---

## Коротко про bridge CDS → SCE

Теоретическая рамка CDS (Constraint-Driven Stability) интерпретируется в SCE как практический decision loop:

- constraints задают допустимые переходы,
- trajectory selection выбирает план,
- structural carrier/backbone объясняет «почему»,
- reliability показывает эмпирическую устойчивость траектории,
- episodic memory переносит результат в следующий цикл,
- adaptive reselection изменяет будущий выбор.

Полная operational mapping: [`constraint_driven_stability.md`](constraint_driven_stability.md).
Научное позиционирование и границы claims: [`scientific_positioning.md`](scientific_positioning.md).

---

## Куда проект движется

Ближний фокус:

- усиление inspectability и replayability,
- улучшение temporal dynamics для reliability/memory,
- развитие набора `supplier-risk` + `hypothesis` + `resource-stability` как benchmark-минимума,
- дальнейшее укрепление API/UI без ломки контрактов.

Исследовательские открытые задачи: [`research_program.md`](research_program.md).
План реализации и приоритеты: [`../ROADMAP.md`](../ROADMAP.md).

---

## Навигация по слоям документации

- Product entrypoint (EN): [`../README.md`](../README.md)
- Origin / история идеи: [`origin.md`](origin.md)
- Theory bridge CDS → SCE: [`constraint_driven_stability.md`](constraint_driven_stability.md)
- Research program: [`research_program.md`](research_program.md)
- Roadmap: [`../ROADMAP.md`](../ROADMAP.md)
