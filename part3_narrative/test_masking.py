from masking import alias_for, assert_no_raw_names_leak


def test_alias_for():
    assert alias_for("RS019") == "ALIAS-19"
    assert alias_for("RS006") == "ALIAS-06"


def test_raw_name_leak_is_detected():
    text = "West region Mumbai Reseller 1 generated strong revenue."

    reseller_names = [
        "Mumbai Reseller 1",
        "Mumbai Reseller 4",
        "Hyderabad Reseller 6",
        "Lucknow Reseller 6",
        "Jaipur Reseller 5",
    ]

    assert assert_no_raw_names_leak(text, reseller_names) is False


def test_final_narrative_has_no_raw_names():
    final_narrative = "West region - ALIAS-19: total revenue of INR 75295.09. North region - ALIAS-05: total revenue of INR 61825.02."
    
    reseller_names = [
        "Mumbai Reseller 1",
        "Mumbai Reseller 4",
        "Hyderabad Reseller 6",
        "Lucknow Reseller 6",
        "Jaipur Reseller 5",
    ]

    assert assert_no_raw_names_leak(
        final_narrative,
        reseller_names
    ) is True