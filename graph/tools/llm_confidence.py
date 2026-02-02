"""
LLM Confidence Scoring Tool for duplicate detection.
"""
import os
from typing import Dict, Any
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv()


class LLMConfidenceTool:
    """
    Tool for scoring confidence that two premises records represent the same location.
    Uses GPT-4 for semantic similarity assessment.
    """

    def __init__(self):
        """Initialize the LLM client."""
        self.llm = ChatOpenAI(
            model="gpt-4",
            api_key=os.getenv('OPENAI_API_KEY'),
            temperature=0,  # Deterministic for consistency
        )

    def score_duplicate_confidence(
        self,
        new_record: Dict[str, Any],
        existing_record: Dict[str, Any]
    ) -> int:
        """
        Score the confidence that two records represent the same physical location.

        Args:
            new_record: New premise record with keys: name, address_line_1, city, state
            existing_record: Existing premise record from database

        Returns:
            Confidence score from 1-10 (10 = definitely same location)
        """
        prompt = f"""You are comparing a new premises record against an existing database record to determine if they represent the SAME BUSINESS.

IMPORTANT: These records are already at the same/nearby location (within 100 meters). Your job is to determine if they represent the SAME BUSINESS or DIFFERENT businesses at the same location.

New Record:
- Name: {new_record.get('name', 'N/A')}
- Address: {new_record.get('address_line_1', 'N/A')}
- City: {new_record.get('city', 'N/A')}
- State: {new_record.get('state', 'N/A')}

Existing Record (from database):
- Name: {existing_record.get('premise_name', 'N/A')}
- Address: {existing_record.get('address_line_1', 'N/A')}

Rate the confidence (1-10) that these are the SAME BUSINESS (not just same location):

SCORING RULES (NAME IS THE PRIMARY FACTOR):
- 10: Exact name match or trivial variations (capitalization, punctuation, "Inc" vs "LLC")
- 8-9: Clearly the same business with minor name variations (abbreviations like "St" vs "Street", "&" vs "and")
- 6-7: Possibly same business with location/branch suffixes ("Main St Store" vs "Main St Store - Branch", "Nike" vs "Nike Location")
- 5-6: Possibly same business (partial name match, could be rebrand or acquisition)
- 4-5: Probably different businesses (significantly different names, same location)
- 1-3: Definitely different businesses (completely different names)

CRITICAL RULES:
- Score 8+ ONLY if the business names are clearly variations of the SAME business name
- Location/branch suffixes ("- Branch", " Location", " #2", " Downtown") should score 6-7, NOT 8+
- Different business names at the same address = score 1-7, NOT 8+
- Examples of score 1-3: "McDonald's" vs "Starbucks", "Take Maru Sushi" vs "New Business LLC"
- Examples of score 6-7: "Nike Store" vs "Nike Store - Branch", "Starbucks" vs "Starbucks Downtown"
- Examples of score 8+: "McDonald's Restaurant" vs "McDonalds", "Nike Inc" vs "Nike LLC"

Respond with ONLY a single number from 1-10. No explanation.
"""

        try:
            response = self.llm.invoke(prompt)
            score_text = response.content.strip()

            # Extract number from response (handle various formats)
            import re
            numbers = re.findall(r'\d+', score_text)
            if numbers:
                score = int(numbers[0])
            else:
                raise ValueError(f"No number found in response: {score_text}")

            # Validate range
            if score < 1:
                score = 1
            elif score > 10:
                score = 10

            return score

        except Exception as e:
            print(f"LLM Confidence Scoring error: {e}")
            # Conservative default: low confidence on error
            return 3
