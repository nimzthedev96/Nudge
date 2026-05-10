# Nudge - Habit Tracking Application

A simple habit tracking application built with Python and SQLite for managing and analyzing daily habits.

## Project Structure

```
nudge/
├── habits/              # Core habit class (Habit)
├── habit_manager/       # Service class for managing habits (HabitManager)
├── storage/             # Service class for database operations (Storage)
├── analytics/           # Functional analytics and statistics
├── cli/                 # Command-line interface
└── __init__.py

tests/                   # Unit tests (pytest)
```

## Requirements

- Python 3.11+
- SQLite3 (included with Python)
- pytest (for testing)

## Installation

### 1. Clone the Repository

```bash
git clone <repository-url>
cd nudge
```

### 2. Create Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

## Usage

### Running the Application

```bash
# Using main.py
python main.py --help

# Or directly with the module
python -m nudge.cli --help
```

### CLI Commands
- TODO

## Testing

Run the test suite using pytest:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=nudge tests/

# Run specific test file
pytest tests/test_habit.py

# Run with verbose output
pytest -v
```

## Project Components
- TODO


## Database Schema

### Habits Table
- `id` (INTEGER, PRIMARY KEY): Auto-incremented unique identifier
- `name` (TEXT): Habit description
- `periodicity` (TEXT): 'daily', 'weekly', or 'monthly'
- `creation_timestamp` (INTEGER): Unix timestamp of habit creation

### Habit Completions Table
- `id` (INTEGER, PRIMARY KEY): Auto-incremented record ID
- `habit_id` (INTEGER, FOREIGN KEY): Reference to habits table
- `completion_timestamp` (INTEGER): Unix timestamp of completion


## Development Notes

- Keep dependencies minimal for simplicity
- Use functional programming patterns in analytics module
- All code includes docstrings for documentation


