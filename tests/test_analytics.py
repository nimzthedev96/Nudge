"""Tests for Analytics module."""

from nudge.habits.habit import Habit, Periodicity
from nudge.analytics import analytics

class TestAnalytics:
    """Test cases for analytics functions."""
    def test_get_habits_by_periodicity(self):
        """Test filtering habits by periodicity."""
        habit1 = Habit("Exercise", Periodicity.DAILY)
        habit2 = Habit("Read", Periodicity.WEEKLY)
        habit3 = Habit("Review goals", Periodicity.WEEKLY)
        habits = [habit1, habit2, habit3]
        # Test filtering for daily habits
        daily_habits = analytics.get_habits_by_periodicity(habits, Periodicity.DAILY)
        assert len(daily_habits) == 1
        assert daily_habits[0].name == "Exercise"
        assert daily_habits[0].periodicity == Periodicity.DAILY

        # Test filtering for weekly habits
        weekly_habits = analytics.get_habits_by_periodicity(habits, Periodicity.WEEKLY)
        assert len(weekly_habits) == 2
        assert weekly_habits[0].name == "Read"
        assert weekly_habits[0].periodicity == Periodicity.WEEKLY
        assert weekly_habits[1].name == "Review goals"
        assert weekly_habits[1].periodicity == Periodicity.WEEKLY

        # Test filtering for monthly habits
        monthly_habits = analytics.get_habits_by_periodicity(habits, Periodicity.MONTHLY)
        assert len(monthly_habits) == 0

    def test_get_all_tracked_habits(self):
        """Test retrieving all tracked habits."""
        habit1 = Habit("Exercise", Periodicity.DAILY)
        habit2 = Habit("Read", Periodicity.WEEKLY)
        habit3 = Habit("Review goals", Periodicity.MONTHLY)
        habit1.completion_timestamps.append("2024-01-01T10:00:00")
        habits = [habit1, habit2, habit3] 
        tracked_habits = analytics.get_all_tracked_habits(habits)
        assert len(tracked_habits) == 1 
        assert tracked_habits[0].name == "Exercise"
        assert tracked_habits[0].periodicity == Periodicity.DAILY 
      
    
    def test_get_longest_streak_for_all(self):
        """Test calculating the longest streak across all habits."""
        # This test will require creating multiple Habit objects with different completion patterns and then calling the function to calculate the longest streak among them.
        pass
    
    def test_get_longest_streak(self):
        """Test calculating the longest streak for a single habit."""
        # This test will require creating a Habit object, marking it as completed on different days, and then calling the function to calculate its longest streak.
        pass
    

    
