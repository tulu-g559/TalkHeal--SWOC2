#!/usr/bin/env python3
"""
Database Setup Script for TalkHeal

This script initializes the required databases for the TalkHeal application.
Run this script once to set up the database schema.
"""

import sqlite3
import os
from auth.auth_utils import init_db

def setup_journals_db():
    """Initialize the journals database"""
    with sqlite3.connect("journals.db") as conn:
        cursor = conn.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS journal_entries (
            id TEXT PRIMARY KEY,
            email TEXT,
            entry TEXT,
            sentiment TEXT,
            date TEXT
        )
        """)
        conn.commit()
    print("Journals database initialized successfully")

def setup_feedback_db():
    """Initialize the feedback database"""
    with sqlite3.connect("feedback.db") as conn:
        cursor = conn.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_email TEXT,
            convo_id INTEGER,
            message TEXT,
            feedback TEXT,
            comment TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """)
        conn.commit()
    print("Feedback database initialized successfully")

def update_feedback_table():
    """Add user_email column if it doesn't exist (for old DBs)"""
    with sqlite3.connect("feedback.db") as conn:
        c = conn.cursor()
        try:
            c.execute("ALTER TABLE feedback ADD COLUMN user_email TEXT")
            print("✅ user_email column added to feedback table")
        except sqlite3.OperationalError:
            # Column already exists
            print("ℹ️ user_email column already exists in feedback table")
        conn.commit()

def main():
    """Main setup function"""
    print("🚀 Setting up TalkHeal databases...")
    
    # Initialize users database
    try:
        init_db()
        print("Users database initialized successfully")
    except Exception as e:
        print(f"Error initializing users database: {e}")
    
    # Initialize journals database
    try:
        setup_journals_db()
    except Exception as e:
        print(f"Error initializing journals database: {e}")
        
    # Initialize feedback database
    try:
        setup_feedback_db()
        update_feedback_table()  # ensure old DBs have user_email
    except Exception as e:
        print(f"Error initializing feedback database: {e}")
    
    print("\n🎉 Database setup complete!")

if __name__ == "__main__":
    main()
