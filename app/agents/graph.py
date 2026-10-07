from langgraph.graph import StateGraph, START, END
from app.agents.state import AgentState
from app.agents.nodes import security_agent, supervisor_agent, claims_agent, prior_auth_agent, rag_agent, response_agent

def build_graph():
    g = StateGraph(AgentState)
    g.add_node("security", security_agent)
    g.add_node("supervisor", supervisor_agent)
    g.add_node("claims", claims_agent)
    g.add_node("prior_auth", prior_auth_agent)
    g.add_node("rag", rag_agent)
    g.add_node("response", response_agent)
    g.add_edge(START, "security")
    g.add_edge("security", "supervisor")
    g.add_edge("supervisor", "claims")
    g.add_edge("claims", "prior_auth")
    g.add_edge("prior_auth", "rag")
    g.add_edge("rag", "response")
    g.add_edge("response", END)
    return g.compile()
