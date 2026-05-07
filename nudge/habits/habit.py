"""Habit class for representing individual habits."""

from datetime import datetime
from enum import StrEnum
from typing import List, Optional


class Periodicity(StrEnum):
    """Enum for habit periodicity. Valid values are 'daily', 'weekly', and 'monthly'."""

    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"


class Habit:
    """Represents a single habit to track."""

    def __init__(self, name: str, periodicity: Periodicity):
        """
        Initialize a new habit.

        Args:
            name: Task description for the habit.
            periodicity: Frequency of the habit (Periodicity enum value).
        """
        self.id: Optional[int] = None  # Set by database on save
        self.name = name
        self.periodicity = periodicity
        self.creation_timestamp = datetime.now()
        self.completion_timestamps: List[datetime] = []

    def mark_complete(self) -> None:
        """Record a completion timestamp for this habit."""
        self.completion_timestamps.append(datetime.now())

    def __repr__(self) -> str:
        """Return a string representation of the habit."""
        return (
            f"Habit(id={self.id!r}, name={self.name!r}, "
            f"periodicity={self.periodicity!r}, completions={len(self.completion_timestamps)})"
        )
