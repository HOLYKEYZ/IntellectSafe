import sqlite3
import os

# Try relative to script location first (assuming running from backend/)
DB_PATH = "sql_app.db"

if not os.path.exists(DB_PATH):
    print(f"DB not found at {DB_PATH}. Trying absolute path...")
    # Try relative to file
    DB_PATH = os.path.join(os.path.dirname(__file__), "..", "sql_app.db")
    
if not os.path.exists(DB_PATH):
    print(f"DB still not found at {DB_PATH}")
else:
    print(f"Using DB at: {os.path.abspath(DB_PATH)}")

try:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    print(f"Tables: {tables}")

    # Check for 'user' table
    print("Checking 'user' columns:")
    cursor.execute("PRAGMA table_info(user);")
    columns = cursor.fetchall()
    print(f"Columns: {columns}")
    
    conn.close()
except Exception as e:
    print(f"Error: {e}")
