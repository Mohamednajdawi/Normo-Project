import json
import re
from typing import Any, Dict, Optional


def extract_json(text: str) -> Optional[Dict[str, Any]]:
    """
    Extract JSON from a string, handling common LLM response patterns.

    Args:
        text: Input string that may contain JSON

    Returns:
        Parsed JSON as dict, or None if no valid JSON found
    """
    if not text:
        return None

    # Clean the text
    text = text.strip()

    # Try to parse the entire string first
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Look for JSON in code blocks: ```json {...} ```
    json_block_match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    if json_block_match:
        try:
            return json.loads(json_block_match.group(1))
        except json.JSONDecodeError:
            pass

    # Look for standalone JSON object in the text
    json_match = re.search(r"\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}", text)
    if json_match:
        try:
            candidate = json_match.group(0)
            # Fix common trailing comma issues
            candidate = re.sub(r",\s*([}\]])", r"\1", candidate)
            return json.loads(candidate)
        except json.JSONDecodeError:
            pass

    return None
