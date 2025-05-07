"""CLI convenience commands for development."""

import argparse
import os
import subprocess
import sys
from typing import List


def run_command(command: List[str], description: str) -> int:
    """Run a shell command and print its output.

    Args:
    ----
        command: The command to run as a list of strings.
        description: A description of the command to display.

    Returns:
    -------
        The exit code of the command.

    """
    print(f"Running: {description}")
    print(f"Command: {' '.join(command)}")
    print("-" * 40)

    result = subprocess.run(command, text=True, check=False)
    return result.returncode


def run_tests() -> int:
    """Run tests with command-line options.

    Returns
    -------
        The exit code of the test command.

    """
    parser = argparse.ArgumentParser(description="Run matcher tests")
    parser.add_argument("--coverage", "-c", action="store_true", help="Generate coverage report")
    parser.add_argument("--html", "-r", action="store_true", help="Generate HTML coverage report")
    parser.add_argument("--parallel", "-p", action="store_true", help="Run tests in parallel")
    parser.add_argument("--unit", action="store_true", help="Run only unit tests")
    parser.add_argument("--integration", action="store_true", help="Run only integration tests")
    parser.add_argument("--e2e", action="store_true", help="Run only end-to-end tests")
    parser.add_argument("--test", "-t", help="Run a specific test path")

    args = parser.parse_args()

    # Build command
    command = ["pytest"]

    if args.parallel:
        command.extend(["-n", "auto"])

    if args.coverage or args.html:
        command.append("--cov=fuzzy_matcher")

    if args.html:
        command.append("--cov-report=html")

    if args.unit:
        command.append("-m")
        command.append("unit")
    elif args.integration:
        command.append("-m")
        command.append("integration")
    elif args.e2e:
        command.append("-m")
        command.append("e2e")

    if args.test:
        command.append(args.test)

    return run_command(command, "tests")


def run_lint() -> int:
    """Run linting checks.

    Returns
    -------
        The exit code of the lint command.

    """
    # Run ruff check
    ruff_result = run_command(["ruff", "check", "fuzzy_matcher", "tests"], "Ruff linting")
    if ruff_result != 0:
        return ruff_result

    # Run ruff format check
    format_result = run_command(
        ["ruff", "format", "--check", "fuzzy_matcher", "tests"], "Ruff format check"
    )
    if format_result != 0:
        return format_result

    # Run mypy
    mypy_result = run_command(["mypy", "fuzzy_matcher"], "Mypy type checking")
    return mypy_result


def run_format() -> int:
    """Apply code formatting.

    Returns
    -------
        The exit code of the format command.

    """
    # Run ruff format
    format_result = run_command(["ruff", "format", "fuzzy_matcher", "tests"], "Ruff formatting")
    if format_result != 0:
        return format_result

    # Run ruff check with fixes
    fix_result = run_command(
        ["ruff", "check", "--fix", "fuzzy_matcher", "tests"], "Ruff auto-fixes"
    )
    return fix_result


def run_check_all() -> int:
    """Run all checks.

    Returns
    -------
        The exit code of the combined checks.

    """
    # Run linting
    print("=== Running Linting Checks ===")
    lint_result = run_lint()
    if lint_result != 0:
        print("❌ Linting failed. Please fix the issues above before continuing.")
        return lint_result

    # Run tests with coverage
    print("\n=== Running Tests with Coverage ===")
    test_result = run_tests()
    if test_result != 0:
        print("❌ Tests failed. Please fix the issues above before continuing.")
        return test_result

    # Run pre-commit hooks if available
    if os.path.exists(".pre-commit-config.yaml"):
        print("\n=== Running Pre-commit Hooks ===")
        precommit_result = run_command(["pre-commit", "run", "--all-files"], "pre-commit hooks")
        if precommit_result != 0:
            print("❌ Pre-commit hooks failed. Please fix the issues above before continuing.")
            return precommit_result

    print("\n✅ All checks passed! Your code is ready to commit.")
    return 0


def list_commands() -> int:
    """List all available commands from pyproject.toml and scripts directory.

    Returns
    -------
        Always returns 0 (success).

    """
    print("=== Fuzzy Matcher Command Reference ===")
    print("")

    # Main CLI commands
    print("Main CLI Commands:")
    print("  poetry run fuzzy --demo all      - Run all demos")
    print("  poetry run fuzzy --demo string   - Run string matching demo")
    print("  poetry run fuzzy --demo entity   - Run entity resolution demo")
    print("  poetry run fuzzy --demo list     - Run list matching demo")
    print("")

    # Development commands
    print("Development Commands:")
    print("  poetry run test            - Run tests")
    print("    --coverage                     - Generate coverage report")
    print("    --html                         - Generate HTML coverage report")
    print("    --parallel                     - Run tests in parallel")
    print("    --unit                         - Run only unit tests")
    print("    --integration                  - Run only integration tests")
    print("    --e2e                          - Run only end-to-end tests")
    print("    --test PATH                    - Run a specific test path")
    print("")
    print("  poetry run lint            - Run linting checks")
    print("  poetry run format          - Apply code formatting")
    print("  poetry run check           - Run all checks")
    print("  poetry run commands        - Show this command reference")
    print("")

    # Shell scripts
    print("Shell Scripts:")
    print("  ./scripts/test.sh                - Run tests (see --help for options)")
    print("  ./scripts/lint.sh                - Run linting checks")
    print("  ./scripts/format.sh              - Apply code formatting")
    print("  ./scripts/check-all.sh           - Run all checks")
    print("  ./scripts/release.sh VERSION     - Release a new version")

    return 0


if __name__ == "__main__":
    sys.exit(run_check_all())
