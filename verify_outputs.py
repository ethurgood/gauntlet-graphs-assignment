"""
Simple output verification script.
Verifies the system is working by checking the generated CSV files.
"""
import os
import csv

def verify_test(test_id, csv_file):
    """Run a test and verify output was generated."""
    # Clear outputs
    os.system('rm -f output/*.csv')

    # Run test
    os.system(f'.venv/bin/python -m graph.orchestrator {csv_file} > /dev/null 2>&1')

    # Check outputs
    has_processed = os.path.exists('output/processed_premises.csv')
    has_errors = os.path.exists('output/errors.csv')
    has_duplicates = os.path.exists('output/duplicates.csv')

    processed_count = 0
    error_count = 0
    duplicate_count = 0

    if has_processed:
        with open('output/processed_premises.csv') as f:
            processed_count = sum(1 for _ in f) - 1  # Subtract header

    if has_errors:
        with open('output/errors.csv') as f:
            error_count = sum(1 for _ in f) - 1

    if has_duplicates:
        with open('output/duplicates.csv') as f:
            duplicate_count = sum(1 for _ in f) - 1

    return {
        'processed': processed_count,
        'errors': error_count,
        'duplicates': duplicate_count
    }

# Test cases
tests = [
    ('test_01', 'golden_set/test_data/test_01_lowercase.csv', 'processed'),
    ('test_02', 'golden_set/test_data/test_02_mixedcase.csv', 'processed'),
    ('test_03', 'golden_set/test_data/test_03_slight_name_diff.csv', 'processed or duplicate'),
    ('test_04', 'golden_set/test_data/test_04_abbreviation.csv', 'processed or duplicate'),
    ('test_05', 'golden_set/test_data/test_05_different_name.csv', 'processed'),
    ('test_06', 'golden_set/test_data/test_06_rebrand.csv', 'processed'),
    ('test_07', 'golden_set/test_data/test_07_near_duplicate.csv', 'processed or duplicate'),
    ('test_08', 'golden_set/test_data/test_08_chain_location.csv', 'processed or duplicate'),
    ('test_09', 'golden_set/test_data/test_09_imaginary.csv', 'errors'),
    ('test_10', 'golden_set/test_data/test_10_fictional.csv', 'errors'),
]

print("\n" + "="*60)
print("OUTPUT VERIFICATION TEST")
print("="*60 + "\n")

passed = 0
failed = 0

for test_id, csv_file, expected in tests:
    result = verify_test(test_id, csv_file)

    # Determine if test passed based on expected output
    success = False
    if 'errors' in expected and result['errors'] > 0:
        success = True
        status = "✓"
    elif 'processed' in expected and result['processed'] > 0:
        success = True
        status = "✓"
    elif 'duplicate' in expected and result['duplicates'] > 0:
        success = True
        status = "✓"
    else:
        status = "✗"

    if success:
        passed += 1
    else:
        failed += 1

    print(f"{status} {test_id}: P={result['processed']} E={result['errors']} D={result['duplicates']} (expected: {expected})")

print(f"\n{'='*60}")
print(f"RESULTS: {passed}/{len(tests)} tests generated correct outputs")
print(f"{'='*60}\n")
