"""
place_order:
Creates a new order.
Steps include selecting product, size, quantity,
asking user confirmation, and completing payment.
Requires human confirmation before payment.
"""

from langgraph.graph import StateGraph
from state.state import OrderState
from langgraph.types import interrupt
from llm.groq import get_llm

from graph.tools_llm.product_tool import TOOLS
from graph.tools.product_recom import product_recommendation_graph
from graph.tools_llm.product_validate import product_validate_graph


from llm.groq import get_llm

llm = get_llm()

def extract_product(state: OrderState):
    # DO NOT overwrite if product already exists (HITL case)
    if state.get("product"):
        return {
            "product": state["product"],   # KEEP IT EXPLICIT
            "messages": [f"Using user-selected product: {state['product']}"]
        }
    prompt = f"""
You are an entity extractor.

Extract the PRODUCT the user wants to buy from the text below.

Rules:
- If a product is clearly mentioned, return ONLY the product name (single word).
- If no product is mentioned, return ONLY: null
- Do NOT explain.
- Do NOT guess.
- They might ask product in form of question, then also return ONLY product name

User text:
"{state['input']}"
"""

    response = llm.invoke(prompt).content.strip().lower()

    product = None if response == "null" else response

    return {
        "product": product,
        "messages": [
            f"Detected product: {product}" if product else "No product detected."
        ],
    }



AVAILABLE_PRODUCTS = ["iphone", "laptop","headphones", "smartwatch"]

def ask_product_again(state: OrderState):
    return interrupt(
        "Product unavailable.\n"
        f"Please choose one of the following products: "
        f"{', '.join(AVAILABLE_PRODUCTS)}: "
    )

def validation_router(state: OrderState):
    if state.get("product_valid") is True:
        return "valid"
    return "invalid"


def ask_quantity(state: OrderState):
    if not state.get("quantity"):
        return interrupt("Enter quantity:")
    return {"messages": [f"Quantity: {state['quantity']}"]}


def place_order(state:OrderState):
    if not state.get("confirmation"):
        return interrupt("Confirm order? (yes/no)")
    
    if state.get("confirmation").lower() != "yes":
        return {
            "messages": [
                "Order was not placed."
            ]
        }

    return {
        "messages": [
            "Order confirmed",
        ]
    }

builder = StateGraph(OrderState)

#-----proiduct input analysis node-----------
builder.add_node("extract_product", extract_product)
builder.add_node("select_product", TOOLS["product"])
builder.add_node("validate_product", product_validate_graph)
builder.add_node("recommend", product_recommendation_graph)
builder.add_node("ask_product", ask_product_again)

# ---------normal node----------
builder.add_node("select_size", TOOLS["size"])
builder.add_node("ask_quantity", ask_quantity
                 )
builder.add_node("confirm_order", place_order)
builder.add_node("payment", TOOLS["payment"])

builder.set_entry_point("extract_product")

builder.add_edge("extract_product", "select_product")
builder.add_edge("select_product", "validate_product")

builder.add_conditional_edges(
    "validate_product",
    validation_router,
    {
        "valid": "select_size",
        "invalid": "recommend",
    }
)
builder.add_edge("recommend", "ask_product")
builder.add_edge("ask_product", "select_product")

# ---- normal flow -------------
builder.add_edge("select_size", "ask_quantity")
builder.add_edge("ask_quantity", "confirm_order")
builder.add_edge("confirm_order", "payment")

place_order_graph = builder.compile()
