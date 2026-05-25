from schema import AppState
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import InMemorySaver
from agents import *
from router import *

def build_graph():
    builder = StateGraph(AppState)

    checkpointer = InMemorySaver()

    #NODES
    builder.add_node("input_node", input_agent)
    builder.add_node("generator_node", generator_agent)
    builder.add_node("hitl_node", hitl_agent)
    builder.add_node("formatter_node", formatter_agent)
    builder.add_node("tts_node", tts_agent)

    #EDGES
    builder.add_edge(START, "input_node")
    builder.add_edge("input_node", "generator_node")
    builder.add_edge("generator_node", "hitl_node")
    builder.add_conditional_edges(
        "hitl_node",
        hitl_router, {
            "APPROVED": "formatter_node",
            "NEEDS_REVISION": "generator_node",
        }
    )
    builder.add_edge("formatter_node", "tts_node")
    builder.add_edge("tts_node", END)

    return builder.compile(checkpointer=checkpointer)
