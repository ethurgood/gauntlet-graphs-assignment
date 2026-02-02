"""Occupancy type classification node."""
from typing import Dict, Any
from graph.tools import LIVDatabaseTool, LLMOccupancyTool


def occupancy_classification_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Classify occupancy type using LLM and database options.

    Filters occupancy types by state, then uses LLM to select best match.
    """
    state_code = state.get('state_code', '')
    places_type = state.get('places_type', 'establishment')
    standardized_name = state.get('standardized_name', '')

    # Get valid occupancy types for this state
    db_tool = LIVDatabaseTool()
    occupancy_options = []

    if state_code:
        occupancy_options = db_tool.get_occupancy_types_by_state(state_code)

    if not occupancy_options:
        # No occupancy types found for state - skip classification
        return {
            'occupancy_type_options': [],
            'selected_occupancy_type': None,
            'next_step': 'format_output',
            'error_message': 'No occupancy types available for state',
        }

    # Use LLM to classify
    llm_tool = LLMOccupancyTool()
    selected_id = llm_tool.classify_occupancy_type(
        places_type=places_type,
        business_name=standardized_name,
        occupancy_options=occupancy_options
    )

    # Find the selected occupancy type details
    selected_occupancy = None
    if selected_id:
        for opt in occupancy_options:
            if opt['occupancy_type_id'] == selected_id:
                selected_occupancy = opt
                break

    return {
        'occupancy_type_options': occupancy_options,
        'selected_occupancy_type': selected_occupancy,
        'next_step': 'format_output',
        'error_message': None,
    }
