"""Persistencia en un único archivo JSON local (RF-9, RF-11)."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from habits.types import Habit, HabitStore

VERSION = 1


class StorageError(Exception):
    """El archivo de datos existe pero no se puede interpretar (RF-11)."""


PROJECT_ROOT = Path(__file__).resolve().parent.parent


def default_path() -> Path:
    """Ruta del único archivo de datos: ``habits.json`` en la raíz del proyecto."""
    return PROJECT_ROOT / "habits.json"


def empty_store() -> HabitStore:
    """Estructura inicial cuando todavía no hay archivo."""
    return HabitStore(version=VERSION, habits=[])


def empty_data() -> HabitStore:
    """Alias para retrocompatibilidad con la API de almacenamiento."""
    return empty_store()


def _dict_to_store(data: dict[str, Any], path: Path | None = None) -> HabitStore:
    """Convierte un diccionario JSON validado a HabitStore.

    Lanza StorageError si la estructura no es la esperada.
    """
    path_str = f"{path}: " if path else ""
    if not isinstance(data, dict) or not isinstance(data.get("habits"), list):
        raise StorageError(f"{path_str}no tiene la estructura esperada.")

    version = data.get("version", VERSION)
    if not isinstance(version, int):
        raise StorageError(f"{path_str}no tiene la estructura esperada.")

    habits: list[Habit] = []
    for item in data["habits"]:
        if (
            not isinstance(item, dict)
            or "name" not in item
            or "created_at" not in item
        ):
            raise StorageError(f"{path_str}no tiene la estructura esperada.")

        name = item["name"]
        created_at = item["created_at"]
        completions = item.get("completions", [])

        if (
            not isinstance(name, str)
            or not isinstance(created_at, str)
            or not isinstance(completions, list)
        ):
            raise StorageError(f"{path_str}no tiene la estructura esperada.")

        habits.append(
            Habit(name=name, created_at=created_at, completions=list(completions))
        )

    return HabitStore(version=version, habits=habits)


def _store_to_dict(store: HabitStore) -> dict[str, Any]:
    """Convierte HabitStore a un diccionario legible para serialización JSON."""
    return {
        "version": store.version,
        "habits": [
            {
                "name": habit.name,
                "created_at": habit.created_at,
                "completions": list(habit.completions),
            }
            for habit in store.habits
        ],
    }


def load(path: Path) -> HabitStore:
    """Lee el archivo de datos y devuelve un objeto HabitStore.

    Si no existe, devuelve una estructura vacía. Si existe pero no es
    JSON válido o no tiene la forma esperada, lanza ``StorageError``.
    """
    try:
        raw = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return empty_store()
    except OSError as error:
        raise StorageError(f"No se pudo leer {path}: {error}") from error

    try:
        data = json.loads(raw)
    except json.JSONDecodeError as error:
        raise StorageError(f"{path} no contiene JSON válido: {error}") from error

    return _dict_to_store(data, path=path)


def save(path: Path, store: HabitStore | dict[str, Any]) -> None:
    """Escribe el objeto HabitStore completo en formato JSON legible."""
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")

    if isinstance(store, dict):
        data_dict = store
    else:
        data_dict = _store_to_dict(store)

    text = json.dumps(data_dict, indent=2, ensure_ascii=False) + "\n"

    try:
        temporary.write_text(text, encoding="utf-8")
        os.replace(temporary, path)
    except OSError as error:
        temporary.unlink(missing_ok=True)
        raise StorageError(f"No se pudo escribir {path}: {error}") from error
