#!/bin/bash
# Script to automate the release process

set -e

# Check if a version argument was provided
if [ -z "$1" ]; then
  echo "Error: No version specified"
  echo "Usage: $0 <version> [--test]"
  echo "Example: $0 0.2.0"
  echo "Example: $0 0.2.0 --test (to publish to TestPyPI)"
  exit 1
fi

VERSION=$1
TEST_FLAG=$2

# Check if current directory is clean
if [[ -n $(git status -s) ]]; then
  echo "❌ Working directory is not clean. Please commit all changes before releasing."
  exit 1
fi

echo "=== Preparing release v$VERSION ==="

# Update version in pyproject.toml
echo "Updating version in pyproject.toml..."
sed -i.bak "s/^version = \".*\"/version = \"$VERSION\"/" pyproject.toml && rm pyproject.toml.bak

# Run all checks
echo "Running quality checks..."
./scripts/check-all.sh
if [ $? -ne 0 ]; then
  echo "❌ Quality checks failed. Aborting release."
  exit 1
fi

# Commit version bump
echo "Committing version bump..."
git add pyproject.toml
git commit -m "Bump version to $VERSION"

# Create git tag
echo "Creating git tag v$VERSION..."
git tag -a "v$VERSION" -m "Release version $VERSION"

# Build the package
echo "Building package..."
poetry build

# Publish to PyPI or TestPyPI
if [ "$TEST_FLAG" == "--test" ]; then
  echo "Publishing to TestPyPI..."
  poetry publish -r testpypi
else
  echo "Publishing to PyPI..."
  poetry publish
fi

echo "✅ Released v$VERSION successfully!"
echo
echo "Next steps:"
echo "1. Push the commit: git push origin main"
echo "2. Push the tag: git push origin v$VERSION"
echo "3. Create a GitHub release at: https://github.com/aorlando/fuzzy/releases/new?tag=v$VERSION"
