"""Database seeding module for initializing sample habit data."""

from calendar import monthrange
from datetime import datetime, timedelta

from nudge.habits.habit import Habit, Periodicity
from nudge.storage.storage import Storage


def seed_initial_habits(storage: Storage) -> None:
    """
    Seed the database with initial habit data.

    This function creates sample habits with realistic completion patterns.
    It only runs if the database is empty (no existing habits).

    Args:
        storage: The Storage instance to seed.
    """
    # Check if database already has habits
    existing_habits = storage.load_all_habits()
    if existing_habits:
        return

    # Define sample habits with different periodicities
    sample_habits = [
        Habit("Morning Exercise", Periodicity.DAILY),
        Habit("Read for 30 minutes", Periodicity.DAILY),
        Habit("Weekly Review", Periodicity.WEEKLY),
        Habit("Meditation", Periodicity.DAILY),
        Habit("Team Standup", Periodicity.WEEKLY),
        Habit("Monthly Goal Planning", Periodicity.MONTHLY),
        Habit("Prayer", Periodicity.WEEKLY_FIXED_DAY),
        Habit("Health Checkup", Periodicity.MONTHLY_FIXED_DAY),
    ]

    # Create completion patterns for each habit
    completion_patterns = {
        "Morning Exercise": _generate_daily_pattern(14, 0.8),  # 80% adherence
        "Read for 30 minutes": _generate_daily_pattern(14, 0.6),  # 60% adherence
        "Weekly Review": _generate_weekly_pattern(8, 0.9),  # 90% adherence
        "Meditation": _generate_daily_pattern(14, 0.5),  # 50% adherence
        "Team Standup": _generate_weekly_pattern(8, 1.0),  # 100% adherence
        "Monthly Goal Planning": _generate_monthly_pattern(3, 1.0),  # 100% adherence
        "Prayer": _generate_weekly_fixed_day_pattern(8, 0.95),  # 95% adherence, same weekday
        "Health Checkup": _generate_monthly_fixed_day_pattern(3, 1.0),  # 100% adherence, same day
    }

    # Save habits and their completions
    for habit in sample_habits:
        storage.save_habit(habit)

        # Get the completion dates for this habit
        completions = completion_patterns.get(habit.name, [])

        # Save each completion
        for completion_date in completions:
            if habit.id is not None:
                storage.save_completion(habit.id, completion_date)


def _generate_daily_pattern(days_back: int, adherence_rate: float) -> list[datetime]:
    """
    Generate a realistic daily habit completion pattern.

    Args:
        days_back: Number of days in the past to generate completions for.
        adherence_rate: Percentage of days the habit was completed (0.0 to 1.0).

    Returns:
        List of completion datetime objects.
    """
    completions = []
    now = datetime.now().replace(hour=9, minute=0, second=0, microsecond=0)

    for day in range(days_back):
        if _should_complete(adherence_rate):
            # Vary the time slightly to be realistic
            completion_time = now - timedelta(days=day, minutes=_random_offset(60))
            completions.append(completion_time)

    return sorted(completions)


def _generate_weekly_pattern(weeks_back: int, adherence_rate: float) -> list[datetime]:
    """
    Generate a realistic weekly habit completion pattern.

    Args:
        weeks_back: Number of weeks in the past to generate completions for.
        adherence_rate: Percentage of weeks the habit was completed (0.0 to 1.0).

    Returns:
        List of completion datetime objects.
    """
    completions = []
    now = datetime.now().replace(hour=10, minute=0, second=0, microsecond=0)

    for week in range(weeks_back):
        if _should_complete(adherence_rate):
            # Complete on a random day of the week
            day_offset = _random_offset(7)
            completion_time = now - timedelta(
                weeks=week, days=day_offset, minutes=_random_offset(120)
            )
            completions.append(completion_time)

    return sorted(completions)


def _generate_monthly_pattern(months_back: int, adherence_rate: float) -> list[datetime]:
    """
    Generate a realistic monthly habit completion pattern.

    Args:
        months_back: Number of months in the past to generate completions for.
        adherence_rate: Percentage of months the habit was completed (0.0 to 1.0).

    Returns:
        List of completion datetime objects.
    """
    completions = []
    now = datetime.now().replace(hour=14, minute=0, second=0, microsecond=0)

    for month in range(months_back):
        if _should_complete(adherence_rate):
            # Complete on a random day of the month
            days_in_current_month = 28 + _random_offset(4)  # 28-31 days
            day_offset = _random_offset(days_in_current_month)

            # Calculate date for this month
            completion_time = now - timedelta(
                days=30 * month + day_offset, minutes=_random_offset(240)
            )
            completions.append(completion_time)

    return sorted(completions)


def _generate_weekly_fixed_day_pattern(weeks_back: int, adherence_rate: float) -> list[datetime]:
    """
    Generate a realistic weekly habit completion pattern for fixed weekday habits.

    Args:
        weeks_back: Number of weeks in the past to generate completions for.
        adherence_rate: Percentage of weeks the habit was completed (0.0 to 1.0).

    Returns:
        List of completion datetime objects, all on the same weekday.
    """
    completions = []
    now = datetime.now().replace(hour=7, minute=0, second=0, microsecond=0)

    fixed_weekday_offset = 2  # Wednesday

    for week in range(weeks_back):
        if _should_complete(adherence_rate):
            # Calculate days to the fixed weekday
            days_to_weekday = (now.weekday() - fixed_weekday_offset) % 7
            completion_time = now - timedelta(
                weeks=week, days=days_to_weekday, minutes=_random_offset(120)
            )
            completions.append(completion_time)

    return sorted(completions)


def _generate_monthly_fixed_day_pattern(months_back: int, adherence_rate: float) -> list[datetime]:
    """
    Generate a realistic monthly habit completion pattern for fixed day-of-month habits.

    Args:
        months_back: Number of months in the past to generate completions for.
        adherence_rate: Percentage of months the habit was completed (0.0 to 1.0).

    Returns:
        List of completion datetime objects, all on the same day of the month.
    """
    completions = []
    now = datetime.now().replace(hour=15, minute=0, second=0, microsecond=0)

    # Use the current day of the month as the fixed day
    fixed_day = now.day

    for month in range(months_back):
        if _should_complete(adherence_rate):
            # Calculate the date on the fixed day of each month
            try:
                completion_date = now.replace(
                    month=((now.month - month - 1) % 12) + 1,
                    year=now.year - (1 if (now.month - month - 1) < 0 else 0),
                    day=fixed_day,
                    minute=_random_offset(60),
                )
                completions.append(completion_date)
            except ValueError:
                # Handle months with fewer days (e.g., February, 31st)
                # Use the last day of the month
                year = now.year - (1 if (now.month - month - 1) < 0 else 0)
                month_num = ((now.month - month - 1) % 12) + 1
                last_day = monthrange(year, month_num)[1]
                day_to_use = min(fixed_day, last_day)
                completion_date = now.replace(
                    month=month_num, year=year, day=day_to_use, minute=_random_offset(60)
                )
                completions.append(completion_date)

    return sorted(completions)


def _should_complete(adherence_rate: float) -> bool:
    """
    Determine if a habit should be marked complete based on adherence rate.

    Args:
        adherence_rate: Percentage rate (0.0 to 1.0).

    Returns:
        True if the habit should be completed.
    """
    import random

    return random.random() < adherence_rate


def _random_offset(max_value: int) -> int:
    """
    Generate a random offset up to max_value.

    Args:
        max_value: Maximum value for the offset.

    Returns:
        Random integer between 0 and max_value.
    """
    import random

    return random.randint(0, max_value)
