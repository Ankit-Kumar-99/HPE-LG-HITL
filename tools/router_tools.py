from langchain_core.tools import tool


@tool

def csr_flow():
    """
    Use this tool when customer needs:

    - Customer self repair
    - Spare replacement
    - Part shipment
    - DIY repair
    - CSR order
    """


@tool

def onsite_flow():
    """
    Use this tool when customer needs:

    - Engineer visit
    - Onsite support
    - Field technician
    - Hardware issue requiring visit
    """


@tool

def track_status():
    """
    Use this tool when user wants:

    - order status
    - engineer status
    - shipment tracking
    - CSR tracking
    """