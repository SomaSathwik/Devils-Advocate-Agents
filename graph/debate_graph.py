from langgraph.graph import StateGraph, END
from agents.state import DebateState
from agents.proposal_analyzer import analyze_proposal
from agents.personas.pessimist import attack as pessimist_attack
from agents.personas.lawyer import attack as lawyer_attack
from agents.personas.competitor import attack as competitor_attack
from agents.personas.user_voice import attack as user_voice_attack
from agents.personas.data_skeptic import attack as data_skeptic_attack
from agents.core_advocate import synthesize_verdict

def init_attacks(state: DebateState) -> DebateState:
    state["attacks"] = {}
    return state

graph = StateGraph(DebateState)
graph.add_node("init",         init_attacks)           # type: ignore[arg-type]
graph.add_node("analyze",      analyze_proposal)       # type: ignore[arg-type]
graph.add_node("pessimist",    pessimist_attack)       # type: ignore[arg-type]
graph.add_node("lawyer",       lawyer_attack)          # type: ignore[arg-type]
graph.add_node("competitor",   competitor_attack)      # type: ignore[arg-type]
graph.add_node("user_voice",   user_voice_attack)      # type: ignore[arg-type]
graph.add_node("data_skeptic", data_skeptic_attack)    # type: ignore[arg-type]
graph.add_node("verdict",      synthesize_verdict)     # type: ignore[arg-type]

graph.set_entry_point("init")
graph.add_edge("init",    "analyze")
graph.add_edge("analyze", "pessimist")
graph.add_edge("analyze", "lawyer")
graph.add_edge("analyze", "competitor")
graph.add_edge("analyze", "user_voice")
graph.add_edge("analyze", "data_skeptic")

for persona in ["pessimist", "lawyer", "competitor", "user_voice", "data_skeptic"]:
    graph.add_edge(persona, "verdict")

graph.add_edge("verdict", END)
debate_app = graph.compile()