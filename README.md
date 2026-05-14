# HPE-LG-HITL

Human-in-the-Loop (HITL) workflow orchestration using **LangGraph** for:

* CSR (Customer Self Repair)
* Onsite Service Preparation
* Status Tracking
* Tool-based intelligent routing using LLM

---

# Project Structure

```text
HPE-LG-HITL
│
├── app/
│   └── main.py
│
├── graph/
│   ├── orch.py
│   ├── csr_flow.py
│   ├── onsite_flow.py
│   ├── track_status.py
│   └── product_recom.py
│
├── llm/
│   └── groq.py
│
├── state/
│   └── state.py
│
├── tools/
│   ├── router_tools.py
│   ├── geo_service.py
│   ├── inventory_service.py
│   └── onsite_service.py
│
├── .env
├── requirements.txt
└── README.md
```

---

# High Level Architecture

```text
                USER INPUT
                     │
                     ▼
              graph/orch.py
                     │
         ┌───────────┼───────────┐
         ▼           ▼           ▼
      CSR FLOW    ONSITE      TRACK
                  FLOW        STATUS
```

The orchestrator uses an LLM with tools to determine which workflow should execute.

---

# Supported Workflows

| Workflow     | Purpose                             |
| ------------ | ----------------------------------- |
| CSR Flow     | Customer Self Repair order handling |
| Onsite Flow  | Engineer onsite scheduling          |
| Track Status | Track order/shipment/service        |

---

# Technologies Used

* LangGraph
* LangChain
* Groq LLM
* Python
* HITL Interrupts
* Stateful Graph Execution

---

# Environment Setup

## 1. Create Virtual Environment

```bash
python -m venv venv
```

Activate:

```bash
source venv/bin/activate
```

---

## 2. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 3. Add Environment Variables

Create `.env`

```env
GROQ_API_KEY=your_key_here
```

---

# Run Application

```bash
python -m app.main
```

---

# Router Workflow (`graph/orch.py`)

The orchestrator decides which workflow to execute.

## Supported Router Tools

### CSR Tool

Triggered when user mentions:

* self repair
* csr
* spare replacement
* diy repair
* repair on my own
* part shipment

---

### Onsite Tool

Triggered when user mentions:

* onsite
* engineer visit
* technician
* field support
* hardware issue

---

### Track Status Tool

Triggered when user mentions:

* track order
* shipment status
* engineer status
* csr tracking

---

# CSR FLOW (`graph/csr_flow.py`)

---

# CSR Workflow Overview

```text
1. Mandatory Field Validation
2. Geo Eligibility Validation
3. CSR Eligibility Summary
4. Part Selection (HITL)
5. Inventory Validation
6. Final Confirmation (HITL)
7. Place CSR Order
```

---

# CSR Detailed Flow

---

## STEP 1 — Mandatory Field Validation

### Required Fields

| Field         |
| ------------- |
| customer_name |
| address       |
| geo           |
| device_type   |

---

## Trigger Condition

If any field is missing:

```python
if missing_fields:
```

### HITL Interrupt Triggered

System asks user:

```text
Please provide values in format:
customer_name=Ankit,
address=Bangalore,
geo=India,
device_type=Laptop
```

---

## STEP 2 — Geo Validation

### Allowed Geographies

```python
allowed_geos = [
    "india",
    "usa",
    "germany"
]
```

---

## Trigger Conditions

### Allowed

```python
if geo in allowed_geos
```

Flow continues.

---

### Not Allowed

If geo not supported:

```text
CSR not allowed in geo
```

Flow ends.

---

## STEP 3 — CSR Summary

Displays:

* Mandatory validation status
* Geo validation status
* CSR eligibility confirmation

---

## STEP 4 — Part Selection (HITL)

### Default Values

```python
DEFAULT_PART = "PART-123"
DEFAULT_QUANTITY = 3
```

---

## HITL Trigger

User sees:

```text
Suggested Part Details:
Part Number: PART-123
Quantity: 3
```

---

## Supported User Inputs

### Accept Defaults

```text
accept
```

Triggers:

```python
part_number = PART-123
quantity = 3
```

---

### Custom Input

```text
part_number=PART-001, quantity=2
```

---

## Invalid Format Trigger

If parsing fails:

```text
Invalid format.
Please enter:
part_number=PART-001, quantity=2
```

---

# STEP 5 — Inventory Validation

## Mock Inventory

```python
available_inventory = {
    "PART-123": 10,
    "PART-001": 5,
    "PART-555": 0
}
```

---

## Conditions

### Inventory Available

```python
available_qty >= quantity
```

Flow continues.

---

### Inventory Unavailable

```text
Insufficient inventory
```

Flow ends.

---

# STEP 6 — Final Confirmation (HITL)

## Trigger

System asks:

```text
Confirm CSR Order?
(yes/no)
```

---

## Conditions

### YES

```python
confirmation == "yes"
```

Flow continues.

---

### NO

```text
CSR order cancelled
```

Flow ends.

---

# STEP 7 — Place CSR Order

Final state:

```python
order_status = "placed"
```

System prints:

* Order placed
* Part number
* Quantity

---

# ONSITE FLOW (`graph/onsite_flow.py`)

---

# Onsite Workflow Overview

```text
1. Mandatory Validation
2. Severity Check
3. Onsite Eligibility
4. Delivery Instructions (HITL)
5. Onsite Preparation
6. Final Confirmation (HITL)
```

---

# ONSITE Detailed Flow

---

## STEP 1 — Mandatory Validation

### Required Fields

| Field          |
| -------------- |
| customer_name  |
| address        |
| contact_number |
| issue_type     |

---

## HITL Trigger

If missing:

```text
Please provide:
customer_name=Ankit,
address=Bangalore,
contact_number=9876543210,
issue_type=Hardware Failure
```

---

# STEP 2 — Issue Severity Check (HITL)

If severity missing:

```text
Please provide issue severity:
(low / medium / high / critical)
```

---

## Supported Values

| Severity | Result              |
| -------- | ------------------- |
| low      | onsite not required |
| medium   | onsite not required |
| high     | onsite required     |
| critical | onsite required     |

---

# STEP 3 — Onsite Eligibility

## Conditions

### High/Critical

```python
if severity in ["high", "critical"]
```

Flow continues.

---

### Low/Medium

```text
Onsite visit not required
```

Flow ends.

---

# STEP 4 — Delivery Instructions (HITL)

System asks:

```text
Please provide delivery/entry instructions
```

Examples:

* Gate pass required
* Call before arrival
* Apartment security approval needed

---

# STEP 5 — Prepare Onsite

Mock preparation logic:

* Engineer assigned
* Visit scheduled
* Onsite preparation completed

---

# STEP 6 — Final Confirmation (HITL)

System asks:

```text
Do you confirm the onsite visit? (yes/no)
```

---

## Conditions

### YES

Flow ends successfully.

---

### NO

Onsite visit cancelled.

---

# HITL (Human-in-the-Loop)

The project heavily uses:

```python
from langgraph.types import interrupt
```

---

# HITL Use Cases

| Workflow | Interrupt Purpose     |
| -------- | --------------------- |
| CSR      | Missing fields        |
| CSR      | Part selection        |
| CSR      | Final confirmation    |
| ONSITE   | Missing fields        |
| ONSITE   | Severity              |
| ONSITE   | Delivery instructions |
| ONSITE   | Final confirmation    |

---

# Stateful Execution

The graph preserves state using:

```python
MemorySaver()
```

Thread config:

```python
thread_id = "csr-onsite-demo"
```

---

# Example CSR Run

```text
USER:
self repair

SYSTEM:
Missing mandatory fields

USER:
customer_name=Ankit,
address=Bangalore,
geo=India,
device_type=Laptop

SYSTEM:
Suggested Part Details

USER:
accept

SYSTEM:
Confirm CSR Order?

USER:
yes

FINAL RESULT:
CSR order placed successfully
```

---

# Example Onsite Run

```text
USER:
onsite

SYSTEM:
Missing mandatory fields

USER:
customer_name=Ankit,
address=Bangalore,
contact_number=9876543210,
issue_type=Hardware Failure

SYSTEM:
Please provide issue severity

USER:
critical

SYSTEM:
Please provide delivery instructions

USER:
Call before arrival

SYSTEM:
Confirm onsite visit?

USER:
yes
```

---

# Future Improvements

* Real inventory APIs
* Real geo validation APIs
* Database persistence
* Authentication
* Multi-agent architecture
* Retry workflows
* SLA calculations
* Ticket creation
* Email/SMS notifications
* UI dashboard
* LangSmith tracing

---

# Key Concepts Demonstrated

* LangGraph orchestration
* Stateful execution
* Conditional routing
* Interrupt-based HITL
* Tool calling
* Multi-workflow orchestration
* Dynamic branching
* Validation pipelines

---

