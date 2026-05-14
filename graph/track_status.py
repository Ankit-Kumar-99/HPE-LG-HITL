from langgraph.graph import StateGraph, END

from state.state import OrderState


def fetch_status(state: OrderState):

    return {
        "messages": [
            "Tracking workflow executed",
            "Shipment status: In Transit"
        ]
    }


builder = StateGraph(OrderState)

builder.add_node(
    "fetch_status",
    fetch_status
)

builder.set_entry_point(
    "fetch_status"
)

builder.add_edge(
    "fetch_status",
    END
)

track_status_graph = builder.compile()