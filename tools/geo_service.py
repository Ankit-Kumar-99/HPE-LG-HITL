
from langgraph.graph import StateGraph
from state.state import OrderState
from langgraph.types import interrupt

#---------------- Product tool ----------------
"""
product_tool:
Selects a product for ordering.
"""
def product_tool_fn(state: OrderState):
    return {
        "product": state["product"],   # 🔑 WRITE IT BACK
        "messages": [
            f"Tool(product): product selected = {state['product']}"
        ]
    }



b = StateGraph(OrderState)
b.add_node("run", product_tool_fn)
b.set_entry_point("run")
product_tool = b.compile()


# ---------------- Size tool ----------------
"""
size_tool:
Determines size for the product.
"""
def size_tool_fn(state: OrderState):
    return {
        "size": "M",
        "messages": ["Tool(size): M selected"]
    }

b = StateGraph(OrderState)
b.add_node("run", size_tool_fn)
b.set_entry_point("run")
size_tool = b.compile()


# ---------------- Payment tool ----------------
"""
payment_tool:
Processes payment for the order.
"""
def payment_tool_fn(state: OrderState):
    return {
        "payment_status": "success",
        "messages": ["Tool(payment): success"]
    }

b = StateGraph(OrderState)
b.add_node("run", payment_tool_fn)
b.set_entry_point("run")
payment_tool = b.compile()


# 🔑 EXPORT REGISTRY
TOOLS = {
    "product": product_tool,
    "size": size_tool,
    # "quantity": quantity_tool,
    "payment": payment_tool,
}
