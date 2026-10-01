# Meesho Reseller Growth & Alert Intelligence Pipeline

This project analyzes reseller and category sales data, calculates monthly revenue changes, and drafts updates for human review. It uses local Python, SQLite, and CSV files. **No API keys are required, and no messages are sent.**

## Requirements

- Python 3
- `pytest` to run the tests

Install pytest from the project root:

```powershell
python -m pip install pytest
```

## Regenerate the dataset

From the project root, run:

```powershell
python data/generate_seed_data.py
```

This regenerates the reseller and order CSV files and the SQLite database in the `data/` folder. The script uses a fixed random seed, so the generated data is repeatable.

## Run every part in order

Run each command from the project root.

### Part 1 — SQL analysis

The seed-generation command above creates `data/meesho_reseller.db`. Run the queries in `part1_sql/queries.sql` against that database using SQLite.

Export the monthly category revenue query results to:

```text
part1_sql/output/monthly_category_revenue.csv
```

Parts 2 and 4 use this CSV.

### Part 2 — Growth engine

Run the Part 2 tests:

```powershell
python -m pytest -q part2_engine/test_growth_engine.py
```

This part validates revenue feeds, calculates month-on-month growth, and classifies changes against the 8% threshold.

### Part 3 — Narrative and masking

Run the Part 3 tests:

```powershell
python -m pytest -q part3_narrative/test_masking.py
```

The reusable narrative prompt is in `part3_narrative/prompt_pack.md`. Worked examples are in `part3_narrative/narrative_report.md`.

### Part 4 — Mock agent runner

Run the Part 4 tests:

```powershell
python -m pytest -q part4_agent/test_mock_agent_runner.py
```

Run the May scenario:

```powershell
python -m part4_agent.mock_agent_runner May part1_sql/output/monthly_category_revenue.csv part1_sql/output/monthly_category_revenue.csv
```

Run the June scenario:

```powershell
python -m part4_agent.mock_agent_runner June part1_sql/output/monthly_category_revenue.csv part1_sql/output/monthly_category_revenue.csv
```

Check the invalid-feed hard stop:

```powershell
python -m part4_agent.mock_agent_runner July part1_sql/output/monthly_category_revenue.csv part2_engine/fixtures/corrupted_feed.csv
```

Each run prints one JSON object. The runner validates the feeds, calculates and sorts flagged changes by absolute percentage, drafts messages for at most the top three categories, and records suppressed or exact-boundary categories separately. Drafts are held for human approval. No messages are sent.

## API keys and external services

The complete pipeline runs with **zero API keys set**. It uses local Python code, SQLite, CSV files, and a prompt-pack template. It makes no network or API calls and does not connect to a messaging service.

## Workflow pattern

- **Part 1 → Part 2:** Compute real numbers with SQL first, then hand the verified revenue data to the growth engine.
- **Part 2:** Validate inputs before calculating metrics, then apply a clear threshold decision.
- **Part 3:** Turn verified results into a Context → Insight → Implication narrative, with masking rules for reseller information.
- **Part 4:** Follow an **Intake → Summary → Report Draft → Validate** flow: validate the feed, summarize category changes, draft a capped number of messages, and hold them for human approval.
