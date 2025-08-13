#!/usr/bin/env python3
"""
Master test runner for all SlideAgent test suites.

This script runs all test files in the tests directory and provides
a comprehensive test report covering all aspects of SlideAgent functionality.
"""

import sys
import os
import subprocess
from pathlib import Path


def run_test_file(test_file):
    """Run a single test file and return (success, output)"""
    try:
        # Use uv run to ensure proper environment
        result = subprocess.run(
            ["uv", "run", "python", str(test_file)],
            cwd=Path(__file__).parent.parent,  # Run from project root
            capture_output=True,
            text=True,
            timeout=120  # 2 minute timeout per test file
        )
        
        success = result.returncode == 0
        output = result.stdout + result.stderr
        
        return success, output
    
    except subprocess.TimeoutExpired:
        return False, "Test timed out after 2 minutes"
    except Exception as e:
        return False, f"Error running test: {e}"


def main():
    """Run all test files and provide comprehensive report"""
    print("SlideAgent Comprehensive Test Suite")
    print("=" * 60)
    
    # Find all test files
    tests_dir = Path(__file__).parent
    test_files = [
        tests_dir / "test_constants.py",
        tests_dir / "test_css_paths.py", 
        tests_dir / "test_template_discovery.py",
        tests_dir / "test_project_structure.py",
        tests_dir / "test_theme_management.py",
        tests_dir / "test_live_viewer.py",
        tests_dir / "test_mcp_tools.py",
        tests_dir / "test_plotbuddy.py"
    ]
    
    # Filter to existing files
    existing_test_files = [f for f in test_files if f.exists()]
    
    print(f"Found {len(existing_test_files)} test files to run:")
    for test_file in existing_test_files:
        print(f"  - {test_file.name}")
    print()
    
    # Run all tests
    results = {}
    total_tests = 0
    passed_tests = 0
    
    for test_file in existing_test_files:
        print(f"Running {test_file.name}...")
        success, output = run_test_file(test_file)
        
        results[test_file.name] = (success, output)
        
        if success:
            print(f"✅ {test_file.name} PASSED")
            passed_tests += 1
        else:
            print(f"❌ {test_file.name} FAILED")
        
        total_tests += 1
        print()
    
    # Print summary
    print("=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"Total test files: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {total_tests - passed_tests}")
    print(f"Success rate: {passed_tests/total_tests*100:.1f}%")
    print()
    
    # Print failed test details
    failed_tests = [(name, output) for name, (success, output) in results.items() if not success]
    
    if failed_tests:
        print("FAILED TEST DETAILS:")
        print("=" * 60)
        for name, output in failed_tests:
            print(f"\n{name}:")
            print("-" * 40)
            # Print last part of output (usually contains the error)
            lines = output.split('\n')
            error_lines = lines[-20:] if len(lines) > 20 else lines
            print('\n'.join(error_lines))
    
    # Print success details for passed tests
    if passed_tests > 0:
        print("\nPASSED TESTS COVERAGE:")
        print("=" * 60)
        for name, (success, output) in results.items():
            if success:
                # Extract test count from output
                lines = output.split('\n')
                summary_lines = [l for l in lines if '✅ All' in l and 'tests passed' in l]
                if summary_lines:
                    test_count = summary_lines[-1]
                    print(f"✅ {name}: {test_count.split('✅ All')[1]}")
    
    print("\n" + "=" * 60)
    if passed_tests == total_tests:
        print("🎉 ALL TESTS PASSED! SlideAgent is working correctly.")
        return 0
    else:
        print(f"⚠️  {total_tests - passed_tests} test file(s) failed. Review the details above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())