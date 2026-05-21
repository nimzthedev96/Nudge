"""Tests for HabitManager class."""

import os
import tempfile

import pytest

from nudge.habit_manager import HabitManager
from nudge.habits.habit import Periodicity
from nudge.storage.storage import Storage

# TODO: Add tests delete habit function


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
        habit_manager.create_habit("Exercise", "Daily")

        habits = storage.load_all_habits()
        assert len(habits) == 1
        assert habits[0].name == "Exercise"
        assert habits[0].periodicity == Periodicity.DAILY

    def test_create_weekly_habit(self, habit_manager, storage):
        """Test creating a weekly habit."""
        habit_manager.create_habit("Read", "Weekly")

        habits = storage.load_all_habits()
        assert len(habits) == 1
        assert habits[0].name == "Read"
        assert habits[0].periodicity == Periodicity.WEEKLY

    def test_create_weekly_fixed_day_habit(self, habit_manager, storage):
        """Test creating a weekly fixed day habit."""
        habit_manager.create_habit("Prayer", "Weekly (Fixed Day)")

        habits = storage.load_all_habits()
        assert len(habits) == 1
        assert habits[0].name == "Prayer"
        assert habits[0].periodicity == Periodicity.WEEKLY_FIXED_DAY

    def test_create_monthly_fixed_day_habit(self, habit_manager, storage):
        """Test creating a monthly fixed day habit."""
        habit_manager.create_habit("Checkup", "Monthly (Fixed Day)")

        habits = storage.load_all_habits()
        assert len(habits) == 1
        assert habits[0].name == "Checkup"
        assert habits[0].periodicity == Periodicity.MONTHLY_FIXED_DAY

    def test_create_multiple_habits(self, habit_manager, storage):
        """Test creating multiple habits."""
        habit_manager.create_habit("Exercise", "Daily")
        habit_manager.create_habit("Read", "Weekly")
        habit_manager.create_habit("Journal", "Daily")

        habits = storage.load_all_habits()
        assert len(habits) == 3
        habit_names = {h.name for h in habits}
        assert habit_names == {"Exercise", "Read", "Journal"}

    def test_mark_habit_complete(self, habit_manager, storage):
        """Test marking a habit as complete."""
        habit_manager.create_habit("Exercise", "Daily")

        # Mark the habit as complete
        habit_manager.mark_habit_complete("Exercise")

        # Verify it was marked
        habit = storage.load_habit_by_name("Exercise")
        assert len(habit.completion_timestamps) == 1

    def test_mark_habit_complete_multiple_times(self, habit_manager, storage):
        """Test marking a habit as complete multiple times."""
        habit_manager.create_habit("Exercise", "Daily")

        # Mark the habit as complete multiple times
        habit_manager.mark_habit_complete("Exercise")
        habit_manager.mark_habit_complete("Exercise")
        habit_manager.mark_habit_complete("Exercise")

        # Verify all completions were recorded
        habit = storage.load_habit_by_name("Exercise")
        assert len(habit.completion_timestamps) == 3

    def test_create_duplicate_habit_raises_error(self, habit_manager):
        """Test that creating a duplicate habit (same name and periodicity) raises ValueError."""
        # Create the first habit
        habit_manager.create_habit("Exercise", "Daily")

        # Attempt to create a duplicate habit
        with pytest.raises(ValueError, match="already exists"):
            habit_manager.create_habit("Exercise", "Daily")

    def test_create_same_name_different_periodicity_allowed(self, habit_manager, storage):
        """Test that creating a habit with same name but different periodicity is allowed."""
        # Create a daily habit
        habit_manager.create_habit("Exercise", "Daily")

        # Create a weekly habit with the same name (should succeed)
        habit_manager.create_habit("Exercise", "Weekly")

        # Verify both habits exist
        habits = storage.load_all_habits()
        assert len(habits) == 2
        assert all(h.name == "Exercise" for h in habits)
