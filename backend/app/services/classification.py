import json
import logging
from typing import Optional
from groq import Groq
from app.config import settings

logger = logging.getLogger(__name__)


class ClassificationService:
    def __init__(self):
        self.client = Groq(api_key=settings.groq_api_key) if settings.groq_api_key else None
        self.model = settings.groq_model
        self.valid_labels = settings.classification_labels

    def _build_prompt(self, text: str) -> str:
        labels_str = ", ".join(self.valid_labels)
        return f"""You are a precise Roman Urdu sentiment classifier.

TASK: Classify the given Roman Urdu text into EXACTLY ONE label: {labels_str}.

INSTRUCTIONS:
1. Output ONLY a JSON object with exactly these keys: "label" and "confidence"
2. "label" must be one of: {labels_str}
3. "confidence" must be a number between 0.0 and 1.0
4. Do NOT include any other text, explanation, reasoning, or formatting
5. The JSON should be valid and parseable by itself

TEXT TO CLASSIFY:
{text}

OUTPUT JSON ONLY:"""

    def _parse_response(self, response_text: str) -> tuple[str, float]:
        """Parse and validate the model response."""
        # Try to find JSON object in the response
        text = response_text.strip()
        
        # Attempt 1: Direct JSON parse
        try:
            data = json.loads(text)
            label = data.get("label", "").lower().strip()
            confidence = float(data.get("confidence", 0.0))
            
            # Validate label
            if label not in self.valid_labels and label != "unclassifiable":
                logger.warning(f"Invalid label from model: {label}, defaulting to neutral")
                return "neutral", 0.5
            
            # Validate confidence
            confidence = max(0.0, min(1.0, confidence))
            
            return label, confidence
        except (json.JSONDecodeError, ValueError, KeyError):
            pass
        
        # Attempt 2: Extract JSON from text (look for { ... })
        try:
            start = text.index('{')
            end = text.rindex('}') + 1
            json_str = text[start:end]
            data = json.loads(json_str)
            label = data.get("label", "").lower().strip()
            confidence = float(data.get("confidence", 0.0))
            
            # Validate label
            if label not in self.valid_labels and label != "unclassifiable":
                logger.warning(f"Invalid label from model: {label}, defaulting to neutral")
                return "neutral", 0.5
            
            # Validate confidence
            confidence = max(0.0, min(1.0, confidence))
            
            return label, confidence
        except (json.JSONDecodeError, ValueError, KeyError, IndexError):
            pass
        
        # Attempt 3: Look for label and confidence patterns in text
        try:
            import re
            label_match = re.search(r'"label"\s*:\s*"([^"]+)"', text)
            conf_match = re.search(r'"confidence"\s*:\s*([0-9.]+)', text)
            
            if label_match and conf_match:
                label = label_match.group(1).lower().strip()
                confidence = float(conf_match.group(1))
                
                # Validate label
                if label not in self.valid_labels and label != "unclassifiable":
                    return "neutral", 0.5
                
                confidence = max(0.0, min(1.0, confidence))
                return label, confidence
        except (ValueError, IndexError, re.error):
            pass
        
        # Fallback: default to neutral
        logger.error(f"Could not parse model response: {response_text}")
        return "neutral", 0.5


classification_service = ClassificationService()