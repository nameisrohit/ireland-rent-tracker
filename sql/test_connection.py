# sql/test_connection.py
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

def test_connection():
    print("🔌 Testing Redshift connection...")

    try:
        conn = psycopg2.connect(
            host=os.getenv("REDSHIFT_HOST"),
            port=int(os.getenv("REDSHIFT_PORT", 5439)),
            dbname=os.getenv("REDSHIFT_DB", "dev"),
            user=os.getenv("REDSHIFT_USER"),
            password=os.getenv("REDSHIFT_PASSWORD"),
            connect_timeout=10,
            sslmode="require"
        )

        cursor = conn.cursor()
        cursor.execute("SELECT current_database(), current_user, version();")
        result = cursor.fetchone()

        print(f"✅ Connected successfully!")
        print(f"   Database : {result[0]}")
        print(f"   User     : {result[1]}")
        print(f"   Version  : {result[2][:50]}")

        cursor.close()
        conn.close()

    except Exception as e:
        print(f"❌ Connection failed: {e}")

if __name__ == "__main__":
    test_connection()