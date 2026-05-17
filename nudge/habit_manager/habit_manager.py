"""HabitManager service class for managing habits."""

import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from nudge.storage.storage import Storage


class HabitManager:
    """Service class for managing habits"""

    def __init__(self, storage: "Storage") -> None:
        """
        Initialize the HabitManager.

        Args:
            storage: An instance of the Storage class for database operations.
        """
        self.storage = storage

    def create_habit(self, name: str, periodicity: str) -> None:
        """Create a new habit and save it to the database.

        Args:
            name: The name of the habit.
            periodicity: The periodicity of the habit (e.g., 'daily', 'weekly').

        Raises:
            ValueError: If a habit with the same name and periodicity already exists.
        """
        from nudge.habits.habit import Habit, Periodicity

        # Validate that a habit with the same name and periodicity doesn't exist
        if self.storage.habit_exists(name, periodicity):
            raise ValueError(
                f"A habit named '{name}' with periodicity '{periodicity}' already exists."
            )

        habit = Habit(name, Periodicity(periodicity))
        self.storage.save_habit(habit)

    def mark_habit_complete(self, name: str) -> None:
        """Record a completion of a habit and save it to the database."""

        habit = self.storage.load_habit_by_name(name)
        if not habit:
            raise ValueError(f"Habit '{name}' not found.")
        habit.mark_complete()
        if habit.id is not None:
            self.storage.save_completion(habit.id, datetime.datetime.now())

    def delete_habit(self, name: str) -> None:
        """Delete a habit from the database.

        Args:
            name: The name of the habit to delete.

        Raises:
            ValueError: If habit with the given name does not exist.
        """
        habit = self.storage.load_habit_by_name(name)
        if not habit:
            raise ValueError(f"Habit '{name}' not found.")
        if habit.id is not None:
            self.storage.delete_habit(habit.id)
