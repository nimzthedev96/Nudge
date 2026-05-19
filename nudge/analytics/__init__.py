"""Analytics module using functional programming."""

from .analytics import (
    get_all_tracked_habits,
    get_habits_by_periodicity,
    get_longest_streak,
    get_longest_streak_for_all,
)

__all__ = [
    "get_habits_by_periodicity",
    "get_all_tracked_habits",
    "get_longest_streak_for_all",
    "get_longest_streak",
]
