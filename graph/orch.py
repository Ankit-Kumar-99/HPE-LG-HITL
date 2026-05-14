from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

from state.state import OrderState

from llm.groq import get_llm

from tools.router_tools import (
    csr_flow,
    onsite_flow,
    track_status
)

from graph.csr_flow import csr_flow_graph
from graph.onsite_flow import onsite_graph
from graph.track_status import track_status_graph


# -------------------------------------------------
# INITIALIZE LLM
# -------------------------------------------------

llm = get_llm()


# -------------------------------------------------
# BIND TOOLS
# -------------------------------------------------

llm_with_tools = llm.bind_tools([
    csr_flow,
    onsite_flow,
    track_status
])


# -------------------------------------------------
# ROUTER NODE
# -------------------------------------------------

def tool_select(state: OrderState):

    user_input = state["input"]

    response = llm_with_tools.invoke([
        {
            "role": "system",
            "content": (
                "You are a support workflow router. "
                "Always call the correct tool."
            )
        },
        {
            "role": "user",
            "content": user_input
        }
    ])

    # -------------------------------------------------
    # SAFETY CHECK
    # -------------------------------------------------

    if not response.tool_calls:

        return {
            "selected_tool": "track_status",
            "messages": [
                "No tool selected by LLM. "
                "Defaulting to track_status."
            ]
        }

    tool_call = response.tool_calls[0]

    return {
        "selected_tool": tool_call["name"],
        "tool_args": tool_call.get("args", {}),
        "messages": [
            f"Router selected: {tool_call['name']}"
        ]
    }


# -------------------------------------------------
# BUILD ROOT GRAPH
# -------------------------------------------------

builder = StateGraph(OrderState)


# -------------------------------------------------
# ADD NODES
# -------------------------------------------------

builder.add_node(
    "start",
    tool_select
)

builder.add_node(
    "csr_flow",
    csr_flow_graph
)

builder.add_node(
    "onsite_flow",
    onsite_graph
)

builder.add_node(
    "track_status",
    track_status_graph
)


# -------------------------------------------------
# ENTRY POINT
# -------------------------------------------------

builder.set_entry_point("start")


# -------------------------------------------------
# CONDITIONAL ROUTING
# -------------------------------------------------

builder.add_conditional_edges(
    "start",
    lambda s: s["selected_tool"],
    {
        "csr_flow": "csr_flow",
        "onsite_flow": "onsite_flow",
        "track_status": "track_status"
    }
)


# -------------------------------------------------
# FINAL EDGES
# -------------------------------------------------

builder.add_edge(
    "csr_flow",
    END
)

builder.add_edge(
    "onsite_flow",
    END
)

builder.add_edge(
    "track_status",
    END
)


# -------------------------------------------------
# COMPILE GRAPH
# -------------------------------------------------

graph = builder.compile(
    checkpointer=MemorySaver()
)