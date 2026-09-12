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

TASK: Classify the given Roman Urdu text and provide sentiment probabilities for each category.

INSTRUCTIONS:
1. Output ONLY a JSON object with exactly these keys: "label", "confidence", and "probabilities"
2. "label" must be one of: {labels_str}
3. "confidence" must be the probability of the chosen label, between 0.0 and 1.0
4. "probabilities" must be an object with "positive", "neutral", and "negative" keys, each a number between 0.0 and 1.0
5. The three probabilities MUST sum to 1.0 (within rounding tolerance of ±0.01)
6. Do NOT include any other text, explanation, reasoning, or formatting
7. The JSON should be valid and parseable by itself

TEXT TO CLASSIFY:
{text}

OUTPUT JSON ONLY:"""

    def _parse_response(self, response_text: str) -> tuple[str, float, dict[str, float]]:
        """Parse and validate the model response. Returns (label, confidence, probabilities)."""
        text = response_text.strip()

        default_probs = {"positive": 0.33, "neutral": 0.34, "negative": 0.33}

        def _extract(data: dict) -> tuple[str, float, dict[str, float]]:
            label = data.get("label", "").lower().strip()
            confidence = float(data.get("confidence", 0.0))

            if label not in self.valid_labels and label != "unclassifiable":
                logger.warning(f"Invalid label from model: {label}, defaulting to neutral")
                label = "neutral"
                confidence = 0.5

            confidence = max(0.0, min(1.0, confidence))

            probs = data.get("probabilities", {})
            pos = max(0.0, min(1.0, float(probs.get("positive", 0.33))))
            neu = max(0.0, min(1.0, float(probs.get("neutral", 0.34))))
            neg = max(0.0, min(1.0, float(probs.get("negative", 0.33))))

            total = pos + neu + neg
            if total > 0:
                pos /= total
                neu /= total
                neg /= total
            else:
                pos, neu, neg = 0.33, 0.34, 0.33

            return label, confidence, {"positive": round(pos, 4), "neutral": round(neu, 4), "negative": round(neg, 4)}

        # Attempt 1: Direct JSON parse
        try:
            data = json.loads(text)
            return _extract(data)
        except (json.JSONDecodeError, ValueError, KeyError):
            pass

        # Attempt 2: Extract JSON from text (look for { ... })
        try:
            start = text.index('{')
            end = text.rindex('}') + 1
            json_str = text[start:end]
            data = json.loads(json_str)
            return _extract(data)
        except (json.JSONDecodeError, ValueError, KeyError, IndexError):
            pass

        # Attempt 3: Regex extraction
        try:
            import re
            label_match = re.search(r'"label"\s*:\s*"([^"]+)"', text)
            conf_match = re.search(r'"confidence"\s*:\s*([0-9.]+)', text)

            if label_match and conf_match:
                label = label_match.group(1).lower().strip()
                confidence = float(conf_match.group(1))

                if label not in self.valid_labels and label != "unclassifiable":
                    label = "neutral"

                confidence = max(0.0, min(1.0, confidence))

                pos_match = re.search(r'"positive"\s*:\s*([0-9.]+)', text)
                neu_match = re.search(r'"neutral"\s*:\s*([0-9.]+)', text)
                neg_match = re.search(r'"negative"\s*:\s*([0-9.]+)', text)

                if pos_match and neu_match and neg_match:
                    pos = max(0.0, min(1.0, float(pos_match.group(1))))
                    neu = max(0.0, min(1.0, float(neu_match.group(1))))
                    neg = max(0.0, min(1.0, float(neg_match.group(1))))
                    total = pos + neu + neg
                    if total > 0:
                        pos /= total
                        neu /= total
                        neg /= total
                    else:
                        pos, neu, neg = 0.33, 0.34, 0.33
                    return label, confidence, {"positive": round(pos, 4), "neutral": round(neu, 4), "negative": round(neg, 4)}

                return label, confidence, default_probs
        except (ValueError, IndexError, re.error):
            pass

        # Fallback: default to neutral
        logger.error(f"Could not parse model response: {response_text}")
        return "neutral", 0.5, default_probs

    def classify(self, text: str) -> tuple[str, float, dict[str, float], str | None]:
        """Classify Roman Urdu text and return (label, confidence, probabilities, raw_output)."""
        prompt = self._build_prompt(text)
        # Use Groq client if available, otherwise use rule-based fallback
        if self.client:
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.3,
                )
                response_text = response.choices[0].message.content
            except Exception as e:
                logger.warning(f"Groq API error: {e}, using fallback")
                response_text = self._fallback_classify(text)
        else:
            response_text = self._fallback_classify(text)
        
        label, confidence, probabilities = self._parse_response(response_text)
        return label, confidence, probabilities, response_text

    def _fallback_classify(self, text: str) -> str:
        """Fallback classification when Groq API is not available."""
        text_lower = text.lower().strip()
        # Simple keyword-based fallback for Roman Urdu
        positive_words = ["achha", "achhi", "bharosa", "khush", "sukoon", "achha"]
        negative_words = ["bura", "dukh", "ro", "gum", "pareshani", "buri"]
        
        for word in positive_words:
            if word in text_lower:
                return json.dumps({"label": "positive", "confidence": 0.7, "probabilities": {"positive": 0.7, "neutral": 0.2, "negative": 0.1}})
        for word in negative_words:
            if word in text_lower:
                return json.dumps({"label": "negative", "confidence": 0.7, "probabilities": {"positive": 0.1, "neutral": 0.2, "negative": 0.7}})
        return json.dumps({"label": "neutral", "confidence": 0.5, "probabilities": {"positive": 0.15, "neutral": 0.7, "negative": 0.15}})


classification_service = ClassificationService()