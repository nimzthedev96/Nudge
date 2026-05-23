"""Tests for Analytics module."""

from datetime import datetime, timedelta

from nudge.analytics import analytics
from nudge.habits.habit import Habit, Periodicity


class TestAnalytics:
    """Test cases for analytics functions."""

    def test_get_habits_by_periodicity(self):
        """Test filtering habits by periodicity."""
        habit1 = Habit("Exercise", Periodicity.DAILY)
        habit2 = Habit("Read", Periodicity.WEEKLY)
        habit3 = Habit("Review goals", Periodicity.WEEKLY)
        habits = [habit1, habit2, habit3]
        # Test filtering for daily habits
        daily_habits = analytics.get_habits_by_periodicity(habits, Periodicity.DAILY)
        assert len(daily_habits) == 1
        assert daily_habits[0].name == "Exercise"
        assert daily_habits[0].periodicity == Periodicity.DAILY

        # Test filtering for weekly habits
        weekly_habits = analytics.get_habits_by_periodicity(habits, Periodicity.WEEKLY)
        assert len(weekly_habits) == 2
        assert weekly_habits[0].name == "Read"
        assert weekly_habits[0].periodicity == Periodicity.WEEKLY
        assert weekly_habits[1].name == "Review goals"
        assert weekly_habits[1].periodicity == Periodicity.WEEKLY

        # Test filtering for monthly habits
        monthly_habits = analytics.get_habits_by_periodicity(habits, Periodicity.MONTHLY)
        assert len(monthly_habits) == 0

    def test_get_all_tracked_habits(self):
        """Test retrieving all tracked habits."""
        habit1 = Habit("Exercise", Periodicity.DAILY)
        habit2 = Habit("Read", Periodicity.WEEKLY)
        habit3 = Habit("Review goals", Periodicity.MONTHLY)
        habit1.completion_timestamps.append("2024-01-01T10:00:00")
        habits = [habit1, habit2, habit3]
        tracked_habits = analytics.get_all_tracked_habits(habits)
        assert len(tracked_habits) == 1
        assert tracked_habits[0].name == "Exercise"
        assert tracked_habits[0].periodicity == Periodicity.DAILY

    def test_get_longest_streak_for_all(self):
        """Test calculating the longest streak across all habits."""
        habit1 = Habit("Exercise", Periodicity.DAILY)
        habit2 = Habit("Read", Periodicity.WEEKLY)

        # Add completions to habit1 (3-day streak)
        base_date = datetime(2024, 1, 1, 10, 0, 0)
        habit1.completion_timestamps = [
            base_date,
            base_date + timedelta(days=1),
            base_date + timedelta(days=2),
        ]

        # Add completions to habit2 (2-week streak)
        habit2.completion_timestamps = [
            base_date,
            base_date + timedelta(days=5),
        ]

        habits = [habit1, habit2]
        longest = analytics.get_longest_streak_for_all(habits)
        assert longest == 3  # habit1's streak is longer

    def test_get_longest_streak_empty(self):
        """Test get_longest_streak with no completions."""
        habit = Habit("Exercise", Periodicity.DAILY)
        streak = analytics.get_longest_streak(habit)
        assert streak == 0

    def test_get_longest_streak_single_completion(self):
        """Test get_longest_streak with a single completion."""
        habit = Habit("Exercise", Periodicity.DAILY)
        habit.completion_timestamps = [datetime(2024, 1, 1, 10, 0, 0)]
        streak = analytics.get_longest_streak(habit)
        assert streak == 1

    def test_get_longest_streak_daily_consecutive(self):
        """Test get_longest_streak for DAILY periodicity with consecutive days."""
        habit = Habit("Exercise", Periodicity.DAILY)
        base_date = datetime(2024, 1, 1, 10, 0, 0)
        # 5 consecutive days
        habit.completion_timestamps = [
            base_date,
            base_date + timedelta(days=1),
            base_date + timedelta(days=2),
            base_date + timedelta(days=3),
            base_date + timedelta(days=4),
        ]
        streak = analytics.get_longest_streak(habit)
        assert streak == 5

    def test_get_longest_streak_daily_with_breaks(self):
        """Test get_longest_streak for DAILY with multiple streaks and breaks."""
        habit = Habit("Exercise", Periodicity.DAILY)
        base_date = datetime(2024, 1, 1, 10, 0, 0)
        # Streak 1: 3 days
        # Break: 2 days
        # Streak 2: 4 days (longer)
        habit.completion_timestamps = [
            base_date,
            base_date + timedelta(days=1),
            base_date + timedelta(days=2),
            # Gap of 2 days
            base_date + timedelta(days=5),
            base_date + timedelta(days=6),
            base_date + timedelta(days=7),
            base_date + timedelta(days=8),
        ]
        streak = analytics.get_longest_streak(habit)
        assert streak == 4

    def test_get_longest_streak_daily_same_day_multiple_times(self):
        """Test get_longest_streak for DAILY with multiple completions on same day."""
        habit = Habit("Exercise", Periodicity.DAILY)
        base_date = datetime(2024, 1, 1, 10, 0, 0)
        # Multiple completions on same day count as continuous (0 days apart)
        # Each pair is <= 1 day apart, so they all form one streak
        habit.completion_timestamps = [
            base_date,
            base_date + timedelta(hours=2),
            base_date + timedelta(days=1),
            base_date + timedelta(days=1, hours=3),
            base_date + timedelta(days=2),
        ]
        streak = analytics.get_longest_streak(habit)
        assert streak == 5  # All form one continuous streak

    def test_get_longest_streak_weekly_consecutive(self):
        """Test get_longest_streak for WEEKLY periodicity with consecutive weeks."""
        habit = Habit("Read", Periodicity.WEEKLY)
        base_date = datetime(2024, 1, 1, 10, 0, 0)  # Monday
        # 3 consecutive weeks
        habit.completion_timestamps = [
            base_date,
            base_date + timedelta(days=5),  # 5 days later (same week or within 14 days)
            base_date + timedelta(days=12),  # 12 days later (next week)
        ]
        streak = analytics.get_longest_streak(habit)
        assert streak == 3

    def test_get_longest_streak_weekly_with_breaks(self):
        """Test get_longest_streak for WEEKLY with breaks."""
        habit = Habit("Read", Periodicity.WEEKLY)
        base_date = datetime(2024, 1, 1, 10, 0, 0)
        # Streak 1: 2 weeks
        # Break: >14 days
        # Streak 2: 2 weeks
        habit.completion_timestamps = [
            base_date,
            base_date + timedelta(days=10),
            # Gap of 20 days
            base_date + timedelta(days=30),
            base_date + timedelta(days=40),
        ]
        streak = analytics.get_longest_streak(habit)
        assert streak == 2

    def test_get_longest_streak_weekly_fixed_day(self):
        """Test get_longest_streak for WEEKLY_FIXED_DAY periodicity."""
        habit = Habit("Meditation", Periodicity.WEEKLY_FIXED_DAY)
        # Start on a Monday
        base_date = datetime(2024, 1, 1, 10, 0, 0)  # Monday
        # 3 consecutive Mondays (7 days apart each)
        habit.completion_timestamps = [
            base_date,
            base_date + timedelta(days=7),
            base_date + timedelta(days=14),
        ]
        streak = analytics.get_longest_streak(habit)
        assert streak == 3

    def test_get_longest_streak_weekly_fixed_day_wrong_day_breaks_streak(self):
        """Test that WEEKLY_FIXED_DAY breaks streak on different weekday."""
        habit = Habit("Meditation", Periodicity.WEEKLY_FIXED_DAY)
        base_date = datetime(2024, 1, 1, 10, 0, 0)  # Monday
        # Monday -> Tuesday (different day) -> Monday
        habit.completion_timestamps = [
            base_date,
            base_date + timedelta(days=1),  # Tuesday (different weekday)
            base_date + timedelta(days=7),  # Next Monday
        ]
        streak = analytics.get_longest_streak(habit)
        assert streak == 1  # Only the last Monday counts as a streak start

    def test_get_longest_streak_monthly_consecutive(self):
        """Test get_longest_streak for MONTHLY periodicity with consecutive months."""
        habit = Habit("Review", Periodicity.MONTHLY)
        # Jan 15, Feb 15, Mar 15 (consecutive months)
        habit.completion_timestamps = [
            datetime(2024, 1, 15, 10, 0, 0),
            datetime(2024, 2, 15, 10, 0, 0),
            datetime(2024, 3, 15, 10, 0, 0),
        ]
        streak = analytics.get_longest_streak(habit)
        assert streak == 3

    def test_get_longest_streak_monthly_with_breaks(self):
        """Test get_longest_streak for MONTHLY with breaks."""
        habit = Habit("Review", Periodicity.MONTHLY)
        # Jan 15, Feb 15 (consecutive)
        # Gap of 1 month
        # Apr 15, May 15 (consecutive)
        habit.completion_timestamps = [
            datetime(2024, 1, 15, 10, 0, 0),
            datetime(2024, 2, 15, 10, 0, 0),
            datetime(2024, 4, 15, 10, 0, 0),
            datetime(2024, 5, 15, 10, 0, 0),
        ]
        streak = analytics.get_longest_streak(habit)
        assert streak == 2

    def test_get_longest_streak_monthly_fixed_day(self):
        """Test get_longest_streak for MONTHLY_FIXED_DAY periodicity."""
        habit = Habit("Checkup", Periodicity.MONTHLY_FIXED_DAY)
        # 15th of consecutive months
        habit.completion_timestamps = [
            datetime(2024, 1, 15, 10, 0, 0),
            datetime(2024, 2, 15, 10, 0, 0),
            datetime(2024, 3, 15, 10, 0, 0),
            datetime(2024, 4, 15, 10, 0, 0),
        ]
        streak = analytics.get_longest_streak(habit)
        assert streak == 4

    def test_get_longest_streak_monthly_fixed_day_wrong_day_breaks_streak(self):
        """Test that MONTHLY_FIXED_DAY breaks on different day of month."""
        habit = Habit("Checkup", Periodicity.MONTHLY_FIXED_DAY)
        # 15th, 14th (different day), 15th
        habit.completion_timestamps = [
            datetime(2024, 1, 15, 10, 0, 0),
            datetime(2024, 2, 14, 10, 0, 0),  # Different day of month
            datetime(2024, 3, 15, 10, 0, 0),
        ]
        streak = analytics.get_longest_streak(habit)
        assert streak == 1  # Only one streak from the last 15th

    def test_get_best_performing_habit_empty_list(self):
        """Test get_best_performing_habit with empty habits list."""
        habits = []
        result = analytics.get_best_performing_habit(habits)
        assert result is None

    def test_get_best_performing_habit_single_habit(self):
        """Test get_best_performing_habit with a single habit."""
        habit = Habit("Exercise", Periodicity.DAILY)
        habit.completion_timestamps = [datetime(2024, 1, 1, 10, 0, 0)]
        habits = [habit]
        result = analytics.get_best_performing_habit(habits)
        assert result is habit
        assert result.name == "Exercise"

    def test_get_best_performing_habit_multiple_different_streaks(self):
        """Test get_best_performing_habit returns habit with longest streak."""
        habit1 = Habit("Exercise", Periodicity.DAILY)
        habit2 = Habit("Read", Periodicity.DAILY)
        habit3 = Habit("Meditate", Periodicity.DAILY)

        base_date = datetime(2024, 1, 1, 10, 0, 0)

        # habit1: 2-day streak
        habit1.completion_timestamps = [
            base_date,
            base_date + timedelta(days=1),
        ]

        # habit2: 5-day streak (longest)
        habit2.completion_timestamps = [
            base_date,
            base_date + timedelta(days=1),
            base_date + timedelta(days=2),
            base_date + timedelta(days=3),
            base_date + timedelta(days=4),
        ]

        # habit3: 3-day streak
        habit3.completion_timestamps = [
            base_date,
            base_date + timedelta(days=1),
            base_date + timedelta(days=2),
        ]

        habits = [habit1, habit2, habit3]
        result = analytics.get_best_performing_habit(habits)
        assert result is habit2
        assert result.name == "Read"

    def test_get_best_performing_habit_same_streak_tiebreaker_completions(self):
        """Test get_best_performing_habit uses completion count as tiebreaker."""
        habit1 = Habit("Exercise", Periodicity.DAILY)
        habit2 = Habit("Read", Periodicity.DAILY)

        base_date = datetime(2024, 1, 1, 10, 0, 0)

        # Both have same longest streak (3 days)
        # but habit2 has more total completions due to multiple same-day completions
        habit1.completion_timestamps = [
            base_date,
            base_date + timedelta(days=1),
            base_date + timedelta(days=2),
        ]

        habit2.completion_timestamps = [
            base_date,
            base_date + timedelta(hours=1),  # Same day, extra completion
            base_date + timedelta(days=1),
            base_date + timedelta(days=1, hours=2),  # Same day, extra completion
            base_date + timedelta(days=2),
        ]

        habits = [habit1, habit2]
        result = analytics.get_best_performing_habit(habits)
        assert result is habit2  # Should be selected due to more completions
        assert len(result.completion_timestamps) == 5

    def test_get_best_performing_habit_no_completions(self):
        """Test get_best_performing_habit when all habits have no completions."""
        habit1 = Habit("Exercise", Periodicity.DAILY)
        habit2 = Habit("Read", Periodicity.DAILY)
        habit3 = Habit("Meditate", Periodicity.DAILY)

        habits = [habit1, habit2, habit3]
        result = analytics.get_best_performing_habit(habits)
        # Should return one of the habits (max picks first when all equal)
        assert result is not None
        assert result in habits

    def test_get_longest_streak_for_all_empty_list(self):
        """Test get_longest_streak_for_all with empty habits list."""
        habits = []
        longest = analytics.get_longest_streak_for_all(habits)
        assert longest == 0

    def test_get_longest_streak_for_all_no_completions(self):
        """Test get_longest_streak_for_all when all habits are untracked."""
        habit1 = Habit("Exercise", Periodicity.DAILY)
        habit2 = Habit("Read", Periodicity.WEEKLY)
        habit3 = Habit("Meditate", Periodicity.MONTHLY)

        habits = [habit1, habit2, habit3]
        longest = analytics.get_longest_streak_for_all(habits)
        assert longest == 0

    def test_get_longest_streak_weekly_boundary_14_days(self):
        """Test get_longest_streak for WEEKLY at exactly 14-day boundary."""
        habit = Habit("Read", Periodicity.WEEKLY)
        base_date = datetime(2024, 1, 1, 10, 0, 0)
        # Exactly 14 days apart - should still be consecutive weeks
        habit.completion_timestamps = [
            base_date,
            base_date + timedelta(days=14),  # Exactly 14 days
        ]
        streak = analytics.get_longest_streak(habit)
        assert streak == 2

    def test_get_longest_streak_weekly_boundary_15_days(self):
        """Test get_longest_streak for WEEKLY beyond 14-day boundary."""
        habit = Habit("Read", Periodicity.WEEKLY)
        base_date = datetime(2024, 1, 1, 10, 0, 0)
        # 15 days apart - should break the streak
        habit.completion_timestamps = [
            base_date,
            base_date + timedelta(days=15),  # 15 days (breaks streak)
        ]
        streak = analytics.get_longest_streak(habit)
        assert streak == 1

    def test_get_longest_streak_monthly_year_break_resets_streak(self):
        """Test get_longest_streak for MONTHLY breaks on year boundary."""
        habit = Habit("Review", Periodicity.MONTHLY)
        # Dec (2023), Jan (2024) - different years break the streak
        habit.completion_timestamps = [
            datetime(2023, 12, 15, 10, 0, 0),
            datetime(2024, 1, 15, 10, 0, 0),
        ]
        streak = analytics.get_longest_streak(habit)
        assert streak == 1  # Breaks due to year change

    def test_get_longest_streak_monthly_fixed_day_end_of_month(self):
        """Test get_longest_streak for MONTHLY_FIXED_DAY with end-of-month dates."""
        habit = Habit("Checkup", Periodicity.MONTHLY_FIXED_DAY)
        # 31st of consecutive months (handling months with fewer days)
        # Jan 31, Feb 28 (different day), Mar 31
        # The Feb 28 breaks the streak
        habit.completion_timestamps = [
            datetime(2024, 1, 31, 10, 0, 0),
            datetime(2024, 2, 29, 10, 0, 0),  # Different day (Feb has only 29 in leap year)
            datetime(2024, 3, 31, 10, 0, 0),
        ]
        streak = analytics.get_longest_streak(habit)
        assert streak == 1  # Breaks at Feb 29 (different day)

    def test_get_longest_streak_longest_among_multiple_streaks(self):
        """Test that the function returns the longest streak among all streaks."""
        habit = Habit("Study", Periodicity.DAILY)
        base_date = datetime(2024, 1, 1, 10, 0, 0)
        # Streak 1: 2 days
        # Break
        # Streak 2: 3 days
        # Break
        # Streak 3: 5 days (longest)
        habit.completion_timestamps = [
            base_date,
            base_date + timedelta(days=1),
            # Gap
            base_date + timedelta(days=4),
            base_date + timedelta(days=5),
            base_date + timedelta(days=6),
            # Gap
            base_date + timedelta(days=10),
            base_date + timedelta(days=11),
            base_date + timedelta(days=12),
            base_date + timedelta(days=13),
            base_date + timedelta(days=14),
        ]
        streak = analytics.get_longest_streak(habit)
        assert streak == 5
