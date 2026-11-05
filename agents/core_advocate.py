from langchain_anthropic import ChatAnthropic
from langchain_core.messages import SystemMessage, HumanMessage
import json, re
from dotenv import load_dotenv
from typing import Any
from agents.state import DebateState

load_dotenv()

llm = ChatAnthropic(  # type: ignore[call-arg]
    model_name="claude-opus-4-5",
    temperature=0.7,
    timeout=60,
    stop=None
)

SYSTEM = """You are the Chief Devil's Advocate. You received attack reports from 5 critics.
Your job:
1. Rank all attacks by severity (highest first)
2. Identify TOP 3 killer blows most likely to kill the proposal
3. Generate Counter-Conditions: what must be TRUE for this idea to survive
4. Give an overall survivability score (0-100)

Output ONLY valid JSON:
{
  "top_3_killers": ["...", "...", "..."],
  "ranked_attacks": [{"persona": "...", "severity": 0, "key_point": "..."}],
  "counter_conditions": ["For this to work, X must be true", "..."],
  "survivability_score": 0,
  "verdict": "one sentence brutal summary"
}"""

def extract_text(content: Any) -> str:
    if isinstance(content, str):
        return content.strip()
    if isinstance(content, list):
        for block in content:
            if isinstance(block, dict) and block.get("type") == "text":
                return str(block.get("text", "")).strip()
    return ""

def synthesize_verdict(state: dict) -> dict:
    attacks_summary = json.dumps(state["attacks"], indent=2)
    response = llm.invoke([
        SystemMessage(content=SYSTEM),
        HumanMessage(content=f"Proposal: {state['user_input']}\n\nAttack reports:\n{attacks_summary}")
    ])
    raw = extract_text(response.content)
    match = re.search(r'\{.*\}', raw, re.DOTALL)
    state["final_verdict"] = json.loads(match.group()) if match else {"verdict": raw}
    return state