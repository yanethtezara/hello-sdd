# Plan técnico — Spec 002

## Estructura de módulos
- `habits/types.py` [NUEVO] → Dataclasses de dominio (`Habit`, `HabitStore`, `HabitSummary`) y excepciones de dominio. Sin dependencias de otros módulos de `habits`.
- `habits/storage.py` → Funciones de conversión entre dict/JSON y `HabitStore` (`_dict_to_store`, `_store_to_dict`). Operaciones `load()` (devuelve `HabitStore`) y `save()` (recibe `HabitStore`).
- `habits/core.py` → Funciones de conveniencia que delegan en las dataclasses de `types.py` y mantienen compatibilidad de firmas.
- `habits/cli.py` → Actualizado para trabajar con objetos `HabitStore` y atributos tipados en lugar de claves de diccionarios.
- `tests/` → Tests unitarios actualizados y ampliados para verificar `types.py` y el nuevo comportamiento orientado a objetos.

## Modelo de clases (`habits/types.py`)

### Excepciones
- `HabitError(Exception)`
- `EmptyNameError(HabitError)`
- `DuplicateHabitError(HabitError)`
- `HabitNotFoundError(HabitError)`

### Dataclasses
- `Habit`:
  - Campos: `name: str`, `created_at: str`, `completions: list[str]`
  - Métodos: `normalize_name() -> str`, `streak(today: date) -> int`, `mark_done(today: date) -> bool`
- `HabitSummary`:
  - Campos: `name: str`, `streak: int`
- `HabitStore`:
  - Campos: `version: int = 1`, `habits: list[Habit]`
  - Métodos: `find_habit(name: str) -> Habit | None`, `add_habit(name: str, today: date) -> Habit`, `mark_done(name: str, today: date) -> tuple[Habit, bool]`, `list_habits(today: date) -> list[HabitSummary]`

## Estrategia de Persistencia (`habits/storage.py`)
- `_dict_to_store(data: dict) -> HabitStore`: Valida tipos y reconstruye `HabitStore` y `Habit`s. Lanza `StorageError` si la estructura no coincide.
- `_store_to_dict(store: HabitStore) -> dict`: Convierte `HabitStore` a diccionario listo para `json.dumps`.

## Estrategia de Tests
- `tests/test_types.py`: Tests unitarios para las dataclasses `Habit`, `HabitStore` y sus métodos (`streak`, `mark_done`, `add_habit`, `list_habits`).
- `tests/test_storage.py`: Adaptar tests para verificar la carga/guardado de `HabitStore`.
- `tests/test_core.py`: Verificar la integración de funciones fachada con `types.py`.
- `tests/test_cli.py`: Probar comandos CLI con el nuevo modelo.
