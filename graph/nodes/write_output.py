"""Write output CSVs node."""
import os
import csv
from typing import Dict, Any


def write_output_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Write output CSVs for successful rows, errors, and duplicates.

    Creates three output files:
    - output/processed_premises.csv: Successfully processed rows
    - output/errors.csv: Rows that encountered errors
    - output/duplicates.csv: High-confidence duplicate matches
    """
    successful_rows = state.get('successful_rows', [])
    error_rows = state.get('error_rows', [])
    duplicate_log = state.get('duplicate_log', [])

    # Ensure output directory exists
    os.makedirs('output', exist_ok=True)

    # Write successful rows
    if successful_rows:
        with open('output/processed_premises.csv', 'w', newline='') as f:
            fieldnames = successful_rows[0].keys()
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(successful_rows)
        print(f"✓ Wrote {len(successful_rows)} successful rows to output/processed_premises.csv")
    else:
        print("⚠ No successful rows to write")

    # Write error rows
    if error_rows:
        with open('output/errors.csv', 'w', newline='') as f:
            fieldnames = error_rows[0].keys()
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(error_rows)
        print(f"✓ Wrote {len(error_rows)} error rows to output/errors.csv")
    else:
        print("✓ No errors encountered")

    # Write duplicate log
    if duplicate_log:
        with open('output/duplicates.csv', 'w', newline='') as f:
            fieldnames = duplicate_log[0].keys()
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(duplicate_log)
        print(f"✓ Wrote {len(duplicate_log)} duplicates to output/duplicates.csv")
    else:
        print("✓ No duplicates detected")

    return {
        'next_step': 'END',
        'error_message': None,
    }
