"""Guardrails for input/output validation."""
import re
from typing import Dict, Any
from app.core.logging_config import get_logger

logger = get_logger(__name__)

# Patterns that indicate potentially harmful or off-topic content
HARMFUL_PATTERNS = [
    r"\b(hack|exploit|inject|malware|virus|phishing)\b",
    r"\b(password|credentials|api.key|secret)\s*[:=]\s*\S+",
]

# Patterns for PII detection
PII_PATTERNS = [
    r"\b\d{3}-\d{2}-\d{4}\b",  # SSN
    r"\b\d{16}\b",  # Credit card (simplified)
    r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",  # Email
]

MAX_INPUT_LENGTH = 10000
MAX_OUTPUT_LENGTH = 50000


class Guardrails:
    """Input and output validation guardrails."""

    def validate_input(self, text: str) -> Dict[str, Any]:
        """Validate user input for safety and appropriateness."""
        if not text or not text.strip():
            return {"is_valid": False, "reason": "Empty input"}

        if len(text) > MAX_INPUT_LENGTH:
            return {
                "is_valid": False,
                "reason": f"Input too long. Maximum {MAX_INPUT_LENGTH} characters allowed.",
            }

        for pattern in HARMFUL_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                logger.warning("Potentially harmful input detected", pattern=pattern)
                return {
                    "is_valid": False,
                    "reason": "Input contains potentially harmful content",
                }

        return {"is_valid": True, "reason": None}

    def validate_output(self, text: str) -> Dict[str, Any]:
        """Validate LLM output for safety."""
        if not text:
            return {"is_valid": False, "reason": "Empty output"}

        if len(text) > MAX_OUTPUT_LENGTH:
            sanitized = text[:MAX_OUTPUT_LENGTH] + "\n\n[Response truncated for safety]"
            return {"is_valid": True, "sanitized": sanitized}

        return {"is_valid": True}

    def detect_pii(self, text: str) -> Dict[str, Any]:
        """Detect PII in text."""
        found_pii = []
        for pattern in PII_PATTERNS:
            matches = re.findall(pattern, text)
            if matches:
                found_pii.extend(matches)

        return {
            "has_pii": len(found_pii) > 0,
            "pii_count": len(found_pii),
        }

    def sanitize_output(self, text: str) -> str:
        """Remove or mask PII from output."""
        sanitized = text
        for pattern in PII_PATTERNS:
            sanitized = re.sub(pattern, "[REDACTED]", sanitized)
        return sanitized
