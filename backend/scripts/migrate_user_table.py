import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from app.db.session import engine
from sqlalchemy import text

def migrate():
    print("Attempting to migrate User table...")
    with engine.connect() as conn:
        # List tables
        result = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table';"))
        tables = [row[0] for row in result]
        print(f"Existing tables: {tables}")

        try:
            conn.execute(text("ALTER TABLE user ADD COLUMN safety_provider VARCHAR"))
            conn.commit()
            print("Migration successful: Added safety_provider column.")
        except Exception as e:
            print(f"Migration note: {e}")
            # Likely "duplicate column name" if run twice

if __name__ == "__main__":
    migrate()
