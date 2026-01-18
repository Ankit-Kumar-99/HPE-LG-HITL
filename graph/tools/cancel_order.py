"""
cancel_order:
Cancels an existing order.
Requires order ID and human confirmation before cancellation.
"""

from langgraph.graph import StateGraph
from langgraph.types import interrupt
from state.state import OrderState

def get_order_id(state: OrderState):
    return {
        "order_id": "ORD-1234",
        "messages": ["Order ID verified"]}

def confirm_cancel(state: OrderState):
    if not state.get("confirmation"):
        return interrupt("Are you sure you want to cancel the order? (yes/no)")
    
    if state.get("confirmation").lower() == "no":
        return {
            "order_id": "ORD-1234",
            "messages": [
                "Order cancellation declined."
            ]
        }
    return {"messages": ["Cancellation confirmed"]}

def cancel_order(state: OrderState):
    return {
        "order_id": "ORD-1234",
        "messages": ["Order cancelled successfully"]}

builder = StateGraph(OrderState)

builder.add_node("get_order_id", get_order_id)
builder.add_node("confirm_cancel", confirm_cancel)
builder.add_node("cancel_order", cancel_order)

builder.set_entry_point("get_order_id")
builder.add_edge("get_order_id", "confirm_cancel")
builder.add_edge("confirm_cancel", "cancel_order")

cancel_order_graph = builder.compile()

