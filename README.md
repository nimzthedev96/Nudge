# Nudge - A Gentle Habit Tracking Application

A gentle habit tracking application built with Python and SQLite for managing and analyzing daily habits. Built for a university project.

## Features

- Habit creation and tracking
- Streak tracking per habit
- Analytics
- Supportive messages (nudges) to encourage habit completion
- Easy to use interface
- Convenient summary view

## Requirements

- Python 3.11+
- SQLite3 (included with Python)

## Installation

### 1. Clone the Repository

```bash
git clone github.com/nimzthedev96/Nudge
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

## Development

### Code Quality Tools

The project uses modern Python tools for code quality. All configurations are in `pyproject.toml`:

- **mypy** - Static type checking
- **black** - Code formatter
- **ruff** - Fast Python linter

Run these tools on your code:

```bash
# Type checking
mypy nudge

# Format code
black nudge tests

# Lint code
ruff check nudge tests

# Run all checks together
mypy nudge && black --check nudge tests && ruff check nudge tests
```

### Project Configuration

The `pyproject.toml` file contains all project metadata and tool configurations:
- Package dependencies and optional dev dependencies
- Build system configuration
- Type checker settings (mypy)
- Code formatter settings (black)
- Linter settings (ruff)
- Test runner settings (pytest)
- Coverage reporting settings

## Project Structure

```
nudge/
├── analytics/           # Functional analytics and statistics
├── cli/                 # Command-line interface
├── habits/              # Core habit class (Habit)
├── habit_manager/       # Service class for managing habits (HabitManager)
├── storage/             # Service class for database operations (Storage)
tests/                   # Unit tests (pytest)
```

## Project Components
- HabitManager: Service class acts as an API to the CLI
- CLI: Service class for CLI interactions and UI
- Storage: Service class for database operations

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


