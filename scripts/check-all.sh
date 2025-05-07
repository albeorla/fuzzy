#!/bin/bash
# Run all checks before committing or pushing

echo "=== Fuzzy Matcher Quality Check ==="
echo

echo "Step 1: Running linting checks"
./scripts/lint.sh
if [ $? -ne 0 ]; then
  echo "❌ Linting failed. Please fix the issues above before continuing."
  exit 1
fi
echo

echo "Step 2: Running all tests with coverage"
./scripts/test.sh --coverage --parallel
if [ $? -ne 0 ]; then
  echo "❌ Tests failed. Please fix the failing tests before continuing."
  exit 1
fi
echo

# Skip pre-commit hooks when running from pre-commit to avoid recursion
if [ "$SKIP_PRE_COMMIT" != "1" ] && [ "$PRE_COMMIT_HOOK_TYPE" == "" ]; then
  echo "Step 3: Running pre-commit hooks"
  pre-commit run --all-files
  if [ $? -ne 0 ]; then
    echo "❌ Pre-commit hooks failed. Please fix the issues before continuing."
    exit 1
  fi
  echo
fi

echo "All checks passed!"
