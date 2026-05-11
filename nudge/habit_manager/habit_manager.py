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
        self.storage.save_completion(habit.id, datetime.datetime.now())
    
    def calculate_streak(self, habit):
        """Calculate the current streak for a habit."""
        if not habit.completion_timestamps:
            return 0

        # Sort timestamps in descending order
        timestamps = sorted(habit.completion_timestamps, reverse=True)
        streak = 0
        if (datetime.datetime.now() - timestamps[0]).days <= 1:
            streak = 1
        today = datetime.datetime.now().date()

        # Go through the timestamps and count consecutive days
        # TODO: Adjust logic for weekly and monthly habits
        for i in range(1, len(timestamps)):
            current_date = timestamps[i].date()
            previous_date = timestamps[i - 1].date()

            if (previous_date - current_date).days == 1:
                streak += 1
            elif (today - current_date).days > 1:
                break

        return streak

