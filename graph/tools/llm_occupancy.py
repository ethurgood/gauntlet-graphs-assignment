"""
LLM Occupancy Type Classification Tool.
"""
import os
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv()


class LLMOccupancyTool:
    """
    Tool for classifying premises occupancy type based on Google Places type.
    Uses GPT-3.5-turbo for cost-efficient classification.
    """

    def __init__(self):
        """Initialize the LLM client."""
        self.llm = ChatOpenAI(
            model="gpt-3.5-turbo",
            api_key=os.getenv('OPENAI_API_KEY'),
            temperature=0,  # Deterministic for consistency
        )

    def classify_occupancy_type(
        self,
        places_type: str,
        business_name: str,
        occupancy_options: List[Dict[str, Any]]
    ) -> Optional[int]:
        """
        Classify the occupancy type for a premises location.

        Args:
            places_type: Google Places type (e.g., "restaurant", "store")
            business_name: Name of the business
            occupancy_options: List of available occupancy types with keys:
                              occupancy_type_id, occupancy_type_name

        Returns:
            Selected occupancy_type_id or None if unable to classify
        """
        if not occupancy_options:
            return None

        # Build options text
        options_text = "\n".join([
            f"- ID {opt['occupancy_type_id']}: {opt['occupancy_type_name']}"
            for opt in occupancy_options
        ])

        prompt = f"""You are classifying a premises location into an occupancy type category for fire safety regulation purposes.

Business Information:
- Name: {business_name}
- Google Places Type: {places_type}

Available Occupancy Types:
{options_text}

Select the BEST matching occupancy type ID from the list above.

Guidelines:
- Match the Google Places type to the most appropriate occupancy category
- Consider the business name for additional context
- Choose the most specific applicable category
- If multiple could apply, choose the most common/general one

Respond with ONLY the occupancy type ID number. No explanation.
"""

        try:
            response = self.llm.invoke(prompt)
            response_text = response.content.strip()

            # Extract number from response (handle various formats)
            import re
            numbers = re.findall(r'\d+', response_text)
            if numbers:
                occupancy_type_id = int(numbers[0])
            else:
                raise ValueError(f"No number found in response: {response_text}")

            # Validate that the ID is in the options
            valid_ids = [opt['occupancy_type_id'] for opt in occupancy_options]
            if occupancy_type_id in valid_ids:
                return occupancy_type_id
            else:
                print(f"LLM returned invalid occupancy type ID: {occupancy_type_id}")
                # Return first option as fallback
                return occupancy_options[0]['occupancy_type_id'] if occupancy_options else None

        except Exception as e:
            print(f"LLM Occupancy Classification error: {e}")
            # Return first option as fallback
            return occupancy_options[0]['occupancy_type_id'] if occupancy_options else None
