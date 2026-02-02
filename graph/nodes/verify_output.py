"""Output verification node."""
from typing import Dict, Any
import re


def verify_output_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Verify formatted output meets all requirements before writing.

    Checks:
    - Required fields are populated
    - Data formats are correct
    - Coordinates are valid
    - State codes are valid
    """
    output_row = state.get('output_row', {})
    successful_rows = state.get('successful_rows', [])
    validation_errors = []

    # Check required fields
    required_fields = {
        'Premise Name': output_row.get('Premise Name'),
        'Address Line 1': output_row.get('Address Line 1'),
        'City': output_row.get('City'),
        'State': output_row.get('State'),
        'Postal Code': output_row.get('Postal Code'),
        'Status': output_row.get('Status'),
        'Latitude': output_row.get('Latitude'),
        'Longitude': output_row.get('Longitude'),
        'Premise Occupancy': output_row.get('Premise Occupancy'),
    }

    for field_name, value in required_fields.items():
        if not value or str(value).strip() == '':
            validation_errors.append(f"Missing required field: {field_name}")

    # Validate latitude/longitude
    try:
        lat = float(output_row.get('Latitude', 0))
        lng = float(output_row.get('Longitude', 0))

        if not (-90 <= lat <= 90):
            validation_errors.append(f"Invalid latitude: {lat} (must be -90 to 90)")
        if not (-180 <= lng <= 180):
            validation_errors.append(f"Invalid longitude: {lng} (must be -180 to 180)")
        if lat == 0 and lng == 0:
            validation_errors.append("Coordinates are 0,0 (likely invalid)")
    except (ValueError, TypeError):
        validation_errors.append(f"Latitude/Longitude must be valid numbers")

    # Validate state code (2 letters)
    state = output_row.get('State', '')
    if state and not re.match(r'^[A-Z]{2}$', state):
        validation_errors.append(f"Invalid state code: {state} (must be 2 uppercase letters)")

    # Validate postal code format (US ZIP)
    postal = output_row.get('Postal Code', '')
    if postal and not re.match(r'^\d{5}(-\d{4})?$', postal):
        validation_errors.append(f"Invalid postal code format: {postal}")

    # Validate status
    status = output_row.get('Status', '')
    if status not in ['Active', 'Inactive']:
        validation_errors.append(f"Invalid status: {status} (must be 'Active' or 'Inactive')")

    # Validate country
    country = output_row.get('Country', '')
    if country and country != 'USA':
        validation_errors.append(f"Invalid country: {country} (must be 'USA')")

    country_short = output_row.get('Country ShortName', '')
    if country_short and country_short != 'US':
        validation_errors.append(f"Invalid country short name: {country_short} (must be 'US')")

    # Check if validation passed
    if validation_errors:
        error_message = '; '.join(validation_errors)
        print(f"[Verify] FAILED validation: {error_message}")

        return {
            'verification_passed': False,
            'validation_errors': validation_errors,
            'next_step': 'error_handler',
            'error_message': f"Output validation failed: {error_message}",
        }
    else:
        print(f"[Verify] ✓ Output validation passed for: {output_row.get('Premise Name')}")

        # Add to successful rows after validation
        updated_successful_rows = successful_rows + [output_row]

        return {
            'successful_rows': updated_successful_rows,
            'verification_passed': True,
            'validation_errors': [],
            'next_step': 'next_row',
            'error_message': None,
        }
