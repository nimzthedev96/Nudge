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
        """Calculate the current streak for a habit based on periodicity.
        
        For flexible periodicities (WEEKLY, MONTHLY): checks consecutive periods.
        For fixed-day periodicities (WEEKLY_FIXED_DAY, MONTHLY_FIXED_DAY): checks same day in consecutive periods.
        """
        if not habit.completion_timestamps:
            return 0

        timestamps = sorted(habit.completion_timestamps, reverse=True)
        today = datetime.datetime.now().date()
        streak = 0

        match habit.periodicity:
            case habit.periodicity.DAILY:
                # Streak for daily: consecutive days
                if (today - timestamps[0].date()).days <= 1:
                    streak = 1
                for i in range(1, len(timestamps)):
                    current_date = timestamps[i].date()
                    previous_date = timestamps[i - 1].date()
                    if (previous_date - current_date).days == 1:
                        streak += 1
                    else:
                        break

            case habit.periodicity.WEEKLY:
                # Streak for flexible weekly: completed in consecutive weeks
                # Only consider dates, not times
                days_since_completion = (today - timestamps[0].date()).days
                if days_since_completion <= 7:
                    streak = 1
                
                for i in range(1, len(timestamps)):
                    current_date = timestamps[i].date()
                    previous_date = timestamps[i - 1].date()
                    days_between = (previous_date - current_date).days
                    
                    # Same week (0-7 days apart means could be same week) or consecutive weeks
                    if 0 < days_between <= 14:
                        streak += 1
                    else:
                        break

            case habit.periodicity.WEEKLY_FIXED_DAY:
                # Streak for fixed-day weekly: same weekday in consecutive weeks
                today_weekday = today.weekday()
                recent_date = timestamps[0].date()
                recent_weekday = recent_date.weekday()
                
                if today_weekday == recent_weekday and (today - recent_date).days <= 7:
                    streak = 1
                
                for i in range(1, len(timestamps)):
                    current_ts = timestamps[i].date()
                    previous_ts = timestamps[i - 1].date()
                    
                    current_weekday = current_ts.weekday()
                    previous_weekday = previous_ts.weekday()
                    current_week = current_ts.isocalendar()[1]
                    previous_week = previous_ts.isocalendar()[1]
                    
                    # Same weekday and consecutive weeks
                    if current_weekday == previous_weekday and (previous_week - current_week) == 1:
                        streak += 1
                    else:
                        break

            case habit.periodicity.MONTHLY:
                # Streak for flexible monthly: completed in consecutive months
                if (today.year - timestamps[0].date().year) * 12 + (today.month - timestamps[0].date().month) <= 1:
                    streak = 1
                
                for i in range(1, len(timestamps)):
                    current_month = timestamps[i].month
                    current_year = timestamps[i].year
                    previous_month = timestamps[i - 1].month
                    previous_year = timestamps[i - 1].year
                    
                    # Check if in consecutive months
                    if current_year == previous_year and (previous_month - current_month) == 1:
                        streak += 1
                    else:
                        break

            case habit.periodicity.MONTHLY_FIXED_DAY:
                # Streak for fixed-day monthly: same day of month in consecutive months
                today_day = today.day
                recent_date = timestamps[0].date()
                recent_day = recent_date.day
                
                if today_day == recent_day and (today.year - recent_date.year) * 12 + (today.month - recent_date.month) <= 1:
                    streak = 1
                
                for i in range(1, len(timestamps)):
                    current_ts = timestamps[i].date()
                    previous_ts = timestamps[i - 1].date()
                    
                    current_day = current_ts.day
                    previous_day = previous_ts.day
                    current_month = current_ts.month
                    current_year = current_ts.year
                    previous_month = previous_ts.month
                    previous_year = previous_ts.year
                    
                    # Same day of month and consecutive months
                    if current_day == previous_day and current_year == previous_year and (previous_month - current_month) == 1:
                        streak += 1
                    else:
                        break

        return streak

