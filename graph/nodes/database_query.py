"""Database query node for duplicate detection."""
from typing import Dict, Any
from graph.tools import LIVDatabaseTool


def database_query_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Query database for existing premises at the same location.

    Searches by latitude/longitude within a small radius.
    """
    latitude = state.get('latitude')
    longitude = state.get('longitude')
    standardized_address = state.get('standardized_address', {})
    state_code = standardized_address.get('state_code', '')

    # Get state_id from database
    db_tool = LIVDatabaseTool()

    state_id = None
    if state_code:
        state_record = db_tool.get_state_by_code(state_code)
        if not state_record:
            # Try by full name
            state_name = standardized_address.get('state', '')
            if state_name:
                state_record = db_tool.get_state_by_name(state_name)

        if state_record:
            state_id = state_record['id']

    # Query for nearby premises
    existing_premises = []
    if latitude and longitude:
        print(f"[DB Query] Searching for premises near {latitude},{longitude} (radius: 0.001 degrees)")
        existing_premises = db_tool.query_premises_by_location(
            latitude=latitude,
            longitude=longitude,
            state_id=state_id,
            radius_degrees=0.001  # ~100m radius
        )
        print(f"[DB Query] Found {len(existing_premises)} existing premises")
        for p in existing_premises:
            print(f"[DB Query]   - {p.get('premise_name')} at {p.get('address_line_1')}")

    if existing_premises:
        return {
            'existing_premises': existing_premises,
            'duplicate_found': True,
            'state_id': state_id,
            'state_code': state_code,
            'next_step': 'confidence_scoring',
            'error_message': None,
        }
    else:
        return {
            'existing_premises': [],
            'duplicate_found': False,
            'state_id': state_id,
            'state_code': state_code,
            'next_step': 'occupancy_classification',
            'error_message': None,
        }
