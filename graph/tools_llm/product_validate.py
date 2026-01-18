"""
product_validate:
Checks if selected product is available.
"""

from langgraph.graph import StateGraph
from state.state import OrderState

AVAILABLE_PRODUCTS = ["iphone", "laptop"]

def validate_product(state: OrderState):
    if state.get("product_valid") is True:
        return {}


    product = state.get("product")
    if not product:
        return {
            "product_valid": False,
            "messages": ["No product selected yet."]
            
        }
    is_valid = product in AVAILABLE_PRODUCTS


    return {
        "product_valid": is_valid,
        "messages": [f"Product '{product}' available: {is_valid}"]
    }

builder = StateGraph(OrderState)
builder.add_node("validate", validate_product)
builder.set_entry_point("validate")

product_validate_graph = builder.compile()
