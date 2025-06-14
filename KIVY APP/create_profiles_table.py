import sqlite3
import os
from werkzeug.security import generate_password_hash

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'database.db')

def create_profiles_table():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Create users table if it doesn't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            email TEXT UNIQUE,
            username TEXT UNIQUE,
            password_hash TEXT,
            is_admin INTEGER DEFAULT 0
        )
    ''')

    # Create admin user
    admin_username = "admin"
    admin_password = "admin123"
    admin_password_hash = generate_password_hash(admin_password)

    # First check if admin exists
    cursor.execute("SELECT * FROM users WHERE username = ?", (admin_username,))
    existing_admin = cursor.fetchone()

    if existing_admin is None:
        # Create new admin user
        try:
            cursor.execute(
                "INSERT INTO users (username, password_hash, is_admin, name) VALUES (?, ?, 1, 'Administrator')",
                (admin_username, admin_password_hash)
            )
            print("Admin user created successfully")
        except sqlite3.Error as e:
            print(f"Error creating admin user: {e}")
    else:
        # Update existing admin user
        try:
            cursor.execute(
                "UPDATE users SET password_hash = ?, is_admin = 1 WHERE username = ?",
                (admin_password_hash, admin_username)
            )
            print("Admin user updated successfully")
        except sqlite3.Error as e:
            print(f"Error updating admin user: {e}")

    # Verify admin user
    cursor.execute("SELECT * FROM users WHERE username = ?", (admin_username,))
    admin_user = cursor.fetchone()
    if admin_user:
        print(f"Admin user verified in database: {admin_user['username']}")
    else:
        print("WARNING: Admin user not found in database after creation/update!")

    conn.commit()
    conn.close()

if __name__ == "__main__":
    create_profiles_table()
