"""HabitManager service class for managing habits."""

import datetime


class HabitManager:
    """Service class for managing habits"""

    def __init__(self, storage):
        """
        Initialize the HabitManager.

        Args:
            storage: An instance of the Storage class for database operations.
        """
        self.storage = storage

    def create_habit(self, name: str, periodicity: str):
        """Create a new habit and save it to the database."""
        from nudge.habits.habit import Habit, Periodicity

        #TODO: Add validation for name and periodicity

        habit = Habit(name, Periodicity(periodicity))
        self.storage.save_habit(habit)

    def mark_habit_complete(self, name: str):
        """Record a completion of a habit and save it to the database."""
        from nudge.habits.habit import Habit, Periodicity

        habit = self.storage.load_habit_by_name(name)
        habit.mark_complete()
        self.storage.save_completion(habit.id, datetime.now())
        

