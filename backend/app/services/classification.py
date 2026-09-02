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
        return f"""You are a sentiment classifier for Roman Urdu text (Urdu written in Latin script).

Classify the following text into EXACTLY ONE of these labels: {labels_str}

Rules:
1. Return ONLY a valid JSON object with keys: "label" and "confidence"
2. "label" must be exactly one of: {labels_str}
3. "confidence" must be a float between 0.0 and 1.0
4. If the text is empty, gibberish, or cannot be classified, return {{"label": "unclassifiable", "confidence": 0.0}}
5. Do not add any explanation, reasoning, or extra text

Text to classify:
{text}

JSON response:"""
    
    def _parse_response(self, response_text: str) -> tuple[str, float]:
        """Parse and validate the model response."""
        try:
            data = json.loads(response_text.strip())
            label = data.get("label", "").lower().strip()
            confidence = float(data.get("confidence", 0.0))
            
            # Validate label
            if label not in self.valid_labels and label != "unclassifiable":
                logger.warning(f"Invalid label from model: {label}, defaulting to neutral")
                return "neutral", 0.5
            
            # Validate confidence
            confidence = max(0.0, min(1.0, confidence))
            
            return label, confidence
            
        except (json.JSONDecodeError, ValueError, KeyError) as e:
            logger.error(f"Failed to parse model response: {response_text}, error: {e}")
            return "neutral", 0.5
    
    async def classify(self, text: str) -> tuple[str, float, str]:
        """
        Classify Roman Urdu text.
        Returns: (label, confidence, raw_output)
        """
        # Guardrail: empty or whitespace-only text
        if not text or not text.strip():
            return "unclassifiable", 0.0, "Empty input"
        
        # Guardrail: text too short (likely gibberish)
        if len(text.strip()) < 3:
            return "unclassifiable", 0.0, "Input too short"
        
        if not self.client:
            logger.warning("Groq client not configured, returning neutral")
            return "neutral", 0.5, "Groq not configured"
        
        prompt = self._build_prompt(text.strip())
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a precise sentiment classifier. Output only valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.0,
                max_tokens=100,
                response_format={"type": "json_object"}
            )
            
            raw_output = response.choices[0].message.content
            logger.info(f"Raw model output: {raw_output}")
            
            label, confidence = self._parse_response(raw_output)
            return label, confidence, raw_output
            
        except Exception as e:
            logger.error(f"Groq API error: {e}")
            return "neutral", 0.5, f"API error: {str(e)}"


classification_service = ClassificationService()