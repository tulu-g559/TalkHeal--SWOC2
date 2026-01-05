import sqlite3
import bcrypt
from datetime import datetime
from auth.password_validator import PasswordValidator

def init_db():
    with sqlite3.connect("users.db") as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password TEXT,
                updated_at TEXT NOT NULL,
                provider TEXT DEFAULT 'email',
                provider_id TEXT,
                profile_picture TEXT,
                verified BOOLEAN DEFAULT 0
            )
        """)
        
        # Add new columns if they don't exist (for existing databases)
        try:
            cursor.execute("ALTER TABLE users ADD COLUMN provider TEXT DEFAULT 'email'")
        except sqlite3.OperationalError:
            pass  # Column already exists
        
        try:
            cursor.execute("ALTER TABLE users ADD COLUMN provider_id TEXT")
        except sqlite3.OperationalError:
            pass  # Column already exists
        
        try:
            cursor.execute("ALTER TABLE users ADD COLUMN profile_picture TEXT")
        except sqlite3.OperationalError:
            pass  # Column already exists
        
        try:
            cursor.execute("ALTER TABLE users ADD COLUMN verified BOOLEAN DEFAULT 0")
        except sqlite3.OperationalError:
            pass  # Column already exists
        
        conn.commit()

def hash_password(password):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def check_password(password, hashed):
    return bcrypt.checkpw(password.encode(), hashed.encode())

def register_user(name, email, password, provider='email', provider_id=None, profile_picture=None, verified=False):
    # Hash password only if provided (OAuth users don't need passwords)
    hashed_pw = hash_password(password) if password else None
    current_time = datetime.now().isoformat()
    
    with sqlite3.connect("users.db") as conn:
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO users (name, email, password, updated_at, provider, provider_id, profile_picture, verified) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (name, email, hashed_pw, current_time, provider, provider_id, profile_picture, verified))
            conn.commit()
            return True, "User registered successfully"
        except sqlite3.IntegrityError:
            return False, "Email already registered"

def authenticate_user(email, password):
    with sqlite3.connect("users.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT name, password FROM users WHERE email = ?", (email,))
        result = cursor.fetchone()
    
    if result and check_password(password, result[1]):
        user = {"name": result[0], "email": email}
        return True, user
    return False, None

def check_user(email):
    with sqlite3.connect("users.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
        result = cursor.fetchone()
    
    if result:
        return True, result[4]
    return False, None

def get_user_by_email(email):
    """Get user data by email for OAuth authentication"""
    with sqlite3.connect("users.db") as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, name, email, provider, provider_id, profile_picture, verified, updated_at 
            FROM users WHERE email = ?
        """, (email,))
        result = cursor.fetchone()
    
    if result:
        return {
            "id": result[0],
            "name": result[1],
            "email": result[2],
            "provider": result[3],
            "provider_id": result[4],
            "profile_picture": result[5],
            "verified": result[6],
            "updated_at": result[7]
        }
    return None

def reset_password(email, new_password):
    hashed_pw = hash_password(new_password)
    current_time = datetime.now().isoformat()
    
    try:
        with sqlite3.connect("users.db") as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
            result = cursor.fetchone()

            if not result:
                return False, "User with this email does not exist."

            cursor.execute("UPDATE users SET password = ? , updated_at = ? WHERE email = ?", (hashed_pw, current_time, email))
            conn.commit()
            return True, "Password updated successfully."
    except sqlite3.Error as e:
        return False, f"Database error: {str(e)}"

def verify_token_count(email, token_updated_at):
    try:
        with sqlite3.connect("users.db") as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT updated_at FROM users WHERE email = ?", (email,))
            result = cursor.fetchone()
            
            if not result:
                return False, "User with this email does not exist."

            db_updated_at = result[0]

            if str(db_updated_at) != str(token_updated_at):
                return False, "Reset link is no longer valid (token outdated)."

            return True, None

    except sqlite3.Error as e:
        return False, f"Database error: {str(e)}"