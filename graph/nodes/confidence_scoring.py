"""Confidence scoring node for duplicate detection."""
from typing import Dict, Any
from graph.tools import LLMConfidenceTool


def confidence_scoring_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Score confidence that new record matches existing database record.

    Uses LLM to assess semantic similarity.
    """
    standardized_name = state.get('standardized_name', '')
    standardized_address = state.get('standardized_address', {})
    existing_premises = state.get('existing_premises', [])
    current_row = state.get('current_row', {})

    if not existing_premises:
        # No duplicates found, proceed to occupancy classification
        return {
            'confidence_score': None,
            'matched_premise_id': None,
            'next_step': 'occupancy_classification',
            'error_message': None,
        }

    # Compare against first (closest) existing premise
    existing = existing_premises[0]

    # Use ORIGINAL user input name for comparison, not standardized
    # This preserves suffixes like "- Branch" or " Location" that indicate user intent
    original_name = current_row.get('name', '').strip()

    new_record = {
        'name': original_name or standardized_name,  # Fallback to standardized if no original
        'address_line_1': standardized_address.get('address_line_1', ''),
        'city': standardized_address.get('city', ''),
        'state': standardized_address.get('state', ''),
    }

    # Use LLM to score confidence
    llm_tool = LLMConfidenceTool()
    confidence_score = llm_tool.score_duplicate_confidence(new_record, existing)

    comparison_name = original_name or standardized_name
    print(f"[Confidence] Comparing '{comparison_name}' vs '{existing.get('premise_name')}'")
    print(f"[Confidence] Score: {confidence_score}/10 (threshold: 8)")

    # High confidence threshold: 8 or higher
    if confidence_score >= 8:
        next_step = 'log_duplicate'
        print(f"[Confidence] HIGH confidence - marking as duplicate")
    else:
        next_step = 'occupancy_classification'
        print(f"[Confidence] LOW confidence - treating as new record")

    return {
        'confidence_score': confidence_score,
        'matched_premise_id': existing.get('id'),
        'next_step': next_step,
        'error_message': None,
    }
