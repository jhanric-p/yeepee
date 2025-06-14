# py-cute/pup_study_style/db.py
import sqlite3
import os
import click
from flask import current_app, g

DATABASE_FILENAME = 'database.db' # Consistent filename

def get_db():
    if 'db' not in g:
        # Use current_app.config['DATABASE'] which points to instance folder
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row
    return g.db

def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_db():
    db = get_db()
    schema_path = os.path.join(os.path.dirname(__file__), '..', '..', 'schema.sql') # Relative to this file's location
    if not os.path.exists(schema_path):
        print(f"CRITICAL: schema.sql not found at {schema_path}. Cannot initialize database schema.")
        # Create a default schema.sql if not found (as in your original code)
        print("Creating a default schema.sql file as it was not found in the root.")
        with open(schema_path, 'w') as f:
            # (Paste your schema.sql content here if you want this fallback)
            f.write('''
DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS products;

CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    address1_line1 TEXT,
    contact_no1 TEXT,
    address2_line1 TEXT,
    contact_no2 TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT,
    price REAL NOT NULL,
    image_url TEXT,
    stock_quantity INTEGER DEFAULT 0,
    variations TEXT,
    category TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
            ''')


    try:
        with current_app.open_resource(schema_path, mode='r') as f: # This looks relative to app root
            db.executescript(f.read())
        print("Initialized the database schema from schema.sql.")
    except FileNotFoundError: # Fallback if current_app.open_resource fails for relative path
         with open(schema_path, 'r') as f_alt:
            db.executescript(f_alt.read())
         print("Initialized the database schema from schema.sql (using direct path).")


    # Add dummy products
    cursor = db.cursor()
    products_data = [
        (1, 'PUP Baybayin Lace - Minimalist', 'Minimalist Baybayin Lanyard - Coquette', 140.00, 'assets/product_placeholder.png', 50, 'Coquette,Classic,Mono Chrome'),
        (2, 'PUP Jeepney Signage', 'PUP Jeepney Signage Sticker', 20.00, 'assets/product_placeholder.png', 100, None),
        (3, 'PUP Iskolar TOTE BAG', 'PUP Iskolar themed Tote Bag', 160.00, 'assets/product_placeholder.png', 30, None),
        (4, 'PUP Study With Style TOTE', 'Branded Tote Bag', 150.00, 'assets/product_placeholder.png', 25, None)
    ]
    try:
        cursor.executemany('''
            INSERT OR IGNORE INTO products (id, name, description, price, image_url, stock_quantity, variations)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', products_data)
        db.commit()
        print("Added/updated dummy products.")
    except sqlite3.IntegrityError:
        print("Dummy products might already exist or there was an issue adding them.")
    except sqlite3.Error as e:
        print(f"SQLite error adding dummy products: {e}")


@click.command('init-db')
def init_db_command():
    """Clear existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')

def init_app(app):
    """Register database functions with the Flask app."""
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)

# New function for run.py
def run_init_db_command_from_factory(app):
    with app.app_context():
        init_db()
        print("Database initialization process completed from factory call.")