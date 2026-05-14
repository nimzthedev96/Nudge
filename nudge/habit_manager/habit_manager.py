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

    def mark_habit_complete(self, name: str):
        """Record a completion of a habit and save it to the database."""
        from nudge.habits.habit import Habit, Periodicity

        habit = self.storage.load_habit_by_name(name)
        habit.mark_complete()
        self.storage.save_completion(habit.id, datetime.datetime.now())
    
    def delete_habit(self, name: str):
        """Delete a habit from the database.
        
        Args:
            name: The name of the habit to delete.
            
        Raises:
            ValueError: If habit with the given name does not exist.
        """
        habit = self.storage.load_habit_by_name(name)
        if not habit:
            raise ValueError(f"Habit '{name}' not found.")
        
        self.storage.delete_habit(habit.id)
    
    