# 🧠 LangGraph Human-in-the-Loop Order Management POC

This repository demonstrates an **end-to-end LangGraph workflow** for an order management system with **Human-in-the-Loop (HITL)** support.
The system intelligently routes user intent to the correct workflow (**Place Order, Track Order, Cancel Order**) and pauses execution whenever human confirmation or input is required.

---
## 🚀 Concepts to know 

* **LangGraph – Framework for building stateful, graph-based LLM workflows**
* **StateGraph – Defines nodes and edges operating on a shared mutable state.**
* **Typed State (TypedDict) – Enforces a strict schema for workflow state.**
* **LLM Tool Calling – Forces the LLM to choose an action instead of free text.**
* **Sub-Graphs – Independent graphs embedded as nodes inside a parent graph.**
* **Interrupt (HITL) – Pauses execution and waits for human input.**
* **Checkpointer – Stores intermediate state to support pause and resume.**
* **MemorySaver – In-memory checkpointer used for this POC.**
* **Thread ID – Unique identifier to resume the correct workflow instance.**
* **Conditional Edges – Dynamic branching based on state values.**
* **Messages Aggregation – Automatically accumulates messages across nodes.**
  
---
## 🚀 Key Features

* **Intent routing using LLM tool calling**
* **Stateful workflows using LangGraph**
* **Human-in-the-Loop (pause & resume) via interrupts**
* **Thread-safe execution using MemorySaver**
* **Modular, extensible graph design**
* **Typed state management using `TypedDict`**

---

## 🧩 High-Level Architecture

```
User Input
   ↓
Tool Router (LLM)
   ↓
──────────────────────────────
│ Place Order | Track | Cancel│
──────────────────────────────
   ↓
HITL Interrupts (if required)
   ↓
Final State Output
```

* A **router LLM** selects exactly one tool.
* Each tool is implemented as an **independent LangGraph sub-graph**.
* **Human input** is requested using LangGraph `interrupt`.
* Execution resumes using the same `thread_id`.

---

## 📂 Project Structure

```
.
├── main.py                  # CLI entry point + HITL loop
├── orch.py                  # Orchestrator graph & tool routing
├── state.py                 # Global OrderState definition
│
├── graph/
│   ├── tools/
│   │   ├── place_order.py   # Place order workflow
│   │   ├── track_order.py   # Track order workflow
│   │   └── cancel_order.py  # Cancel order workflow
│   │
│   ├── tools_llm/
│   │   ├── lc_tools.py      # Tool schemas for LLM routing
│   │   ├── product_tool.py
│   │   └── product_validate.py
│   │
│   └── orch.py              # Root graph compilation
│
└── llm/
    └── groq.py              # LLM configuration
```

---

## 🧠 OrderState

All workflows share a common typed state:

```python
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
    messages: list[str]
```

This ensures:

* Strong schema consistency
* Predictable state transitions
* Easy debugging and extension

---

## 🔀 Tool Routing Logic

The router:

* Uses **LLM tool calling**
* Must select **exactly one tool**
* Never responds with free text

Supported tools:

* `place_order`
* `track_order`
* `cancel_order`

---

## 🧑‍💻 Human-in-the-Loop (HITL)

HITL is implemented using:

```python
from langgraph.types import interrupt
```

Examples of pauses:

* Product not detected / invalid
* Quantity missing
* Order confirmation required

The workflow:

1. Pauses execution
2. Prompts the user
3. Resumes from the same state using `thread_id`

---

## 💾 State Persistence

This project uses:

```python
checkpointer = MemorySaver()
```

Benefits:

* Stateful execution across interruptions
* Thread-safe resume
* No external storage required (POC-friendly)

---

## ▶️ How to Run

1. Install dependencies

```bash
pip install langgraph langchain
```

2. Set up LLM credentials (Groq or compatible)

3. Run the application

```bash
python main.py
```

4. Interact via CLI:

```text
How can I help you?
> I want to buy an iphone
```

The system will automatically:

* Route intent
* Ask missing inputs
* Confirm actions
* Complete the workflow

---

## 🧪 Example Workflows

### Place Order

* Extract product from input
* Validate product
* Recommend alternatives if invalid
* Ask size & quantity
* Confirm order
* Process payment

### Track Order

* Ask for order ID
* Return order status

### Cancel Order

* Ask for order ID
* Request confirmation
* Cancel order


---

## 📌 Purpose of This POC

This project is intended to:

* Demonstrate **LangGraph orchestration patterns**
* Showcase **HITL design in production-like flows**
* Serve as a **template for agentic workflows**

---
