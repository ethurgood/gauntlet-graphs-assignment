"""
LangGraph orchestrator for premises processing workflow.
"""
import csv
from typing import Dict, Any, List
from langgraph.graph import StateGraph, END
from graph.state import PremiseState
from graph.nodes import (
    parse_row_node,
    places_search_node,
    error_handler_node,
    standardize_node,
    database_query_node,
    confidence_scoring_node,
    log_duplicate_node,
    occupancy_classification_node,
    format_output_node,
    verify_output_node,
    next_row_node,
    write_output_node,
    route_after_parse,
    route_after_places,
    route_after_database,
    route_after_confidence,
    route_after_verify,
    route_next_row,
)


def create_premises_graph():
    """
    Create the LangGraph workflow for premises processing.

    Graph Flow:
    1. parse_row → places_search
    2. places_search → (standardize | error_handler)
    3. standardize → database_query
    4. database_query → (confidence_scoring | occupancy_classification)
    5. confidence_scoring → (log_duplicate | occupancy_classification)
    6. occupancy_classification → format_output
    7. format_output → verify_output
    8. verify_output → (next_row | error_handler) [VALIDATION]
    9. error_handler → next_row
    10. log_duplicate → next_row
    11. next_row → (parse_row | write_output) [LOOP]
    12. write_output → END
    """
    # Create the state graph
    workflow = StateGraph(PremiseState)

    # Add all nodes
    workflow.add_node("parse_row", parse_row_node)
    workflow.add_node("places_search", places_search_node)
    workflow.add_node("error_handler", error_handler_node)
    workflow.add_node("standardize", standardize_node)
    workflow.add_node("database_query", database_query_node)
    workflow.add_node("confidence_scoring", confidence_scoring_node)
    workflow.add_node("log_duplicate", log_duplicate_node)
    workflow.add_node("occupancy_classification", occupancy_classification_node)
    workflow.add_node("format_output", format_output_node)
    workflow.add_node("verify_output", verify_output_node)
    workflow.add_node("next_row", next_row_node)
    workflow.add_node("write_output", write_output_node)

    # Set entry point
    workflow.set_entry_point("parse_row")

    # Add conditional edges (branching)
    workflow.add_conditional_edges(
        "parse_row",
        route_after_parse,
        {
            "places_search": "places_search",
            "write_output": "write_output",
        }
    )

    workflow.add_conditional_edges(
        "places_search",
        route_after_places,
        {
            "standardize": "standardize",
            "error_handler": "error_handler",
        }
    )

    workflow.add_conditional_edges(
        "database_query",
        route_after_database,
        {
            "confidence_scoring": "confidence_scoring",
            "occupancy_classification": "occupancy_classification",
        }
    )

    workflow.add_conditional_edges(
        "confidence_scoring",
        route_after_confidence,
        {
            "log_duplicate": "log_duplicate",
            "occupancy_classification": "occupancy_classification",
        }
    )

    workflow.add_conditional_edges(
        "verify_output",
        route_after_verify,
        {
            "next_row": "next_row",
            "error_handler": "error_handler",
        }
    )

    # Main loop: next_row decides whether to continue or finish
    workflow.add_conditional_edges(
        "next_row",
        route_next_row,
        {
            "parse_row": "parse_row",
            "write_output": "write_output",
        }
    )

    # Add simple edges (no branching)
    workflow.add_edge("standardize", "database_query")
    workflow.add_edge("occupancy_classification", "format_output")
    workflow.add_edge("format_output", "verify_output")
    workflow.add_edge("error_handler", "next_row")
    workflow.add_edge("log_duplicate", "next_row")
    workflow.add_edge("write_output", END)

    # Compile the graph
    return workflow.compile()


def load_csv(file_path: str) -> List[Dict[str, str]]:
    """Load CSV file and return list of row dicts."""
    with open(file_path, 'r') as f:
        reader = csv.DictReader(f)
        return list(reader)


def run_premises_processing(csv_file_path: str) -> Dict[str, Any]:
    """
    Run the complete premises processing workflow.

    Args:
        csv_file_path: Path to input CSV file

    Returns:
        Final state after processing
    """
    # Load CSV
    print(f"Loading CSV from {csv_file_path}...")
    csv_rows = load_csv(csv_file_path)
    print(f"✓ Loaded {len(csv_rows)} rows")

    # Initialize state
    initial_state = PremiseState(
        csv_rows=csv_rows,
        current_row_index=0,
        current_row={},
        places_result=None,
        places_found=False,
        standardized_name='',
        standardized_address={},
        latitude=None,
        longitude=None,
        places_type=None,
        existing_premises=[],
        duplicate_found=False,
        confidence_score=None,
        matched_premise_id=None,
        state_id=None,
        state_code=None,
        occupancy_type_options=[],
        selected_occupancy_type=None,
        output_row=None,
        successful_rows=[],
        error_rows=[],
        duplicate_log=[],
        verification_passed=False,
        validation_errors=[],
        next_step='parse_row',
        error_message=None,
    )

    # Create and run graph
    print("\nBuilding LangGraph workflow...")
    graph = create_premises_graph()
    print("✓ Graph compiled successfully")

    print("\nProcessing rows...")
    print("=" * 60)

    # Run the graph
    final_state = graph.invoke(initial_state)

    print("=" * 60)
    print("\n✓ Processing complete!")

    # Summary
    print("\nSummary:")
    print(f"  Total rows processed: {len(csv_rows)}")
    print(f"  Successful: {len(final_state.get('successful_rows', []))}")
    print(f"  Errors: {len(final_state.get('error_rows', []))}")
    print(f"  Duplicates: {len(final_state.get('duplicate_log', []))}")

    return final_state


if __name__ == "__main__":
    # Example usage
    import sys

    if len(sys.argv) > 1:
        csv_path = sys.argv[1]
    else:
        print("Usage: python -m graph.orchestrator <csv_file_path>")
        print("\nExample: python -m graph.orchestrator golden_set/test_data/test_01_lowercase.csv")
        sys.exit(1)

    run_premises_processing(csv_path)
