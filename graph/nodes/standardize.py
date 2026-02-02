"""Standardize name and address node."""
from typing import Dict, Any
from graph.tools import GooglePlacesTool


def standardize_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Standardize business name and address format.

    Uses Google Places data if available, otherwise applies title case.
    """
    current_row = state.get('current_row', {})
    places_result = state.get('places_result')
    places_found = state.get('places_found', False)

    if places_found and places_result:
        # Use Google Places standardized name
        places_name = places_result.get('name', '').strip()
        original_name = current_row.get('name', '').strip()

        # Check if Places returned an address instead of a business name
        # (addresses typically start with numbers)
        import re
        if places_name and re.match(r'^\d+\s', places_name):
            # Places returned an address, use original name with title case
            standardized_name = original_name.title() if original_name else places_name
            print(f"[Standardize] Places returned address '{places_name}', using original name: '{standardized_name}'")
        else:
            # Use Places name if it looks like a business name
            standardized_name = places_name if places_name else original_name.title()

        # Remove duplicate spaces
        standardized_name = re.sub(r'\s+', ' ', standardized_name)

        # Parse address components
        places_tool = GooglePlacesTool()
        address_components = places_result.get('address_components', [])
        parsed_address = places_tool.parse_address_components(address_components)

        # Use formatted address from Places API
        formatted_addr = places_result.get('formatted_address', '')
        if not parsed_address.get('address_line_1'):
            parsed_address['address_line_1'] = formatted_addr.split(',')[0] if formatted_addr else ''

        standardized_address = {
            'address_line_1': parsed_address.get('address_line_1', current_row.get('address', '')),
            'city': parsed_address.get('city', current_row.get('city', '')),
            'state': parsed_address.get('state', current_row.get('state', '')),
            'state_code': parsed_address.get('state_code', current_row.get('state', '')),
            'postal_code': parsed_address.get('postal_code', current_row.get('postal_code', '')),
        }
    else:
        # No Places match - apply title case to name
        import re
        standardized_name = current_row.get('name', '').title()
        # Remove duplicate spaces
        standardized_name = re.sub(r'\s+', ' ', standardized_name)

        standardized_address = {
            'address_line_1': current_row.get('address', ''),
            'city': current_row.get('city', ''),
            'state': current_row.get('state', ''),
            'state_code': current_row.get('state', ''),  # Assume 2-letter code
            'postal_code': current_row.get('postal_code', ''),
        }

    return {
        'standardized_name': standardized_name,
        'standardized_address': standardized_address,
        'next_step': 'database_query',
        'error_message': None,
    }
