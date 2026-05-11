"""Entry point for Nudge application."""

from nudge.storage.storage import Storage
from nudge.habit_manager.habit_manager import HabitManager
from nudge.cli import main as cli_main

if __name__ == "__main__":
    storage = Storage("nudge_habits.db", auto_seed=True)
    manager = HabitManager(storage)
    cli_main(manager)
