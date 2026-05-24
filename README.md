# Nudge - A Gentle Habit Tracking Application

A gentle habit tracking application built with Python and SQLite for managing and analyzing daily habits. Built for a university project.

## Features

- Habit creation and tracking
- Streak tracking per habit
- Analytics
- Supportive messages (nudges) to encourage habit completion
- Easy to use interface
- Convenient summary view

## Habit Periodicities

Nudge supports five different periodicity types for habits:

- **Daily** - Must be completed every day. Streaks continue when completions are within 1 day of each other.
- **Weekly** - Must be completed once per week. Streaks continue when completions are within 14 days of each other.
- **Weekly Fixed Day** - Must be completed on the same day of the week (e.g., every Monday). Streaks require completions on the same weekday in consecutive weeks.
- **Monthly** - Must be completed once per month. Streaks continue when completions occur in consecutive months.
- **Monthly Fixed Day** - Must be completed on the same day of each month (e.g., the 15th). Streaks require completions on the same day in consecutive months.


## Requirements

- Python 3.11+
- SQLite3 (included with Python)

## Installation

### Prerequisites

Install python

```bash
# Windows
winget install Python.Python.3.12

# macOS/Linux
brew install python@3.12
```

After installation, you may need to re-open a new terminal session.

### 1. Clone the Repository

```bash
git clone https://github.com/nimzthedev96/Nudge.git
cd Nudge
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

### 3. Install the Package

```bash
# Install in development mode with dependencies
pip install -e .

# Optional: Install with development tools (testing, type checking, linting)
pip install -e ".[dev]"
```

## Usage

### Running the Application
```bash

python main.py

```

### Using the Application
Nudge offers an interactive command line interface, allowing the user to easily create habits, mark habits as complete and run analytics. Choose a menu option and start tracking your habits today!

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

Screenshots of the user testing of the CLI tool can be founding testing_screenshots/cli


## Development

### Code Quality Tools

The project uses modern Python tools for code quality. All configurations are in `pyproject.toml`:

- **mypy** - Static type checking
- **black** - Code formatter
- **ruff** - Fast Python linter
Run code quality checks:

```bash
# Type checking
mypy nudge

# Format code
black nudge tests

# Lint code
ruff check nudge tests
```

## Project Structure

```
nudge/
├── analytics/           # Analytics and statistics
├── cli/                 # Command-line interface
├── habits/              # Habit model
├── habit_manager/       # Habit management service
├── storage/             # Database operations
├── testing_screenshots  # Contains screenshots for CLI testing
tests/                   # Unit tests
```

## Database Schema

### Habits Table
- `id` (INTEGER, PRIMARY KEY): Auto-incremented unique identifier
- `name` (TEXT): Habit description
- `periodicity` (TEXT): 'daily', 'weekly', or 'monthly'
- `creation_timestamp` (DATETIME): Unix timestamp of habit creation

### Habit Completions Table
- `id` (INTEGER, PRIMARY KEY): Auto-incremented record ID
- `habit_id` (INTEGER, FOREIGN KEY): Reference to habits table
- `completion_timestamp` (DATETIME): Unix timestamp of completion


