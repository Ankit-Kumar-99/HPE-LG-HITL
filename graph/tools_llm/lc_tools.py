from langchain_core.tools import tool
from graph.tools.place_order import place_order_graph
from graph.tools.track_order import track_order_graph
from graph.tools.cancel_order import cancel_order_graph

# ---------------- PLACE ORDER TOOL ----------------
@tool
def place_order(input: str) -> dict:
    """
    Creates a new order.

    Steps:
    - Extract product
    - Validate availability
    - Recommend alternatives if unavailable
    - Ask quantity (HITL)
    - Ask confirmation (HITL)
    - Complete payment

    Uses LangGraph with human-in-the-loop support.
    """
    return place_order_graph.invoke(
        {"input": input, "messages": []}
    )


# ---------------- TRACK ORDER TOOL ----------------
@tool
def track_order(input: str) -> dict:
    """
    Tracks an existing order and returns delivery status.
    """
    return track_order_graph.invoke(
        {"input": input, "messages": []}
    )


# ---------------- CANCEL ORDER TOOL ----------------
@tool
def cancel_order(input: str) -> dict:
    """
    Cancels an existing order after human confirmation.
    """
    return cancel_order_graph.invoke(
        {"input": input, "messages": []}
    )
