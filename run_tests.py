#!/usr/bin/env python3
"""
Test runner script for the triple-i-backend test suite.
"""
import subprocess
import sys
import os
from pathlib import Path


def run_tests(test_type="all", verbose=True, coverage=False):
    """
    Run the test suite with specified options.
    
    Args:
        test_type: Type of tests to run ("all", "unit", "integration", "performance")
        verbose: Whether to run in verbose mode
        coverage: Whether to generate coverage report
    """
    # Change to project root directory
    project_root = Path(__file__).parent
    os.chdir(project_root)
    
    # Base pytest command
    cmd = ["python", "-m", "pytest"]
    
    # Add test selection based on type
    if test_type == "unit":
        cmd.extend(["tests/test_file_export.py", "tests/test_report_generation.py"])
    elif test_type == "integration":
        cmd.extend(["tests/test_integration.py"])
    elif test_type == "performance":
        cmd.extend(["-m", "performance"])
    else:  # all
        cmd.extend(["tests/"])
    
    # Add verbosity
    if verbose:
        cmd.append("-v")
    
    # Add coverage if requested
    if coverage:
        cmd.extend(["--cov=app", "--cov-report=html", "--cov-report=term"])
    
    # Add other useful options
    cmd.extend([
        "--tb=short",
        "--durations=10",
        "--color=yes"
    ])
    
    print(f"Running tests: {' '.join(cmd)}")
    print("=" * 60)
    
    try:
        result = subprocess.run(cmd, check=True)
        print("\n" + "=" * 60)
        print("✅ All tests passed!")
        return True
    except subprocess.CalledProcessError as e:
        print("\n" + "=" * 60)
        print(f"❌ Tests failed with exit code {e.returncode}")
        return False
    except FileNotFoundError:
        print("❌ pytest not found. Please install it with: pip install pytest")
        return False


def main():
    """Main entry point for the test runner."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Run the triple-i-backend test suite")
    parser.add_argument(
        "--type", 
        choices=["all", "unit", "integration", "performance"],
        default="all",
        help="Type of tests to run"
    )
    parser.add_argument(
        "--no-verbose", 
        action="store_true",
        help="Run tests in non-verbose mode"
    )
    parser.add_argument(
        "--coverage", 
        action="store_true",
        help="Generate coverage report"
    )
    
    args = parser.parse_args()
    
    success = run_tests(
        test_type=args.type,
        verbose=not args.no_verbose,
        coverage=args.coverage
    )
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
