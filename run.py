# py-cute/run.py
import os
from pup_study_style import create_app, DATABASE # Import DATABASE constant
from pup_study_style.db import run_init_db_command_from_factory # We'll create this

app = create_app()

if __name__ == '__main__':
    # Construct path relative to the instance folder if that's where you want it
    # Or keep it at the root like before. For simplicity with current setup, let's assume root.
    db_path = os.path.join(app.root_path, '..', DATABASE) # Adjust if DATABASE is in instance_path
    
    # A slightly better way to check and initialize DB
    # if not os.path.exists(db_path): # Check if the database file exists
    with app.app_context(): # DB operations need app context
        if not os.path.exists(os.path.join(app.instance_path, DATABASE)) and not os.path.exists(DATABASE): # Check both common locations
            print(f"{DATABASE} not found. Initializing database...")
            run_init_db_command_from_factory(app)
        else:
            # Even if DB file exists, tables might not. Check for users table.
            from pup_study_style.db import get_db
            try:
                db_conn = get_db()
                cursor = db_conn.cursor()
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users';")
                if cursor.fetchone() is None:
                    print("Users table not found in existing DB. Re-initializing database...")
                    run_init_db_command_from_factory(app)
                else:
                    print("Database already seems to be initialized with users table.")
                    # Optionally re-run init_db for dummy data if needed (it's idempotent for products)
                    from pup_study_style.db import init_db
                    init_db() # This will try to add dummy products
            except Exception as e:
                print(f"Error during DB check/init: {e}")
                print("Attempting to initialize DB.")
                run_init_db_command_from_factory(app)

    app.run(debug=True)