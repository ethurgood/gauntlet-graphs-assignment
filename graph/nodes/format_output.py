"""Format output CSV row node."""
from typing import Dict, Any


def format_output_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Format processed data into output CSV row matching sample.csv schema.

    Generates a row with all required fields for the output CSV.
    """
    current_row = state.get('current_row', {})
    standardized_name = state.get('standardized_name', '')
    standardized_address = state.get('standardized_address', {})
    latitude = state.get('latitude')
    longitude = state.get('longitude')
    selected_occupancy = state.get('selected_occupancy_type')
    state_code = state.get('state_code', '')
    confidence_score = state.get('confidence_score')  # For evaluation tracking
    successful_rows = state.get('successful_rows', [])

    # Map to sample.csv schema (32 columns)
    output_row = {
        'Id': '',  # Will be assigned by database
        'Reference Number': '',  # Will be generated
        'Unique Reference Number': '',  # Will be generated
        'Building Number': '',
        'Premise Name': standardized_name,
        'Address Line 1': standardized_address.get('address_line_1', ''),
        'Address Line 2': '',
        'Postal Code': standardized_address.get('postal_code', ''),
        'Status': 'Active',
        'AHJ Name': '',  # Could be populated from occupancy type's AHJ
        'AHJ Geofence Name': '',
        'Record Type': 'Standard',
        'Country': 'USA',
        'State': state_code or standardized_address.get('state_code', ''),
        'City': standardized_address.get('city', ''),
        'System Type': '',
        'Internal System Type': '',
        'Preferred Communication Type': 'Email',
        'Parent Premises': '',
        'Premise Occupancy': selected_occupancy['occupancy_type_name'] if selected_occupancy else '',
        'Contact Name': '',
        'Contact Email': '',
        'Contact Number': '',
        'Latitude': str(latitude) if latitude else '',
        'Longitude': str(longitude) if longitude else '',
        'Fire Station Number': '',
        'Has Knox Box': 'No',
        'Knox Box Location': '',
        'Knox Box Description': '',
        'Enable Geofence Auto Assign': 'No',
        'Country ShortName': 'US',
        'Parent Reference': '',
        'Labels': '',
        # Metadata for evaluation (not written to CSV)
        '_confidence_score': confidence_score,  # Track if duplicate was checked
        '_duplicate_checked': confidence_score is not None,  # Whether we ran confidence scoring
    }

    # Don't add to successful_rows yet - verify_output will do that after validation
    return {
        'output_row': output_row,
        'next_step': 'verify_output',
        'error_message': None,
    }
