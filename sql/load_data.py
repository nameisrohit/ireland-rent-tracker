# sql/load_data.py
# ============================================================
# Loads data from S3 into Redshift using COPY command
#
# What is COPY?
# Redshift's COPY command is the fastest way to load data.
# It reads directly from S3 in parallel.
# Much faster than INSERT row by row.
# This is what every data engineer uses in production.
# ============================================================

import psycopg2
import boto3
import os
from dotenv import load_dotenv

load_dotenv()

def get_connection():
    return psycopg2.connect(
        host=os.getenv("REDSHIFT_HOST"),
        port=int(os.getenv("REDSHIFT_PORT", 5439)),
        dbname=os.getenv("REDSHIFT_DB", "dev"),
        user=os.getenv("REDSHIFT_USER"),
        password=os.getenv("REDSHIFT_PASSWORD"),
        connect_timeout=10,
        sslmode="require"
    )

def get_iam_role_arn():
    """
    Gets the IAM role ARN attached to Redshift.
    Redshift uses this role to read from S3.
    ARN = Amazon Resource Name — unique ID for any AWS resource.
    """
    client = boto3.client("redshift-serverless", region_name="eu-west-1")
    response = client.get_namespace(
        namespaceName="ireland-rent-tracker"
    )
    roles = response["namespace"].get("iamRoles", [])
    if not roles:
        raise Exception("No IAM role found. Check AWS console.")

    # Extract just the ARN string from the IamRole object
    role = roles[0]
    if hasattr(role, 'iamRoleArn'):
        arn = role.iamRoleArn
    else:
        arn = str(role).split("iamRoleArn=")[1].split(",")[0].strip(")")

    print(f"   IAM Role ARN: {arn}")
    return arn

def get_latest_s3_file():
    """
    Finds the most recent file in S3.
    We always load the latest scrape.
    """
    s3 = boto3.client("s3", region_name="eu-west-1")
    bucket = os.getenv("S3_BUCKET")
    prefix = "raw/rtb/"

    response = s3.list_objects_v2(Bucket=bucket, Prefix=prefix)

    if "Contents" not in response:
        raise Exception("No files found in S3. Run the scraper first.")

    # Sort by last modified — get the newest file
    files = sorted(
        response["Contents"],
        key=lambda x: x["LastModified"],
        reverse=True
    )

    latest = files[0]["Key"]
    print(f"   Latest S3 file: s3://{bucket}/{latest}")
    return f"s3://{bucket}/{latest}"

def truncate_raw_table(cursor):
    """
    Clears the raw_data table before loading fresh data.
    Truncate + reload = always fresh, no duplicates.
    This is called a full refresh pattern.
    """
    print("🗑️  Truncating raw_data table...")
    cursor.execute("TRUNCATE TABLE raw_data.rtb_rents;")
    print("   ✅ Table cleared")

def load_s3_to_redshift(cursor, s3_path, iam_role):
    """
    Uses Redshift COPY command to load S3 data.

    COPY is Redshift's superpower:
    - Reads S3 files in parallel
    - Handles CSV parsing automatically
    - Loads millions of rows in seconds
    - Industry standard for Redshift data loading
    """
    print(f"📥 Loading data from S3 into Redshift...")

    copy_sql = f"""
        COPY raw_data.rtb_rents (
            year,
            bedrooms,
            property_type,
            location_code,
            location,
            avg_monthly_rent,
            county,
            scraped_at
        )
        FROM '{s3_path}'
        IAM_ROLE '{iam_role}'
        FORMAT AS CSV
        IGNOREHEADER 1
        REGION 'eu-west-1'
        TIMEFORMAT 'auto'
        ACCEPTINVCHARS;
    """

    cursor.execute(copy_sql)
    print("   ✅ COPY command executed")

def verify_load(cursor):
    """
    Checks how many rows were loaded.
    Always verify after loading — never assume it worked.
    """
    cursor.execute("SELECT COUNT(*) FROM raw_data.rtb_rents;")
    count = cursor.fetchone()[0]
    print(f"   ✅ Rows in Redshift: {count:,}")

    cursor.execute("""
        SELECT year, county, avg_monthly_rent
        FROM raw_data.rtb_rents
        ORDER BY year DESC
        LIMIT 5;
    """)
    rows = cursor.fetchall()
    print("\n   Sample rows:")
    for row in rows:
        print(f"   Year: {row[0]} | County: {row[1]} | Rent: €{row[2]}")

def main():
    print("🚀 Loading S3 data into Redshift")
    print("=" * 50)

    print("🔍 Getting IAM role and S3 file...")
    iam_role = get_iam_role_arn()
    s3_path  = get_latest_s3_file()

    conn = get_connection()
    conn.autocommit = True
    cursor = conn.cursor()

    truncate_raw_table(cursor)
    load_s3_to_redshift(cursor, s3_path, iam_role)
    verify_load(cursor)

    cursor.close()
    conn.close()

    print("=" * 50)
    print("🎉 Data loaded into Redshift successfully!")

if __name__ == "__main__":
    main()