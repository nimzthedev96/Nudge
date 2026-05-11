"""Motivational messages and streak tracking utilities."""

import random
from datetime import datetime, date, timedelta

DAILY_QUOTES = [
    "Every small step counts. You're building a better version of yourself! 🌱",
    "Progress, not perfection. Keep going! 💪",
    "Your future self will thank you for today's effort. 🚀",
    "Consistency is the key to success. You've got this! 🔑",
    "Small daily habits lead to extraordinary results. ✨",
    "You're stronger than you think. Keep pushing! 💥",
    "Done is better than perfect. Keep building momentum! 🎯",
    "Every day is a new opportunity to be better. 🌟",
    "You're not just tracking habits, you're building character. 💎",
    "The secret of success is consistency. Stay committed! 🏆",
]

COMPLETION_MESSAGES = [
    "🎉 Awesome! You're crushing it!",
    "✨ Fantastic work today!",
    "💪 Keep up the great momentum!",
    "🌟 You're unstoppable!",
    "🔥 On fire! Love the dedication!",
    "🎯 Perfect! Another win for you!",
    "👏 Excellent progress!",
    "🚀 You're soaring today!",
    "💯 Nailed it! You're amazing!",
    "⭐ Simply stellar work!",
]

ENCOURAGEMENT_MESSAGES = {
    1: "🌱 You've started! Great beginning!",
    3: "🔥 3-day streak! You're building momentum!",
    7: "🏆 A whole week! That's impressive!",
    14: "👑 Two weeks of consistency! You're a champion!",
    30: "🌟 One month! You're officially a habit master!",
    60: "💎 Two months! Extraordinary dedication!",
    100: "🚀 100 days! You're a legend!",
}

PENDING_REMINDERS = [
    "Come on, you've got this today! 💪",
    "Don't break the chain! Just one more habit! 🔗",
    "You can do it! Complete this habit! 🎯",
    "One step at a time. You're almost there! 👣",
    "Show up for yourself today! 🌟",
]


def get_daily_quote():
    """Get a random daily motivational quote."""
    return random.choice(DAILY_QUOTES)


def get_completion_message():
    """Get a random completion encouragement message."""
    return random.choice(COMPLETION_MESSAGES)

