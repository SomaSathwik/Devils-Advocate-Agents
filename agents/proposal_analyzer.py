from langchain_anthropic import ChatAnthropic
from langchain_core.messages import SystemMessage, HumanMessage
import json, re, os
from dotenv import load_dotenv
from agents.state import DebateState


load_dotenv()

llm = ChatAnthropic(  # type: ignore[call-arg]
    model_name="claude-opus-4-5",
    temperature=0.3,
    timeout=60,
    stop=None
)

SYSTEM = """You are a neutral proposal analyst. Break down the given proposal into 
critique dimensions. Return ONLY a valid JSON object like:
{"dimensions": ["technical", "financial", "legal", "market", "ethical"], 
 "summary": "one sentence summary of the proposal"}"""

def analyze_proposal(state: dict) -> dict:
    response = llm.invoke([
        SystemMessage(content=SYSTEM),
        HumanMessage(content=f"Proposal: {state['user_input']}")
    ])
    if isinstance(response.content, str):
        raw = response.content.strip()
    else:
        raw = next((b["text"] for b in response.content if isinstance(b, dict) and b.get("type") == "text"), "")

    match = re.search(r'\{.*\}', raw, re.DOTALL)
    parsed = json.loads(match.group()) if match else {
        "dimensions": ["technical", "financial", "legal", "market", "ethical"],
        "summary": state["user_input"]
    }
    state["dimensions"] = parsed.get("dimensions", [])
    state["proposal_summary"] = parsed.get("summary", state["user_input"])
    return state