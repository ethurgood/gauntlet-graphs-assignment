"""Error handler node for failed processing."""
from typing import Dict, Any


def error_handler_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handle rows that encountered errors during processing.
    Accumulates error rows for later output.
    """
    current_row = state.get('current_row', {})
    error_message = state.get('error_message', 'Unknown error')
    error_rows = state.get('error_rows', [])

    # Add to error list with reason
    error_entry = {
        **current_row,
        'error_reason': error_message,
    }
    error_rows.append(error_entry)

    # Move to next row
    return {
        'error_rows': error_rows,
        'next_step': 'next_row',
        'error_message': None,  # Clear error for next row
    }
