# scraper/rtb_scraper.py
# ============================================================
# Ireland Rent Tracker — RTB Data Scraper
#
# ETL Pipeline:
# E = Extract  → Download from CSO API
# T = Transform → Clean columns, fix types, remove nulls
# L = Load      → Upload to S3
# ============================================================

import requests
import certifi
import pandas as pd
import boto3
from io import BytesIO, StringIO
from datetime import datetime

# ============================================================
# CONFIGURATION
# ============================================================

RTB_URL = "https://ws.cso.ie/public/api.restful/PxStat.Data.Cube_API.ReadDataset/RIA02/CSV/1.0/en"
S3_BUCKET = "ireland-rent-tracker-raw-data"
S3_PREFIX = "raw/rtb/"

# ============================================================
# FUNCTION 1 — EXTRACT
# ============================================================

def extract_rtb_data(url):
    """
    Downloads RTB rental data from the CSO API.
    Handles BOM characters that government CSV files often have.
    
    BOM = Byte Order Mark — an invisible character at the start
    of some files that breaks column name detection.
    """

    print(f"📥 Downloading RTB data from CSO API...")

    response = requests.get(url, timeout=60, verify=certifi.where())
    response.raise_for_status()

    # Read CSV — utf-8-sig encoding automatically strips BOM
    # This is the clean way to handle government CSV files
    df = pd.read_csv(
        StringIO(response.text),
        encoding_errors="replace"
    )

    # Strip BOM and quotes from ALL column names
    # Government files often have "STATISTIC" with quotes
    df.columns = [
        col.encode("ascii", "ignore")
           .decode("ascii")
           .strip()
           .strip('"')
        for col in df.columns
    ]

    print(f"✅ Downloaded {len(df):,} rows")
    print(f"📋 Columns: {list(df.columns)}")

    return df

# ============================================================
# FUNCTION 2 — TRANSFORM
# ============================================================

def transform_rtb_data(df):
    """
    Cleans raw RTB data into a consistent, usable format.
    
    What we fix:
    - Cryptic column names → readable names
    - Drop columns we don't need
    - Convert rent from string → number
    - Remove rows with no rent value
    - Extract county from location
    - Add scrape timestamp
    """

    print("🧹 Transforming data...")
    print(f"   Raw columns: {list(df.columns)}")

    # ── Step 1: Rename columns ──
    df = df.rename(columns={
        "STATISTIC":           "statistic_code",
        "STATISTIC Label":     "statistic_label",
        "TLIST(A1)":           "year_code",
        "Year":                "year",
        "C02970V03592":        "bedroom_code",
        "Number of Bedrooms":  "bedrooms",
        "C02969V03591":        "property_code",
        "Property Type":       "property_type",
        "C03004V03625":        "location_code",
        "Location":            "location",
        "UNIT":                "unit",
        "VALUE":               "avg_monthly_rent"
    })

    # ── Step 2: Drop columns we don't need ──
    cols_to_drop = [
        c for c in [
            "statistic_code", "statistic_label",
            "year_code", "bedroom_code",
            "property_code", "unit"
        ] if c in df.columns
    ]
    df = df.drop(columns=cols_to_drop)

    # ── Step 3: Clean rent value — string to number ──
    # Empty strings become NaN (Not a Number)
    df["avg_monthly_rent"] = pd.to_numeric(
        df["avg_monthly_rent"],
        errors="coerce"
    )

    # ── Step 4: Drop rows with no rent value ──
    before = len(df)
    df = df.dropna(subset=["avg_monthly_rent"])
    after = len(df)
    print(f"   Removed {before - after:,} rows with missing rent")

    # ── Step 5: Convert year to integer ──
    df["year"] = df["year"].astype(int)

    # ── Step 6: Clean text columns ──
    df["location"]      = df["location"].str.strip()
    df["bedrooms"]      = df["bedrooms"].str.strip()
    df["property_type"] = df["property_type"].str.strip()

    # ── Step 7: Extract county from location ──
    # 'Ballsbridge, Dublin' → 'Dublin'
    # 'Carlow'              → 'Carlow'
    df["county"] = df["location"].apply(extract_county)

    # ── Step 8: Add scrape timestamp ──
    df["scraped_at"] = datetime.now().isoformat()

    print(f"✅ Transform complete — {len(df):,} clean rows")
    print(f"   Years: {df['year'].min()} to {df['year'].max()}")
    print(f"   Locations: {df['location'].nunique():,} unique areas")
    print(f"   Counties: {df['county'].nunique()} unique counties")

    return df


def extract_county(location):
    """
    Extracts county from location string.
    
    'Ballsbridge, Dublin' → 'Dublin'
    'Carlow Town'         → 'Carlow Town'
    'Ennis, Clare'        → 'Clare'
    """
    if "," in location:
        return location.split(",")[-1].strip()
    return location

# ============================================================
# FUNCTION 3 — LOAD
# ============================================================

def load_to_s3(df, bucket, prefix):
    """
    Uploads cleaned DataFrame to AWS S3.
    
    Each run creates a NEW file — nothing is overwritten.
    This is called immutable data — industry standard practice.
    You can always go back to any day's data.
    """

    print(f"☁️  Loading to S3...")

    today = datetime.now().strftime("%Y-%m-%d")
    filename = f"rtb_rents_{today}.csv"
    s3_key = f"{prefix}{filename}"

    # Write to memory buffer — no temp file on disk
    csv_buffer = BytesIO()
    df.to_csv(csv_buffer, index=False, encoding="utf-8")
    csv_buffer.seek(0)

    s3 = boto3.client("s3", region_name="eu-west-1")
    s3.put_object(
        Bucket=bucket,
        Key=s3_key,
        Body=csv_buffer.getvalue(),
        ContentType="text/csv"
    )

    print(f"✅ Uploaded to s3://{bucket}/{s3_key}")
    return s3_key

# ============================================================
# MAIN
# ============================================================

def main():
    print("🚀 Ireland Rent Tracker — RTB Scraper")
    print("=" * 50)

    # Extract
    raw_df = extract_rtb_data(RTB_URL)

    # Transform
    clean_df = transform_rtb_data(raw_df)

    # Preview
    print("\n📊 Sample of clean data:")
    print(clean_df.head(3).to_string())
    print()

    # Load
    s3_key = load_to_s3(clean_df, S3_BUCKET, S3_PREFIX)

    print("=" * 50)
    print(f"🎉 Pipeline complete!")
    print(f"   Rows uploaded : {len(clean_df):,}")
    print(f"   S3 location   : s3://{S3_BUCKET}/{s3_key}")

if __name__ == "__main__":
    main()