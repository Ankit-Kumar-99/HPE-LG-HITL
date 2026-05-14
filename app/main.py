from graph.orch import graph


# -------------------------------------------------
# THREAD CONFIG
# -------------------------------------------------

thread_id = "csr-onsite-demo"

config = {
    "configurable": {
        "thread_id": thread_id
    }
}
# -------------------------------------------------
# INITIAL USER INPUT
# -------------------------------------------------

user_input = input("How can I help you? ")

initial_state = {
    "input": user_input,
    "messages": []
}


# -------------------------------------------------
# INITIAL GRAPH INVOCATION
# -------------------------------------------------

result = graph.invoke(
    initial_state,
    config=config
)


# -------------------------------------------------
# HITL LOOP
# -------------------------------------------------

while "__interrupt__" in result:

    interrupt_data = result["__interrupt__"][0]

    print("\nSYSTEM:")
    print(interrupt_data.value)

    user_reply = input("\nUSER: ")

    state_update = {}

    interrupt_text = interrupt_data.value.lower()

    # -------------------------------------------------
    # MANDATORY FIELD INPUTS
    # -------------------------------------------------

    if "missing mandatory fields" in interrupt_text:

        values = {}

        try:

            for item in user_reply.split(","):

                key, value = item.split("=")

                values[key.strip()] = value.strip()

            state_update.update(values)

        except Exception:

            print("\nInvalid input format.")
            print(
                "\nExpected format examples:\n"
                "CSR:\n"
                "customer_name=John, "
                "address=Bangalore, "
                "geo=India, "
                "device_type=Laptop\n\n"
                "ONSITE:\n"
                "customer_name=John, "
                "address=Bangalore, "
                "contact_number=9876543210, "
                "issue_type=Hardware Failure"
            )

            continue

    # -------------------------------------------------
    # ISSUE SEVERITY
    # -------------------------------------------------

    elif "issue severity" in interrupt_text:

        state_update["issue_severity"] = (
            user_reply.strip().lower()
        )

    # -------------------------------------------------
    # DELIVERY INSTRUCTIONS
    # -------------------------------------------------

    elif "delivery/entry instructions" in interrupt_text:

        state_update["delivery_instructions"] = (
            user_reply.strip()
        )

    # -------------------------------------------------
    # CONFIRMATIONS
    # IMPORTANT:
    # KEEP BEFORE PART SELECTION CHECK
    # -------------------------------------------------

    elif "confirm" in interrupt_text:

        state_update["confirmation"] = (
            user_reply.strip().lower()
        )

    # -------------------------------------------------
    # CSR PART SELECTION
    # -------------------------------------------------

    elif (
        "suggested part details" in interrupt_text
        or "part_number=" in interrupt_text
        or "invalid format" in interrupt_text
    ):

        state_update["user_response"] = (
            user_reply.strip()
        )

    # -------------------------------------------------
    # FALLBACK
    # -------------------------------------------------

    else:

        state_update["user_response"] = (
            user_reply.strip()
        )

    # -------------------------------------------------
    # RESUME GRAPH
    # -------------------------------------------------

    result = graph.invoke(
        state_update,
        config=config
    )


# -------------------------------------------------
# FINAL RESULT
# -------------------------------------------------

print("\nFINAL RESULT")
print("=" * 50)

messages = result.get("messages", [])

seen = set()

for msg in messages:

    msg_text = str(msg)

    # Avoid duplicate router messages
    if msg_text in seen:
        continue

    seen.add(msg_text)

    print(f"- {msg_text}")

print("=" * 50)