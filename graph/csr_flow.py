"""
csr_flow:
Customer Self Repair (CSR) workflow.

Flow:
1. Check mandatory fields
2. Validate geo eligibility for CSR
3. Show CSR eligibility summary
4. Select part number and quantity (HITL supported)
5. Inventory check
6. Final order confirmation
7. Place CSR order

Interrupts are used where human interaction is required.
"""

from langgraph.graph import StateGraph, END
from langgraph.types import interrupt
from state.state import OrderState


# -------------------------------------------------------------------
# NODE 1 -> CHECK MANDATORY FIELDS
# -------------------------------------------------------------------

def check_mandatory_fields(state: OrderState):

    mandatory_fields = [
        "customer_name",
        "address",
        "geo",
        "device_type"
    ]

    missing_fields = [
        field for field in mandatory_fields
        if not state.get(field)
    ]

    # ---------------------------------------------------------
    # HITL FOR MISSING FIELDS
    # ---------------------------------------------------------

    if missing_fields:

        return interrupt(
            "Missing mandatory fields:\n"
            f"{', '.join(missing_fields)}\n\n"
            "Please provide values in format:\n"
            "customer_name=Ankit, "
            "address=Bangalore, "
            "geo=India, "
            "device_type=Laptop"
        )

    return {
        "mandatory_flag": 1,
        "messages": [
            "Mandatory fields validation passed"
        ]
    }


def mandatory_router(state: OrderState):

    if state.get("mandatory_flag") == 1:
        return "passed"

    return "failed"


# -------------------------------------------------------------------
# NODE 2 -> GEO SPECIFIC CSR RULE CHECK
# -------------------------------------------------------------------

def check_geo_rules(state: OrderState):

    """
    Example:
    CSR allowed only in selected geographies
    """

    allowed_geos = ["india", "usa", "germany"]

    geo = state.get("geo", "").lower()

    if geo in allowed_geos:

        return {
            "geo_flag": 1,
            "messages": [
                f"CSR allowed in geo: {geo}"
            ]
        }

    return {
        "geo_flag": 0,
        "messages": [
            f"CSR not allowed in geo: {geo}"
        ]
    }


def geo_router(state: OrderState):

    if state.get("geo_flag") == 1:
        return "allowed"

    return "not_allowed"


# -------------------------------------------------------------------
# NODE 3 -> CSR SUMMARY
# -------------------------------------------------------------------

def csr_summary(state: OrderState):

    return {
        "messages": [
            "CSR eligibility summary:",
            "Mandatory fields check: PASSED",
            f"Geo eligibility check: PASSED ({state.get('geo')})",
            "Customer is eligible for CSR flow"
        ]
    }


# -------------------------------------------------------------------
# NODE 4 -> PART SELECTION (HITL)
# -------------------------------------------------------------------

DEFAULT_PART = "PART-123"
DEFAULT_QUANTITY = 3


def select_part_and_quantity(state: OrderState):

    """
    Handles:
    1. Initial interrupt
    2. Resume after HITL
    3. Default acceptance
    4. Custom part input
    """

    # ---------------------------------------------------------
    # VALUES ALREADY AVAILABLE
    # ---------------------------------------------------------

    if state.get("part_number") and state.get("quantity"):

        return {
            "messages": [
                "Part selection already completed"
            ]
        }

    # ---------------------------------------------------------
    # USER RESPONSE AFTER INTERRUPT
    # ---------------------------------------------------------

    user_response = (
        state.get("user_response", "")
        .strip()
    )

    if user_response:

        # -----------------------------------------------------
        # ACCEPT DEFAULT VALUES
        # -----------------------------------------------------

        if user_response.lower() == "accept":

            return {
                "part_number": DEFAULT_PART,
                "quantity": DEFAULT_QUANTITY,
                "messages": [
                    "Default part selection accepted"
                ]
            }

        # -----------------------------------------------------
        # CUSTOM USER INPUT
        # -----------------------------------------------------

        try:

            values = {}

            for item in user_response.split(","):

                key, value = item.split("=")

                clean_key = key.strip()

                # keep part number uppercase
                if clean_key == "part_number":

                    values[clean_key] = (
                        value.strip().upper()
                    )

                else:

                    values[clean_key] = (
                        value.strip()
                    )

            return {
                "part_number": values.get("part_number"),
                "quantity": int(values.get("quantity")),
                "messages": [
                    "Custom part selection received"
                ]
            }

        # -----------------------------------------------------
        # INVALID INPUT
        # -----------------------------------------------------

        except Exception:

            return interrupt(
                "Invalid format.\n"
                "Please enter:\n"
                "part_number=PART-001, quantity=2"
            )

    # ---------------------------------------------------------
    # INITIAL INTERRUPT
    # ---------------------------------------------------------

    return interrupt(
        f"Suggested Part Details:\n"
        f"Part Number: {DEFAULT_PART}\n"
        f"Quantity: {DEFAULT_QUANTITY}\n\n"
        f"Type 'accept' to continue with default values "
        f"OR provide your own values in format:\n"
        f"part_number=PART-001, quantity=2"
    )


# -------------------------------------------------------------------
# NODE 5 -> INVENTORY CHECK
# -------------------------------------------------------------------

def inventory_check(state: OrderState):

    """
    Mock inventory logic
    """

    available_inventory = {
        "PART-123": 10,
        "PART-001": 5,
        "PART-555": 0
    }

    part_number = state.get("part_number")
    quantity = state.get("quantity")

    available_qty = available_inventory.get(
        part_number,
        0
    )

    if available_qty >= quantity:

        return {
            "inventory_flag": 1,
            "messages": [
                f"Inventory available for "
                f"{part_number} "
                f"(Requested: {quantity})"
            ]
        }

    return {
        "inventory_flag": 0,
        "messages": [
            f"Insufficient inventory for "
            f"{part_number}"
        ]
    }


def inventory_router(state: OrderState):

    if state.get("inventory_flag") == 1:
        return "available"

    return "unavailable"


# -------------------------------------------------------------------
# NODE 6 -> FINAL CONFIRMATION (HITL)
# -------------------------------------------------------------------

def confirm_csr_order(state: OrderState):

    # ---------------------------------------------------------
    # ASK CONFIRMATION
    # ---------------------------------------------------------

    if not state.get("confirmation"):

        return interrupt(
            f"Confirm CSR Order?\n"
            f"Part Number: {state.get('part_number')}\n"
            f"Quantity: {state.get('quantity')}\n"
            f"(yes/no)"
        )

    # ---------------------------------------------------------
    # USER DECLINED
    # ---------------------------------------------------------

    if state.get("confirmation").lower() != "yes":

        return {
            "messages": [
                "CSR order was cancelled by user"
            ]
        }

    # ---------------------------------------------------------
    # USER CONFIRMED
    # ---------------------------------------------------------

    return {
        "messages": [
            "CSR order confirmed"
        ]
    }


# -------------------------------------------------------------------
# NODE 7 -> PLACE ORDER
# -------------------------------------------------------------------

def place_csr_order(state: OrderState):

    return {
        "order_status": "placed",
        "messages": [
            "CSR order placed successfully",
            f"Part Number: {state.get('part_number')}",
            f"Quantity: {state.get('quantity')}"
        ]
    }


# -------------------------------------------------------------------
# BUILD GRAPH
# -------------------------------------------------------------------

builder = StateGraph(OrderState)


# -------------------------------------------------------------------
# ADD NODES
# -------------------------------------------------------------------

builder.add_node(
    "check_mandatory_fields",
    check_mandatory_fields
)

builder.add_node(
    "check_geo_rules",
    check_geo_rules
)

builder.add_node(
    "csr_summary",
    csr_summary
)

builder.add_node(
    "select_part_and_quantity",
    select_part_and_quantity
)

builder.add_node(
    "inventory_check",
    inventory_check
)

builder.add_node(
    "confirm_csr_order",
    confirm_csr_order
)

builder.add_node(
    "place_csr_order",
    place_csr_order
)


# -------------------------------------------------------------------
# ENTRY POINT
# -------------------------------------------------------------------

builder.set_entry_point(
    "check_mandatory_fields"
)


# -------------------------------------------------------------------
# CONDITIONAL FLOW -> MANDATORY CHECK
# -------------------------------------------------------------------

builder.add_conditional_edges(
    "check_mandatory_fields",
    mandatory_router,
    {
        "passed": "check_geo_rules",
        "failed": END
    }
)


# -------------------------------------------------------------------
# CONDITIONAL FLOW -> GEO CHECK
# -------------------------------------------------------------------

builder.add_conditional_edges(
    "check_geo_rules",
    geo_router,
    {
        "allowed": "csr_summary",
        "not_allowed": END
    }
)


# -------------------------------------------------------------------
# NORMAL FLOW
# -------------------------------------------------------------------

builder.add_edge(
    "csr_summary",
    "select_part_and_quantity"
)

builder.add_edge(
    "select_part_and_quantity",
    "inventory_check"
)


# -------------------------------------------------------------------
# CONDITIONAL FLOW -> INVENTORY
# -------------------------------------------------------------------

builder.add_conditional_edges(
    "inventory_check",
    inventory_router,
    {
        "available": "confirm_csr_order",
        "unavailable": END
    }
)


# -------------------------------------------------------------------
# FINAL FLOW
# -------------------------------------------------------------------

builder.add_edge(
    "confirm_csr_order",
    "place_csr_order"
)

builder.add_edge(
    "place_csr_order",
    END
)


# -------------------------------------------------------------------
# COMPILE GRAPH
# -------------------------------------------------------------------

csr_flow_graph = builder.compile()