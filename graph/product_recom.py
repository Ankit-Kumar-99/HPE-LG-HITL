"""
product_recommendation:
Analyzes the user's original request and unavailable product,
then recommends the best alternative product.
"""

from langgraph.graph import StateGraph
from state.state import OrderState
from llm.groq import get_llm

llm = get_llm()

AVAILABLE_PRODUCTS = ["iphone", "laptop"]


def recommend_product(state: OrderState):
    unavailable_product = state.get("product")
    user_intent = state.get("input")

    prompt = f"""
A user wants to buy a product, but it is unavailable.

Unavailable product: {unavailable_product}
User request: {user_intent}

Available products:
{AVAILABLE_PRODUCTS}

Recommend the single best alternative product.
Return ONLY the product name.
"""

    recommendation = llm.invoke(prompt).content.strip().lower()

    # Safety fallback
    if recommendation not in AVAILABLE_PRODUCTS:
        recommendation = AVAILABLE_PRODUCTS[0]
    print("RECOMMENDED PRODUCT--->",AVAILABLE_PRODUCTS)

    return {
        "recommended_product": recommendation,
        "messages": [
            f"Product '{unavailable_product}' is unavailable.",
            f"Recommended alternative: {recommendation}:"
        ]
    }


builder = StateGraph(OrderState)
builder.add_node("recommend", recommend_product)
builder.set_entry_point("recommend")

product_recommendation_graph = builder.compile()
