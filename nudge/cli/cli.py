"""Command-line interface for Nudge application."""

import sys
import time
from datetime import date
from typing import TYPE_CHECKING, Optional

import questionary
from questionary import Style
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

if TYPE_CHECKING:
    from nudge.habit_manager.habit_manager import HabitManager
    from nudge.habits.habit import Habit

from nudge.analytics.analytics import (
    get_all_tracked_habits,
    get_best_performing_habit,
    get_habits_by_periodicity,
    get_longest_streak,
    get_longest_streak_for_all,
)
from nudge.cli.motivational import (
    ENCOURAGEMENT_MESSAGES,
    get_completion_message,
    get_daily_quote,
)
from nudge.cli import graphs

console = Console()


def is_completed_today(habit: "Habit") -> bool:
    """Check if a habit has been completed today."""
    if not habit.completion_timestamps:
        return False

    today = date.today()
    latest_completion = habit.completion_timestamps[-1]
    return latest_completion.date() == today


def display_today_view(manager: "HabitManager") -> None:
    """Display today's habit view with streaks and progress."""
    try:
        habits = manager.storage.load_all_habits()

        if not habits:
            console.print("[yellow]No habits found.[/yellow]\n")
            return

        table = Table(
            title="Today's Habits", title_style="bold", show_header=True, header_style="bold cyan"
        )
        table.add_column("Habit", style="cyan")
        table.add_column("Periodicity", style="white")
        table.add_column("Current streak", style="white")
        table.add_column("Status", style="white")
        table.add_column("Last completed", style="white")

        for habit in habits:
            status_style = (
                "[green]✓ Done[/green]" if is_completed_today(habit) else "[yellow]Pending[/yellow]"
            )
            streak = habit.current_streak()
            streak_type = (
                "days"
                if habit.periodicity == "Daily"
                else "weeks" if habit.periodicity in ["Weekly", "Weekly (Fixed Day)"] else "months"
            )
            if streak == 1:
                streak_type = streak_type[:-1]  # Strip the s for singular form
            last_completed = (
                habit.completion_timestamps[-1].strftime("%Y-%m-%d")
                if habit.completion_timestamps
                else "Never"
            )
            table.add_row(
                habit.name,
                habit.periodicity.value,
                f"[bold cyan]{streak}[/bold cyan] {streak_type}",
                status_style,
                last_completed,
            )

        console.print(table)

    except Exception as e:
        console.print(f"[red]✗ Error loading today view: {e}[/red]\n")


def display_menu() -> Optional[str]:
    """Display the interactive main menu."""

    style = Style.from_dict(
        {
            "highlighted": "bg:#0084f8 #ffffff bold",  # Blue background with white text
            "pointer": "#0084f8 bold",  # Blue pointer
        }
    )

    choice = questionary.select(
        "Select an option:",
        choices=[
            "Create a new habit",
            "Mark habit as complete",
            "View analytics",
            "Delete a habit",
            "Exit",
        ],
        style=style,
        use_indicator=True,
        pointer="->",
        instruction="Use arrow keys to navigate and Enter to select",
    ).ask()
    return choice  # type: ignore


def main(manager: "HabitManager") -> None:
    """Main CLI entry point."""
    # Display welcome banner
    console.print(
        Panel(
            "[bold white]NUDGE[/bold white] - [italic]A Gentle Habit Tracker[/italic]",
            expand=True,
            title_align="center",
            border_style="cyan",
        )
    )

    # Display daily motivational quote
    quote = get_daily_quote()
    console.print(f"\n[italic white]{quote}[/italic white]\n")

    while True:
        # Display today's view before the menu
        display_today_view(manager)

        choice = display_menu()

        if choice == "Create a new habit":
            create_habit(manager)
        elif choice == "Mark habit as complete":
            mark_complete(manager)
        elif choice == "View analytics":
            view_analytics(manager)
        elif choice == "Delete a habit":
            delete_habit(manager)
        elif choice == "Exit":
            console.print("\n[bold yellow]Goodbye![/bold yellow]")
            sys.exit(0)


def select_habit(
    manager: "HabitManager", prompt_title: str = "Select a habit:", color: str = "blue"
) -> Optional[str]:
    """Display a menu to select a habit with a back option.

    Args:
        manager: The HabitManager instance.
        prompt_title: The title for the selection prompt.
        color: The color scheme for the menu ('blue' or 'red').

    Returns:
        The habit name if selected, or None if back is selected.
    """
    habits = manager.storage.load_all_habits()

    if not habits:
        console.print("[yellow]No habits found.[/yellow]")
        return None

    habit_names = [habit.name for habit in habits]
    choices = habit_names + ["« Back to menu"]

    # Define styles based on color
    if color == "red":
        style = Style.from_dict(
            {
                "highlighted": "bg:#ff0000 #ffffff bold",  # Red background with white text
                "pointer": "#ff0000 bold",  # Red pointer
            }
        )
    else:  # default blue
        style = Style.from_dict(
            {
                "highlighted": "bg:#0084f8 #ffffff bold",  # Blue background with white text
                "pointer": "#0084f8 bold",  # Blue pointer
            }
        )

    selected = questionary.select(
        prompt_title,
        choices=choices,
        style=style,
        use_indicator=True,
        pointer="->",
    ).ask()

    if selected == "« Back to menu":
        return None

    return selected  # type: ignore


def create_habit(manager: "HabitManager") -> None:
    """Create a new habit through interactive CLI prompts.

    Prompts the user for habit name and periodicity, then creates the habit
    in the database. Displays success or error messages to the user.

    Args:
        manager: The HabitManager instance for habit operations.
    """
    console.print("\n[bold green]--- Create Habit ---[/bold green]")

    name = questionary.text("Habit name:").ask()
    if not name:
        console.print("[red]✗ Habit name cannot be empty[/red]")
        return

    periodicity = questionary.select(
        "Periodicity:",
        choices=["Daily", "Weekly", "Monthly", "Weekly (Fixed Day)", "Monthly (Fixed Day)"],
    ).ask()

    try:
        manager.create_habit(name, periodicity)
        console.print(f"[green]✓ Habit '[bold]{name}[/bold]' created successfully![/green]")
        # Pause briefly to let the user see the message before going back to the main menu
        time.sleep(3)
    except Exception as e:
        console.print(f"[red]✗ Error creating habit: {e}[/red]")


def mark_complete(manager: "HabitManager") -> None:
    """Mark a selected habit as complete and display streak achievements.

    Allows user to select a habit from interactive menu, marks it complete,
    and displays motivational messages including streak milestones.

    Args:
        manager: The HabitManager instance for habit operations.
    """
    console.print("\n[bold blue]--- Mark Habit Complete ---[/bold blue]")

    name = select_habit(manager, "Select a habit to mark complete:", color="blue")
    if not name:
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
            streak = habit.current_streak()
            if streak in [1, 3, 7, 14, 30, 60, 100]:
                encouragement_msg = ENCOURAGEMENT_MESSAGES.get(streak, "")
                if encouragement_msg:
                    console.print(f"\n[bold magenta]{encouragement_msg}[/bold magenta]")
            # Pause briefly to let the user see the message before going back to the main menu
            time.sleep(3)

    except Exception as e:
        console.print(f"[red]✗ Error: {e}[/red]")


def view_analytics(manager: "HabitManager") -> None:
    """View habit analytics and statistics.

    Displays an analytics sub-menu with options for different views:
    - Summary Dashboard
    - Detailed Habit Analysis
    - View Graphs

    Args:
        manager: The HabitManager instance for retrieving habit data.
    """
    style = Style.from_dict(
        {
            "highlighted": "bg:#0084f8 #ffffff bold",  # Blue background with white text
            "pointer": "#0084f8 bold",  # Blue pointer
        }
    )

    while True:
        choice = questionary.select(
            "[bold cyan]Analytics Menu[/bold cyan]",
            choices=[
                "Summary Dashboard",
                "Detailed Habit Analysis",
                "View Graphs",
                "« Back to menu",
            ],
            style=style,
            use_indicator=True,
            pointer="->",
        ).ask()

        if choice == "« Back to menu":
            return
        elif choice == "Summary Dashboard":
            display_summary_dashboard(manager)
        elif choice == "Detailed Habit Analysis":
            view_detailed_habit_analysis(manager)
        elif choice == "View Graphs":
            view_graphs(manager)


def display_summary_dashboard(manager: "HabitManager") -> None:
    """Display an overview dashboard with global statistics and habit summary table.

    Args:
        manager: The HabitManager instance for retrieving habit data.
    """
    try:
        habits = manager.storage.load_all_habits()

        if not habits:
            console.print("[yellow]No habits found.[/yellow]\n")
            return

        tracked_habits = get_all_tracked_habits(habits)
        longest_streak_all = get_longest_streak_for_all(habits)
     
        # Create and display habits table
        table = Table(title="All Habits Summary", title_style="bold", show_header=True, header_style="bold cyan")
        table.add_column("Habit", style="cyan")
        table.add_column("Periodicity", style="white")
        table.add_column("Current Streak", style="white")
        table.add_column("Longest Streak", style="white")
        table.add_column("Total Completions", style="white")

        for habit in habits:
            current_streak = habit.current_streak()
            longest_streak = get_longest_streak(habit)
            total_completions = len(habit.completion_timestamps)

            table.add_row(
                habit.name,
                habit.periodicity.value,
                f"[bold cyan]{current_streak}[/bold cyan]",
                f"[bold cyan]{longest_streak}[/bold cyan]",
                str(total_completions),
            )

        console.print(table)
        console.print()  # Add spacing

        console.print(f"[cyan]Total Habits:[/cyan] [bold]{len(habits)}[/bold]")
        console.print(f"[cyan]Tracked Habits:[/cyan] [bold]{len(tracked_habits)}[/bold]")
       
        # Find and display best performing habit
        best_habit = get_best_performing_habit(habits)
        if best_habit:
            best_streak = get_longest_streak(best_habit)
            console.print(f"[bold white]🏆 Best Performing Habit:[/bold white] [white]{best_habit.name} with a longest streak of {best_streak}[/white]")

        # Display random motivational quote
        console.print()  # Add spacing
        quote = get_daily_quote()
        console.print(f"[italic cyan]{quote}[/italic cyan]")

    except Exception as e:
        console.print(f"[red]✗ Error loading summary dashboard: {e}[/red]\n")
    
    # Back to analytics menu
    console.input("\n[cyan]Press Enter to return to analytics menu...[/cyan]")


def view_detailed_habit_analysis(manager: "HabitManager") -> None:
    """Display detailed analytics for a selected habit.

    Allows user to select a habit and view detailed information including
    streaks, completion history, and creation date.

    Args:
        manager: The HabitManager instance for retrieving habit data.
    """
    habit_name = select_habit(manager, "Select a habit to analyze:", color="blue")
    if not habit_name:
        return

    try:
        habit = manager.storage.load_habit_by_name(habit_name)
        if not habit:
            console.print(f"[red]✗ Habit '{habit_name}' not found[/red]\n")
            return

        current_streak = habit.current_streak()
        longest_streak = get_longest_streak(habit)
        total_completions = len(habit.completion_timestamps)

        console.print(f"\n[bold white]Habit Analysis: {habit_name}[/bold white]")
        console.print(f"[cyan]Periodicity:[/cyan] [bold]{habit.periodicity.value}[/bold]")
        console.print(f"[cyan]Created:[/cyan] [bold]{habit.creation_timestamp.strftime('%Y-%m-%d')}[/bold]")
        console.print(f"[cyan]Current Streak:[/cyan] [bold]{current_streak}[/bold]")
        console.print(f"[cyan]Longest Streak:[/cyan] [bold]{longest_streak}[/bold]")
        console.print(f"[cyan]Total Completions:[/cyan] [bold]{total_completions}[/bold]")

        if habit.completion_timestamps:
            first_completion = min(habit.completion_timestamps).strftime("%Y-%m-%d")
            last_completion = max(habit.completion_timestamps).strftime("%Y-%m-%d")
            console.print(f"[cyan]First Completion:[/cyan] [bold]{first_completion}[/bold]")
            console.print(f"[cyan]Last Completion:[/cyan] [bold]{last_completion}[/bold]")

        console.print()  # Add spacing

    except Exception as e:
        console.print(f"[red]✗ Error loading habit analysis: {e}[/red]\n")
    
    # Back to analytics menu
    console.input("\n[cyan]Press Enter to return to analytics menu...[/cyan]")


def view_graphs(manager: "HabitManager") -> None:
    """Display graph visualization options for habit analytics.

    Allows user to select different graph types to visualize habit data
    including streak comparisons, completion totals, timelines, and
    periodicity distribution.

    Args:
        manager: The HabitManager instance for retrieving habit data.
    """
    style = Style.from_dict(
        {
            "highlighted": "bg:#0084f8 #ffffff bold",  # Blue background with white text
            "pointer": "#0084f8 bold",  # Blue pointer
        }
    )

    while True:
        choice = questionary.select(
            "[bold cyan]Graphs Menu[/bold cyan]",
            choices=[
                "Streak Comparison",
                "Total Completions",
                "Periodicity Distribution",
                "« Back to analytics",
            ],
            style=style,
            use_indicator=True,
            pointer="->",
        ).ask()

        if choice == "« Back to analytics":
            return
        elif choice == "Streak Comparison":
            graphs.render_streak_comparison(manager)
        elif choice == "Total Completions":
            graphs.render_total_completions(manager)
        elif choice == "Periodicity Distribution":
            graphs.render_periodicity_distribution(manager)


def delete_habit(manager: "HabitManager") -> None:
    """Delete a selected habit after user confirmation.

    Allows user to select a habit to delete and requires confirmation
    before permanently removing it from the database.

    Args:
        manager: The HabitManager instance for habit operations.
    """
    console.print("\n[bold red]--- Delete Habit ---[/bold red]")

    name = select_habit(manager, "Select a habit to delete:", color="red")
    if not name:
        return

    # Confirm deletion
    confirm = questionary.confirm(
        f"Are you sure you want to delete '[bold]{name}[/bold]'? This action cannot be undone.",
        auto_enter=False,
    ).ask()

    if not confirm:
        console.print("[yellow]✗ Deletion cancelled[/yellow]")
        return

    try:
        manager.delete_habit(name)
        console.print(f"[green]✓ Habit '[bold]{name}[/bold]' deleted successfully![/green]")
        time.sleep(2)
    except Exception as e:
        console.print(f"[red]✗ Error: {e}[/red]")


# Allow this script to be run directly for testing purposes
if __name__ == "__main__":
    from nudge.habit_manager.habit_manager import HabitManager
    from nudge.storage.storage import Storage

    storage = Storage("nudge_habits.db", auto_seed=False)
    manager = HabitManager(storage)
    main(manager)
