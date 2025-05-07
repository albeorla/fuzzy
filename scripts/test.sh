#!/bin/bash
# Run tests with options

# Default values
COVERAGE=0
HTML_REPORT=0
PARALLEL=0
MARKERS=""
SPECIFIC_TEST=""

# Parse arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --coverage|-c)
      COVERAGE=1
      shift
      ;;
    --html|-h)
      HTML_REPORT=1
      COVERAGE=1  # HTML report requires coverage
      shift
      ;;
    --parallel|-p)
      PARALLEL=1
      shift
      ;;
    --unit)
      MARKERS="unit"
      shift
      ;;
    --integration)
      MARKERS="integration"
      shift
      ;;
    --e2e)
      MARKERS="e2e"
      shift
      ;;
    --test|-t)
      SPECIFIC_TEST="$2"
      shift 2
      ;;
    *)
      echo "Unknown option: $1"
      echo "Usage: $0 [--coverage|-c] [--html|-h] [--parallel|-p] [--unit|--integration|--e2e] [--test|-t TEST_PATH]"
      exit 1
      ;;
  esac
done

# Build the command
CMD="poetry run pytest"

# Add parallel option if requested
if [[ $PARALLEL -eq 1 ]]; then
  CMD="$CMD -n auto"
fi

# Add coverage options
if [[ $COVERAGE -eq 1 ]]; then
  CMD="$CMD --cov=fuzzy_matcher"

  if [[ $HTML_REPORT -eq 1 ]]; then
    CMD="$CMD --cov-report=html"
  fi
fi

# Add marker if specified
if [[ -n "$MARKERS" ]]; then
  CMD="$CMD -m $MARKERS"
fi

# Add specific test if provided
if [[ -n "$SPECIFIC_TEST" ]]; then
  CMD="$CMD $SPECIFIC_TEST"
fi

# Print and execute command
echo "Running: $CMD"
eval "$CMD"

# If HTML report was generated, print path
if [[ $HTML_REPORT -eq 1 ]]; then
  echo "HTML coverage report generated at: coverage_html/index.html"
fi
