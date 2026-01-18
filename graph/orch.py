from langgraph.graph import StateGraph
from langgraph.types import interrupt
from langgraph.checkpoint.memory import MemorySaver
from state.state import OrderState
from graph.tools.place_order import place_order_graph
from graph.tools.track_order import track_order_graph
from graph.tools.cancel_order import cancel_order_graph
from llm.groq import get_llm

from graph.tools_llm.lc_tools import place_order, track_order, cancel_order

llm = get_llm()

llm_with_tools = llm.bind_tools([
    place_order,
    track_order,
    cancel_order
])

def tool_select(state: OrderState):
    response = llm_with_tools.invoke(
        [
            {
                "role": "system",
                "content": (
                    "You are an AI router.\n"
                    "You MUST select exactly ONE tool.\n"
                    "Do NOT respond with text.\n"
                    "Always call a tool."
                )
            },
            {
                "role": "user",
                "content": state["input"]
            }
        ]
    )

    if not response.tool_calls:
        raise RuntimeError("❌ LLM failed to select a tool")

    tool_call = response.tool_calls[0]

    return {
        "selected_tool": tool_call["name"],
        "tool_args": tool_call["args"]
    }


#Build the graph
builder = StateGraph(OrderState)

builder.add_node("start", tool_select)
builder.add_node("place_order", place_order_graph)
builder.add_node("track_order", track_order_graph)
builder.add_node("cancel_order", cancel_order_graph)

# Conditional edges from router → tool nodes
builder.add_conditional_edges(
    "start",
    lambda s: s["selected_tool"],
    {
        "place_order": "place_order",
        "track_order": "track_order",
        "cancel_order": "cancel_order",
    }
)

builder.set_entry_point("start")

# Compile the graph
graph = builder.compile(checkpointer=MemorySaver())
