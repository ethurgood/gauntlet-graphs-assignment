"""Next row node for incrementing row index."""
from typing import Dict, Any


def next_row_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Increment row index and prepare for next iteration.

    This node is called after a row is fully processed (successfully or with error).
    """
    current_index = state.get('current_row_index', 0)

    return {
        'current_row_index': current_index + 1,
        'current_row': {},  # Clear current row
        'places_result': None,  # Clear Places result
        'places_found': False,
        'existing_premises': [],  # Clear database results
        'confidence_score': None,
        'matched_premise_id': None,
        'next_step': 'parse_row',  # Will be routed by route_next_row
        'error_message': None,
    }
