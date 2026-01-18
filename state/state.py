from typing import TypedDict, Annotated
from langgraph.graph import add_messages

class OrderState(TypedDict):
    input: str
    selected_tool: str | None
    confirmation: str | None

    product: str | None
    product_valid: bool | None
    size: str | None
    quantity: int | None
    order_id: str | None
    order_status: str | None

    messages: Annotated[list[str], add_messages]
