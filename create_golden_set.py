"""
Script to create golden set test CSVs from real database data.
"""
import csv
import random
from graph.tools import LIVDatabaseTool


def get_real_premises_samples():
    """Get 8 real premises from the database."""
    db = LIVDatabaseTool()
    connection = db._get_connection()

    try:
        with connection.cursor() as cursor:
            # Get a diverse sample of premises from California
            query = """
                SELECT
                    p.id,
                    p.premise_name,
                    p.address_line_1,
                    p.latitude,
                    p.longitude,
                    c.name as city_name,
                    s.state_code
                FROM premises p
                LEFT JOIN cities c ON p.city_id = c.id
                LEFT JOIN states s ON p.state_id = s.id
                WHERE p.deleted_at IS NULL
                    AND p.latitude IS NOT NULL
                    AND p.longitude IS NOT NULL
                    AND p.premise_name IS NOT NULL
                    AND p.address_line_1 IS NOT NULL
                    AND s.state_code = 'CA'
                ORDER BY RAND()
                LIMIT 8
            """
            cursor.execute(query)
            results = cursor.fetchall()
            return results
    finally:
        connection.close()


def create_test_csv(filename, data, column_order=None):
    """
    Create a test CSV file with specified data and column order.

    Args:
        filename: Output filename
        data: List of row dicts
        column_order: Optional list of column names in desired order
    """
    if not data:
        print(f"Warning: No data for {filename}")
        return

    # Default column order
    if column_order is None:
        column_order = ['name', 'address', 'city', 'state']

    with open(filename, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=column_order)
        writer.writeheader()
        writer.writerows(data)

    print(f"✓ Created {filename} with {len(data)} rows")


def main():
    """Create all 10 golden set test CSV files."""
    print("Querying database for real premises...")
    samples = get_real_premises_samples()

    if len(samples) < 8:
        print(f"Warning: Only got {len(samples)} samples from database")

    premises_ids = []

    # Category 1: Case Normalization (test_01, test_02)
    # Use lowercase names
    if len(samples) >= 2:
        test_01_data = [{
            'name': samples[0]['premise_name'].lower(),  # lowercase
            'address': samples[0]['address_line_1'],
            'city': samples[0]['city_name'] or 'Unknown',
            'state': samples[0]['state_code'],
        }]
        create_test_csv(
            'golden_set/test_data/test_01_lowercase.csv',
            test_01_data,
            column_order=['name', 'address', 'city', 'state']
        )
        premises_ids.append(samples[0]['id'])

        # Mixed case
        test_02_data = [{
            'business_name': samples[1]['premise_name'].upper(),  # UPPERCASE
            'street': samples[1]['address_line_1'],
            'city_name': samples[1]['city_name'] or 'Unknown',
            'state_code': samples[1]['state_code'],
        }]
        create_test_csv(
            'golden_set/test_data/test_02_mixedcase.csv',
            test_02_data,
            column_order=['business_name', 'street', 'city_name', 'state_code']
        )
        premises_ids.append(samples[1]['id'])

    # Category 2: High Confidence Duplicates (test_03, test_04)
    # Slight name variations
    if len(samples) >= 4:
        # Add " Inc" to name
        test_03_data = [{
            'premise_name': samples[2]['premise_name'] + " Inc",
            'address_line_1': samples[2]['address_line_1'],
            'municipality': samples[2]['city_name'] or 'Unknown',
            'state': samples[2]['state_code'],
        }]
        create_test_csv(
            'golden_set/test_data/test_03_slight_name_diff.csv',
            test_03_data,
            column_order=['premise_name', 'address_line_1', 'municipality', 'state']
        )
        # DON'T add to premises_ids - this is a duplicate

        # Abbreviation
        test_04_data = [{
            'location_name': samples[3]['premise_name'].replace('Street', 'St').replace('Avenue', 'Ave'),
            'street_address': samples[3]['address_line_1'],
            'city': samples[3]['city_name'] or 'Unknown',
            'state_name': samples[3]['state_code'],
        }]
        create_test_csv(
            'golden_set/test_data/test_04_abbreviation.csv',
            test_04_data,
            column_order=['location_name', 'street_address', 'city', 'state_name']
        )
        # DON'T add to premises_ids - this is a duplicate

    # Category 3: Low Confidence Matches (test_05, test_06)
    # Very different names (simulated rebrands)
    if len(samples) >= 6:
        test_05_data = [{
            'name': 'New Business Name LLC',  # Completely different name
            'address': samples[4]['address_line_1'],
            'city': samples[4]['city_name'] or 'Unknown',
            'state': samples[4]['state_code'],
        }]
        create_test_csv(
            'golden_set/test_data/test_05_different_name.csv',
            test_05_data,
            column_order=['name', 'address', 'city', 'state']
        )
        premises_ids.append(samples[4]['id'])

        test_06_data = [{
            'business': 'Rebrand Corp',  # Another different name
            'location': samples[5]['address_line_1'],
            'town': samples[5]['city_name'] or 'Unknown',
            'st': samples[5]['state_code'],
        }]
        create_test_csv(
            'golden_set/test_data/test_06_rebrand.csv',
            test_06_data,
            column_order=['business', 'location', 'town', 'st']
        )
        premises_ids.append(samples[5]['id'])

    # Category 4: Potential Duplicates (test_07, test_08)
    # These should score 6-7 confidence
    if len(samples) >= 8:
        test_07_data = [{
            'name': samples[6]['premise_name'] + ' - Branch',
            'address': samples[6]['address_line_1'],
            'city': samples[6]['city_name'] or 'Unknown',
            'state': samples[6]['state_code'],
        }]
        create_test_csv(
            'golden_set/test_data/test_07_near_duplicate.csv',
            test_07_data,
            column_order=['name', 'address', 'city', 'state']
        )
        # DON'T add - this is flagged as potential duplicate

        test_08_data = [{
            'facility_name': samples[7]['premise_name'] + ' Location',
            'street': samples[7]['address_line_1'],
            'city': samples[7]['city_name'] or 'Unknown',
            'state': samples[7]['state_code'],
        }]
        create_test_csv(
            'golden_set/test_data/test_08_chain_location.csv',
            test_08_data,
            column_order=['facility_name', 'street', 'city', 'state']
        )
        # DON'T add - this is flagged as potential duplicate

    # Category 5: Imaginary Locations (test_09, test_10)
    # These won't match in Google Places API
    test_09_data = [{
        'company_name': 'Acme Corp Headquarters',
        'address': '123 Fake Street',
        'city': 'Nowhereville',
        'state': 'XX',
    }]
    create_test_csv(
        'golden_set/test_data/test_09_imaginary.csv',
        test_09_data,
        column_order=['company_name', 'address', 'city', 'state']
    )

    test_10_data = [{
        'name': 'Fictional Industries Inc',
        'street': '999 Imaginary Lane',
        'municipality': 'Fantasyland',
        'st': 'ZZ',
    }]
    create_test_csv(
        'golden_set/test_data/test_10_fictional.csv',
        test_10_data,
        column_order=['name', 'street', 'municipality', 'st']
    )

    # Create premises_ids_to_delete.txt
    with open('golden_set/premises_ids_to_delete.txt', 'w') as f:
        f.write('# Premise IDs used in golden set test CSVs\n')
        f.write('# Mark these as deleted in the database to avoid duplicates\n')
        f.write('# Note: IDs for duplicate test cases are NOT included\n\n')
        for pid in premises_ids:
            f.write(f"{pid}\n")

    print(f"\n✓ Created premises_ids_to_delete.txt with {len(premises_ids)} IDs")
    print("\nGolden set creation complete!")
    print(f"Total test files: 10")
    print(f"Real premises used: {len(samples)}")
    print(f"IDs to mark as deleted: {len(premises_ids)}")


if __name__ == '__main__':
    main()
