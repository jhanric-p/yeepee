DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS products;
-- Add other tables like orders, cart_items if needed for full functionality

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
    image_url TEXT, -- Path relative to static/assets/
    stock_quantity INTEGER DEFAULT 0,
    variations TEXT, -- Comma-separated string e.g., "Small,Medium,Large" or "Red,Blue"
    category TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT NOT NULL,
    message TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- You might also want:
-- CREATE TABLE orders ( ... );
-- CREATE TABLE order_items ( ... );
-- CREATE TABLE cart (user_id INTEGER, product_id INTEGER, quantity INTEGER ...); 
