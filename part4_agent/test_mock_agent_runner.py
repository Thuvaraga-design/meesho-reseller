import csv
import re
from pathlib import Path

import part4_agent.mock_agent_runner as mock_agent_runner
from part4_agent.mock_agent_runner import run


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_june_run_sorts_flags_caps_drafts_and_suppresses_remaining():
    revenue_csv = str(
        PROJECT_ROOT / "part1_sql" / "output" / "monthly_category_revenue.csv"
    )

    result = run("June", revenue_csv, revenue_csv)

    assert result["validation_status"] == "valid"
    assert len([entry for entry in result["flagged_categories"] if entry["drafted"]]) == 3
    assert [entry["category"] for entry in result["flagged_categories"]] == [
        "Ethnic Wear",
        "Home & Kitchen",
        "Kids Wear",
        "Western Wear",
    ]
    assert [round(entry["mom_pct"], 2) for entry in result["flagged_categories"]] == [
        -58.74,
        42.59,
        23.9,
        11.97,
    ]
    assert [entry["drafted"] for entry in result["flagged_categories"]] == [
        True,
        True,
        True,
        False,
    ]
    assert result["suppressed_categories"] == ["Western Wear"]
    assert all(
        entry["category"] != "Beauty & Personal Care"
        for entry in result["flagged_categories"]
    )
    assert "Beauty & Personal Care" not in result["suppressed_categories"]
    assert result["escalated_categories"] == []
    assert result["action_taken"] == "drafted_and_held_for_approval"


def test_exact_boundary_is_escalated_without_a_draft(tmp_path):
    previous_csv = tmp_path / "previous.csv"
    current_csv = tmp_path / "current.csv"
    for path, month, revenue in (
        (previous_csv, "April", "100000"),
        (current_csv, "May", "108000"),
    ):
        with path.open("w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(["month", "category", "revenue", "n_orders"])
            writer.writerow([month, "Example Category", revenue, "1"])

    result = run("May", str(previous_csv), str(current_csv))

    assert result["flagged_categories"] == []
    assert result["suppressed_categories"] == []
    assert result["escalated_categories"] == ["Example Category"]


def test_may_run_has_no_escalations():
    revenue_csv = str(
        PROJECT_ROOT / "part1_sql" / "output" / "monthly_category_revenue.csv"
    )

    result = run("May", revenue_csv, revenue_csv)

    assert result["validation_status"] == "valid"
    assert result["escalated_categories"] == []


def test_invalid_feed_hard_stops_with_engine_errors(monkeypatch):
    valid_csv = str(
        PROJECT_ROOT / "part1_sql" / "output" / "monthly_category_revenue.csv"
    )
    corrupted_csv = str(
        PROJECT_ROOT / "part2_engine" / "fixtures" / "corrupted_feed.csv"
    )

    def fail_if_mom_is_computed(*args, **kwargs):
        raise AssertionError("MoM must not be computed for an invalid feed")

    monkeypatch.setattr(mock_agent_runner, "mom_growth", fail_if_mom_is_computed)

    result = run("July", valid_csv, corrupted_csv)

    assert result["validation_status"] == "invalid"
    assert result["action_taken"] == "hard_stop"
    assert result["validation_errors"] == [
        "line 3: negative revenue (-4200.0) for category=Western Wear",
        "line 4: missing category (month=July)",
        "line 6: missing revenue (category=Home & Kitchen)",
    ]
    assert result["flagged_categories"] == []
    assert result["suppressed_categories"] == []
