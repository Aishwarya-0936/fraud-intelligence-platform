import re

SUSPICIOUS_PATTERNS = [
    r"ignore (all )?(previous|prior|above) instructions",
    r"disregard (all )?(previous|prior|above)",
    r"you are now",
    r"system prompt",
    r"act as",
    r"new instructions",
    r"forget (everything|all)",
]

_compiled = [re.compile(p, re.IGNORECASE) for p in SUSPICIOUS_PATTERNS]


def detect_prompt_injection(text: str) -> bool:
    """Returns True if suspicious instruction-like content is found in free text fields."""
    if not text:
        return False
    return any(pattern.search(text) for pattern in _compiled)


def sanitize_free_text_fields(transaction: dict) -> dict:
    """Checks merchant name and other free text fields for injection attempts;
    replaces flagged content rather than passing it to the LLM."""
    safe = transaction.copy()
    for field in ["merchant", "location"]:
        value = safe.get(field)
        if value and detect_prompt_injection(value):
            safe[field] = "[FLAGGED_CONTENT_REMOVED]"
    return safe