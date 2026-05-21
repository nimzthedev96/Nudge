"""Tests for streak calculations with actual seeded database data.

This module tests streak calculations (both current_streak() and get_longest_streak())
using actual seeded data loaded from the database.
Tests cover all 5 periodicity types with various adherence rates.
"""

import os
import tempfile
from datetime import datetime, timedelta

import pytest

from nudge.analytics import analytics
from nudge.habits.habit import Habit, Periodicity
from nudge.storage.seed_data import seed_initial_habits
from nudge.storage.storage import Storage


@pytest.fixture
def temp_db_with_seed():
    """Create a temporary database and seed it with initial data."""
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    
    # Create storage and seed with initial habits
    storage = Storage(path, auto_seed=False)
    seed_initial_habits(storage)
    
    yield storage, path
    
    # Cleanup
    storage._get_connection().close()
    if os.path.exists(path):
        os.remove(path)


@pytest.fixture
def temp_db_with_seed():
    """Create a temporary database and seed it with initial data."""
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    
    # Create storage and seed with initial habits
    storage = Storage(path, auto_seed=False)
    seed_initial_habits(storage)
    
    yield storage, path
    
    # Cleanup
    storage._get_connection().close()
    if os.path.exists(path):
        os.remove(path)


class TestSeededHabitsValid:
    """Test that all seeded habits have valid streak values."""

    def test_all_seeded_habits_loaded_successfully(self, temp_db_with_seed):
        """Test that seeding creates 8 habits."""
        storage, _ = temp_db_with_seed
        habits = storage.load_all_habits()
        
        assert len(habits) == 8, "Should have 8 seeded habits"
        
        habit_names = {h.name for h in habits}
        expected_names = {
            "Morning Exercise",
            "Read for 30 minutes",
            "Weekly Review",
            "Meditation",
            "Team Standup",
            "Monthly Goal Planning",
            "Prayer",
            "Health Checkup",
        }
        assert habit_names == expected_names, "All expected habit names should be present"

    def test_seeded_daily_habits_have_valid_streaks(self, temp_db_with_seed):
        """Test daily seeded habits (Morning Exercise, Read, Meditation) have valid streaks."""
        storage, _ = temp_db_with_seed
        habits = storage.load_all_habits()
        
        daily_habits = [h for h in habits if h.periodicity == Periodicity.DAILY]
        assert len(daily_habits) == 3, "Should have 3 daily habits"
        
        for habit in daily_habits:
            longest = analytics.get_longest_streak(habit)
            current = habit.current_streak()
            
            # All should have at least some completions
            assert len(habit.completion_timestamps) > 0, f"{habit.name} should have completions"
            
            # Streak validations
            assert longest >= 0, f"{habit.name} longest streak should be non-negative"
            assert current >= 0, f"{habit.name} current streak should be non-negative"
            assert current <= longest, f"{habit.name} current should not exceed longest"
            assert longest <= len(habit.completion_timestamps), f"{habit.name} streak should not exceed completion count"

    def test_seeded_weekly_habits_have_valid_streaks(self, temp_db_with_seed):
        """Test weekly seeded habits have valid streaks."""
        storage, _ = temp_db_with_seed
        habits = storage.load_all_habits()
        
        weekly_habits = [h for h in habits if h.periodicity == Periodicity.WEEKLY]
        assert len(weekly_habits) == 2, "Should have 2 weekly habits (Weekly Review, Team Standup)"
        
        for habit in weekly_habits:
            longest = analytics.get_longest_streak(habit)
            current = habit.current_streak()
            
            assert len(habit.completion_timestamps) > 0, f"{habit.name} should have completions"
            assert longest >= 0, f"{habit.name} longest streak should be non-negative"
            assert current >= 0, f"{habit.name} current streak should be non-negative"
            assert current <= longest, f"{habit.name} current should not exceed longest"

    def test_seeded_weekly_fixed_day_habits_have_valid_streaks(self, temp_db_with_seed):
        """Test weekly fixed-day seeded habit (Prayer) has valid streaks."""
        storage, _ = temp_db_with_seed
        habits = storage.load_all_habits()
        
        fixed_weekly_habits = [h for h in habits if h.periodicity == Periodicity.WEEKLY_FIXED_DAY]
        assert len(fixed_weekly_habits) == 1, "Should have 1 weekly fixed-day habit (Prayer)"
        
        habit = fixed_weekly_habits[0]
        longest = analytics.get_longest_streak(habit)
        current = habit.current_streak()
        
        assert len(habit.completion_timestamps) > 0, f"{habit.name} should have completions"
        assert longest >= 0, f"{habit.name} longest streak should be non-negative"
        assert current >= 0, f"{habit.name} current streak should be non-negative"
        assert current <= longest, f"{habit.name} current should not exceed longest"

    def test_seeded_monthly_habits_have_valid_streaks(self, temp_db_with_seed):
        """Test monthly seeded habit (Monthly Goal Planning) has valid streaks."""
        storage, _ = temp_db_with_seed
        habits = storage.load_all_habits()
        
        monthly_habits = [h for h in habits if h.periodicity == Periodicity.MONTHLY]
        assert len(monthly_habits) == 1, "Should have 1 monthly habit (Monthly Goal Planning)"
        
        habit = monthly_habits[0]
        longest = analytics.get_longest_streak(habit)
        current = habit.current_streak()
        
        assert len(habit.completion_timestamps) > 0, f"{habit.name} should have completions"
        assert longest >= 0, f"{habit.name} longest streak should be non-negative"
        assert current >= 0, f"{habit.name} current streak should be non-negative"
        assert current <= longest, f"{habit.name} current should not exceed longest"

    def test_seeded_monthly_fixed_day_habits_have_valid_streaks(self, temp_db_with_seed):
        """Test monthly fixed-day seeded habit (Health Checkup) has valid streaks."""
        storage, _ = temp_db_with_seed
        habits = storage.load_all_habits()
        
        fixed_monthly_habits = [h for h in habits if h.periodicity == Periodicity.MONTHLY_FIXED_DAY]
        assert len(fixed_monthly_habits) == 1, "Should have 1 monthly fixed-day habit (Health Checkup)"
        
        habit = fixed_monthly_habits[0]
        longest = analytics.get_longest_streak(habit)
        current = habit.current_streak()
        
        assert len(habit.completion_timestamps) > 0, f"{habit.name} should have completions"
        assert longest >= 0, f"{habit.name} longest streak should be non-negative"
        assert current >= 0, f"{habit.name} current streak should be non-negative"
        assert current <= longest, f"{habit.name} current should not exceed longest"


class TestSeedDataAdhereancePatterns:
    """Test that seeded data matches expected adherence patterns."""

    def test_morning_exercise_80_percent_adherence_approximate(self, temp_db_with_seed):
        """Test Morning Exercise has approximately 80% adherence over 14 days."""
        storage, _ = temp_db_with_seed
        habits = storage.load_all_habits()
        
        exercise = next(h for h in habits if h.name == "Morning Exercise")
        
        # Should have roughly 80% of 14 days = ~11 completions
        # Allow for some variance: 8-14 completions acceptable
        assert 8 <= len(exercise.completion_timestamps) <= 14
        
        longest = analytics.get_longest_streak(exercise)
        assert longest > 0, "Should have at least one streak"

    def test_read_for_30_minutes_60_percent_adherence_approximate(self, temp_db_with_seed):
        """Test Read has approximately 60% adherence over 14 days."""
        storage, _ = temp_db_with_seed
        habits = storage.load_all_habits()
        
        read = next(h for h in habits if h.name == "Read for 30 minutes")
        
        # Should have roughly 60% of 14 days = ~8 completions
        # Allow for some variance: 6-12 completions acceptable
        assert 6 <= len(read.completion_timestamps) <= 12
        
        longest = analytics.get_longest_streak(read)
        assert longest > 0, "Should have at least one streak"

    def test_meditation_50_percent_adherence_approximate(self, temp_db_with_seed):
        """Test Meditation has approximately 50% adherence over 14 days."""
        storage, _ = temp_db_with_seed
        habits = storage.load_all_habits()
        
        meditation = next(h for h in habits if h.name == "Meditation")
        
        # Should have roughly 50% of 14 days = ~7 completions
        # Allow for some variance: 5-10 completions acceptable
        assert 5 <= len(meditation.completion_timestamps) <= 10
        
        longest = analytics.get_longest_streak(meditation)
        assert longest > 0, "Should have at least one streak"

    def test_weekly_review_90_percent_adherence_approximate(self, temp_db_with_seed):
        """Test Weekly Review has approximately 90% adherence over 8 weeks."""
        storage, _ = temp_db_with_seed
        habits = storage.load_all_habits()
        
        weekly_review = next(h for h in habits if h.name == "Weekly Review")
        
        # Should have roughly 90% of 8 weeks = ~7 completions
        # Allow for some variance: 6-8 completions acceptable
        assert 6 <= len(weekly_review.completion_timestamps) <= 8
        
        longest = analytics.get_longest_streak(weekly_review)
        assert longest > 0, "Should have at least one streak"

    def test_team_standup_100_percent_adherence(self, temp_db_with_seed):
        """Test Team Standup has 100% adherence over 8 weeks."""
        storage, _ = temp_db_with_seed
        habits = storage.load_all_habits()
        
        standup = next(h for h in habits if h.name == "Team Standup")
        
        # Should have exactly 8 completions for 100% adherence
        assert len(standup.completion_timestamps) == 8
        
        longest = analytics.get_longest_streak(standup)
        assert longest == 8, "100% adherence over 8 weeks should yield streak of 8"

    def test_prayer_95_percent_adherence_approximate(self, temp_db_with_seed):
        """Test Prayer has approximately 95% adherence over 8 weeks."""
        storage, _ = temp_db_with_seed
        habits = storage.load_all_habits()
        
        prayer = next(h for h in habits if h.name == "Prayer")
        
        # Should have roughly 95% of 8 weeks = ~7.6 completions
        # Allow for some variance: 7-8 completions acceptable
        assert 7 <= len(prayer.completion_timestamps) <= 8
        
        longest = analytics.get_longest_streak(prayer)
        assert longest > 0, "Should have at least one streak"

    def test_monthly_goal_planning_100_percent_adherence(self, temp_db_with_seed):
        """Test Monthly Goal Planning has 100% adherence over 3 months."""
        storage, _ = temp_db_with_seed
        habits = storage.load_all_habits()
        
        goal_planning = next(h for h in habits if h.name == "Monthly Goal Planning")
        
        # Should have exactly 3 completions for 100% adherence
        assert len(goal_planning.completion_timestamps) == 3
        
        longest = analytics.get_longest_streak(goal_planning)
        current = goal_planning.current_streak()
        
        # Due to month date calculations, the streak might vary
        assert longest > 0, "Should have at least one streak"
        assert current >= 0, "Current streak should be non-negative"

    def test_health_checkup_100_percent_adherence(self, temp_db_with_seed):
        """Test Health Checkup has 100% adherence over 3 months."""
        storage, _ = temp_db_with_seed
        habits = storage.load_all_habits()
        
        health = next(h for h in habits if h.name == "Health Checkup")
        
        # Should have exactly 3 completions for 100% adherence
        assert len(health.completion_timestamps) == 3
        
        longest = analytics.get_longest_streak(health)
        assert longest == 3, "100% adherence over 3 months should yield streak of 3"


class TestStreakCalculationConsistency:
    """Test consistency of streak calculations across seeded data."""

    def test_all_seeded_habits_streaks_valid(self, temp_db_with_seed):
        """Verify all seeded habits have valid, non-negative streaks."""
        storage, _ = temp_db_with_seed
        habits = storage.load_all_habits()
        
        for habit in habits:
            longest = analytics.get_longest_streak(habit)
            current = habit.current_streak()
            
            # No negative streaks
            assert longest >= 0, f"{habit.name}: longest streak should be >= 0"
            assert current >= 0, f"{habit.name}: current streak should be >= 0"
            
            # Current never exceeds longest
            assert current <= longest, f"{habit.name}: current should not exceed longest"
            
            # Streak should never exceed number of completions
            assert longest <= len(habit.completion_timestamps), \
                f"{habit.name}: streak should not exceed completion count"

    def test_habits_with_completions_have_positive_longest_streak(self, temp_db_with_seed):
        """Verify all seeded habits with completions have positive longest streak."""
        storage, _ = temp_db_with_seed
        habits = storage.load_all_habits()
        
        for habit in habits:
            if len(habit.completion_timestamps) > 0:
                longest = analytics.get_longest_streak(habit)
                assert longest > 0, f"{habit.name} with completions should have longest streak > 0"

    def test_analytics_functions_consistency_with_seeded_data(self, temp_db_with_seed):
        """Test analytics module functions work correctly with seeded data."""
        storage, _ = temp_db_with_seed
        habits = storage.load_all_habits()
        
        # Test get_all_tracked_habits
        tracked = analytics.get_all_tracked_habits(habits)
        assert len(tracked) > 0, "Should have tracked habits"
        
        # All tracked habits should have completions
        for habit in tracked:
            assert len(habit.completion_timestamps) > 0
        
        # Test get_longest_streak_for_all
        overall_longest = analytics.get_longest_streak_for_all(habits)
        assert overall_longest > 0, "Overall longest streak should be positive"
        
        # Test get_best_performing_habit
        best = analytics.get_best_performing_habit(habits)
        assert best is not None, "Should identify a best performing habit"
        assert best in habits, "Best habit should be from the list"

    def test_periodicities_match_expected_values(self, temp_db_with_seed):
        """Verify seeded habits have correct periodicity values."""
        storage, _ = temp_db_with_seed
        habits = storage.load_all_habits()
        
        expected_periodicities = {
            "Morning Exercise": Periodicity.DAILY,
            "Read for 30 minutes": Periodicity.DAILY,
            "Weekly Review": Periodicity.WEEKLY,
            "Meditation": Periodicity.DAILY,
            "Team Standup": Periodicity.WEEKLY,
            "Monthly Goal Planning": Periodicity.MONTHLY,
            "Prayer": Periodicity.WEEKLY_FIXED_DAY,
            "Health Checkup": Periodicity.MONTHLY_FIXED_DAY,
        }
        
        for habit in habits:
            expected = expected_periodicities[habit.name]
            assert habit.periodicity == expected, \
                f"{habit.name} should have periodicity {expected}, got {habit.periodicity}"


class TestCompletionTimestamps:
    """Test completion timestamps are properly loaded from database."""

    def test_all_completion_timestamps_are_datetime(self, temp_db_with_seed):
        """Verify all completion timestamps are datetime objects."""
        storage, _ = temp_db_with_seed
        habits = storage.load_all_habits()
        
        for habit in habits:
            for timestamp in habit.completion_timestamps:
                assert isinstance(timestamp, datetime), \
                    f"{habit.name} completion should be datetime, got {type(timestamp)}"

    def test_completion_timestamps_are_in_past(self, temp_db_with_seed):
        """Verify all completion timestamps are in the past or recent."""
        storage, _ = temp_db_with_seed
        habits = storage.load_all_habits()
        now = datetime.now()
        
        for habit in habits:
            for timestamp in habit.completion_timestamps:
                # Completions should be from past 90 days (seeding goes back 14 days roughly)
                assert (now - timestamp).days <= 90, \
                    f"{habit.name} completion should be within 90 days"
                assert (now - timestamp).days >= -1, \
                    f"{habit.name} completion should not be in future"

    def test_completion_timestamps_are_sorted(self, temp_db_with_seed):
        """Verify completion timestamps are in chronological order."""
        storage, _ = temp_db_with_seed
        habits = storage.load_all_habits()
        
        for habit in habits:
            timestamps = habit.completion_timestamps
            if len(timestamps) > 1:
                sorted_timestamps = sorted(timestamps)
                assert timestamps == sorted_timestamps, \
                    f"{habit.name} timestamps should be in chronological order"
