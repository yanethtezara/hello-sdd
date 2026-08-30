"""Dataclasses de dominio y excepciones de habits-cli.

Este módulo no importa de ningún otro módulo interno de la aplicación.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import Iterable


class HabitError(Exception):
    """Error de dominio; la CLI lo traduce a un mensaje en español."""


class EmptyNameError(HabitError):
    """El nombre está vacío o solo tiene espacios (RF-3)."""


class DuplicateHabitError(HabitError):
    """Ya existe un hábito con ese nombre (RF-2)."""


class HabitNotFoundError(HabitError):
    """No existe ningún hábito con ese nombre (RF-6)."""


def normalize(name: str) -> str:
    """Clave de comparación: sin espacios exteriores y sin mayúsculas."""
    return name.strip().casefold()


@dataclass
class Habit:
    """Representa un hábito individual y su historial de cumplimiento."""

    name: str
    created_at: str
    completions: list[str] = field(default_factory=list)

    def normalize_name(self) -> str:
        """Clave de comparación del hábito."""
        return normalize(self.name)

    def streak(self, today: date) -> int:
        """Días consecutivos completados hasta hoy o ayer (RF-10 Spec 001)."""
        days = sorted({date.fromisoformat(stamp) for stamp in self.completions})
        if not days:
            return 0

        last = days[-1]
        if last < today - timedelta(days=1):
            return 0

        count = 1
        expected = last - timedelta(days=1)
        for day in reversed(days[:-1]):
            if day != expected:
                break
            count += 1
            expected -= timedelta(days=1)

        return count

    def mark_done(self, today: date) -> bool:
        """Marca el hábito como hecho hoy de forma idempotente.

        Devuelve True si ya estaba marcado hoy, False si es nuevo.
        """
        stamp = today.isoformat()
        already_done = stamp in self.completions
        if not already_done:
            self.completions = sorted({*self.completions, stamp})
        return already_done


@dataclass
class HabitSummary:
    """Fila proyectada al listar hábitos (nombre y racha)."""

    name: str
    streak: int


@dataclass
class HabitStore:
    """Contenedor de todos los hábitos y versión del esquema."""

    version: int = 1
    habits: list[Habit] = field(default_factory=list)

    def find_habit(self, name: str) -> Habit | None:
        """Busca un hábito por nombre (insensible a mayúsculas y espacios)."""
        key = normalize(name)
        for habit in self.habits:
            if habit.normalize_name() == key:
                return habit
        return None

    def add_habit(self, name: str, today: date) -> Habit:
        """Crea y añade un nuevo hábito al almacén."""
        display_name = name.strip()
        if not display_name:
            raise EmptyNameError(name)

        existing = self.find_habit(display_name)
        if existing is not None:
            raise DuplicateHabitError(existing.name)

        habit = Habit(
            name=display_name,
            created_at=today.isoformat(),
            completions=[],
        )
        self.habits.append(habit)
        return habit

    def mark_done(self, name: str, today: date) -> tuple[Habit, bool]:
        """Marca el hábito especificado como realizado hoy."""
        habit = self.find_habit(name)
        if habit is None:
            raise HabitNotFoundError(name.strip())

        already_done = habit.mark_done(today)
        return habit, already_done

    def list_habits(self, today: date) -> list[HabitSummary]:
        """Devuelve hábitos ordenados por racha descendente y nombre alfabético."""
        rows = [
            HabitSummary(name=habit.name, streak=habit.streak(today))
            for habit in self.habits
        ]
        rows.sort(key=lambda row: (-row.streak, row.name.casefold()))
        return rows
