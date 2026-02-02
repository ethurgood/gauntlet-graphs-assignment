"""Google Places search node."""
from typing import Dict, Any
from graph.tools import GooglePlacesTool


# Valid US state codes
VALID_US_STATE_CODES = {
    'AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'FL', 'GA',
    'HI', 'ID', 'IL', 'IN', 'IA', 'KS', 'KY', 'LA', 'ME', 'MD',
    'MA', 'MI', 'MN', 'MS', 'MO', 'MT', 'NE', 'NV', 'NH', 'NJ',
    'NM', 'NY', 'NC', 'ND', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC',
    'SD', 'TN', 'TX', 'UT', 'VT', 'VA', 'WA', 'WV', 'WI', 'WY',
    'DC'  # District of Columbia
}

# Non-business types that should be rejected from Places API results
NON_BUSINESS_TYPES = {
    'street_address', 'route', 'intersection', 'political',
    'country', 'administrative_area_level_1', 'administrative_area_level_2',
    'administrative_area_level_3', 'administrative_area_level_4',
    'administrative_area_level_5', 'locality', 'sublocality',
    'neighborhood', 'premise', 'subpremise', 'postal_code',
    'natural_feature', 'airport', 'park', 'point_of_interest'
}


def places_search_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Search for the location using Google Places API.
    Uses geocoding first to validate address and ensure location accuracy.
    """
    current_row = state.get('current_row', {})
    places_tool = GooglePlacesTool()

    # Step 1: Validate input data
    address = current_row.get('address', '')
    city = current_row.get('city', '')
    state_code = current_row.get('state', '').upper()

    if not address or not city or not state_code:
        return {
            'places_result': None,
            'places_found': False,
            'latitude': None,
            'longitude': None,
            'places_type': None,
            'next_step': 'error_handler',
            'error_message': "Incomplete address information",
        }

    # Validate state code
    if state_code not in VALID_US_STATE_CODES:
        return {
            'places_result': None,
            'places_found': False,
            'latitude': None,
            'longitude': None,
            'places_type': None,
            'next_step': 'error_handler',
            'error_message': f"Invalid US state code: {state_code}",
        }

    geocode_result = places_tool.geocode_address(address, city, state_code)

    if not geocode_result:
        # Address doesn't exist
        return {
            'places_result': None,
            'places_found': False,
            'latitude': None,
            'longitude': None,
            'places_type': None,
            'next_step': 'error_handler',
            'error_message': f"Address not found: {address}, {city}, {state_code}",
        }

    # Step 2: Search for businesses near the geocoded location
    name = current_row.get('name', '')
    query = f"{name}, {address}, {city}, {state_code}" if name else f"{address}, {city}, {state_code}"

    result = places_tool.search_place(
        query=query,
        latitude=geocode_result['latitude'],
        longitude=geocode_result['longitude']
    )

    # Check if Places result is actually near our geocoded location
    # (Places sometimes returns businesses with similar names but wrong locations)
    if result:
        places_lat = result.get('latitude')
        places_lng = result.get('longitude')
        geocode_lat = geocode_result['latitude']
        geocode_lng = geocode_result['longitude']

        # Calculate simple distance (in degrees, ~0.01 degrees = ~1km)
        if places_lat and places_lng:
            distance = ((places_lat - geocode_lat) ** 2 + (places_lng - geocode_lng) ** 2) ** 0.5
            if distance > 0.05:  # More than ~5km away
                print(f"[Places Search] Result too far from geocoded location ({distance:.4f} degrees), using geocoded data only")
                result = None

    # Use Places result if valid and nearby, otherwise use geocoded data
    if result:
        # Check if this is a real business or just a street address
        result_types = set(result.get('types', []))

        # If ALL types are non-business types, use the geocoded address with user's input
        # (This handles cases where Google finds the address but not the specific business)
        if result_types and result_types.issubset(NON_BUSINESS_TYPES):
            print(f"[Places Search] Result is address only (types: {result_types}), using geocoded data with user input")
            return {
                'places_result': {
                    'name': name,
                    'formatted_address': geocode_result['formatted_address'],
                    'latitude': geocode_result['latitude'],
                    'longitude': geocode_result['longitude'],
                    'types': ['premise'],
                    'address_components': geocode_result.get('address_components', [])
                },
                'places_found': True,
                'latitude': geocode_result['latitude'],
                'longitude': geocode_result['longitude'],
                'places_type': 'premise',
                'next_step': 'standardize',
                'error_message': None,
            }

        # Extract place type (first business type from the list)
        places_type = result.get('types', ['establishment'])[0] if result.get('types') else 'establishment'

        # Use geocoded coordinates for duplicate detection (not Places coordinates)
        # This ensures we search for duplicates at the actual address location
        return {
            'places_result': result,
            'places_found': True,
            'latitude': geocode_result['latitude'],
            'longitude': geocode_result['longitude'],
            'places_type': places_type,
            'next_step': 'standardize',
            'error_message': None,
        }
    else:
        # No business found, but address is valid - use geocoded coordinates with user input
        print(f"[Places Search] No business found, using geocoded address with user input")
        return {
            'places_result': {
                'name': name,
                'formatted_address': geocode_result['formatted_address'],
                'latitude': geocode_result['latitude'],
                'longitude': geocode_result['longitude'],
                'types': ['premise'],
                'address_components': geocode_result.get('address_components', [])
            },
            'places_found': True,
            'latitude': geocode_result['latitude'],
            'longitude': geocode_result['longitude'],
            'places_type': 'premise',
            'next_step': 'standardize',
            'error_message': None,
        }
