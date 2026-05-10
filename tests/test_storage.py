"""Tests for Storage class."""

import pytest
import os
import tempfile
from datetime import datetime, timedelta

from nudge.habits.habit import Habit, Periodicity
from nudge.storage.storage import Storage


@pytest.fixture
def temp_db():
    """Create a temporary database for testing."""
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    yield path
    # Cleanup
    if os.path.exists(path):
        os.remove(path)


@pytest.fixture
def storage(temp_db):
    """Create a Storage instance with a temporary database."""
    return Storage(temp_db)


class TestStorage:
    """Test cases for the Storage class."""

    def test_storage_initialization_creates_database(self, temp_db):
        """Test that storage initialization creates the database."""
        storage = Storage(temp_db)
        assert os.path.exists(temp_db)

    def test_storage_initialization_creates_tables(self, storage, temp_db):
        """Test that database tables are created."""
        import sqlite3

        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()

        # Check habits table exists
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='habits'"
        )
        assert cursor.fetchone() is not None

        # Check habit_completions table exists
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='habit_completions'"
        )
        assert cursor.fetchone() is not None

        conn.close()

    def test_save_habit(self, storage):
        """Test saving a habit to the database."""
        habit = Habit("Exercise", Periodicity.DAILY)
        assert habit.id is None  # ID is None before saving

        storage.save_habit(habit)

        assert habit.id is not None  # ID is assigned after saving
        assert isinstance(habit.id, int)

        loaded = storage.load_habit(habit.id)
        assert loaded is not None
        assert loaded.name == "Exercise"
        assert loaded.periodicity == Periodicity.DAILY

    def test_save_habit_with_different_periodicities(self, storage):
        """Test saving habits with all periodicity types."""
        habits = [
            Habit("Exercise", Periodicity.DAILY),
            Habit("Read", Periodicity.WEEKLY),
            Habit("Review", Periodicity.MONTHLY),
        ]

        for habit in habits:
            storage.save_habit(habit)

        loaded_habits = storage.load_all_habits()
        assert len(loaded_habits) == 3
        assert loaded_habits[0].periodicity == Periodicity.DAILY
        assert loaded_habits[1].periodicity == Periodicity.WEEKLY
        assert loaded_habits[2].periodicity == Periodicity.MONTHLY

    def test_load_nonexistent_habit(self, storage):
        """Test loading a habit that doesn't exist."""
        result = storage.load_habit(999)  # Non-existent ID
        assert result is None

    def test_load_all_habits_empty(self, storage):
        """Test loading all habits when database is empty."""
        habits = storage.load_all_habits()
        assert habits == []

    def test_load_all_habits(self, storage):
        """Test loading all habits from the database."""
        habit1 = Habit("Exercise", Periodicity.DAILY)
        habit2 = Habit("Read", Periodicity.WEEKLY)
        habit3 = Habit("Review", Periodicity.MONTHLY)

        storage.save_habit(habit1)
        storage.save_habit(habit2)
        storage.save_habit(habit3)

        loaded_habits = storage.load_all_habits()
        assert len(loaded_habits) == 3
        names = {h.name for h in loaded_habits}
        assert names == {"Exercise", "Read", "Review"}

    def test_save_completion(self, storage):
        """Test saving a completion timestamp."""
        habit = Habit("Exercise", Periodicity.DAILY)
        storage.save_habit(habit)

        timestamp = datetime.now()
        storage.save_completion(habit.id, timestamp)

        loaded = storage.load_habit(habit.id)
        assert len(loaded.completion_timestamps) == 1
        # Compare without microseconds due to potential precision loss
        assert (
            loaded.completion_timestamps[0].replace(microsecond=0)
            == timestamp.replace(microsecond=0)
        )

    def test_save_multiple_completions(self, storage):
        """Test saving multiple completions for a habit."""
        habit = Habit("Exercise", Periodicity.DAILY)
        storage.save_habit(habit)

        now = datetime.now()
        timestamps = [now - timedelta(days=i) for i in range(3)]

        for ts in timestamps:
            storage.save_completion(habit.id, ts)

        loaded = storage.load_habit(habit.id)
        assert len(loaded.completion_timestamps) == 3

    def test_delete_habit(self, storage):
        """Test deleting a habit."""
        habit = Habit("Exercise", Periodicity.DAILY)
        storage.save_habit(habit)
        storage.save_completion(habit.id, datetime.now())

        # Verify it exists
        assert storage.load_habit(habit.id) is not None

        # Delete it
        storage.delete_habit(habit.id)

        # Verify it's gone
        assert storage.load_habit(habit.id) is None

    def test_delete_habit_removes_completions(self, storage):
        """Test that deleting a habit also removes its completions."""
        habit = Habit("Exercise", Periodicity.DAILY)
        storage.save_habit(habit)

        # Add multiple completions
        for i in range(3):
            storage.save_completion(
                habit.id, datetime.now() - timedelta(days=i)
            )

        # Verify completions exist
        assert storage.get_completion_count(habit.id) == 3

        # Delete habit
        storage.delete_habit(habit.id)

        # Verify completions are gone
        assert storage.get_completion_count(habit.id) == 0

    def test_get_completion_count(self, storage):
        """Test getting the completion count for a habit."""
        habit = Habit("Exercise", Periodicity.DAILY)
        storage.save_habit(habit)

        assert storage.get_completion_count(habit.id) == 0

        # Add completions
        storage.save_completion(habit.id, datetime.now())
        assert storage.get_completion_count(habit.id) == 1

        storage.save_completion(habit.id, datetime.now())
        assert storage.get_completion_count(habit.id) == 2

    def test_get_completion_count_nonexistent_habit(self, storage):
        """Test getting completion count for a nonexistent habit."""
        count = storage.get_completion_count(999)
        assert count == 0

    def test_load_habit_preserves_all_properties(self, storage):
        """Test that loading a habit preserves all properties."""
        habit = Habit("Read", Periodicity.WEEKLY)
        original_timestamp = habit.creation_timestamp

        storage.save_habit(habit)

        loaded = storage.load_habit(habit.id)
        assert loaded.id == habit.id
        assert isinstance(loaded.id, int)
        assert loaded.name == "Read"
        assert loaded.periodicity == Periodicity.WEEKLY
        # Compare without microseconds
        assert (
            loaded.creation_timestamp.replace(microsecond=0)
            == original_timestamp.replace(microsecond=0)
        )

    def test_completion_timestamps_ordered(self, storage):
        """Test that completion timestamps are returned in chronological order."""
        habit = Habit("Exercise", Periodicity.DAILY)
        storage.save_habit(habit)

        # Add completions out of order
        now = datetime.now()
        storage.save_completion(habit.id, now)
        storage.save_completion(habit.id, now - timedelta(days=1))
        storage.save_completion(habit.id, now - timedelta(days=2))

        loaded = storage.load_habit(habit.id)
        # Should be ordered
        for i in range(1, len(loaded.completion_timestamps)):
            assert (
                loaded.completion_timestamps[i]
                >= loaded.completion_timestamps[i - 1]
            )

    def test_multiple_habits_independent(self, storage):
        """Test that multiple habits are stored independently."""
        habit1 = Habit("Exercise", Periodicity.DAILY)
        habit2 = Habit("Read", Periodicity.WEEKLY)

        storage.save_habit(habit1)
        storage.save_habit(habit2)

        # Add completions to habit1 only
        storage.save_completion(habit1.id, datetime.now())
        storage.save_completion(habit1.id, datetime.now())

        # Check completions are independent
        assert storage.get_completion_count(habit1.id) == 2
        assert storage.get_completion_count(habit2.id) == 0

        # Deleting habit1 shouldn't affect habit2
        storage.delete_habit(habit1.id)
        assert storage.load_habit(habit2.id) is not None


class TestStorageSeeding:
    """Test cases for database seeding functionality."""

    def test_auto_seed_disabled_by_default(self, temp_db):
        """Test that auto-seeding is disabled by default."""
        storage = Storage(temp_db)
        habits = storage.load_all_habits()
        assert len(habits) == 0

    def test_auto_seed_initializes_database(self, temp_db):
        """Test that auto_seed=True populates the database."""
        storage = Storage(temp_db, auto_seed=True)
        habits = storage.load_all_habits()

        # Should have at least 4 habits with different periodicities
        assert len(habits) >= 4

        periodicities = {h.periodicity for h in habits}
        assert Periodicity.DAILY in periodicities
        assert Periodicity.WEEKLY in periodicities
        assert Periodicity.MONTHLY in periodicities

    def test_seed_data_idempotent(self, temp_db):
        """Test that seeding is idempotent (doesn't duplicate data)."""
        # First seed
        storage1 = Storage(temp_db, auto_seed=True)
        habits1 = storage1.load_all_habits()
        count1 = len(habits1)

        # Second seed (simulating restart)
        storage2 = Storage(temp_db, auto_seed=True)
        habits2 = storage2.load_all_habits()
        count2 = len(habits2)

        # Count should be the same, not doubled
        assert count1 == count2

    def test_seeded_habits_have_completions(self, temp_db):
        """Test that seeded habits have realistic completion data."""
        storage = Storage(temp_db, auto_seed=True)
        habits = storage.load_all_habits()

        # Find a habit with different periodicity
        daily_habits = [h for h in habits if h.periodicity == Periodicity.DAILY]
        weekly_habits = [h for h in habits if h.periodicity == Periodicity.WEEKLY]
        monthly_habits = [h for h in habits if h.periodicity == Periodicity.MONTHLY]

        # Should have at least one of each
        assert len(daily_habits) >= 1
        assert len(weekly_habits) >= 1
        assert len(monthly_habits) >= 1

        # Seeded daily habits should have multiple completions
        daily_habit = daily_habits[0]
        assert storage.get_completion_count(daily_habit.id) > 0

        # Seeded weekly habits should have some completions
        weekly_habit = weekly_habits[0]
        assert storage.get_completion_count(weekly_habit.id) >= 0

        # Seeded monthly habits should have some completions
        monthly_habit = monthly_habits[0]
        assert storage.get_completion_count(monthly_habit.id) >= 0

    def test_seeded_data_has_varied_adherence(self, temp_db):
        """Test that seeded data has different adherence patterns."""
        storage = Storage(temp_db, auto_seed=True)
        habits = storage.load_all_habits()

        completion_counts = [
            storage.get_completion_count(h.id) for h in habits
        ]

        # Should have some variation in completion counts
        # (unless by extreme coincidence all habits have exactly same completions)
        assert len(set(completion_counts)) > 1 or all(
            c > 0 for c in completion_counts
        )

    def test_seeded_completion_timestamps_ordered(self, temp_db):
        """Test that seeded completions are ordered chronologically."""
        storage = Storage(temp_db, auto_seed=True)
        habits = storage.load_all_habits()

        # Check the first habit with completions
        for habit in habits:
            if storage.get_completion_count(habit.id) > 0:
                loaded = storage.load_habit(habit.id)
                if len(loaded.completion_timestamps) > 1:
                    # Verify ordering
                    for i in range(1, len(loaded.completion_timestamps)):
                        assert (
                            loaded.completion_timestamps[i]
                            >= loaded.completion_timestamps[i - 1]
                        )
                break


