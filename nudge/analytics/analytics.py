"""Functional analytics utilities for habit analysis."""

def get_habits_by_periodicity(habits, periodicity):
    """Return a list of habits that match the given periodicity."""
    return [habit for habit in habits if habit.periodicity == periodicity]

def get_all_tracked_habits(habits):
    """
    Return a list of all currently tracked habits. A tracked habit is defined as one that has at least one completion.
    
    Args:
        habits: A list of Habit objects to filter.
        
    Returns:
        A list of Habit objects that have at least one completion.
    """
    return [habit for habit in habits if len(habit.completion_timestamps) > 0]

def get_longest_streak_for_all(habits):
    """Return the longest run streak of all defined habits."""
    longest_streak = 0
    for habit in habits:
        streak = get_longest_streak(habit)
        if streak > longest_streak:
            longest_streak = streak
    return longest_streak

def get_longest_streak(habit):
    """Calculate the longest run streak for a given habit."""
    if not habit.completion_timestamps:
        return 0

    # TODO: Implement logic to calculate the longest streak based on the habit's periodicity and completion timestamps.
    # Right now, this is a placeholder that simply counts consecutive days for daily habits. You will need to expand this logic to handle weekly and monthly habits, as well as fixed-day habits.
    timestamps = sorted(habit.completion_timestamps)
    longest_streak = 1
    current_streak = 1

    for i in range(1, len(timestamps)):
        if (timestamps[i] - timestamps[i - 1]).days <= 1: 
            current_streak += 1
        else:
            longest_streak = max(longest_streak, current_streak)
            current_streak = 1

    longest_streak = max(longest_streak, current_streak)  # Check at the end
    return longest_streak
