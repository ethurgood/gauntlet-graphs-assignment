"""
State schema for the premises processing graph.
"""
from typing import TypedDict, Optional, List, Dict, Any


class PremiseState(TypedDict):
    """
    State object that flows through the graph.
    Tracks the current processing state for CSV row processing.
    """
    # Input
    csv_rows: List[Dict[str, str]]  # All rows from input CSV
    current_row_index: int  # Current position in CSV
    current_row: Dict[str, str]  # Current row being processed

    # Places API Results
    places_result: Optional[Dict[str, Any]]  # Full Places API response
    places_found: bool  # Whether Places API found a match
    standardized_name: str  # Standardized business name
    standardized_address: Dict[str, str]  # Parsed address components
    latitude: Optional[float]  # Latitude from Places API
    longitude: Optional[float]  # Longitude from Places API
    places_type: Optional[str]  # Google Places type (e.g., "restaurant")

    # Database Query Results
    existing_premises: List[Dict[str, Any]]  # Matching premises from DB
    duplicate_found: bool  # Whether a potential duplicate was found
    confidence_score: Optional[int]  # Confidence score 1-10
    matched_premise_id: Optional[int]  # ID of matched premise

    # Occupancy Classification
    state_id: Optional[int]  # State ID from database
    state_code: Optional[str]  # State code (e.g., "CA")
    occupancy_type_options: List[Dict[str, Any]]  # Available occupancy types
    selected_occupancy_type: Optional[Dict[str, Any]]  # Selected occupancy type

    # Output Accumulation
    output_row: Optional[Dict[str, Any]]  # Formatted row pending verification
    successful_rows: List[Dict[str, Any]]  # Successfully processed rows
    error_rows: List[Dict[str, Any]]  # Rows that encountered errors
    duplicate_log: List[Dict[str, Any]]  # High-confidence duplicates

    # Verification
    verification_passed: bool  # Whether output verification passed
    validation_errors: List[str]  # Validation error messages

    # Control Flow
    next_step: str  # Next node to execute
    error_message: Optional[str]  # Error message if processing failed
