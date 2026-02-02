"""Log duplicate node."""
from typing import Dict, Any


def log_duplicate_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Log high-confidence duplicate matches.

    These records will NOT be inserted as new premises.
    """
    current_row = state.get('current_row', {})
    standardized_name = state.get('standardized_name', '')
    matched_premise_id = state.get('matched_premise_id')
    confidence_score = state.get('confidence_score')
    duplicate_log = state.get('duplicate_log', [])

    # Create duplicate log entry
    duplicate_entry = {
        'source_name': current_row.get('name', ''),
        'source_address': current_row.get('address', ''),
        'standardized_name': standardized_name,
        'matched_premise_id': matched_premise_id,
        'confidence_score': confidence_score,
        'reason': f'High confidence match (score: {confidence_score})',
    }

    duplicate_log.append(duplicate_entry)

    # Skip to next row (don't insert)
    return {
        'duplicate_log': duplicate_log,
        'next_step': 'next_row',
        'error_message': None,
    }
