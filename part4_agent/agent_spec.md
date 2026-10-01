# Meesho Reseller Growth & Alert Intelligence Agent

## 1. Goal
Keep Meesho category managers informed of any category whose month-on-month revenue moves beyond the 8% threshold, while ensuring every message is validated, traceable to verified data, and held for human approval before it is considered sent.

## 2. Tools
The monitoring agent uses the following concrete functions from Parts 1–3:

### Part 2 — Validation and Growth Engine
- `validate_feed(csv_path)`  
  Validates the input CSV before any other processing begins.

- `mom_growth(previous, current)`  
  Calculates the Month-on-Month revenue growth percentage.

- `is_flagged(mom_pct, threshold=8.0)`  
  Classifies the result as:
  - `"flagged"` when `abs(mom_pct) > 8.0`
  - `"not_flagged"` when `abs(mom_pct) < 8.0`
  - `"escalate_exact_boundary"` when `abs(mom_pct) == 8.0`

### Part 3 — Narrative Layer
- Prompt-pack template-fill function  
  Uses the verified category, month, previous revenue, current revenue, and MoM percentage to create the Context → Insight → Implication stakeholder narrative.
- `assert_no_raw_names_leak(text, reseller_names)`  
  Ensures that an external-facing narrative does not contain a raw reseller name.
- `alias_for(reseller_id)`  
  Converts a reseller ID into its approved masked alias.

---

## 3. Memory / State
The agent must retain the following state between monthly runs:
- Previous month's revenue for each category.
- Previous month name.
- Current run/month.
- Category-level revenue values already validated.
- MoM results and flag status generated during the current run.
- Draft narratives generated during the current run.
- Human approval status for each draft.
The previous month's category revenue is required so that the agent can calculate the next month's MoM growth.
The agent must not treat an unvalidated value as trusted state.

## 4. Planner
The agent follows this ordered sequence:

### Step 1 — Load Input
Read the monthly category revenue CSV produced by Part 1.

### Step 2 — Validate Input
Run: `validate_feed(csv_path)`.
No other processing is allowed before validation succeeds.
If validation fails, stop the run immediately and surface all validation errors.

### Step 3 — Read Category Values
For each category, obtain the previous month's and current month's verified revenue values.

### Step 4 — Calculate MoM Growth
Run:`mom_growth(previous, current)` for each category.

### Step 5 — Apply the Decision Rule
Run:`is_flagged(mom_pct)` for every category.

The decision rule is:
abs(MoM) > 8%  → flagged
abs(MoM) < 8%  → not_flagged
abs(MoM) = 8%  → escalate_exact_boundary

### Step 6 — Handle Results
- `"flagged"` → generate a stakeholder draft.
- `"not_flagged"` → do not generate a flagged narrative.
- `"escalate_exact_boundary"` → stop automatic narrative generation for that category and hold it for human review.

### Step 7 — Generate Narrative
For every flagged category, fill the Part 3 prompt-pack template using only verified values.
The narrative must contain: Context, Insight, Implication.
No unsupported numbers or causes may be introduced.

### Step 8 — Apply Output Guardrails
Check that every number in the generated narrative can be traced to a verified Part 1 or Part 2 value.
For any external-facing reseller narrative, run the raw-name leak check and use only: **region + masked alias**

### Step 9 — Human Approval
Hold every generated message for human review. The agent must never automatically send the message.
The runner should represent this state with an approval flag such as:
**approved = False** until a human explicitly approves the draft.

---

## 5. Feedback Loop
The final stage of the agent is a human-approval checkpoint.
The workflow is:
  **Verified data -> MoM calculation -> Threshold decision -> Narrative draft -> Validation / traceability checks -> Human review -> Approve -(considered ready to send) or Not approved (held for revision)**

No Gmail, SMTP, or other external sending integration is required. The agent only produces a draft and records whether human approval has occurred.

---

# Guardrails

## Input Guardrail
`validate_feed()` must pass before any growth calculation, flagging decision, or narrative generation occurs.
If validation returns **False** the run must immediately stop. 
The validation errors must be surfaced to the userrather than silently ignored.

---

## Action Guardrail
The agent must never automatically send a message.
Every narrative is *** drafted → validated → held for human approval. ***
Only a human approval flag can move the draft to the approved state.

---

## Output Guardrail
Every number appearing in a drafted narrative must trace back to a verified Part 1 or Part 2 value.
The agent must not invent:
- revenue values
- percentages
- order counts
- causes
- business explanations
- performance claims

If a cause is not supported by the supplied data, it must be presented as a hypothesis or as something to investigate.
For external-facing reseller narratives, raw reseller names must never appear. The narrative must use the reseller's region and masked alias.

---

# Success Conditions
A run is successful when:
1. Input validation passes.
2. Every required category has a valid MoM calculation.
3. Every category receives the correct threshold classification.
4. Drafts are produced for flagged categories.
5. No draft is produced for a `not_flagged` category.
6. Exact-boundary cases are held for human review.
7. Every number in every draft is traceable to verified input data.
8. No raw reseller name appears in an external-facing narrative.
9. Every draft is held for human approval.

A run is also considered successful when no category crosses the threshold and therefore correctly produces zero flagged drafts.

---

# Error Stopping Conditions

The agent must perform a **Hard Stop** 
when: 
  `validate_feed(csv_path)`
returns:
  `(False, errors)`
Then the agent must:
1. Stop all downstream processing.
2. Not calculate MoM values.
3. Not generate narratives.
4. Not produce an approval-ready message.
5. Surface the complete validation error list.

There must be no silent skipping of invalid rows.

---

# Given-When-Then Agent Specifications

## GWT 1 — Ethnic Wear April → May
**GIVEN** April → May Ethnic Wear revenue moves from `104520.77` to `185107.61`
**WHEN** the monitoring agent calculates `mom_growth` and applies `is_flagged`
**THEN** `mom_growth` returns `77.1` and `is_flagged` returns `"flagged"`, after which the agent generates a draft narrative and holds it for human approval.

---

## GWT 2 — Beauty & Personal Care May → June
**GIVEN** May → June Beauty & Personal Care revenue moves from `35542.11` to `37559.07`
**WHEN** the monitoring agent evaluates the category
**THEN** `mom_growth` returns `5.67` and `is_flagged` returns `"not_flagged"`, so the agent does not generate a flagged-category narrative.

---

## GWT 3 — Exact 8% Boundary
**GIVEN** previous revenue is `100000` and current revenue is `108000`
**WHEN** the monitoring agent evaluates the category
**THEN** `mom_growth` returns exactly `8.0` and `is_flagged` returns `"escalate_exact_boundary"`, so the agent does not silently classify the category as either flagged or not flagged and instead holds it for human review.

---

## GWT 4 — Corrupted Feed
**GIVEN** the corrupted feed contains a negative revenue row, a missing category, and a missing revenue value
**WHEN** the monitoring agent runs `validate_feed`
**THEN** validation returns `False` with exactly these three errors in order:
  line 3: negative revenue (-4200.0) for category=Western Wear
  line 4: missing category (month=July)
  line 6: missing revenue (category=Home & Kitchen)
The agent performs a **Hard Stop**, surfaces the errors, and does not continue to MoM calculation or narrative generation.


# 4.2 — Ordered Subtasks
The monitoring agent follows these ordered subtasks for every monthly run.

### 1. Load and Validate the Monthly Revenue Feed
Load the monthly category revenue feed and immediately run: `validate_feed(csv_path)`.
No MoM calculation or narrative generation may occur before validation completes.

---

### 2. Hard Stop if the Feed Is Invalid
If `validate_feed()` returns: `(False, errors)` then perform a **Hard Stop**.
The agent must:
- report all validation errors;
- stop the current run;
- not calculate MoM growth;
- not run `is_flagged`;
- not generate any narrative drafts.

If validation returns: `(True, [])` then continue to Step 3.

---

### 3. Calculate MoM Growth for Every Category
For every category in the validated feed, calculate the month-on-month growth using: `mom_growth(previous_revenue, current_revenue)`.
The calculation must use the current month's revenue and the corresponding previous month's revenue.
Store the resulting `mom_pct` for each category.

---

### 4. Apply the Flagging Decision to Every Category

Run: `is_flagged(mom_pct)` for every category.
Each category must receive exactly one of these results:
1. flagged
2. not_flagged
3. escalate_exact_boundary

The exact-boundary result must be handled separately and must never be silently treated as either `flagged` or `not_flagged`.

---

### 5. Sort Flagged Categories by Magnitude
Select only categories whose result is: **flagged**. For these categories, sort them by: **abs(mom_pct)** in **descending order**. This ensures that the largest magnitude changes are considered first, regardless of whether the movement is positive or negative.

For example:
-58.74% → magnitude 58.74
 42.59% → magnitude 42.59
 23.90% → magnitude 23.90

Therefore, the negative and positive movements are compared by their absolute size.

---

### 6. Draft Messages for at Most the Top 3 Flagged Categories
Take only the first **three** categories after the magnitude sort.
For each selected category, use the Part 3 narrative prompt/template to generate a stakeholder draft containing: Context, Insight, Implication.

The draft must use only verified Part 1/Part 2 values. The agent must not automatically send the draft. All drafts remain subject to the human-approval checkpoint defined in Part 4.1.

The maximum of three drafts is an explicit notification-flooding guardrail. It prevents the agent from producing an unlimited number of messages when many categories are flagged.

---

### 7. Suppress Remaining Flagged Categories
If more than three categories are flagged, all flagged categories after the first three must **not** receive a narrative draft.
Instead, log each remaining category as **suppressed, review manually**.

These categories remain visible in the run output so that they are not lost, but no message is drafted for them.

For example:
Top 3 flagged categories
        ↓
Draft messages

Remaining flagged categories
        ↓
"suppressed, review manually"
        ↓
No draft

---

### 7b. Escalate Exact-Boundary Categories Separately
Independently of the top-3 flagged list, identify every category whose result is: ***escalate_exact_boundary***
Add each such category to: ***escalated_categories***

Do **not** draft a message for these categories.
An exact-boundary category is neither `"flagged"` nor `"not_flagged"`, so it must not be silently dropped, suppressed, or included in either list. It must remain explicitly visible for human review.

---

### 8. Emit One Structured JSON Object per Run
At the end of the run, emit exactly **one structured JSON object** containing the run result.
The JSON should contain the validation status, flagged categories, drafts, suppressed categories, escalated categories, and overall run status.

Example structure:

```json
{
  "run_status": "success",
  "validation": {
    "passed": true,
    "errors": []
  },
  "flagged_categories": [
    {
      "category": "Ethnic Wear",
      "mom_pct": 77.1,
      "status": "flagged"
    }
  ],
  "drafts": [
    {
      "category": "Ethnic Wear",
      "mom_pct": 77.1,
      "approval_status": "pending_human_review",
      "message": {
        "Context": "...",
        "Insight": "...",
        "Implication": "..."
      }
    }
  ],
  "suppressed_categories": [],
  "escalated_categories": [],
  "human_approval_required": true
}
```

If more than three categories are flagged, the additional categories must appear in `suppressed_categories` with the status: ***suppressed, review manually***.

If an exact-boundary category exists, it must appear in: ***escalated_categories*** with no narrative draft.

If validation fails, the JSON should instead report the Hard Stop:

```json
{
  "run_status": "hard_stop",
  "validation": {
    "passed": false,
    "errors": [
      "line 3: negative revenue (-4200.0) for category=Western Wear",
      "line 4: missing category (month=July)",
      "line 6: missing revenue (category=Home & Kitchen)"
    ]
  },
  "flagged_categories": [],
  "drafts": [],
  "suppressed_categories": [],
  "escalated_categories": [],
  "human_approval_required": false
}
```
***No downstream processing occurs after a validation Hard Stop.***

# 4.3 — Structured JSON Output Schema
Every run of the mock agent runner must emit exactly **one JSON object**.
The object must contain exactly these top-level keys:
1.run_month
2.validation_status
3.validation_errors
4.flagged_categories
5.suppressed_categories
6.escalated_categories
7.action_taken


## Schema
```json
{
  "run_month": "May",
  "validation_status": "valid",
  "validation_errors": [],
  "flagged_categories": [
    {
      "category": "Ethnic Wear",
      "mom_pct": 77.1,
      "previous_revenue": 104520.77,
      "current_revenue": 185107.61,
      "drafted": true,
      "message": {
        "Context": "Ethnic Wear revenue is being compared between April and May.",
        "Insight": "FACT: Ethnic Wear revenue increased from INR 104520.77 in April to INR 185107.61 in May, a 77.1% month-on-month increase.",
        "Implication": "HYPOTHESIS: The increase may be associated with stronger customer demand, higher product availability, or successful promotional activity, but the revenue data alone does not establish the cause."
      }
    }
  ],
  "suppressed_categories": [],
  "escalated_categories": [],
  "action_taken": "drafted_and_held_for_approval"
}
```

## Top-Level Fields

### `run_month`

The current month being processed.
Example: ***"run_month": "May"***

### `validation_status`

Must contain exactly one of:
```
"valid"
"invalid"
```
Use `"valid"` when `validate_feed()` returns `(True, [])`.
Use `"invalid"` when `validate_feed()` returns `(False, errors)`.

### `validation_errors`
A list containing all validation errors returned by `validate_feed()`.

For a successful run: ***"validation_errors": []***

For an invalid feed:

```json
"validation_errors": [
  "line 3: negative revenue (-4200.0) for category=Western Wear",
  "line 4: missing category (month=July)",
  "line 6: missing revenue (category=Home & Kitchen)"
]
```

### `flagged_categories`
A list containing categories whose `is_flagged()` result is exactly `"flagged"`.
Each object must contain:

- `category`
- `mom_pct`
- `previous_revenue`
- `current_revenue`
- `drafted`
- `message` when `drafted` is `true`

Only the top three flagged categories by `abs(mom_pct)` should have: ***"drafted": true***
Flagged categories beyond the top three must have:***"drafted": false*** and must also appear in `suppressed_categories`.

### `suppressed_categories`
A list of category names that were flagged but exceeded the top-3 drafting limit.
Example:
```json
"suppressed_categories": [
  "Category A",
  "Category B"
]
```
If there are three or fewer flagged categories: ***"suppressed_categories": []***

### `escalated_categories`
A list containing category names whose `is_flagged()` result is: ***"escalate_exact_boundary"***
Example:
```json
"escalated_categories": [
  "Example Category"
]
```
For the actual May and June scenarios, this list must be:
```json
"escalated_categories": []
```

because neither scenario contains an actual 8.0% boundary case.
The synthetic Part 2 test with:
```
previous = 100000
current = 108000
```

produces exactly 8.0% and should therefore produce:
```json
"escalated_categories": [
  "Example Category"
]
```

if that synthetic case is passed through the mock runner.
Exact-boundary categories must never appear in `flagged_categories` or `suppressed_categories`.

### `action_taken`
Must contain exactly one of:
```
"drafted_and_held_for_approval"
"hard_stop"
```

Use:
```json
"action_taken": "drafted_and_held_for_approval"
```
when validation succeeds and the agent completes the run.

Use:
```json
"action_taken": "hard_stop"
```
when validation fails.

---

# Hard Stop Output
When validation fails, the runner must still emit exactly one JSON object using the same top-level schema.
Example:
```json
{
  "run_month": "July",
  "validation_status": "invalid",
  "validation_errors": [
    "line 3: negative revenue (-4200.0) for category=Western Wear",
    "line 4: missing category (month=July)",
    "line 6: missing revenue (category=Home & Kitchen)"
  ],
  "flagged_categories": [],
  "suppressed_categories": [],
  "escalated_categories": [],
  "action_taken": "hard_stop"
}
```

When validation fails:
- `flagged_categories` must be empty.
- `suppressed_categories` must be empty.
- `escalated_categories` must be empty.
- No narrative must be drafted.
- `action_taken` must be `"hard_stop"`.

---

# Output Rules
The mock runner must follow these rules:

1. Emit exactly one JSON object per run.
2. Use exactly the seven required top-level keys.
3. Never continue processing after a validation failure.
4. Never draft more than three category messages.
5. Sort flagged categories by `abs(mom_pct)` descending before applying the three-message cap.
6. Record additional flagged categories in `suppressed_categories`.
7. Record exact-boundary categories separately in `escalated_categories`.
8. Never draft a message for an exact-boundary category.
9. Set `drafted` to `true` only for categories that actually receive a Part 3 narrative.
10. Every drafted message must use verified Part 1/Part 2 values.
11. Every drafted message remains held for human approval.
12. May and June runs should have an empty `escalated_categories` list.