"""Lógica de dominio: pura, sin entrada/salida ni reloj propio.

Todas las funciones reciben la fecha de hoy como parámetro (``today``) para
poder probar las rachas sin depender del reloj del sistema.
"""

from __future__ import annotations

from collections.abc import Iterable
from datetime import date

from habits.types import (
    DuplicateHabitError,
    EmptyNameError,
    Habit,
    HabitError,
    HabitNotFoundError,
    HabitStore,
    HabitSummary,
    normalize,
)

__all__ = [
    "DuplicateHabitError",
    "EmptyNameError",
    "Habit",
    "HabitError",
    "HabitNotFoundError",
    "HabitStore",
    "HabitSummary",
    "add_habit",
    "list_habits",
    "mark_done",
    "normalize",
    "streak",
]


def streak(completions: Iterable[str], *, today: date) -> int:
    """Función helper para calcular racha a partir de una lista de fechas ISO."""
    dummy = Habit(name="", created_at="", completions=list(completions))
    return dummy.streak(today)


def add_habit(store: HabitStore, name: str, *, today: date) -> HabitStore:
    """Crea un hábito nuevo (RF-1).

    Lanza ``EmptyNameError`` si el nombre está vacío y
    ``DuplicateHabitError`` si ya existe uno equivalente.
    """
    store.add_habit(name, today)
    return store


def mark_done(store: HabitStore, name: str, *, today: date) -> tuple[HabitStore, bool]:
    """Marca el hábito como hecho hoy (RF-4).

    Devuelve la estructura de datos y un booleano que indica si ya estaba marcado.
    Lanza ``HabitNotFoundError`` si el hábito no existe.
    """
    _, already_done = store.mark_done(name, today)
    return store, already_done


def list_habits(store: HabitStore, *, today: date) -> list[HabitSummary]:
    """Hábitos con su racha, por racha descendente y nombre alfabético (RF-7)."""
    return store.list_habits(today)
