"""Command-line interface for Nudge application."""

import sys
from datetime import datetime, date
import questionary
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text

from nudge.cli.motivational import (
    ENCOURAGEMENT_MESSAGES,
    get_daily_quote,
    get_completion_message,
)

console = Console()


def is_completed_today(habit):
    """Check if a habit has been completed today."""
    if not habit.completion_timestamps:
        return False
    
    today = date.today()
    latest_completion = habit.completion_timestamps[-1]
    return latest_completion.date() == today


def display_today_view(manager):
    """Display today's habit view with streaks and progress."""
    try:
        habits = manager.storage.load_all_habits()
        
        if not habits:
            console.print("[yellow]No habits found.[/yellow]\n")
            return
        
        table = Table(title="Today's Habits", show_header=True, header_style="bold cyan")
        table.add_column("Habit", style="green")
        table.add_column("Periodicity", style="yellow")
        table.add_column("Streak", style="magenta")
        table.add_column("Status", style="white")
        
        for habit in habits:
            status_style = "[green]✓ Done[/green]" if is_completed_today(habit) else "[yellow]⚪ Pending[/yellow]"
            streak = manager.calculate_streak(habit)
            table.add_row(
                habit.name,
                habit.periodicity.value,
                f"[bold cyan]{streak}[/bold cyan] days",
                status_style,
            )
        
        console.print(table)
        
        
    except Exception as e:
        console.print(f"[red]✗ Error loading today view: {e}[/red]\n")


def display_menu():
    """Display the interactive main menu."""
    choice = questionary.select(
        "Select an option:",
        choices=[
            "Create a new habit",
            "Mark habit as complete",
            "View all habits",
            "View habit statistics",
            "Delete a habit",
            "Exit",
        ],
    ).ask()
    return choice


def main(manager):
    """Main CLI entry point."""
    # Display welcome banner
    console.print(
        Panel(
            "[bold cyan]NUDGE - Habit Tracker[/bold cyan]",
            expand=False,
            border_style="cyan",
        )
    )
    
    # Display daily motivational quote
    quote = get_daily_quote()
    console.print(f"\n[italic cyan]{quote}[/italic cyan]\n")

    while True:
        # Display today's view before the menu
        display_today_view(manager)
        
        choice = display_menu()

        if choice == "Create a new habit":
            create_habit(manager)
        elif choice == "Mark habit as complete":
            mark_complete(manager)
        elif choice == "View all habits":
            view_all_habits(manager)
        elif choice == "View habit statistics":
            view_statistics(manager)
        elif choice == "Delete a habit":
            delete_habit(manager)
        elif choice == "Exit":
            console.print("\n[bold yellow]Goodbye![/bold yellow]")
            sys.exit(0)


def create_habit(manager):
    """Create a new habit."""
    console.print("\n[bold green]--- Create Habit ---[/bold green]")

    name = questionary.text("Habit name:").ask()
    if not name:
        console.print("[red]✗ Habit name cannot be empty[/red]")
        return

    periodicity = questionary.select(
        "Periodicity:",
        choices=["daily", "weekly", "monthly"],
    ).ask()

    try:
        manager.create_habit(name, periodicity)
        console.print(
            f"[green]✓ Habit '[bold]{name}[/bold]' created successfully![/green]"
        )
    except Exception as e:
        console.print(f"[red]✗ Error creating habit: {e}[/red]")


def mark_complete(manager):
    """Mark a habit as complete."""
    console.print("\n[bold blue]--- Mark Habit Complete ---[/bold blue]")

    name = questionary.text("Habit name:").ask()
    if not name:
        console.print("[red]✗ Habit name cannot be empty[/red]")
        return

    try:
        manager.mark_habit_complete(name)
        
        # Get the habit to show streak achievement
        habit = manager.storage.load_habit_by_name(name)
        if habit:
            # Show completion message
            completion_msg = get_completion_message()
            console.print(f"\n[green]{completion_msg}[/green]")
            console.print(f"[green]✓ Habit '[bold]{name}[/bold]' marked as complete![/green]")
         
            # Check for streak milestones and show a nice message if achieved
            streak = manager.calculate_streak(habit)
            if streak in [1, 3, 7, 14, 30, 60, 100]: 
                encouragement_msg = ENCOURAGEMENT_MESSAGES.get(streak, "")
                if encouragement_msg:
                    console.print(f"\n[bold magenta]{encouragement_msg}[/bold magenta]")
    except Exception as e:
        console.print(f"[red]✗ Error: {e}[/red]")


def view_all_habits(manager):
    """View all habits."""
    console.print("\n[bold magenta]--- All Habits ---[/bold magenta]")

    try:
        habits = manager.storage.load_all_habits()
        if not habits:
            console.print("[yellow]No habits found.[/yellow]")
            return

        table = Table(title="Your Habits", show_header=True, header_style="bold cyan")
        table.add_column("ID", style="dim")
        table.add_column("Name", style="green")
        table.add_column("Periodicity", style="yellow")
        table.add_column("Completions", style="magenta")

        for habit in habits:
            table.add_row(
                str(habit.id),
                habit.name,
                habit.periodicity.value,
                str(len(habit.completion_timestamps)),
            )

        console.print(table)
    except Exception as e:
        console.print(f"[red]✗ Error: {e}[/red]")


def view_statistics(manager):
    """View habit statistics."""
    console.print("\n[bold cyan]--- Habit Statistics ---[/bold cyan]")
    console.print("[yellow]TODO: Implement statistics view[/yellow]")


def delete_habit(manager):
    """Delete a habit."""
    console.print("\n[bold red]--- Delete Habit ---[/bold red]")
    console.print("[yellow]TODO: Implement delete functionality[/yellow]")


if __name__ == "__main__":
    from nudge.storage.storage import Storage
    from nudge.habit_manager.habit_manager import HabitManager

    storage = Storage("nudge_habits.db", auto_seed=False)
    manager = HabitManager(storage)
    main(manager)
