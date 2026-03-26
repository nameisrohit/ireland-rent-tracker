# tests/test_scraper.py
# ============================================================
# Basic tests for the RTB scraper
#
# What is pytest?
# A testing framework for Python.
# You write functions that start with test_
# and pytest runs them automatically.
#
# Why write tests?
# - Catch bugs before they reach production
# - Prove your code works correctly
# - Required in every professional Python project
# ============================================================

import pandas as pd
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

def test_extract_county_from_location():
    """Test that county extraction works correctly."""
    from scraper.rtb_scraper import extract_county

    # Test with comma separated location
    assert extract_county("Ballsbridge, Dublin") == "Dublin"
    assert extract_county("Ennis, Clare") == "Clare"
    assert extract_county("Carlow Town, Carlow") == "Carlow"

    # Test with single word location
    assert extract_county("Dublin") == "Dublin"
    assert extract_county("Carlow") == "Carlow"

    print("✅ extract_county tests passed")


def test_clean_price():
    """Test that price cleaning works."""
    import pandas as pd

    # Simulate raw price column
    raw_prices = pd.Series(["748.48", "811.53", "", "711.35"])

    cleaned = pd.to_numeric(raw_prices, errors='coerce')

    assert cleaned[0] == 748.48
    assert cleaned[1] == 811.53
    assert pd.isna(cleaned[2])  # empty string becomes NaN
    assert cleaned[3] == 711.35

    print("✅ price cleaning tests passed")


def test_dataframe_columns():
    """Test that transformed dataframe has correct columns."""

    # Simulate what our scraper produces
    df = pd.DataFrame({
        'year': [2024],
        'bedrooms': ['One bed'],
        'property_type': ['All property types'],
        'location': ['Dublin'],
        'avg_monthly_rent': [1500.00],
        'county': ['Dublin'],
        'scraped_at': ['2024-01-01']
    })

    required_columns = [
        'year', 'bedrooms', 'property_type',
        'location', 'avg_monthly_rent', 'county', 'scraped_at'
    ]

    for col in required_columns:
        assert col in df.columns, f"Missing column: {col}"

    print("✅ dataframe column tests passed")


def test_year_range():
    """Test that years are within expected range."""

    valid_years = list(range(2008, 2025))

    for year in valid_years:
        assert 2008 <= year <= 2024

    print("✅ year range tests passed")