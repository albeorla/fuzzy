#!/bin/bash
# Run all linting and formatting checks

echo "🔍 Running Ruff linting..."
poetry run ruff check fuzzy_matcher tests || { echo "❌ Ruff linting failed"; exit 1; }

echo "✨ Running Ruff formatting check..."
poetry run ruff format --check fuzzy_matcher tests || { echo "❌ Ruff formatting check failed"; exit 1; }

echo "🧪 Running Mypy type checking..."
poetry run mypy fuzzy_matcher || { echo "❌ Mypy type checking failed"; exit 1; }

echo "All checks passed!"
