#!/bin/bash
# Apply all formatting and auto-fixes

echo "✨ Running Ruff formatting..."
poetry run ruff format fuzzy_matcher tests || { echo "❌ Ruff formatting failed"; exit 1; }

echo "🔍 Running Ruff auto-fixes..."
poetry run ruff check --fix fuzzy_matcher tests || { echo "❌ Ruff auto-fixes failed"; exit 1; }

echo "✅ Formatting completed successfully!"
