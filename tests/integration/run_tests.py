"""
Integration Test Runner and Utilities

This module provides utilities for running and managing integration tests.
"""

import os
import sys
import subprocess
from pathlib import Path


def run_integration_tests():
    """Run all integration tests."""
    project_root = Path(__file__).parent.parent.parent
    integration_dir = project_root / "tests" / "integration"

    # Change to project root
    os.chdir(project_root)

    # Run pytest on integration tests
    cmd = [
        sys.executable,
        "-m",
        "pytest",
        "tests/integration/",
        "-v",
        "--tb=short",
        "--color=yes",
        "-m",
        "integration",
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        print("Integration tests completed successfully!")
        print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print("Integration tests failed!")
        print("STDOUT:", e.stdout)
        print("STDERR:", e.stderr)
        return False


def run_specific_integration_test(test_file):
    """Run a specific integration test file."""
    project_root = Path(__file__).parent.parent.parent

    os.chdir(project_root)

    cmd = [
        sys.executable,
        "-m",
        "pytest",
        f"tests/integration/{test_file}",
        "-v",
        "--tb=long",
        "--color=yes",
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        print(f"Test {test_file} completed successfully!")
        print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Test {test_file} failed!")
        print("STDOUT:", e.stdout)
        print("STDERR:", e.stderr)
        return False


def run_integration_tests_with_coverage():
    """Run integration tests with coverage reporting."""
    project_root = Path(__file__).parent.parent.parent

    os.chdir(project_root)

    cmd = [
        sys.executable,
        "-m",
        "pytest",
        "tests/integration/",
        "--cov=src",
        "--cov-report=html",
        "--cov-report=term-missing",
        "--cov-fail-under=80",
        "-v",
        "--color=yes",
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        print("Integration tests with coverage completed successfully!")
        print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print("Integration tests with coverage failed!")
        print("STDOUT:", e.stdout)
        print("STDERR:", e.stderr)
        return False


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Run integration tests")
    parser.add_argument("--file", help="Run specific test file")
    parser.add_argument(
        "--coverage", action="store_true", help="Run tests with coverage reporting"
    )

    args = parser.parse_args()

    if args.file:
        success = run_specific_integration_test(args.file)
    elif args.coverage:
        success = run_integration_tests_with_coverage()
    else:
        success = run_integration_tests()

    sys.exit(0 if success else 1)
