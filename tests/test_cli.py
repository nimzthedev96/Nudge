"""Tests for CLI module."""

import pytest
import tempfile
import os
from datetime import datetime, date

from nudge.cli.cli import is_completed_today, select_habit
from nudge.habits.habit import Habit, Periodicity
from nudge.storage.storage import Storage
from nudge.habit_manager.habit_manager import HabitManager


class TestCLI:
    """Test cases for CLI functions."""

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

    def test_is_completed_today_with_no_completions(self):
        """Test is_completed_today returns False when habit has no completions."""
        habit = Habit("Exercise", Periodicity.DAILY)
        assert is_completed_today(habit) is False

    def test_is_completed_today_with_today_completion(self):
        """Test is_completed_today returns True when habit completed today."""
        habit = Habit("Exercise", Periodicity.DAILY)
        habit.completion_timestamps.append(datetime.now())
        assert is_completed_today(habit) is True

    def test_is_completed_today_with_old_completion(self):
        """Test is_completed_today returns False when completion is from yesterday."""
        habit = Habit("Exercise", Periodicity.DAILY)
        # Add a timestamp from yesterday
        yesterday = datetime.now().replace(day=datetime.now().day - 1)
        habit.completion_timestamps.append(yesterday)
        assert is_completed_today(habit) is False

    def test_select_habit_no_habits(self, habit_manager, capsys):
        """Test select_habit returns None when no habits exist."""
        result = select_habit(habit_manager, "Select habit:")
        assert result is None
        captured = capsys.readouterr()
        assert "No habits found" in captured.out

    # TODO: Add tests for select_habit with mocked questionary choices
    # TODO: Add tests for create_habit function
    # TODO: Add tests for mark_complete function
    # TODO: Add tests for delete_habit function

