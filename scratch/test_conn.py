import socket
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

host = "aws-1-us-west-2.pooler.supabase.com"
print(f"Resolving {host} via socket.gethostbyname:")
try:
    ip = socket.gethostbyname(host)
    print(f"IP: {ip}")
except Exception as e:
    print(f"Error: {e}")

db_url = os.getenv('DATABASE_URL')
print("\nConnecting using DATABASE_URL:")
try:
    conn = psycopg2.connect(db_url)
    print("Success connecting with URL!")
    conn.close()
except Exception as e:
    print(f"Error connecting with URL: {e}")

# If URL fails, try using IP address directly
if 'ip' in locals():
    print("\nTrying direct IP connection...")
    try:
        # Reconstruct connection string replacing host with IP
        # postgresql://postgres.ftpkhueqooyqvwliifzb:Johnorbes2026%2A@aws-1-us-west-2.pooler.supabase.com:6543/postgres
        # We need to set host header or sslmode?
        # Direct psycopg2 connection parameters:
        conn = psycopg2.connect(
            database="postgres",
            user="postgres.ftpkhueqooyqvwliifzb",
            password="Johnorbes2026*",
            host=ip,
            port=6543,
            sslmode="require"
        )
        print("Success connecting with direct IP!")
        conn.close()
    except Exception as e:
        print(f"Error connecting with direct IP: {e}")
