# Reusable Narrative Prompt Pack

## Trigger

Run this prompt when a category's `is_flagged` result is exactly `"flagged"`.
If the result is `"not_flagged"`, do not generate a flagged-category narrative.
If the result is `"escalate_exact_boundary"`, stop automatic processing and send the case for human review.

## Input List

The prompt requires these placeholder variables:

- `{category}` — category name
- `{prev_month}` — previous month name
- `{month}` — current month name
- `{previous_revenue}` — revenue in the previous month
- `{current_revenue}` — revenue in the current month
- `{mom_pct}` — calculated Month-on-Month growth percentage
- `{flag_status}` — result from `is_flagged()`
Only supplied input values may be used as facts.

## Prompt

You are drafting a short internal business update for a regional manager at Meesho, about the following flagged category result:

Category: {category}
month: {month}
previous month: {prev_month}
Previous revenue ({prev_month}): INR {previous_revenue}
Current revenue ({month}): INR {current_revenue}
Month-on-month change: {mom_pct}%

Write the update using exactly this three-part structure:

Context - one sentence stating what is being measured and over what period. Mention the category and the comparison period ({month} vs. {prev_month}). Do not include any revenue, percentage, or other numeric value in this section.

Insight - one or two sentences stating the specific revenue figures and the {mom_pct}% change. This must be explicitly labeled as a FACT, and every number here must be one of the six supplied placeholders above, used verbatim (same value, same rounding) - never a number invented, estimated, recalculated, or rounded differently from the source data. The insight must describe only what the supplied data shows and must not claim a cause for the revenue change.

Implication - one or two sentences giving a specific, actionable next step for the regional manager. A vague instruction like "look into this" is not acceptable; name a concrete action such as reviewing the category performance, checking the relevant business data, comparing with a previous period, or validating the change with another business source. If this section proposes "why" the change happened, that statement must be explicitly labeled as a HYPOTHESIS, not stated as settled fact, since the revenue data alone does not prove a cause.


## Prompt Rules

1. Use only the supplied input values.
2. Never invent a reason for a revenue or order change.
3. Do not invent, estimate, calculate, or introduce any additional business facts.
4. Never state a number that is not one of the supplied placeholder values.
5. Use `{mom_pct}` exactly as supplied.
6. Do not independently calculate and introduce a new percentage, revenue amount, order count, or other number.
7. Clearly identify the comparison period, such as "May vs. April".
8. Do not describe a category as flagged unless `{flag_status}` is `"flagged"`.
9. Do not convert a hypothesis into a fact.
10. If a possible reason is not present in the supplied inputs, describe it as something that should be investigated rather than as an established cause.
11. Do not reveal confidential reseller names. If a reseller is provided, use only its approved coded alias.
12. Categories are region/product-level, not reseller-level, so this rule should be followed consistently with the masking policy used elsewhere in this project.
13. Keep the narrative concise and suitable for an internal regional manager update.
14. Return only the three sections:
        Context:
        Insight:
        Implication:

## Checklist
  Before using the generated narrative, verify all of the following:
1. Number accuracy: Does every number in the draft exactly match one of the supplied placeholder values?
2. No invented causes: Does the narrative avoid claiming a reason for the revenue change unless that reason was explicitly supplied?
3. Fact vs hypothesis: Is every factual statement supported by the input data, and is any hypothesis clearly identified as a hypothesis?
4. Actionability: Is the implication specific and actionable rather than vague?
5. Period accuracy: Does the narrative clearly identify the correct month comparison, such as "May vs. April"?
6. Flag accuracy: Is the category described as flagged only when {flag_status} is "flagged"?
7. Confidentiality: Is any reseller or internal entity referenced only by its approved coded alias and never by its raw internal name?
8. No unsupported numbers: Has the narrative avoided calculating or introducing additional numbers that were not supplied as inputs?
9. Structure: Does the output contain Context → Insight → Implication in that order?
10. Human review: If the status is "escalate_exact_boundary", has the automatic decision been stopped and sent for human review?