import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'database.db')
SQL_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'create_profiles_table.sql')

def create_profiles_table():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    with open(SQL_PATH, 'r') as f:
        sql_script = f.read()
    cursor.executescript(sql_script)
    conn.commit()
    conn.close()
    print("Database tables created successfully.")

if __name__ == "__main__":
    create_profiles_table()
