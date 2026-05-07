"""Tests for Habit class."""

import pytest
from datetime import datetime, timedelta

from nudge.habits.habit import Habit, Periodicity


class TestHabit:
    """Test cases for the Habit class."""

    def test_habit_creation_with_daily_periodicity(self):
        """Test creating a habit with daily periodicity."""
        habit = Habit("Exercise", Periodicity.DAILY)
        assert habit.name == "Exercise"
        assert habit.periodicity == Periodicity.DAILY

    def test_habit_creation_with_weekly_periodicity(self):
        """Test creating a habit with weekly periodicity."""
        habit = Habit("Read", Periodicity.WEEKLY)
        assert habit.name == "Read"
        assert habit.periodicity == Periodicity.WEEKLY

    def test_habit_creation_with_monthly_periodicity(self):
        """Test creating a habit with monthly periodicity."""
        habit = Habit("Review goals", Periodicity.MONTHLY)
        assert habit.name == "Review goals"
        assert habit.periodicity == Periodicity.MONTHLY

    def test_habit_has_unique_id(self):
        """Test that each habit has a unique ID when saved."""
        # Note: IDs are assigned by the database, so new habits start with id=None
        habit1 = Habit("Exercise", Periodicity.DAILY)
        habit2 = Habit("Exercise", Periodicity.DAILY)

        # IDs should be None initially (assigned by database on save)
        assert habit1.id is None
        assert habit2.id is None
    def test_habit_creation_timestamp(self):
        """Test that creation timestamp is set correctly."""
        before = datetime.now()
        habit = Habit("Exercise", Periodicity.DAILY)
        after = datetime.now()
        
        assert before <= habit.creation_timestamp <= after

    def test_habit_completion_timestamps_initially_empty(self):
        """Test that completion_timestamps list is empty on creation."""
        habit = Habit("Exercise", Periodicity.DAILY)
        assert habit.completion_timestamps == []
        assert len(habit.completion_timestamps) == 0

    def test_mark_complete_adds_timestamp(self):
        """Test that mark_complete adds a timestamp."""
        habit = Habit("Exercise", Periodicity.DAILY)
        before = datetime.now()
        
        habit.mark_complete()
        
        after = datetime.now()
        assert len(habit.completion_timestamps) == 1
        assert before <= habit.completion_timestamps[0] <= after

    def test_mark_complete_multiple_times(self):
        """Test that mark_complete can be called multiple times."""
        habit = Habit("Exercise", Periodicity.DAILY)
        
        habit.mark_complete()
        habit.mark_complete()
        habit.mark_complete()
        
        assert len(habit.completion_timestamps) == 3
        # Timestamps should be in chronological order
        for i in range(1, len(habit.completion_timestamps)):
            assert habit.completion_timestamps[i] >= habit.completion_timestamps[i - 1]

    def test_habit_repr(self):
        """Test the string representation of a habit."""
        habit = Habit("Exercise", Periodicity.DAILY)
        repr_str = repr(habit)
        
        assert "Habit" in repr_str
        assert habit.id in repr_str
        assert "Exercise" in repr_str
        assert "daily" in repr_str
        assert "completions=0" in repr_str

    def test_habit_repr_with_completions(self):
        """Test the string representation after completions."""
        habit = Habit("Exercise", Periodicity.DAILY)
        habit.mark_complete()
        habit.mark_complete()
        
        repr_str = repr(habit)
        assert "completions=2" in repr_str
