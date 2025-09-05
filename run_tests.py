#!/usr/bin/env python3
"""
🧪 Django-CFG Test Runner

Simple test runner following KISS principles.
Run tests by category, module, or all at once.

Usage:
    python run_tests.py                    # Run all tests
    python run_tests.py --unit             # Run only unit tests
    python run_tests.py --integration      # Run only integration tests
    python run_tests.py --apps             # Run only app tests (accounts, support)
    python run_tests.py --core             # Run only core tests
    python run_tests.py --fast             # Skip slow tests
    python run_tests.py --coverage         # Run with coverage report
    python run_tests.py --verbose          # Verbose output
"""

import subprocess
import sys
import argparse
from pathlib import Path


class TestRunner:
    """Simple test runner for django-cfg."""
    
    def __init__(self):
        self.base_dir = Path(__file__).parent
        
    def run_command(self, cmd: list[str]) -> int:
        """Run command and return exit code."""
        print(f"🚀 Running: {' '.join(cmd)}")
        return subprocess.run(cmd, cwd=self.base_dir).returncode
    
    def run_all_tests(self, args) -> int:
        """Run all tests."""
        cmd = ["python", "-m", "pytest"]
        
        if args.verbose:
            cmd.append("-v")
        if args.coverage:
            cmd.extend(["--cov=django_cfg", "--cov-report=term-missing"])
        if args.fast:
            cmd.extend(["-m", "not slow"])
            
        return self.run_command(cmd)
    
    def run_unit_tests(self, args) -> int:
        """Run unit tests only."""
        cmd = ["python", "-m", "pytest", "-m", "unit", "tests/"]
        
        if args.verbose:
            cmd.append("-v")
        if args.coverage:
            cmd.extend(["--cov=django_cfg", "--cov-report=term-missing"])
            
        return self.run_command(cmd)
    
    def run_integration_tests(self, args) -> int:
        """Run integration tests only."""
        cmd = ["python", "-m", "pytest", "-m", "integration", "tests/"]
        
        if args.verbose:
            cmd.append("-v")
        if args.coverage:
            cmd.extend(["--cov=django_cfg", "--cov-report=term-missing"])
            
        return self.run_command(cmd)
    
    def run_app_tests(self, args) -> int:
        """Run app tests (accounts, support)."""
        cmd = ["python", "-m", "pytest", 
               "src/django_cfg/apps/accounts/tests/",
               "src/django_cfg/apps/support/tests/"]
        
        if args.verbose:
            cmd.append("-v")
        if args.coverage:
            cmd.extend(["--cov=django_cfg.apps", "--cov-report=term-missing"])
            
        return self.run_command(cmd)
    
    def run_core_tests(self, args) -> int:
        """Run core configuration tests."""
        cmd = ["python", "-m", "pytest", "tests/test_basic_config.py", "tests/test_limits_config.py"]
        
        if args.verbose:
            cmd.append("-v")
        if args.coverage:
            cmd.extend(["--cov=django_cfg.core", "--cov-report=term-missing"])
            
        return self.run_command(cmd)
    
    def list_tests(self) -> int:
        """List all available tests."""
        print("📋 Available test categories:")
        print("  🔧 Core Tests:")
        print("    - tests/test_basic_config.py")
        print("    - tests/test_limits_config.py")
        print("  🔗 Integration Tests:")
        print("    - tests/test_django_integration.py")
        print("    - tests/test_django_cfg_integration.py")
        print("  👤 Accounts App Tests:")
        print("    - src/django_cfg/apps/accounts/tests/")
        print("  🎫 Support App Tests:")
        print("    - src/django_cfg/apps/support/tests/")
        
        return 0


def main():
    parser = argparse.ArgumentParser(
        description="Django-CFG Test Runner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    
    # Test categories
    parser.add_argument("--unit", action="store_true", help="Run unit tests only")
    parser.add_argument("--integration", action="store_true", help="Run integration tests only")
    parser.add_argument("--apps", action="store_true", help="Run app tests (accounts, support)")
    parser.add_argument("--core", action="store_true", help="Run core configuration tests")
    
    # Options
    parser.add_argument("--fast", action="store_true", help="Skip slow tests")
    parser.add_argument("--coverage", action="store_true", help="Run with coverage report")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--list", action="store_true", help="List available tests")
    
    args = parser.parse_args()
    
    runner = TestRunner()
    
    if args.list:
        return runner.list_tests()
    
    # Determine which tests to run
    if args.unit:
        return runner.run_unit_tests(args)
    elif args.integration:
        return runner.run_integration_tests(args)
    elif args.apps:
        return runner.run_app_tests(args)
    elif args.core:
        return runner.run_core_tests(args)
    else:
        # Run all tests by default
        return runner.run_all_tests(args)


if __name__ == "__main__":
    sys.exit(main())
