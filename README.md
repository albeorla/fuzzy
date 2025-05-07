# Fuzzy Matcher

[![Test Coverage: 98%](https://img.shields.io/badge/coverage-98%25-brightgreen.svg)](docs/test_coverage_summary.md)

A flexible fuzzy string matching and entity resolution library for Python.

## Overview

Fuzzy Matcher provides tools for preprocessing strings, calculating string similarity using various algorithms, and resolving entities based on fuzzy name matching. It's designed to help solve problems like:

- Matching company names with different formats or typos
- Finding similar strings in a large dataset
- Resolving entities across different data sources
- Standardizing and normalizing string inputs

## Features

- **String Preprocessing** with a configurable chain of steps
- **Multiple Matching Algorithms**:
  - Levenshtein distance
  - Damerau-Levenshtein distance
  - Jaro-Winkler similarity
  - Token set ratio
  - Token sort ratio
  - Partial ratio
  - Weighted ratio
- **Phonetic Encoding Algorithms**:
  - Soundex
  - Metaphone
- **Configurable match decision strategies**
- **Entity resolution** from a list of candidates
- **In-memory entity repository** with phonetic indexing
- **Comprehensive testing** with high code coverage

## Installation

### From PyPI (Recommended for users)

Once the package is published, you can install it using pip:

```bash
pip install fuzzy-matcher
```

### From source (For development)

1.  Ensure you have [Poetry](https://python-poetry.org/) installed.
2.  Clone the repository:
    ```bash
    git clone https://github.com/aorlando/fuzzy.git
    cd fuzzy
    ```
3.  Install the package and its dependencies:
    ```bash
    poetry install
    ```
    If you intend to run tests or contribute, install development dependencies as well:
    ```bash
    poetry install --with dev
    ```

## Quick Start

### Basic String Comparison

```python
from fuzzy_matcher.application.facades import EntityResolutionFacade

facade = EntityResolutionFacade()
result = facade.compare_strings("Apple Inc.", "Apple Incorporated")
print(f"Is match: {result['is_match']}")
print(f"Scores: {result['scores']}")
```

### Entity Resolution

```python
from fuzzy_matcher.application.facades import EntityResolutionFacade

facade = EntityResolutionFacade()

# Register entities
facade.register_entity(
    "E001", "Apple Inc.",
    ["Apple Incorporated", "Apple Computer"],
    {"industry": "Technology"}
)

# Find by name (exact or fuzzy)
entity = facade.find_by_name("apple incorporated")
if entity:
    print(f"Found entity: {entity.primary_name}")
```

### Finding Best Matches in a List

```python
from fuzzy_matcher.application.facades import EntityResolutionFacade

facade = EntityResolutionFacade()

query = "Jonh Doe"  # Typo
choices = ["John Doe", "Jane Doe", "Jonathan Doering"]

matches = facade.find_best_matches_in_list(
    query, choices, algorithm_name='jaro_winkler', threshold=0.7
)

for match in matches:
    print(f"Match: {match['matched_candidate_original']} (Score: {match['score']})")
```

## Documentation

See the `docs/` directory for detailed documentation:

- [Usage Guide](docs/usage.md): Detailed examples of how to use the library
- [Architecture](docs/architecture.md): Overview of the library architecture
- [Testing Approach](docs/testing.md): Information about the testing strategy
- [Test Coverage Summary](docs/test_coverage_summary.md): Summary of test coverage

## Code Structure

The codebase follows a clean architecture approach with these main components:

- `fuzzy_matcher/protocols/`: Protocol definitions (interfaces) that define contracts for components
- `fuzzy_matcher/domain/`: Core domain entities that implement the protocols
- `fuzzy_matcher/infrastructure/`: Implementations of algorithms, preprocessors, and repositories
- `fuzzy_matcher/application/`: Higher-level services and facades that compose the components
- `fuzzy_matcher/main.py`: Demo application showcasing the library's functionality

## Development Commands

### Running the Demo

```bash
# Run the full demo application
poetry run demo

# Run specific demo categories
poetry run fuzzy --demo all     # Run all demos (default)
poetry run fuzzy --demo string  # Run only string matching demo
poetry run fuzzy --demo entity  # Run only entity resolution demo
poetry run fuzzy --demo list    # Run only list matching demo
```

### Testing

```bash
# Run all tests
poetry run pytest

# Run tests with coverage
poetry run pytest --cov=fuzzy_matcher

# Run tests with HTML coverage report
poetry run pytest --cov=fuzzy_matcher --cov-report=html

# Use the test script for convenience
./scripts/test.sh --coverage    # Run with coverage
./scripts/test.sh --html        # Generate HTML report
./scripts/test.sh --unit        # Run only unit tests
./scripts/test.sh --test tests/e2e/test_main_examples.py  # Run specific test
```

See [Testing Approach](docs/testing.md) for more details on the testing strategy.

### Code Quality

```bash
# Check and apply code formatting
poetry run ruff format fuzzy_matcher tests

# Run linting checks
poetry run ruff check fuzzy_matcher tests

# Run type checking
poetry run mypy fuzzy_matcher

# Use the convenience scripts
./scripts/lint.sh    # Run all checks
./scripts/format.sh  # Apply all formatting
```

For more development commands, see the [Development Guide](DEV.md).

## Requirements

- Python 3.8+
- Dependencies are managed by Poetry and listed in `pyproject.toml`. Key runtime dependencies include:
  - unidecode (≥ 1.3.0)
  - jellyfish (≥ 0.9.0)
  - thefuzz (≥ 0.19.0) with python-Levenshtein (for speedup)
