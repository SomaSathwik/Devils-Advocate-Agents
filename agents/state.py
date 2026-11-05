from typing import TypedDict, List, Dict, Any

class DebateState(TypedDict):
    user_input: str
    dimensions: List[str]
    proposal_summary: str
    attacks: Dict[str, Any]
    final_verdict: Dict[str, Any]