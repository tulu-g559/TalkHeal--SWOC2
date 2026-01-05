# migrate_db.py
import sqlite3

DB_FILE = "journals.db"
TABLE_NAME = "journal_entries"

# Columns you expect in your schema
EXPECTED_COLUMNS = {
    "id": "INTEGER PRIMARY KEY",
    "email": "TEXT",
    "entry": "TEXT",
    "sentiment": "TEXT",
    "date": "TEXT",
    "tags": "TEXT"  # New column we added
}

def migrate():
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()

        # Get current columns in the table
        cursor.execute(f"PRAGMA table_info({TABLE_NAME})")
        current_columns = [col[1] for col in cursor.fetchall()]

        # Add missing columns
        for col_name, col_type in EXPECTED_COLUMNS.items():
            if col_name not in current_columns:
                cursor.execute(f"ALTER TABLE {TABLE_NAME} ADD COLUMN {col_name} {col_type}")
                print(f"✅ Added missing column: {col_name}")

        conn.commit()
    print("✅ Migration complete!")

if __name__ == "__main__":
    migrate()
