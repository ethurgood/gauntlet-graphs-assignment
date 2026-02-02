"""Parse CSV row node."""
from typing import Dict, Any


def parse_row_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Parse the current CSV row and normalize field names.

    Handles arbitrary column order by looking for common variations of field names.
    """
    csv_rows = state.get('csv_rows', [])
    current_index = state.get('current_row_index', 0)

    if current_index >= len(csv_rows):
        # No more rows to process
        return {
            'next_step': 'write_output',
            'error_message': None,
        }

    raw_row = csv_rows[current_index]

    # Normalize field names (handle various column name formats)
    normalized_row = {}

    # Name field variations
    for key in raw_row.keys():
        key_lower = key.lower().strip()
        if any(name in key_lower for name in ['premise_name', 'business_name', 'company_name', 'facility_name', 'location_name']) or (key_lower == 'name' or key_lower == 'business'):
            normalized_row['name'] = raw_row[key].strip()
        elif any(addr in key_lower for addr in ['address', 'street', 'location']) and 'name' not in key_lower:
            normalized_row['address'] = raw_row[key].strip()
        elif any(city in key_lower for city in ['city', 'municipality', 'town']):
            normalized_row['city'] = raw_row[key].strip()
        elif 'state' in key_lower or key_lower == 'st':
            normalized_row['state'] = raw_row[key].strip()
        elif 'postal' in key_lower or 'zip' in key_lower:
            normalized_row['postal_code'] = raw_row[key].strip()

    # Ensure all required fields exist (with defaults)
    normalized_row.setdefault('name', '')
    normalized_row.setdefault('address', '')
    normalized_row.setdefault('city', '')
    normalized_row.setdefault('state', '')
    normalized_row.setdefault('postal_code', '')

    return {
        'current_row': normalized_row,
        'current_row_index': current_index,
        'next_step': 'places_search',
        'error_message': None,
    }
