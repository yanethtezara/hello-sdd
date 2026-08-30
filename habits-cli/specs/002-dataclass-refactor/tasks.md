# Tareas — Spec 002

- [x] T1. Crear `habits/types.py` con `Habit`, `HabitSummary`, `HabitStore`, excepciones y métodos de dominio. (RF-1, RF-2, RF-3, RF-4, RF-5, RF-6, RF-7, RF-8)
      Hecho cuando: `tests/test_types.py` creado y en verde al ejecutar `uv run pytest -q`.
- [x] T2. Actualizar `habits/storage.py` con funciones de conversión dict <-> dataclass y retorno/recepción de `HabitStore`. (RF-9, RF-10)
      Hecho cuando: `tests/test_storage.py` adaptado y en verde al ejecutar `uv run pytest -q`.
- [x] T3. Actualizar `habits/core.py` para importar y reexportar desde `types.py`. (RF-5..RF-8)
      Hecho cuando: `tests/test_core.py` adaptado y en verde al ejecutar `uv run pytest -q`.
- [x] T4. Actualizar `habits/cli.py` para consumir el modelo `HabitStore`. (RF-11)
      Hecho cuando: `tests/test_cli.py` adaptado y en verde al ejecutar `uv run pytest -q`.
- [x] T5. Validación final de la spec y limpieza. (Todos los RF)
      Hecho cuando: la suite completa pase en verde con `uv run pytest -q`.
