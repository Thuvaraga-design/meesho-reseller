"""Run the monthly growth workflow without sending or externally generating messages."""

import argparse
import calendar
import csv
import json
import sys
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from part2_engine.growth_engine import is_flagged, mom_growth, validate_feed


def _read_rows(csv_path: str) -> list[dict[str, str]]:
    with open(csv_path, "r", newline="", encoding="utf-8") as file:
        return list(csv.DictReader(file))


def _month_rows(
    rows: list[dict[str, str]], month: str, csv_path: str
) -> list[dict[str, str]]:
    matches = [
        row for row in rows
        if row["month"].strip().casefold() == month.strip().casefold()
    ]
    if not matches:
        raise ValueError(f"No rows for month {month!r} in {csv_path!r}")
    return matches


def _previous_month_rows(
    rows: list[dict[str, str]], current_month: str, csv_path: str
) -> tuple[str, list[dict[str, str]]]:
    available_months = list(dict.fromkeys(row["month"].strip() for row in rows))
    if len(available_months) == 1:
        previous_month = available_months[0]
        if previous_month.casefold() == current_month.strip().casefold():
            raise ValueError("Previous-month feed contains the current month")
    else:
        current_index = next(
            (
                index
                for index in range(1, 13)
                if calendar.month_name[index].casefold() == current_month.strip().casefold()
                or calendar.month_abbr[index].casefold() == current_month.strip().casefold()
            ),
            None,
        )
        if current_index is None:
            raise ValueError(
                f"Cannot determine the previous month for {current_month!r}"
            )
        previous_name = calendar.month_name[(current_index - 2) % 12 + 1]
        available = {name.casefold(): name for name in available_months}
        previous_month = available.get(previous_name.casefold())
        if previous_month is None:
            raise ValueError(
                f"No previous-month rows for {current_month!r} in {csv_path!r}"
            )

    return previous_month, _month_rows(rows, previous_month, csv_path)


def _revenue_by_category(
    rows: list[dict[str, str]], month: str, csv_path: str
) -> dict[str, tuple[float, str]]:
    revenue_by_category: dict[str, tuple[float, str]] = {}
    for row in _month_rows(rows, month, csv_path):
        category = row["category"].strip()
        if category in revenue_by_category:
            raise ValueError(
                f"Duplicate revenue row for category {category!r} in month {month!r}"
            )
        revenue_text = row["revenue"].strip()
        revenue_by_category[category] = (float(revenue_text), revenue_text)
    return revenue_by_category


def _fill_narrative(
    category: str,
    previous_month: str,
    month: str,
    previous_revenue: str,
    current_revenue: str,
    mom_pct: float,
) -> dict[str, str]:
    """Fill the Part 3 Context, Insight, and Implication narrative from verified values."""
    values = {
        "category": category,
        "prev_month": previous_month,
        "month": month,
        "previous_revenue": previous_revenue,
        "current_revenue": current_revenue,
        "mom_pct": str(mom_pct),
    }
    return {
        "Context": (
            "{category} revenue is being compared between {prev_month} and {month}."
        ).format(**values),
        "Insight": (
            "FACT: {category} revenue moved from INR {previous_revenue} in "
            "{prev_month} to INR {current_revenue} in {month}, a "
            "{mom_pct}% month-on-month change."
        ).format(**values),
        "Implication": (
            "The regional manager should review the category's sales, order, "
            "inventory, and campaign records for {prev_month} and {month} to "
            "identify which factors warrant further investigation."
        ).format(**values),
    }


def run(month: str, previous_month_csv: str, current_month_csv: str) -> dict[str, Any]:
    """Validate two monthly feeds and return the Part 4.3 run result."""
    previous_valid, previous_errors = validate_feed(previous_month_csv)
    current_valid, current_errors = validate_feed(current_month_csv)
    validation_errors = previous_errors + current_errors
    validation_passed = previous_valid and current_valid

    result: dict[str, Any] = {
        "run_month": month,
        "validation_status": "valid" if validation_passed else "invalid",
        "validation_errors": validation_errors,
        "flagged_categories": [],
        "suppressed_categories": [],
        "escalated_categories": [],
        "action_taken": (
            "drafted_and_held_for_approval" if validation_passed else "hard_stop"
        ),
    }
    if not validation_passed:
        return result

    previous_rows = _read_rows(previous_month_csv)
    current_rows = _read_rows(current_month_csv)
    previous_month, previous_month_rows = _previous_month_rows(
        previous_rows, month, previous_month_csv
    )
    previous_revenue = _revenue_by_category(
        previous_month_rows, previous_month, previous_month_csv
    )
    current_revenue = _revenue_by_category(current_rows, month, current_month_csv)

    missing_previous = [
        category for category in current_revenue if category not in previous_revenue
    ]
    if missing_previous:
        raise ValueError(
            "Missing previous-month revenue for categories: "
            + ", ".join(missing_previous)
        )

    flagged: list[dict[str, Any]] = []
    for category, (current_value, current_text) in current_revenue.items():
        previous_value, previous_text = previous_revenue[category]
        mom_pct = mom_growth(previous_value, current_value)
        status = is_flagged(mom_pct)
        if status == "flagged":
            flagged.append(
                {
                    "category": category,
                    "mom_pct": mom_pct,
                    "previous_revenue": previous_value,
                    "current_revenue": current_value,
                    "previous_revenue_text": previous_text,
                    "current_revenue_text": current_text,
                }
            )
        elif status == "escalate_exact_boundary":
            result["escalated_categories"].append(category)

    flagged.sort(key=lambda item: abs(item["mom_pct"]), reverse=True)
    for index, category_result in enumerate(flagged):
        drafted = index < 3
        category_result["drafted"] = drafted
        if drafted:
            category_result["message"] = _fill_narrative(
                category_result["category"],
                previous_month,
                month,
                category_result.pop("previous_revenue_text"),
                category_result.pop("current_revenue_text"),
                category_result["mom_pct"],
            )
        else:
            category_result.pop("previous_revenue_text")
            category_result.pop("current_revenue_text")
            result["suppressed_categories"].append(category_result["category"])

    result["flagged_categories"] = flagged
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("month", help="Current month being processed")
    parser.add_argument(
        "previous_month_csv", help="CSV containing previous-month revenue"
    )
    parser.add_argument(
        "current_month_csv", help="CSV containing current-month revenue"
    )
    arguments = parser.parse_args()
    print(json.dumps(run(
        arguments.month,
        arguments.previous_month_csv,
        arguments.current_month_csv,
    ), indent=2))
