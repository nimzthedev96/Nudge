"""Terminal-based graph visualization for habit analytics."""

from datetime import datetime, timedelta
from typing import TYPE_CHECKING, List

import plotext as plt
from rich.console import Console

from nudge.analytics.analytics import (
    get_longest_streak,
    get_all_tracked_habits,
)

if TYPE_CHECKING:
    from nudge.habit_manager.habit_manager import HabitManager
    from nudge.habits.habit import Habit

console = Console()


def render_streak_comparison(manager: "HabitManager") -> None:
    """Display a bar chart comparing longest streaks across all habits.
    
    Args:
        manager: The HabitManager instance for retrieving habit data.
    """
    try:
        habits = manager.storage.load_all_habits()
        
        if not habits:
            console.print("[yellow]No habits found.[/yellow]")
            console.input("\n[cyan]Press Enter to return to graphs menu...[/cyan]")
            return
        
        habit_names = [habit.name for habit in habits]
        streaks = [get_longest_streak(habit) for habit in habits]
        
        plt.clear_figure()
        plt.simple_bar(habit_names, streaks)
        plt.title("Longest Streak Comparison")
        plt.show()
        
    except Exception as e:
        console.print(f"[red]✗ Error rendering streak comparison: {e}[/red]\n")
    
    console.input("\n[cyan]Press Enter to return to graphs menu...[/cyan]")


def render_total_completions(manager: "HabitManager") -> None:
    """Display a bar chart showing total completions for each habit.
    
    Args:
        manager: The HabitManager instance for retrieving habit data.
    """
    try:
        habits = manager.storage.load_all_habits()
        
        if not habits:
            console.print("[yellow]No habits found.[/yellow]")
            console.input("\n[cyan]Press Enter to return to graphs menu...[/cyan]")
            return
        
        habit_names = [habit.name for habit in habits]
        completions = [len(habit.completion_timestamps) for habit in habits]
        
        plt.clear_figure()
        plt.simple_bar(habit_names, completions)
        plt.title("Total Completions by Habit")
        plt.show()
        
    except Exception as e:
        console.print(f"[red]✗ Error rendering total completions: {e}[/red]\n")
    
    console.input("\n[cyan]Press Enter to return to graphs menu...[/cyan]")

def render_periodicity_distribution(manager: "HabitManager") -> None:
    """Display a bar chart showing habit distribution by periodicity.
    
    Args:
        manager: The HabitManager instance for retrieving habit data.
    """
    try:
        habits = manager.storage.load_all_habits()
        
        if not habits:
            console.print("[yellow]No habits found.[/yellow]")
            console.input("\n[cyan]Press Enter to return to graphs menu...[/cyan]")
            return
        
        # Count habits by periodicity
        periodicity_counts = {}
        for habit in habits:
            period = habit.periodicity.value
            periodicity_counts[period] = periodicity_counts.get(period, 0) + 1
        
        periods = list(periodicity_counts.keys())
        counts = list(periodicity_counts.values())
        
        plt.clear_figure()
        plt.simple_bar(periods, counts)
        plt.title("Habit Distribution by Periodicity")
        plt.show()
        
    except Exception as e:
        console.print(f"[red]✗ Error rendering periodicity distribution: {e}[/red]\n")
    
    console.input("\n[cyan]Press Enter to return to graphs menu...[/cyan]")
