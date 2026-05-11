"""Tests for HabitManager class."""

import pytest
import tempfile
import os
import datetime

from nudge.habit_manager import HabitManager
from nudge.habits.habit import Habit, Periodicity
from nudge.storage.storage import Storage


class TestHabitManager:
    """Test cases for the HabitManager class."""

    # Fixtures for setting up test environment
    @pytest.fixture
    def temp_db(self):
        """Create a temporary database for testing."""
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
        temp_file.close()
        db_path = temp_file.name
        yield db_path
        # Cleanup
        if os.path.exists(db_path):
            os.remove(db_path)

    @pytest.fixture
    def storage(self, temp_db):
        """Create a Storage instance with a temporary database."""
        return Storage(db_path=temp_db)

    @pytest.fixture
    def habit_manager(self, storage):
        """Create a HabitManager instance with a test storage."""
        return HabitManager(storage)

    # Test cases for HabitManager methods
    def test_create_daily_habit(self, habit_manager, storage):
        """Test creating a daily habit."""
        habit_manager.create_habit("Exercise", "daily")
        
        habits = storage.load_all_habits()
        assert len(habits) == 1
        assert habits[0].name == "Exercise"
        assert habits[0].periodicity == Periodicity.DAILY

    def test_create_weekly_habit(self, habit_manager, storage):
        """Test creating a weekly habit."""
        habit_manager.create_habit("Read", "weekly")
        
        habits = storage.load_all_habits()
        assert len(habits) == 1
        assert habits[0].name == "Read"
        assert habits[0].periodicity == Periodicity.WEEKLY

    def test_create_monthly_habit(self, habit_manager, storage):
        """Test creating a monthly habit."""
        habit_manager.create_habit("Meditate", "monthly")
        
        habits = storage.load_all_habits()
        assert len(habits) == 1
        assert habits[0].name == "Meditate"
        assert habits[0].periodicity == Periodicity.MONTHLY

    def test_create_multiple_habits(self, habit_manager, storage):
        """Test creating multiple habits."""
        habit_manager.create_habit("Exercise", "daily")
        habit_manager.create_habit("Read", "weekly")
        habit_manager.create_habit("Journal", "daily")
        
        habits = storage.load_all_habits()
        assert len(habits) == 3
        habit_names = {h.name for h in habits}
        assert habit_names == {"Exercise", "Read", "Journal"}

    def test_mark_habit_complete(self, habit_manager, storage):
        """Test marking a habit as complete."""
        habit_manager.create_habit("Exercise", "daily")
        
        # Mark the habit as complete
        habit_manager.mark_habit_complete("Exercise")
        
        # Verify it was marked
        habit = storage.load_habit_by_name("Exercise")
        assert len(habit.completion_timestamps) == 1

    def test_mark_habit_complete_multiple_times(self, habit_manager, storage):
        """Test marking a habit as complete multiple times."""
        habit_manager.create_habit("Exercise", "daily")
        
        # Mark the habit as complete multiple times
        habit_manager.mark_habit_complete("Exercise")
        habit_manager.mark_habit_complete("Exercise")
        habit_manager.mark_habit_complete("Exercise")
        
        # Verify all completions were recorded
        habit = storage.load_habit_by_name("Exercise")
        assert len(habit.completion_timestamps) == 3

    def test_calculate_streak_no_completions(self, habit_manager):
        """Test calculating streak with no completions."""
        habit = Habit("Exercise", Periodicity.DAILY)
        streak = habit_manager.calculate_streak(habit)
        assert streak == 0

    def test_calculate_streak_single_completion_today(self, habit_manager):
        """Test calculating streak with a single completion today."""
        habit = Habit("Exercise", Periodicity.DAILY)
        habit.mark_complete()
        
        streak = habit_manager.calculate_streak(habit)
        assert streak == 1

    def test_calculate_streak_consecutive_days(self, habit_manager):
        """Test calculating streak over consecutive days."""
        habit = Habit("Exercise", Periodicity.DAILY)
        
        # Simulate completions over 3 consecutive days
        today = datetime.datetime.now()
        habit.completion_timestamps = [
            today,
            today - datetime.timedelta(days=1),
            today - datetime.timedelta(days=2),
        ]
        
        streak = habit_manager.calculate_streak(habit)
        assert streak == 3

    def test_calculate_streak_broken_by_missed_day(self, habit_manager):
        """Test that streak is broken when a day is missed."""
        habit = Habit("Exercise", Periodicity.DAILY)
        
        # Simulate completions with a gap
        today = datetime.datetime.now()
        habit.completion_timestamps = [
            today,
            today - datetime.timedelta(days=2),  # Gap here
            today - datetime.timedelta(days=3),
        ]
        
        streak = habit_manager.calculate_streak(habit)
        assert streak == 1  # Only today's completion counts

    def test_calculate_streak_with_old_completions(self, habit_manager):
        """Test that old completions don't affect current streak."""
        habit = Habit("Exercise", Periodicity.DAILY)
        
        # Simulate old completions and a recent one
        today = datetime.datetime.now()
        habit.completion_timestamps = [
            today,
            today - datetime.timedelta(days=10),  # Very old
            today - datetime.timedelta(days=20),  # Even older
        ]
        
        streak = habit_manager.calculate_streak(habit)
        assert streak == 1  # Only today counts; older ones are too far back

    def test_calculate_streak_yesterday_completion(self, habit_manager):
        """Test streak when last completion was yesterday."""
        habit = Habit("Exercise", Periodicity.DAILY)
        
        today = datetime.datetime.now()
        yesterday = today - datetime.timedelta(days=1)
        
        habit.completion_timestamps = [yesterday]
        
        streak = habit_manager.calculate_streak(habit)
        # Should have streak of 1 since completion was yesterday (within 1 day)
        assert streak == 1

    def test_mark_habit_complete_nonexistent_habit(self, habit_manager):
        """Test marking a nonexistent habit as complete raises an error."""
        with pytest.raises(Exception):
            habit_manager.mark_habit_complete("NonexistentHabit")

    def test_create_habit_saves_to_storage(self, habit_manager, storage):
        """Test that create_habit properly saves to storage."""
        habit_manager.create_habit("Coding", "daily")
        
        # Retrieve and verify
        habit = storage.load_habit_by_name("Coding")
        assert habit is not None
        assert habit.name == "Coding"
        assert habit.periodicity == Periodicity.DAILY
        assert habit.id is not None

    def test_calculate_streak_empty_list(self, habit_manager):
        """Test calculate_streak with explicitly empty completion list."""
        habit = Habit("Exercise", Periodicity.DAILY)
        habit.completion_timestamps = []
        
        streak = habit_manager.calculate_streak(habit)
        assert streak == 0
