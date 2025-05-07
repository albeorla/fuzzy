# Test Coverage Summary

The Fuzzy Matcher library maintains a high level of test coverage to ensure reliability and maintainability.

## Current Coverage: 98%

As of May 7, 2025, the overall test coverage is 98%.

| Module | Statements | Missing | Coverage |
|--------|------------|---------|----------|
| fuzzy_matcher/application/facades.py | 106 | 4 | 96% |
| fuzzy_matcher/application/services.py | 111 | 3 | 97% |
| fuzzy_matcher/domain/entities.py | 59 | 0 | 100% |
| fuzzy_matcher/infrastructure/algorithms.py | 127 | 2 | 98% |
| fuzzy_matcher/infrastructure/preprocessors.py | 54 | 0 | 100% |
| fuzzy_matcher/infrastructure/repositories.py | 86 | 5 | 94% |
| fuzzy_matcher/protocols/interfaces.py | 48 | 0 | 100% |
| **TOTAL** | **591** | **14** | **98%** |

## Testing Approach

The project follows a comprehensive testing strategy:

1. **Unit Tests**: Testing individual components in isolation
2. **Integration Tests**: Testing interactions between components
3. **End-to-End Tests**: Testing the entire system functionality
4. **Property-Based Tests**: Using Hypothesis to verify properties of the system

For more information on our testing approach, see [Testing Approach](testing.md).

## Running Tests

To run the tests with coverage:

```bash
# Run tests with coverage report
poetry run test --coverage

# Generate HTML coverage report
poetry run test --html
```

The HTML coverage report provides detailed information on which lines of code are covered by tests.
