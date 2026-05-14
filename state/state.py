from typing import TypedDict, Annotated, Optional
from langgraph.graph.message import add_messages


class OrderState(TypedDict, total=False):

    # -------------------------------------------------
    # COMMON
    # -------------------------------------------------

    input: str
    messages: Annotated[list[str], add_messages]

    selected_tool: str
    tool_args: dict

    confirmation: str
    user_response: str

    # -------------------------------------------------
    # CUSTOMER DETAILS
    # -------------------------------------------------

    customer_name: str
    address: str
    contact_number: str
    geo: str

    # -------------------------------------------------
    # DEVICE / ISSUE
    # -------------------------------------------------

    device_type: str
    issue_type: str
    issue_severity: str

    # -------------------------------------------------
    # CSR FLOW
    # -------------------------------------------------

    mandatory_flag: int
    geo_flag: int

    part_number: str
    quantity: int

    inventory_flag: int

    order_status: str

    # -------------------------------------------------
    # ONSITE FLOW
    # -------------------------------------------------

    onsite_required_flag: int
    onsite_status: str

    delivery_instructions: str