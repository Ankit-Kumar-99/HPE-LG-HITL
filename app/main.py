from graph.orch import graph
from langgraph.types import Command

thread_id = "demo-1"

config = {"configurable": {"thread_id": thread_id}}

def pretty_print_result(state: dict):
    tool = state.get("selected_tool")

    print("\n========== WORKFLOW RESULT ==========")

    # ---------------- PLACE ORDER ----------------
    if tool == "place_order":
        if state.get("confirmation") != "yes":
            print("❌ Order was not placed.")
            return

        print("🛒 ORDER PLACED SUCCESSFULLY")
        print(f"📦 Product   : {state.get('product')}")
        print(f"📐 Size      : {state.get('size')}")
        print(f"🔢 Quantity  : {state.get('quantity')}")
        print("💳 Payment   : Success")

    # ---------------- TRACK ORDER ----------------
    elif tool == "track_order":

        print("📍 TRACK ORDER RESULT")
        print(f"🆔 Order ID  : {state.get('order_id')}")
        print(f"📦 Status    : {state.get('order_status')}")

    # ---------------- CANCEL ORDER ----------------
    elif tool == "cancel_order":
        if state.get("confirmation") != "yes":
            print("❌ Order cancellation aborted.")
            return

        print("🚫 ORDER CANCELLED")
        print(f"🆔 Order ID  : {state.get('order_id')}")

    else:
        print("⚠️ Unknown workflow executed.")

    print("====================================\n")

# --- Step 1: Start workflow ---
print("---- START ----")
text=input("How can i help you? ")
initial_input = {"input": text, "messages": []}

result = graph.invoke(initial_input, config=config)
# print(result)

# --- Step 2: HITL loop (pause/resume for human input) ---
while "__interrupt__" in result:
    # Ask user for input
    prompt = result["__interrupt__"][0].value
    user_input = input(f"[HITL] {prompt} ")

    state_update = {}
    if "product" in prompt.lower():
        clean = user_input.strip().lower()

        state_update["product"] = clean
        # state_update["last_product"] = clean_product

        
    elif "quantity" in prompt.lower():
        state_update["quantity"] = int(user_input)
    else:
        state_update["confirmation"] = user_input

    # Resume workflow — MemorySaver automatically uses the same thread_id
    result = graph.invoke(
        state_update,
        config=config
    )
    
# --- Step 3: Final workflow result ---
print(pretty_print_result(result))
# print(result)