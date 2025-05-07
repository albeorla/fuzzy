# Testing Approach

This document describes the testing approach used in the Fuzzy Matcher library.

## Testing Levels

The project follows a comprehensive testing strategy with tests at multiple levels:

### Unit Tests

Unit tests focus on testing individual components in isolation. These tests are located in the `tests/unit/` directory and are marked with the `unit` pytest marker.

Examples include:
- Testing each matching algorithm individually
- Testing each preprocessing step separately
- Testing entity components in isolation

### Integration Tests

Integration tests verify that multiple components work correctly together. These tests are located in the `tests/integration/` directory and are marked with the `integration` pytest marker.

Examples include:
- Testing the application services with real infrastructure components
- Testing facades with underlying services and repositories

### End-to-End (E2E) Tests

E2E tests verify the complete application flow from input to output. These tests are located in the `tests/e2e/` directory and are marked with the `e2e` pytest marker.

Examples include:
- Tests that validate the examples from `main.py`
- Tests that mimic real user workflows

## Test Categories

The test suite includes several types of tests:

### Functional Tests

These tests verify that the code functions correctly according to specifications. They validate inputs, outputs, and behavior.

### Property-Based Tests

The project uses the Hypothesis library for property-based testing. This approach generates test cases automatically based on defined properties and invariants that should hold true for the system.

For example:
- Testing that all algorithms return 1.0 for identical strings
- Testing that preprocessing is idempotent (applying it twice doesn't change the result)

### Boundary Tests

These tests focus on edge cases and boundary conditions:
- Empty strings
- Very long strings
- Strings with special characters
- Minimum/maximum similarity thresholds

## Running Tests

### Basic Test Commands

```bash
# Run all tests
poetry run pytest

# Run with coverage reporting
poetry run pytest --cov=fuzzy_matcher

# Run tests in parallel
poetry run pytest -n auto

# Generate HTML coverage report
poetry run pytest --cov=fuzzy_matcher --cov-report=html
```

### Running Specific Test Categories

```bash
# Run only unit tests
poetry run pytest -m unit

# Run only integration tests
poetry run pytest -m integration

# Run only E2E tests
poetry run pytest -m e2e
```

### Running Specific Tests

```bash
# Run tests in a specific file
poetry run pytest tests/unit/infrastructure/test_algorithms.py

# Run a specific test class
poetry run pytest tests/e2e/test_main_examples.py::TestMainExamples

# Run a specific test method
poetry run pytest tests/e2e/test_main_examples.py::TestMainExamples::test_string_matching_examples
```

### Convenient Script

The project includes a test script with common options:

```bash
# Run all tests with coverage
./scripts/test.sh --coverage

# Run tests with HTML report
./scripts/test.sh --html

# Run tests in parallel
./scripts/test.sh --parallel

# Run specific test category
./scripts/test.sh --unit
./scripts/test.sh --integration
./scripts/test.sh --e2e

# Run a specific test
./scripts/test.sh --test tests/unit/infrastructure/test_algorithms.py
```

## Test Coverage

The project aims to maintain high test coverage. Coverage reports can be generated in various formats:

```bash
# Terminal report
poetry run pytest --cov=fuzzy_matcher

# HTML report
poetry run pytest --cov=fuzzy_matcher --cov-report=html

# XML report (for CI/CD)
poetry run pytest --cov=fuzzy_matcher --cov-report=xml
```

Current test coverage is maintained above 95% for the core codebase.
