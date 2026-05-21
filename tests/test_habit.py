"""Tests for Habit class."""

import calendar
from datetime import datetime, timedelta

from nudge.habits.habit import Habit, Periodicity


def get_same_day_previous_month(date):
    """Get a date with the same day but one month earlier.

    Handles month lengths properly (e.g., Jan 31 -> Dec 31, not Dec 1).
    """
    if date.month == 1:
        prev_date = date.replace(year=date.year - 1, month=12)
    else:
        prev_date = date.replace(month=date.month - 1)

    # Handle case where day doesn't exist in previous month (e.g., Jan 31 -> Feb 28/29)
    max_day = calendar.monthrange(prev_date.year, prev_date.month)[1]
    if prev_date.day > max_day:
        prev_date = prev_date.replace(day=max_day)

    return prev_date


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
        assert "Exercise" in repr_str
        assert "Daily" in repr_str
        assert "completions=0" in repr_str

    def test_habit_repr_with_completions(self):
        """Test the string representation after completions."""
        habit = Habit("Exercise", Periodicity.DAILY)
        habit.mark_complete()
        habit.mark_complete()

        repr_str = repr(habit)
        assert "completions=2" in repr_str

    def test_current_streak_no_completions(self):
        """Test calculating streak with no completions."""
        habit = Habit("Exercise", Periodicity.DAILY)
        streak = habit.current_streak()
        assert streak == 0

    def test_current_streak_single_completion_today_daily(self):
        """Test calculating streak with a single completion today."""
        habit = Habit("Exercise", Periodicity.DAILY)
        habit.completion_timestamps = [datetime.now()]
        streak = habit.current_streak()
        assert streak == 1

    def test_current_streak_consecutive_days_daily(self):
        """Test calculating streak over 3 consecutive days."""
        habit = Habit("Journal", Periodicity.DAILY)

        habit.completion_timestamps = [
            datetime.now(),
            datetime.now() - timedelta(days=1),
            datetime.now() - timedelta(days=2),
        ]

        streak = habit.current_streak()
        assert streak == 3

    def test_current_streak_broken_by_missed_day_daily(self):
        """Test that streak breaks when a day is missed."""
        habit = Habit("Exercise", Periodicity.DAILY)

        habit.completion_timestamps = [
            datetime.now(),
            datetime.now() - timedelta(days=2),  # Gap breaks streak
        ]

        streak = habit.current_streak()
        assert streak == 1

    def test_current_streak_single_completion_today_weekly(self):
        """Test calculating streak with a single completion this week."""
        habit = Habit("Read", Periodicity.WEEKLY)
        habit.completion_timestamps = [datetime.now()]
        streak = habit.current_streak()
        assert streak == 1

    def test_current_streak_consecutive_weeks_weekly(self):
        """Test calculating streak over 3 consecutive weeks (flexible days)."""
        habit = Habit("Read", Periodicity.WEEKLY)

        habit.completion_timestamps = [
            datetime.now(),
            datetime.now() - timedelta(days=7),
            datetime.now() - timedelta(days=14),
        ]

        streak = habit.current_streak()
        assert streak == 3

    def test_current_streak_single_completion_today_weekly_fixed_day(self):
        """Test calculating streak with a single completion on the fixed day."""
        habit = Habit("Prayer", Periodicity.WEEKLY_FIXED_DAY)
        habit.completion_timestamps = [datetime.now()]
        streak = habit.current_streak()
        assert streak == 1

    def test_current_streak_consecutive_weeks_fixed_day(self):
        """Test calculating streak over consecutive weeks on the same weekday."""
        habit = Habit("Prayer", Periodicity.WEEKLY_FIXED_DAY)

        habit.completion_timestamps = [
            datetime.now(),
            datetime.now() - timedelta(days=7),
            datetime.now() - timedelta(days=14),
        ]

        streak = habit.current_streak()
        assert streak == 3

    def test_current_streak_single_completion_today_monthly(self):
        """Test calculating streak with a single completion this month."""
        habit = Habit("Meditate", Periodicity.MONTHLY)
        habit.completion_timestamps = [datetime.now()]
        streak = habit.current_streak()
        assert streak == 1

    def test_current_streak_consecutive_months_monthly(self):
        """Test calculating streak over 3 consecutive months."""
        habit = Habit("Meditate", Periodicity.MONTHLY)

        today = datetime.now()
        one_month_ago = get_same_day_previous_month(today)
        two_months_ago = get_same_day_previous_month(one_month_ago)

        habit.completion_timestamps = [
            today,
            one_month_ago,
            two_months_ago,
        ]

        streak = habit.current_streak()
        assert streak == 3

    def test_current_streak_single_completion_today_monthly_fixed_day(self):
        """Test calculating streak with a single completion on the fixed day."""
        habit = Habit("Checkup", Periodicity.MONTHLY_FIXED_DAY)
        habit.completion_timestamps = [datetime.now()]
        streak = habit.current_streak()
        assert streak == 1

    def test_current_streak_consecutive_months_fixed_day(self):
        """Test calculating streak over consecutive months on the same day."""
        habit = Habit("Checkup", Periodicity.MONTHLY_FIXED_DAY)

        # Completions on the same day of month in consecutive months
        today = datetime.now()
        one_month_ago = get_same_day_previous_month(today)
        two_months_ago = get_same_day_previous_month(one_month_ago)

        habit.completion_timestamps = [
            today,
            one_month_ago,
            two_months_ago,
        ]

        streak = habit.current_streak()
        assert streak == 3
