import csv

# Calculate Month-on-Month growth percentage
def mom_growth(previous_month: float, current_month: float) -> float:
    return round((current_month - previous_month) / previous_month * 100, 2)

# Flag a category if the absolute value of the month-on-month growth percentage exceeds a threshold
def is_flagged(mom_pct: float, threshold: float = 8.0) -> str:
    if abs(mom_pct) > threshold:
        return "flagged"
    elif abs(mom_pct) < threshold:
        return "not_flagged"
    else:
        return "escalate_exact_boundary"


# Validate the feed for missing or invalid data
def validate_feed(csv_path: str) -> tuple[bool, list[str]]:
    errors = []
    with open(csv_path, "r", newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for line_number, row in enumerate(reader, start=2):
            month = row["month"]
            category = row["category"]
            revenue = row["revenue"]

            # Check missing category
            if category.strip() == "":
                errors.append(f"line {line_number}: missing category (month={month})")

            # Check missing revenue
            if revenue.strip() == "":
                errors.append(f"line {line_number}: missing revenue (category={category})")
                continue

            # Check whether revenue is numeric
            try:
                revenue_value = float(revenue)

            except ValueError:
                errors.append(f"line {line_number}: revenue not numeric: {revenue!r}")
                continue

            # Check negative revenue
            if revenue_value < 0:
                errors.append(f"line {line_number}: negative revenue "
                    f"({revenue_value}) for category={category}")

    if len(errors) == 0:
        return True, []

    return False, errors