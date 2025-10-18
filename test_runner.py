import subprocess
import sys
import os
from pathlib import Path


def install_dependencies():
    print("Installing test dependencies...")
    try:
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"],
            check=True,
        )
        print("Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Failed to install dependencies: {e}")
        return False


def run_tests(test_type="all", verbose=True, coverage=False, performance=False):

    project_root = Path(__file__).parent
    os.chdir(project_root)

    cmd = [sys.executable, "-m", "pytest"]

    if test_type == "unit":
        cmd.extend(["tests/test_file_generation.py"])
    elif test_type == "integration":
        cmd.extend(["tests/test_full_integration.py"])
    elif test_type == "performance":
        cmd.extend(
            [
                "tests/test_report_generation_performance.py",
                "tests/test_esrs_tags_and_visuals.py",
            ]
        )
    else:
        cmd.extend(["tests/"])

    if verbose:
        cmd.append("-v")

    if coverage:
        cmd.extend(["--cov=app", "--cov-report=html", "--cov-report=term"])


    if performance and test_type == "all":
        cmd.extend(["-m", "performance"])
        
    cmd.extend(["--tb=short", "--durations=10", "--color=yes", "--strict-markers"])

    print(f"Running tests with: {' '.join(cmd)}")
    print("=" * 80)

    try:
        result = subprocess.run(cmd, check=True)
        print("\n" + "=" * 80)
        print("✅ All tests passed!")

        if coverage:
            print("\n📊 Coverage report generated in htmlcov/index.html")

        return True
    except subprocess.CalledProcessError as e:
        print("\n" + "=" * 80)
        print(f"❌ Tests failed with exit code {e.returncode}")
        return False
    except FileNotFoundError:
        print("❌ pytest not found. Please install it with: pip install pytest")
        return False


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Test runner for triple-i-backend",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "--type",
        choices=["all", "unit", "integration", "performance"],
        default="all",
    )
    parser.add_argument(
        "--no-verbose", action="store_true",
    )
    parser.add_argument(
        "--coverage", action="store_true",
    )
    parser.add_argument(
        "--performance",
        action="store_true",
    )
    parser.add_argument(
        "--install-deps",
        action="store_true",
    )

    args = parser.parse_args()

    # Install dependencies if requested
    if args.install_deps:
        if not install_dependencies():
            sys.exit(1)

    # Run tests
    success = run_tests(
        test_type=args.type,
        verbose=not args.no_verbose,
        coverage=args.coverage,
        performance=args.performance,
    )

    if success:
        print("\n🎉 Test suite completed successfully!")
    else:
        print("\n❌ Test suite failed!")

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
