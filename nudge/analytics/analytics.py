"""Functional analytics utilities for habit analysis."""

from typing import TYPE_CHECKING, List

if TYPE_CHECKING:
    from nudge.habits.habit import Habit


def get_habits_by_periodicity(habits: List["Habit"], periodicity: str) -> List["Habit"]:
    """Return a list of habits that match the given periodicity."""
    return [habit for habit in habits if habit.periodicity == periodicity]


def get_all_tracked_habits(habits: List["Habit"]) -> List["Habit"]:
    """
    Return a list of all currently tracked habits. A tracked habit is defined as one that has at least one completion.

    Args:
        habits: A list of Habit objects to filter.

    Returns:
        A list of Habit objects that have at least one completion.
    """
    return [habit for habit in habits if len(habit.completion_timestamps) > 0]


def get_longest_streak_for_all(habits: List["Habit"]) -> int:
    """Return the longest run streak of all defined habits."""
    longest_streak = 0
    for habit in habits:
        streak = get_longest_streak(habit)
        if streak > longest_streak:
            longest_streak = max(longest_streak, streak)
    return longest_streak


def get_longest_streak(habit: "Habit") -> int:
    """Calculate the longest run streak for a given habit based on periodicity.

    Iterates through all completion timestamps, detecting streaks and breaks,
    and returns the longest streak found.

    Args:
        habit: A Habit object with completion_timestamps and periodicity.

    Returns:
        The longest streak count for the habit.
    """
    if not habit.completion_timestamps:
        return 0

    timestamps = sorted(habit.completion_timestamps)
    longest_streak = 1
    current_streak = 1

    match habit.periodicity:
        case habit.periodicity.DAILY:
            # Streak for daily: consecutive days (<=1 day apart)
            for i in range(1, len(timestamps)):
                if (timestamps[i] - timestamps[i - 1]).days <= 1:
                    current_streak += 1
                else:
                    longest_streak = max(longest_streak, current_streak)
                    current_streak = 1

        case habit.periodicity.WEEKLY:
            # Streak for flexible weekly: completed within 14 days (consecutive weeks)
            for i in range(1, len(timestamps)):
                current_date = timestamps[i].date()
                previous_date = timestamps[i - 1].date()
                days_between = (current_date - previous_date).days

                # 0 < days_between <= 14: same week or consecutive weeks
                if 0 < days_between <= 14:
                    current_streak += 1
                else:
                    longest_streak = max(longest_streak, current_streak)
                    current_streak = 1

        case habit.periodicity.WEEKLY_FIXED_DAY:
            # Streak for fixed-day weekly: same weekday in consecutive weeks
            for i in range(1, len(timestamps)):
                current_ts = timestamps[i].date()
                previous_ts = timestamps[i - 1].date()

                current_weekday = current_ts.weekday()
                previous_weekday = previous_ts.weekday()
                current_week = current_ts.isocalendar()[1]
                previous_week = previous_ts.isocalendar()[1]

                # Same weekday and consecutive weeks
                if current_weekday == previous_weekday and (current_week - previous_week) == 1:
                    current_streak += 1
                else:
                    longest_streak = max(longest_streak, current_streak)
                    current_streak = 1

        case habit.periodicity.MONTHLY:
            # Streak for flexible monthly: completed in consecutive months
            for i in range(1, len(timestamps)):
                current_month = timestamps[i].month
                current_year = timestamps[i].year
                previous_month = timestamps[i - 1].month
                previous_year = timestamps[i - 1].year

                # Check if in consecutive months
                if current_year == previous_year and (current_month - previous_month) == 1:
                    current_streak += 1
                else:
                    longest_streak = max(longest_streak, current_streak)
                    current_streak = 1

        case habit.periodicity.MONTHLY_FIXED_DAY:
            # Streak for fixed-day monthly: same day of month in consecutive months
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
                if (
                    current_day == previous_day
                    and current_year == previous_year
                    and (current_month - previous_month) == 1
                ):
                    current_streak += 1
                else:
                    longest_streak = max(longest_streak, current_streak)
                    current_streak = 1

    longest_streak = max(longest_streak, current_streak)  # Check at the end
    return longest_streak
