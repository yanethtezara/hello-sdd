from datetime import date, timedelta
import pytest

from habits.types import (
    DuplicateHabitError,
    EmptyNameError,
    Habit,
    HabitNotFoundError,
    HabitStore,
    HabitSummary,
    normalize,
)


def test_normalize():
    assert normalize("  Estudiar Python  ") == "estudiar python"


def test_habit_streak():
    today = date(2026, 8, 30)
    habit = Habit(name="Test", created_at="2026-08-01", completions=[])
    assert habit.streak(today) == 0

    habit.completions = ["2026-08-29", "2026-08-30"]
    assert habit.streak(today) == 2

    # Racha rota (último registro anterior a ayer)
    habit.completions = ["2026-08-25"]
    assert habit.streak(today) == 0


def test_habit_mark_done():
    today = date(2026, 8, 30)
    habit = Habit(name="Test", created_at="2026-08-01", completions=[])

    already = habit.mark_done(today)
    assert not already
    assert habit.completions == ["2026-08-30"]

    # Idempotencia
    already_again = habit.mark_done(today)
    assert already_again
    assert habit.completions == ["2026-08-30"]


def test_habit_store_add_habit():
    today = date(2026, 8, 30)
    store = HabitStore()

    h = store.add_habit("  Estudiar Python ", today)
    assert h.name == "Estudiar Python"
    assert len(store.habits) == 1

    with pytest.raises(EmptyNameError):
        store.add_habit("   ", today)

    with pytest.raises(DuplicateHabitError):
        store.add_habit("estudiar python", today)


def test_habit_store_mark_done():
    today = date(2026, 8, 30)
    store = HabitStore()
    store.add_habit("Python", today)

    habit, already = store.mark_done("python", today)
    assert habit.name == "Python"
    assert not already

    with pytest.raises(HabitNotFoundError):
        store.mark_done("Nonexistent", today)


def test_habit_store_list_habits():
    today = date(2026, 8, 30)
    store = HabitStore()
    h1 = store.add_habit("Alfa", today)
    h2 = store.add_habit("Beta", today)

    h2.mark_done(today)

    summaries = store.list_habits(today)
    assert len(summaries) == 2
    assert summaries[0] == HabitSummary(name="Beta", streak=1)
    assert summaries[1] == HabitSummary(name="Alfa", streak=0)
