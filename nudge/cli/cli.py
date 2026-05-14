"""Command-line interface for Nudge application."""

import sys
from datetime import datetime, date
import time
import questionary
from questionary import Style
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
        
        table = Table(title="Today's Habits", title_style="bold", show_header=True, header_style="bold cyan")
        table.add_column("Habit", style="cyan")
        table.add_column("Periodicity", style="white")
        table.add_column("Current streak", style="white")
        table.add_column("Status", style="white")
        table.add_column("Last completed", style="white")
        
        for habit in habits:
            status_style = "[green]✓ Done[/green]" if is_completed_today(habit) else "[yellow]Pending[/yellow]"
            streak = habit.current_streak()
            streak_type = "days" if habit.periodicity == "daily" else "weeks" if habit.periodicity in ["weekly", "weekly_fixed_day"] else "months"
            if streak == 1:
                streak_type = streak_type[:-1]  # Strip the s for singular form
            last_completed = habit.completion_timestamps[-1].strftime("%Y-%m-%d") if habit.completion_timestamps else "Never"
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


def display_menu():
    """Display the interactive main menu."""

    style = Style.from_dict({
        'highlighted': 'bg:#0084f8 #ffffff bold',  # Blue background with white text
        'pointer': '#0084f8 bold',  # Blue pointer
    })

    choice = questionary.select(
        "Select an option:",
        choices=[
            "Create a new habit",
            "Mark habit as complete",
            "View habit statistics",
            "Delete a habit",
            "Exit",
        ],
        style=style,
        use_indicator=True,
        pointer="->",
        instruction="Use arrow keys to navigate and Enter to select"
    ).ask()
    return choice


def main(manager):
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
        elif choice == "View habit analytics":
            view_analytics(manager)
        elif choice == "Delete a habit":
            delete_habit(manager)
        elif choice == "Exit":
            console.print("\n[bold yellow]Goodbye![/bold yellow]")
            sys.exit(0)


def select_habit(manager, prompt_title: str = "Select a habit:", color: str = "blue"):
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
        style = Style.from_dict({
            'highlighted': 'bg:#ff0000 #ffffff bold',  # Red background with white text
            'pointer': '#ff0000 bold',  # Red pointer
        })
    else:  # default blue
        style = Style.from_dict({
            'highlighted': 'bg:#0084f8 #ffffff bold',  # Blue background with white text
            'pointer': '#0084f8 bold',  # Blue pointer
        })
    
    selected = questionary.select(
        prompt_title,
        choices=choices,
        style=style,
        use_indicator=True,
        pointer="->",
    ).ask()
    
    if selected == "« Back to menu":
        return None
    
    return selected


def create_habit(manager):
    """Create a new habit."""
    console.print("\n[bold green]--- Create Habit ---[/bold green]")

    name = questionary.text("Habit name:").ask()
    if not name:
        console.print("[red]✗ Habit name cannot be empty[/red]")
        return

    periodicity = questionary.select(
        "Periodicity:",
        choices=["daily", "weekly", "monthly", "weekly_fixed_day", "monthly_fixed_day"],
    ).ask()

    try:
        manager.create_habit(name, periodicity)
        console.print(
            f"[green]✓ Habit '[bold]{name}[/bold]' created successfully![/green]"
        )
        # Pause briefly to let the user see the message before going back to the main menu
        time.sleep(3) 
    except Exception as e:
        console.print(f"[red]✗ Error creating habit: {e}[/red]")


def mark_complete(manager):
    """Mark a habit as complete."""
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

def view_analytics(manager):
    """View habit analytics."""
    console.print("\n[bold cyan]--- Habit Analytics ---[/bold cyan]")
    console.print("[yellow]TODO: Implement analytics view[/yellow]")


def delete_habit(manager):
    """Delete a habit with confirmation."""
    console.print("\n[bold red]--- Delete Habit ---[/bold red]")

    name = select_habit(manager, "Select a habit to delete:", color="red")
    if not name:
        return

    # Confirm deletion
    confirm = questionary.confirm(
        f"Are you sure you want to delete '[bold]{name}[/bold]'? This action cannot be undone.",
        auto_enter=False
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
    from nudge.storage.storage import Storage
    from nudge.habit_manager.habit_manager import HabitManager

    storage = Storage("nudge_habits.db", auto_seed=False)
    manager = HabitManager(storage)
    main(manager)
