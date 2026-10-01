from growth_engine import mom_growth, is_flagged, validate_feed

def test_ethnic_wear_april_to_may():
    # GIVEN April → May Ethnic Wear revenue
    previous = 104520.77
    current = 185107.61

    # WHEN evaluated
    growth = mom_growth(previous, current)
    result = is_flagged(growth)

    # THEN
    assert growth == 77.1
    assert result == "flagged"

def test_beauty_may_to_june():
    # GIVEN May → June Beauty & Personal Care revenue
    previous = 35542.11
    current = 37559.07

    # WHEN evaluated
    growth = mom_growth(previous, current)
    result = is_flagged(growth)

    # THEN
    assert growth == 5.67
    assert result == "not_flagged"

def test_exact_threshold_boundary():
    # GIVEN exactly 8% growth
    previous = 100000
    current = 108000

    # WHEN evaluated
    growth = mom_growth(previous, current)
    result = is_flagged(growth)

    # THEN
    assert growth == 8.0
    assert result == "escalate_exact_boundary"

def test_corrupted_feed():
    # GIVEN corrupted CSV
    csv_path = "fixtures/corrupted_feed.csv"

    # WHEN validated
    valid, errors = validate_feed(csv_path)

    # THEN
    assert valid is False

    assert errors == [
        "line 3: negative revenue (-4200.0) for category=Western Wear",
        "line 4: missing category (month=July)",
        "line 6: missing revenue (category=Home & Kitchen)",
    ]

def test_valid_monthly_category_revenue():
    csv_path = "../part1_sql/output/monthly_category_revenue.csv"

    valid, errors = validate_feed(csv_path)

    assert valid is True
    assert errors == []

def test_may_vs_april():
    data = {
        "Ethnic Wear": (104520.77, 185107.61),
        "Beauty & Personal Care": (40737.01, 35542.11),
        "Home & Kitchen":(100446.23, 91152.57),
        "Kids Wear": (59847.27, 45793.78),
        "Western Wear": (113866.15, 86998.18)
    }

    for category, (previous, current) in data.items():
        growth = mom_growth(previous, current)
        result = is_flagged(growth)

        print(category, growth, result)


def test_june_vs_may():
    data = {
        "Ethnic Wear": (185107.61, 76371.53),
        "Beauty & Personal Care": (35542.11, 37559.07),
        "Home & Kitchen":(91152.57, 129971.22),
        "Kids Wear": (45793.78, 56737.78),
        "Western Wear": (86998.18, 97415.64)
    }

    for category, (previous, current) in data.items():
        growth = mom_growth(previous, current)
        result = is_flagged(growth)

        print(category, growth, result)