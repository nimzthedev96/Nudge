"""Storage service class for database operations."""

import sqlite3
from pathlib import Path
from typing import List, Optional, Tuple
from datetime import datetime

from nudge.habits.habit import Habit, Periodicity


class Storage:
    """Service class for managing storage of habits and database operations."""

    def __init__(self, db_path: str = "nudge_habits.db"):
        """
        Initialize the Storage service.

        Args:
            db_path: Path to the SQLite database file.
            auto_seed: If True, automatically seed the database with sample data if empty.
        """
        self.db_path = db_path
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        """Get a database connection."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        """Initialize the database schema."""
        conn = self._get_connection()
        cursor = conn.cursor()

        # Create habits table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS habits (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                periodicity TEXT NOT NULL,
                creation_timestamp DATETIME NOT NULL
            )
            """
        )

        # Create habit_completions table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS habit_completions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                habit_id INTEGER NOT NULL,
                completion_timestamp DATETIME NOT NULL,
                FOREIGN KEY (habit_id) REFERENCES habits(id)
            )
            """
        )

        conn.commit()
        conn.close()

    def save_habit(self, habit: Habit) -> None:
        """
        Save a habit to the database.

        Args:
            habit: The Habit object to save.
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO habits (name, periodicity, creation_timestamp)
            VALUES (?, ?, ?)
            """,
            (
                habit.name,
                habit.periodicity.value,
                habit.creation_timestamp.timestamp(),
            ),
        )

        # Get the auto-generated id and assign it to the habit
        habit.id = cursor.lastrowid

        conn.commit()
        conn.close()

    def load_habit(self, habit_id: int) -> Optional[Habit]:
        """
        Load a habit from the database.

        Args:
            habit_id: The ID of the habit to load.

        Returns:
            The Habit object or None if not found.
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM habits WHERE id = ?", (habit_id,))
        row = cursor.fetchone()

        if not row:
            conn.close()
            return None

        habit = Habit(row["name"], Periodicity(row["periodicity"]))
        habit.id = row["id"]
        habit.creation_timestamp = datetime.fromtimestamp(row["creation_timestamp"])

        # Load completion timestamps
        cursor.execute(
            "SELECT completion_timestamp FROM habit_completions WHERE habit_id = ? ORDER BY completion_timestamp",
            (habit_id,),
        )
        completions = cursor.fetchall()
        habit.completion_timestamps = [
            datetime.fromtimestamp(comp["completion_timestamp"]) for comp in completions
        ]

        conn.close()
        return habit

    def load_all_habits(self) -> List[Habit]:
        """
        Load all habits from the database.

        Returns:
            A list of all Habit objects.
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT id FROM habits ORDER BY creation_timestamp")
        rows = cursor.fetchall()
        conn.close()

        habits = []
        for row in rows:
            habit = self.load_habit(row["id"])
            if habit:
                habits.append(habit)

        return habits

    def save_completion(self, habit_id: int, completion_timestamp: datetime) -> None:
        """
        Save a completion timestamp for a habit.

        Args:
            habit_id: The ID of the habit.
            completion_timestamp: The timestamp of the completion.
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO habit_completions (habit_id, completion_timestamp) VALUES (?, ?)",
            (habit_id, int(completion_timestamp.timestamp())),
        )

        conn.commit()
        conn.close()

    def delete_habit(self, habit_id: int) -> None:
        """
        Delete a habit and its completions from the database.

        Args:
            habit_id: The ID of the habit to delete.
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        # Delete completions first
        cursor.execute("DELETE FROM habit_completions WHERE habit_id = ?", (habit_id,))
        # Delete the habit
        cursor.execute("DELETE FROM habits WHERE id = ?", (habit_id,))

        conn.commit()
        conn.close()

    def get_completion_count(self, habit_id: int) -> int:
        """
        Get the number of completions for a habit.

        Args:
            habit_id: The ID of the habit.

        Returns:
            The number of completions.
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT COUNT(*) as count FROM habit_completions WHERE habit_id = ?",
            (habit_id,),
        )
        result = cursor.fetchone()
        conn.close()

        return result["count"] if result else 0

    def _seed_if_empty(self) -> None:
        """Seed the database with initial habit data if empty."""
        from nudge.storage.seed_data import seed_initial_habits

        seed_initial_habits(self)

