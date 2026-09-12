import json
import pytest
from unittest.mock import MagicMock, patch
from app.services.classification import ClassificationService


@pytest.fixture
def service():
    """Create a ClassificationService instance with mocked Groq client."""
    with patch('app.services.classification.settings') as mock_settings:
        mock_settings.groq_api_key = "test-key"
        mock_settings.groq_model = "test-model"
        mock_settings.classification_labels = ["positive", "negative", "neutral"]
        svc = ClassificationService()
        svc.client = MagicMock()
        yield svc


class TestParseResponse:
    """Tests for the _parse_response method."""

    def test_parse_valid_json(self, service):
        response = '{"label": "positive", "confidence": 0.9, "probabilities": {"positive": 0.9, "neutral": 0.05, "negative": 0.05}}'
        label, confidence, probs = service._parse_response(response)
        assert label == "positive"
        assert confidence == 0.9
        assert probs["positive"] == 0.9
        assert probs["neutral"] == 0.05
        assert probs["negative"] == 0.05

    def test_parse_json_with_extra_text(self, service):
        response = 'Here is the result: {"label": "negative", "confidence": 0.8, "probabilities": {"positive": 0.05, "neutral": 0.15, "negative": 0.8}} hope this helps'
        label, confidence, probs = service._parse_response(response)
        assert label == "negative"
        assert confidence == 0.8
        assert probs["negative"] == 0.8

    def test_parse_json_with_newlines(self, service):
        response = '```\n{"label": "neutral", "confidence": 0.6, "probabilities": {"positive": 0.1, "neutral": 0.8, "negative": 0.1}}\n```'
        label, confidence, probs = service._parse_response(response)
        assert label == "neutral"
        assert confidence == 0.6

    def test_parse_invalid_label_defaults_to_neutral(self, service):
        response = '{"label": "invalid_label", "confidence": 0.9, "probabilities": {"positive": 0.9, "neutral": 0.05, "negative": 0.05}}'
        label, confidence, probs = service._parse_response(response)
        assert label == "neutral"
        assert confidence == 0.5

    def test_parse_confidence_clamped_above_one(self, service):
        response = '{"label": "positive", "confidence": 1.5, "probabilities": {"positive": 1.0, "neutral": 0.0, "negative": 0.0}}'
        label, confidence, probs = service._parse_response(response)
        assert confidence == 1.0

    def test_parse_confidence_clamped_below_zero(self, service):
        response = '{"label": "positive", "confidence": -0.5, "probabilities": {"positive": 0.5, "neutral": 0.3, "negative": 0.2}}'
        label, confidence, probs = service._parse_response(response)
        assert confidence == 0.0

    def test_parse_completely_invalid_returns_neutral(self, service):
        response = 'This is not JSON at all'
        label, confidence, probs = service._parse_response(response)
        assert label == "neutral"
        assert confidence == 0.5
        assert "positive" in probs
        assert "neutral" in probs
        assert "negative" in probs

    def test_parse_empty_string_returns_neutral(self, service):
        label, confidence, probs = service._parse_response('')
        assert label == "neutral"
        assert confidence == 0.5

    def test_parse_regex_fallback_extracts_label_and_confidence(self, service):
        response = '"label": "positive", "confidence": 0.75, "positive": 0.75, "neutral": 0.15, "negative": 0.10'
        label, confidence, probs = service._parse_response(response)
        assert label == "positive"
        assert confidence == 0.75

    def test_parse_case_insensitive_label(self, service):
        response = '{"label": "POSITIVE", "confidence": 0.8, "probabilities": {"positive": 0.8, "neutral": 0.1, "negative": 0.1}}'
        label, confidence, probs = service._parse_response(response)
        assert label == "positive"

    def test_parse_label_with_whitespace(self, service):
        response = '{"label": "  negative  ", "confidence": 0.7, "probabilities": {"positive": 0.1, "neutral": 0.2, "negative": 0.7}}'
        label, confidence, probs = service._parse_response(response)
        assert label == "negative"

    def test_parse_probabilities_normalized(self, service):
        response = '{"label": "positive", "confidence": 0.9, "probabilities": {"positive": 2.0, "neutral": 0.5, "negative": 0.5}}'
        label, confidence, probs = service._parse_response(response)
        total = probs["positive"] + probs["neutral"] + probs["negative"]
        assert abs(total - 1.0) < 0.01

    def test_parse_missing_probabilities_uses_defaults(self, service):
        response = '{"label": "positive", "confidence": 0.9}'
        label, confidence, probs = service._parse_response(response)
        assert label == "positive"
        assert confidence == 0.9
        assert "positive" in probs
        assert "neutral" in probs
        assert "negative" in probs


class TestBuildPrompt:
    """Tests for the _build_prompt method."""

    def test_prompt_contains_text(self, service):
        prompt = service._build_prompt("yeh bahut acha hai")
        assert "yeh bahut acha hai" in prompt

    def test_prompt_contains_valid_labels(self, service):
        prompt = service._build_prompt("test")
        assert "positive" in prompt
        assert "negative" in prompt
        assert "neutral" in prompt

    def test_prompt_requests_json_output(self, service):
        prompt = service._build_prompt("test")
        assert "JSON" in prompt.upper()

    def test_prompt_requests_probabilities(self, service):
        prompt = service._build_prompt("test")
        assert "probabilities" in prompt.lower()


class TestClassify:
    """Tests for the classify method (with mocked Groq client)."""

    def test_classify_calls_groq_api(self, service):
        mock_response = MagicMock()
        mock_response.choices = [MagicMock(message=MagicMock(content='{"label": "positive", "confidence": 0.9, "probabilities": {"positive": 0.9, "neutral": 0.05, "negative": 0.05}}'))]
        service.client.chat.completions.create.return_value = mock_response

        label, confidence, probs, raw = service.classify("main khush hun")

        assert label == "positive"
        assert confidence == 0.9
        assert probs["positive"] == 0.9
        service.client.chat.completions.create.assert_called_once()

    def test_classify_handles_groq_api_error(self, service):
        service.client.chat.completions.create.side_effect = Exception("API error")

        label, confidence, probs, raw = service.classify("test text")

        assert label in ["positive", "negative", "neutral"]
        assert 0.0 <= confidence <= 1.0
        data = json.loads(raw)
        assert "label" in data
        assert "confidence" in data
        assert "probabilities" in data

    def test_classify_without_client_uses_fallback(self, service):
        service.client = None

        label, confidence, probs, raw = service.classify("main khush hun")

        assert label == "positive"
        assert confidence == 0.7
        data = json.loads(raw)
        assert data["label"] == "positive"
        assert data["confidence"] == 0.7
        assert "probabilities" in data


class TestFallbackClassify:
    """Tests for the _fallback_classify method."""

    def test_fallback_positive_words(self, service):
        result = service._fallback_classify("main khush hun")
        data = json.loads(result)
        assert data["label"] == "positive"
        assert data["confidence"] == 0.7
        assert data["probabilities"]["positive"] == 0.7

    def test_fallback_negative_words(self, service):
        result = service._fallback_classify("yeh bura hai")
        data = json.loads(result)
        assert data["label"] == "negative"
        assert data["confidence"] == 0.7
        assert data["probabilities"]["negative"] == 0.7

    def test_fallback_neutral_default(self, service):
        result = service._fallback_classify("theek thak hai")
        data = json.loads(result)
        assert data["label"] == "neutral"
        assert data["confidence"] == 0.5
        assert data["probabilities"]["neutral"] == 0.7

    def test_fallback_case_insensitive(self, service):
        result = service._fallback_classify("KHUSH")
        data = json.loads(result)
        assert data["label"] == "positive"

    def test_fallback_probabilities_sum_to_one(self, service):
        result = service._fallback_classify("main khush hun")
        data = json.loads(result)
        total = sum(data["probabilities"].values())
        assert abs(total - 1.0) < 0.01
