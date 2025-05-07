# Development Guide

This document contains all commands necessary for developing, testing, and running the Fuzzy Matcher library using Poetry.

## Setup and Installation

1.  **Install Poetry**:
    If you don't have Poetry installed, follow the instructions on the [official Poetry website](https://python-poetry.org/docs/#installation).

2.  **Clone the repository**:

    ```bash
    git clone https://github.com/aorlando/fuzzy.git
    cd fuzzy
    ```

3.  **Install dependencies**:
    This command installs the package and its dependencies, including development tools.
    ```bash
    poetry install --with dev
    ```
    To install only main dependencies (e.g., for a production-like environment check):
    ```bash
    poetry install
    ```

## Development Scripts

The project includes several convenience scripts in the `scripts/` directory:

```bash
# Run all linting and code quality checks
./scripts/lint.sh

# Apply all formatting and auto-fixes
./scripts/format.sh

# Run tests with options
./scripts/test.sh --coverage    # Run with coverage
./scripts/test.sh --html        # Generate HTML report
./scripts/test.sh --parallel    # Run in parallel
./scripts/test.sh --unit        # Run only unit tests
./scripts/test.sh --integration # Run only integration tests
./scripts/test.sh --e2e         # Run only e2e tests
./scripts/test.sh --test PATH   # Run specific test
```

Make these scripts executable if needed:

```bash
chmod +x scripts/*.sh
```

## Running the Application

To run the demo application:

```bash
poetry run python -m fuzzy_matcher.main
```

You can also use the Poetry scripts that have been set up:

```bash
# Run the interactive demo with command-line arguments
poetry run fuzzy --demo all    # Run all demos (default)
poetry run fuzzy --demo string # Run only string matching demo
poetry run fuzzy --demo entity # Run only entity resolution demo
poetry run fuzzy --demo list   # Run only list matching demo

# Run all demos directly without arguments
poetry run demo
```

## Testing

To run all tests:

```bash
poetry run pytest
```

To run tests with coverage:

```bash
poetry run pytest --cov=fuzzy_matcher
```

To generate an HTML coverage report:

```bash
poetry run pytest --cov=fuzzy_matcher --cov-report=html
```

The report will be in `coverage_html/index.html`.

To run specific test categories (using pytest markers or paths):

```bash
poetry run pytest -m unit
poetry run pytest -m integration
poetry run pytest -m e2e
# Or by path
poetry run pytest tests/unit/
```

To run tests in parallel (faster):

```bash
poetry run pytest -n auto
```

## Code Quality

Ruff is used for both linting and formatting in this project:

To check and fix code formatting with Ruff:

```bash
poetry run ruff format fuzzy_matcher tests
```

To check formatting without making changes:

```bash
poetry run ruff format --check fuzzy_matcher tests
```

To run linting with Ruff:

```bash
poetry run ruff check fuzzy_matcher tests
```

To auto-fix linting issues with Ruff where possible:

```bash
poetry run ruff check --fix fuzzy_matcher tests
```

To run type checking with Mypy:

```bash
poetry run mypy fuzzy_matcher
```

## Building and Distribution

To build the package (sdist and wheel):

```bash
poetry build
```

The built files will be in the `dist/` directory.

To publish the package to PyPI (ensure you have credentials configured):

```bash
poetry publish
```

You might want to publish to TestPyPI first:

```bash
poetry publish -r testpypi
```

## Activating the Virtual Environment

Poetry creates and manages a virtual environment for the project. To activate it directly in your shell:

```bash
poetry shell
```

Once activated, you can run commands like `python`, `pytest`, etc., without the `poetry run` prefix.

## Pre-commit hooks

To ensure consistent code quality, this project uses pre-commit hooks. To set them up:

1. Install pre-commit:

   ```bash
   pip install pre-commit
   ```

2. Install the hooks:

   ```bash
   pre-commit install
   ```

3. To manually run the hooks on all files:
   ```bash
   pre-commit run --all-files
   ```

### Pre-commit Workflow

Our pre-commit workflow automatically runs the following checks when you commit:

1. **Standard pre-commit hooks**: Ensures no trailing whitespace, properly formatted YAML/TOML files, and no merge conflicts remain.

2. **Custom linting script**: Runs our `./scripts/lint.sh` script, which performs:
   - Ruff linting with auto-fixes when possible
   - Ruff formatter check
   - Mypy type checking

3. **Poetry checks**: Ensures poetry.lock is consistent with pyproject.toml

For more comprehensive checks (including running tests), use:

```bash
./scripts/check-all.sh
```

This script runs:
- All linting checks via `./scripts/lint.sh`
- All tests with coverage via `./scripts/test.sh --coverage --parallel`
- Pre-commit hooks on all files

It's recommended to run this before pushing important changes to ensure all tests pass.

## Documentation

The project documentation is available in the `docs/` directory:

- [Usage Guide](docs/usage.md): Detailed examples of how to use the library
- [Architecture](docs/architecture.md): Overview of the library architecture
- [Testing Approach](docs/testing.md): Information about the testing strategy
- [Test Coverage Summary](docs/test_coverage_summary.md): Summary of test coverage

To update the documentation, edit the corresponding Markdown files in the `docs/` directory.
