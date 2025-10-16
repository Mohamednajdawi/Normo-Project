from langgraph.graph import END, StateGraph

from normo_backend.agents import (meta_data_agent, pdf_selector_agent,
                                  planner_agent, rag_retriever_agent,
                                  summarizer_agent)
from normo_backend.models import AgentState


def route_planner(state: AgentState) -> str:
        """Route based on planner's first step, with fallback to retrieve_pdfs"""
        if not state.steps:
            return "retrieve_pdfs"  # Default fallback
        
        first_step = state.steps[0].lower().strip()
        
        # Handle exact matches
        if first_step == "retrieve_pdfs":
            return "pdf_selector"
        elif first_step == "summarize":
            return "summarizer"
        
        # Default to retrieving PDFs for any unrecognized action
        return "pdf_selector"
    
def create_workflow_graph() -> StateGraph:
    graph = StateGraph(AgentState)

    graph.add_node("planner", planner_agent)
    graph.add_node("pdf_selector", pdf_selector_agent)
    graph.add_node("meta_data_extractor", meta_data_agent)
    graph.add_node("rag_retriever", rag_retriever_agent)
    graph.add_node("summarizer", summarizer_agent)

    graph.set_entry_point("meta_data_extractor")
    graph.add_edge("meta_data_extractor", "planner")
    

    graph.add_conditional_edges(
        "planner",
        route_planner,
        {
            "pdf_selector": "pdf_selector",
            "summarizer": "summarizer",
        },
    )
    graph.add_edge("pdf_selector", "rag_retriever")
    graph.add_edge("rag_retriever", "summarizer")
    graph.add_edge("summarizer", END)

    return graph.compile()


graph = create_workflow_graph()
