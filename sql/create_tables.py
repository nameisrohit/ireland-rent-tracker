# sql/create_tables.py
# ============================================================
# Creates all schemas and tables in Redshift
# Run this ONCE to set up the database structure
#
# We create 3 schemas — this is called medallion architecture:
# raw     = bronze layer — data exactly as it came from S3
# staging = silver layer — cleaned and standardised
# marts   = gold layer   — ready for dashboard
# ============================================================

import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

def get_connection():
    """
    Creates a connection to Redshift.
    We reuse this function everywhere — DRY principle.
    DRY = Don't Repeat Yourself — core coding principle.
    """
    return psycopg2.connect(
        host=os.getenv("REDSHIFT_HOST"),
        port=int(os.getenv("REDSHIFT_PORT", 5439)),
        dbname=os.getenv("REDSHIFT_DB", "dev"),
        user=os.getenv("REDSHIFT_USER"),
        password=os.getenv("REDSHIFT_PASSWORD"),
        connect_timeout=10,
        sslmode="require"
    )

def create_schemas(cursor):
    """
    Creates schemas in Redshift.
    Redshift doesn't support IF NOT EXISTS for schemas
    so we check if it exists first then create it.
    """
    print("📁 Creating schemas...")

    schemas = ["raw_data", "staging", "marts"]
    for schema in schemas:
        # Check if schema already exists
        cursor.execute("""
            SELECT count(*)
            FROM pg_namespace
            WHERE nspname = %s;
        """, (schema,))

        exists = cursor.fetchone()[0]

        if not exists:
            cursor.execute(f"CREATE SCHEMA {schema};")
            print(f"   ✅ Created schema: {schema}")
        else:
            print(f"   ⏭️  Schema already exists: {schema}")

def create_raw_tables(cursor):
    """
    Creates the raw layer table.
    This matches exactly what our scraper produces.
    Column names and types match our CSV file.
    """
    print("📋 Creating raw tables...")

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS raw_data.rtb_rents (
            year                INTEGER,
            bedrooms            VARCHAR(50),
            property_type       VARCHAR(100),
            location_code       VARCHAR(20),
            location            VARCHAR(200),
            avg_monthly_rent    DECIMAL(10, 2),
            county              VARCHAR(100),
            scraped_at          VARCHAR(50)
        );
    """)
    print("   ✅ Table: raw_data.rtb_rents")

def create_staging_tables(cursor):
    """
    Creates staging layer tables.
    These will be populated by dbt later.
    For now we just create the structure.
    """
    print("📋 Creating staging tables...")

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS staging.stg_rents (
            year                INTEGER,
            bedrooms            VARCHAR(50),
            property_type       VARCHAR(100),
            location            VARCHAR(200),
            county              VARCHAR(100),
            avg_monthly_rent    DECIMAL(10, 2),
            scraped_at          VARCHAR(50)
        );
    """)
    print("   ✅ Table: staging.stg_rents")

def create_mart_tables(cursor):
    """
    Creates mart layer tables — final business-ready tables.
    These feed directly into the dashboard.
    
    We create 4 marts:
    1. rent_by_county     — average rent per county per year
    2. rent_by_bedrooms   — average rent by bedroom count
    3. rent_trends        — year on year change
    4. falling_rents      — areas where rent is dropping
    """
    print("📋 Creating mart tables...")

    # Mart 1 — Rent by county
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS marts.rent_by_county (
            year                INTEGER,
            county              VARCHAR(100),
            avg_monthly_rent    DECIMAL(10, 2),
            yoy_change_pct      DECIMAL(10, 2)
        );
    """)
    print("   ✅ Table: marts.rent_by_county")

    # Mart 2 — Rent by bedrooms
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS marts.rent_by_bedrooms (
            year                INTEGER,
            county              VARCHAR(100),
            bedrooms            VARCHAR(50),
            avg_monthly_rent    DECIMAL(10, 2)
        );
    """)
    print("   ✅ Table: marts.rent_by_bedrooms")

    # Mart 3 — National trends
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS marts.national_trends (
            year                INTEGER,
            avg_monthly_rent    DECIMAL(10, 2),
            yoy_change_pct      DECIMAL(10, 2),
            min_rent            DECIMAL(10, 2),
            max_rent            DECIMAL(10, 2)
        );
    """)
    print("   ✅ Table: marts.national_trends")

    # Mart 4 — Falling rents
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS marts.falling_rents (
            county              VARCHAR(100),
            location            VARCHAR(200),
            year                INTEGER,
            avg_monthly_rent    DECIMAL(10, 2),
            prev_year_rent      DECIMAL(10, 2),
            change_pct          DECIMAL(10, 2)
        );
    """)
    print("   ✅ Table: marts.falling_rents")

def main():
    print("🚀 Setting up Redshift database structure")
    print("=" * 50)

    conn = get_connection()

    # autocommit = True means each SQL statement
    # runs immediately without needing conn.commit()
    conn.autocommit = True
    cursor = conn.cursor()

    create_schemas(cursor)
    create_raw_tables(cursor)
    create_staging_tables(cursor)
    create_mart_tables(cursor)

    cursor.close()
    conn.close()

    print("=" * 50)
    print("🎉 Database structure ready!")

if __name__ == "__main__":
    main()