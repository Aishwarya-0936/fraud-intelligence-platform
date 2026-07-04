from typing import TypedDict, List, Optional, Annotated


def take_latest(old, new):
    return new


class FraudAnalysisState(TypedDict):
    transaction: Annotated[dict, take_latest]
    user_profile: Annotated[dict, take_latest]

    amount_signals: Annotated[List[str], take_latest]
    amount_score: Annotated[int, take_latest]

    behavioral_signals: Annotated[List[str], take_latest]
    behavioral_score: Annotated[int, take_latest]

    pattern_signals: Annotated[List[str], take_latest]
    pattern_score: Annotated[int, take_latest]

    similar_cases: Annotated[List[dict], take_latest]
    related_patterns: Annotated[List[dict], take_latest]

    all_signals: Annotated[List[str], take_latest]
    total_score: Annotated[int, take_latest]
    risk_level: Annotated[str, take_latest]
    summary: Annotated[Optional[str], take_latest]