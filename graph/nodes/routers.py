"""Router functions for conditional edges."""
from typing import Dict, Any, Literal


def route_by_next_step(state: Dict[str, Any]) -> str:
    """
    Generic router that routes based on the 'next_step' field in state.

    This is the main routing mechanism for the graph.
    """
    return state.get('next_step', 'END')


def route_after_parse(state: Dict[str, Any]) -> Literal['places_search', 'write_output']:
    """Route after parsing a row."""
    next_step = state.get('next_step', 'places_search')
    if next_step == 'write_output':
        return 'write_output'
    return 'places_search'


def route_after_places(state: Dict[str, Any]) -> Literal['standardize', 'error_handler']:
    """Route after Places API search."""
    next_step = state.get('next_step', 'error_handler')
    if next_step == 'standardize':
        return 'standardize'
    return 'error_handler'


def route_after_database(state: Dict[str, Any]) -> Literal['confidence_scoring', 'occupancy_classification']:
    """Route after database query."""
    next_step = state.get('next_step', 'occupancy_classification')
    if next_step == 'confidence_scoring':
        return 'confidence_scoring'
    return 'occupancy_classification'


def route_after_confidence(state: Dict[str, Any]) -> Literal['log_duplicate', 'occupancy_classification']:
    """Route after confidence scoring."""
    next_step = state.get('next_step', 'occupancy_classification')
    if next_step == 'log_duplicate':
        return 'log_duplicate'
    return 'occupancy_classification'


def route_after_verify(state: Dict[str, Any]) -> Literal['next_row', 'error_handler']:
    """Route after output verification."""
    next_step = state.get('next_step', 'error_handler')
    if next_step == 'next_row':
        return 'next_row'
    return 'error_handler'


def route_next_row(state: Dict[str, Any]) -> Literal['parse_row', 'write_output']:
    """
    Route to either process next row or finish.

    This creates the main loop for processing multiple CSV rows.
    """
    csv_rows = state.get('csv_rows', [])
    current_index = state.get('current_row_index', 0)

    # Increment index for next iteration
    next_index = current_index + 1

    if next_index < len(csv_rows):
        # More rows to process
        return 'parse_row'
    else:
        # No more rows, write output
        return 'write_output'
