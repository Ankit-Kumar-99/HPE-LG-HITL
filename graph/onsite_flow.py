"""
onsite:
Handles onsite service preparation workflow.

Flow:
1. Check mandatory fields
2. Validate if onsite visit is required
3. Check delivery instructions
4. Prepare for onsite
5. Confirm onsite with human confirmation (HITL)

Interrupts are used where human confirmation/input is required.
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
        "contact_number",
        "issue_type"
    ]

    missing_fields = [
        field for field in mandatory_fields
        if not state.get(field)
    ]

    # ---------------------------------------------------------
    # ASK ONLY FOR MISSING FIELDS
    # ---------------------------------------------------------

    if missing_fields:

        example_map = {
            "customer_name": "Ankit",
            "address": "Bangalore",
            "contact_number": "9876543210",
            "issue_type": "Hardware Failure"
        }

        example_text = ", ".join(
            [
                f"{field}={example_map[field]}"
                for field in missing_fields
            ]
        )

        return interrupt(
            "Missing mandatory fields:\n"
            f"{', '.join(missing_fields)}\n\n"
            "Please provide values in format:\n"
            f"{example_text}"
        )

    # ---------------------------------------------------------
    # VALIDATION PASSED
    # ---------------------------------------------------------

    return {
        "mandatory_flag": 1,
        "messages": [
            "Mandatory fields passed"
        ]
    }


def mandatory_router(state: OrderState):

    if state.get("mandatory_flag") == 1:
        return "passed"

    return "failed"


# -------------------------------------------------------------------
# NODE 2 -> CHECK ONSITE REQUIRED
# -------------------------------------------------------------------

def check_onsite_required(state: OrderState):

    """
    If issue severity is not available,
    ask user through HITL.
    """

    # ---------------------------------------------------------
    # ASK ISSUE SEVERITY
    # ---------------------------------------------------------

    if not state.get("issue_severity"):

        return interrupt(
            "Please provide issue severity:\n"
            "(low / medium / high / critical)"
        )

    issue_severity = (
        state.get("issue_severity", "")
        .strip()
        .lower()
    )

    # ---------------------------------------------------------
    # ONSITE REQUIRED
    # ---------------------------------------------------------

    if issue_severity in ["high", "critical"]:

        return {
            "onsite_required_flag": 1,
            "messages": [
                f"Onsite visit required for severity: "
                f"{issue_severity}"
            ]
        }

    # ---------------------------------------------------------
    # ONSITE NOT REQUIRED
    # ---------------------------------------------------------

    return {
        "onsite_required_flag": 0,
        "messages": [
            f"Onsite visit not required for severity: "
            f"{issue_severity}"
        ]
    }


def onsite_router(state: OrderState):

    if state.get("onsite_required_flag") == 1:
        return "required"

    return "not_required"


# -------------------------------------------------------------------
# NODE 3 -> DELIVERY INSTRUCTIONS
# -------------------------------------------------------------------

def check_delivery_instructions(state: OrderState):

    """
    Prevent repeated HITL loop.
    """

    # ---------------------------------------------------------
    # ALREADY AVAILABLE
    # ---------------------------------------------------------

    if state.get("delivery_instructions"):

        return {
            "messages": [
                "Delivery instructions received",
                f"Instructions: "
                f"{state['delivery_instructions']}"
            ]
        }

    # ---------------------------------------------------------
    # ASK USER
    # ---------------------------------------------------------

    return interrupt(
        "Please provide delivery/entry instructions "
        "for onsite visit:"
    )


# -------------------------------------------------------------------
# NODE 4 -> PREPARE ONSITE
# -------------------------------------------------------------------

def prepare_for_onsite(state: OrderState):

    return {
        "onsite_status": "prepared",
        "messages": [
            "Onsite preparation completed",
            "Engineer assigned",
            "Visit scheduled"
        ]
    }


# -------------------------------------------------------------------
# NODE 5 -> CONFIRM ONSITE
# -------------------------------------------------------------------

def confirm_onsite(state: OrderState):

    # ---------------------------------------------------------
    # ASK CONFIRMATION
    # ---------------------------------------------------------

    if not state.get("confirmation"):

        return interrupt(
            "Do you confirm the onsite visit? (yes/no)"
        )

    confirmation = (
        state.get("confirmation", "")
        .strip()
        .lower()
    )

    # ---------------------------------------------------------
    # USER DECLINED
    # ---------------------------------------------------------

    if confirmation != "yes":

        return {
            "messages": [
                "Onsite visit was cancelled by user"
            ]
        }

    # ---------------------------------------------------------
    # USER CONFIRMED
    # ---------------------------------------------------------

    return {
        "messages": [
            "Onsite visit confirmed successfully"
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
    "check_onsite_required",
    check_onsite_required
)

builder.add_node(
    "check_delivery_instructions",
    check_delivery_instructions
)

builder.add_node(
    "prepare_for_onsite",
    prepare_for_onsite
)

builder.add_node(
    "confirm_onsite",
    confirm_onsite
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
        "passed": "check_onsite_required",
        "failed": END
    }
)


# -------------------------------------------------------------------
# CONDITIONAL FLOW -> ONSITE REQUIRED
# -------------------------------------------------------------------

builder.add_conditional_edges(
    "check_onsite_required",
    onsite_router,
    {
        "required": "check_delivery_instructions",
        "not_required": END
    }
)


# -------------------------------------------------------------------
# NORMAL FLOW
# -------------------------------------------------------------------

builder.add_edge(
    "check_delivery_instructions",
    "prepare_for_onsite"
)

builder.add_edge(
    "prepare_for_onsite",
    "confirm_onsite"
)

builder.add_edge(
    "confirm_onsite",
    END
)


# -------------------------------------------------------------------
# COMPILE GRAPH
# -------------------------------------------------------------------

onsite_graph = builder.compile()
