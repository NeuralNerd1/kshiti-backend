"""Quick Supabase connection test."""
import traceback
try:
    import psycopg
    print(f"psycopg version: {psycopg.__version__}")
    conn = psycopg.connect(
        host="aws-1-ap-northeast-2.pooler.supabase.com",
        port=5432,
        dbname="postgres",
        user="postgres.izabcheevqretdbnbamp",
        password="Copperstone@l1202",
        sslmode="require",
        connect_timeout=15,
    )
    print("Connected successfully!")
    cur = conn.cursor()
    cur.execute("SELECT version()")
    print("PostgreSQL version:", cur.fetchone()[0])
    conn.close()
    print("Connection closed.")
except Exception:
    traceback.print_exc()
