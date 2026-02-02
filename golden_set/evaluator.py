"""
Golden Set Evaluator for Premises Processing Graph.

Runs all test cases and validates outputs against expected behavior.
"""
import os
import sys
import csv
import yaml
from typing import Dict, Any, List
from dataclasses import dataclass

# Add parent directory to path so we can import graph module
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
sys.path.insert(0, project_root)

from graph.orchestrator import run_premises_processing


@dataclass
class TestResult:
    """Result of a single test case evaluation."""
    test_id: str
    passed: bool
    checks_passed: int
    checks_total: int
    failures: List[str]
    details: Dict[str, Any]


class GoldenSetEvaluator:
    """Evaluator for running and validating golden set tests."""

    def __init__(self, golden_data_path: str = None):
        """Initialize evaluator with golden data."""
        if golden_data_path is None:
            # Use path relative to this script's location
            script_dir = os.path.dirname(os.path.abspath(__file__))
            golden_data_path = os.path.join(script_dir, 'golden_data.yaml')

        with open(golden_data_path, 'r') as f:
            self.golden_data = yaml.safe_load(f)
        self.test_cases = self.golden_data['test_cases']

    def run_test_case(self, test_case: Dict[str, Any]) -> TestResult:
        """
        Run a single test case and validate results.
        """
        test_id = test_case['id']
        csv_file = test_case['file']

        print(f"\n{'='*60}")
        print(f"Running {test_id}: {test_case['description']}")
        print(f"{'='*60}")

        # Run the graph
        try:
            final_state = run_premises_processing(csv_file)
        except Exception as e:
            print(f"✗ Test {test_id} failed with exception: {e}")
            return TestResult(
                test_id=test_id,
                passed=False,
                checks_passed=0,
                checks_total=0,
                failures=[f"Exception: {str(e)}"],
                details={}
            )

        # Validate checks
        checks = test_case.get('checks', {})
        failures = []
        checks_passed = 0
        checks_total = len(checks)

        # Get output arrays from state
        error_rows = final_state.get('error_rows', [])
        duplicate_log = final_state.get('duplicate_log', [])
        successful_rows = final_state.get('successful_rows', [])

        # Infer places_found: if row NOT in error_rows, then places was found
        if 'places_found' in checks:
            expected = checks['places_found']
            actual = len(error_rows) == 0  # No errors means places were found
            if expected == actual:
                checks_passed += 1
                print(f"  ✓ places_found: {actual}")
            else:
                failures.append(f"places_found: expected {expected}, got {actual}")
                print(f"  ✗ places_found: expected {expected}, got {actual}")

        # Infer duplicate_detected: check if confidence scoring was run
        # This happens when a duplicate was found in DB (regardless of confidence score)
        if 'duplicate_detected' in checks:
            expected = checks['duplicate_detected']
            # Check metadata in successful_rows or if row is in duplicate_log
            actual = False
            if duplicate_log:
                actual = True
            elif successful_rows:
                # Check if any successful row has _duplicate_checked metadata
                for row in successful_rows:
                    if isinstance(row, dict) and row.get('_duplicate_checked'):
                        actual = True
                        break

            if expected == actual:
                checks_passed += 1
                print(f"  ✓ duplicate_detected: {actual}")
            else:
                failures.append(f"duplicate_detected: expected {expected}, got {actual}")
                print(f"  ✗ duplicate_detected: expected {expected}, got {actual}")

        # Check confidence score range
        if 'confidence_score_min' in checks or 'confidence_score_max' in checks:
            min_score = checks.get('confidence_score_min', 0)
            max_score = checks.get('confidence_score_max', 10)

            # Extract score from duplicate_log or successful_rows metadata
            score = None
            if duplicate_log:
                # Try to find score in the last duplicate log entry
                last_dup = duplicate_log[-1] if isinstance(duplicate_log[-1], dict) else None
                if last_dup and 'confidence_score' in last_dup:
                    score = last_dup['confidence_score']
            elif successful_rows:
                # Check metadata in successful_rows
                for row in successful_rows:
                    if isinstance(row, dict) and row.get('_confidence_score') is not None:
                        score = row.get('_confidence_score')
                        break

            if score is not None:
                if min_score <= score <= max_score:
                    checks_passed += 1
                    print(f"  ✓ confidence_score: {score} (within {min_score}-{max_score})")
                else:
                    failures.append(f"confidence_score: {score} not in range {min_score}-{max_score}")
                    print(f"  ✗ confidence_score: {score} not in range {min_score}-{max_score}")
            else:
                # No confidence score when duplicate not detected
                if not checks.get('duplicate_detected', False):
                    checks_passed += 1
                    print(f"  ✓ confidence_score: None (no duplicate detected)")
                else:
                    failures.append(f"confidence_score: expected score, got None")
                    print(f"  ✗ confidence_score: expected score, got None")

        if 'in_errors' in checks:
            expected = checks['in_errors']
            actual = len(error_rows) > 0
            if expected == actual:
                checks_passed += 1
                print(f"  ✓ in_errors: {actual}")
            else:
                failures.append(f"in_errors: expected {expected}, got {actual}")
                print(f"  ✗ in_errors: expected {expected}, got {actual}")

        if 'in_duplicates_log' in checks:
            expected = checks['in_duplicates_log']
            actual = len(duplicate_log) > 0
            if expected == actual:
                checks_passed += 1
                print(f"  ✓ in_duplicates_log: {actual}")
            else:
                failures.append(f"in_duplicates_log: expected {expected}, got {actual}")
                print(f"  ✗ in_duplicates_log: expected {expected}, got {actual}")

        if 'in_processed' in checks:
            expected = checks['in_processed']
            actual = len(successful_rows) > 0
            if expected == actual:
                checks_passed += 1
                print(f"  ✓ in_processed: {actual}")
            else:
                failures.append(f"in_processed: expected {expected}, got {actual}")
                print(f"  ✗ in_processed: expected {expected}, got {actual}")

        # Overall pass/fail
        passed = len(failures) == 0
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"\n{status}: {checks_passed}/{checks_total} checks passed")

        return TestResult(
            test_id=test_id,
            passed=passed,
            checks_passed=checks_passed,
            checks_total=checks_total,
            failures=failures,
            details={
                'error_rows': len(error_rows),
                'duplicate_log': len(duplicate_log),
                'successful_rows': len(successful_rows),
            }
        )

    def run_all_tests(self) -> List[TestResult]:
        """Run all test cases."""
        results = []

        for test_case in self.test_cases:
            result = self.run_test_case(test_case)
            results.append(result)

        return results

    def print_summary(self, results: List[TestResult]):
        """Print summary of all test results."""
        print(f"\n{'='*60}")
        print("GOLDEN SET EVALUATION SUMMARY")
        print(f"{'='*60}\n")

        total_tests = len(results)
        passed_tests = sum(1 for r in results if r.passed)
        total_checks = sum(r.checks_total for r in results)
        passed_checks = sum(r.checks_passed for r in results)

        print(f"Tests Passed: {passed_tests}/{total_tests} ({passed_tests/total_tests*100:.1f}%)")
        print(f"Checks Passed: {passed_checks}/{total_checks} ({passed_checks/total_checks*100:.1f}%)")

        # Category breakdown
        print(f"\n{'='*60}")
        print("BY CATEGORY")
        print(f"{'='*60}\n")

        categories = {}
        for i, test_case in enumerate(self.test_cases):
            category = test_case['category']
            if category not in categories:
                categories[category] = []
            categories[category].append(results[i])

        for category, cat_results in categories.items():
            passed = sum(1 for r in cat_results if r.passed)
            total = len(cat_results)
            print(f"{category}: {passed}/{total} passed")

        # Failed tests detail
        failed_tests = [r for r in results if not r.passed]
        if failed_tests:
            print(f"\n{'='*60}")
            print("FAILED TESTS")
            print(f"{'='*60}\n")

            for result in failed_tests:
                print(f"{result.test_id}:")
                for failure in result.failures:
                    print(f"  - {failure}")
                print()

        # Final verdict
        print(f"{'='*60}")
        if passed_tests == total_tests:
            print("✓ ALL TESTS PASSED!")
        else:
            print(f"✗ {total_tests - passed_tests} TEST(S) FAILED")
        print(f"{'='*60}\n")


def main():
    """Run golden set evaluation."""
    # Change to project root directory for correct file paths
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    os.chdir(project_root)

    evaluator = GoldenSetEvaluator()

    print("Starting Golden Set Evaluation...")
    print(f"Total test cases: {len(evaluator.test_cases)}")

    results = evaluator.run_all_tests()
    evaluator.print_summary(results)


if __name__ == '__main__':
    main()
