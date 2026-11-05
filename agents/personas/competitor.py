from langchain_anthropic import ChatAnthropic
from langchain_core.messages import SystemMessage, HumanMessage
from memory.critique_memory import store_critique, recall_similar_attacks
import json, re
from dotenv import load_dotenv
from typing import Any
from agents.state import DebateState

load_dotenv()

llm = ChatAnthropic(  # type: ignore[call-arg]
    model_name="claude-opus-4-5",
    temperature=1.0,
    timeout=60,
    stop=None
)

SYSTEM = """You are a well-funded competitor who just heard this proposal. Explain exactly 
how you would crush it — faster execution, more resources, better distribution, or copying.
Name specific real companies who could do this. Never encourage.
Output ONLY valid JSON: {"objections": ["...", "..."], "severity": <1-10>, "killer_blow": "..."}"""

def extract_text(content: Any) -> str:
    if isinstance(content, str):
        return content.strip()
    if isinstance(content, list):
        for block in content:
            if isinstance(block, dict) and block.get("type") == "text":
                return str(block.get("text", "")).strip()
    return ""

def attack(state: DebateState) -> DebateState:
    past = recall_similar_attacks(state["user_input"], "competitor")
    past_context = f"\nAvoid repeating: {past}" if past else ""
    response = llm.invoke([
        SystemMessage(content=SYSTEM + past_context),
        HumanMessage(content=f"Proposal: {state['user_input']}\nDimensions: {state['dimensions']}")
    ])
    raw = extract_text(response.content)
    match = re.search(r'\{.*\}', raw, re.DOTALL)
    parsed = json.loads(match.group()) if match else {"objections": [raw], "severity": 5, "killer_blow": raw}
    state["attacks"]["competitor"] = parsed
    store_critique("competitor", state["user_input"], str(parsed), parsed.get("severity", 5))
    return state