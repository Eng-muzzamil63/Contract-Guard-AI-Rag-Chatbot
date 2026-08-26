from typing import TypedDict, List, Dict, Any
from langgraph.graph import StateGraph, END
from graph import ContractGraph
from llm import answer_question

class AgentState(TypedDict, total=False):
    question: str
    context: List[Dict[str, Any]]
    answer: str


def build_graph_agent(kg: ContractGraph):
    def retrieve(state: AgentState):
        return {"context": kg.graph_context(state["question"])}

    def reason(state: AgentState):
        return {"answer": answer_question(state["question"], state.get("context", []))}

    graph = StateGraph(AgentState)
    graph.add_node("retrieve_from_graph", retrieve)
    graph.add_node("reason_over_graph", reason)
    graph.set_entry_point("retrieve_from_graph")
    graph.add_edge("retrieve_from_graph", "reason_over_graph")
    graph.add_edge("reason_over_graph", END)
    return graph.compile()
