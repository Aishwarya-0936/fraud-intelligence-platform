MAX_SUMMARY_LENGTH = 1000
MIN_SUMMARY_LENGTH = 10


def validate_llm_output(summary: str) -> tuple:
    """
    Validates the LLM-generated summary before it's stored/returned.
    Returns (is_valid, cleaned_summary_or_error_message).
    """
    if not summary or len(summary.strip()) < MIN_SUMMARY_LENGTH:
        return False, "Summary generation produced insufficient output; manual review required."

    if len(summary) > MAX_SUMMARY_LENGTH:
        return False, summary[:MAX_SUMMARY_LENGTH] + "... [truncated for length]"

    return True, summary