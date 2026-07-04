import re

ACCOUNT_PATTERN = re.compile(r"\b\d{9,18}\b")
CARD_PATTERN = re.compile(r"\b(?:\d[ -]*?){13,16}\b")


def scrub_pii(text: str) -> str:
    """Masks likely account/card numbers before sending text to an LLM."""
    if not text:
        return text
    text = CARD_PATTERN.sub("[CARD_REDACTED]", text)
    text = ACCOUNT_PATTERN.sub("[ACCOUNT_REDACTED]", text)
    return text


def scrub_transaction_for_llm(transaction: dict) -> dict:
    """Returns a copy of the transaction dict with PII-sensitive fields masked."""
    safe = transaction.copy()
    if safe.get("destination_account"):
        # Keep only last 4 characters visible, mask the rest
        acc = str(safe["destination_account"])
        safe["destination_account"] = f"***{acc[-4:]}" if len(acc) > 4 else "***"
    if safe.get("device_id"):
        safe["device_id"] = "[DEVICE_ID_MASKED]"
    return safe