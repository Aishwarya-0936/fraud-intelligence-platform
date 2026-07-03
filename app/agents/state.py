from typing import TypedDict, List, Optional

class FraudAnalysisState(TypedDict):
    # Input transaction data
    transaction: dict
    user_profile: dict

    # Each agent writes their signals and score contribution here
    amount_signals: List[str]
    amount_score: int

    behavioral_signals: List[str]
    behavioral_score: int

    pattern_signals: List[str]
    pattern_score: int
    similar_cases: list
    
    # Final outputs — supervisor fills these
    all_signals: List[str]
    total_score: int
    risk_level: str
    summary: Optional[str]