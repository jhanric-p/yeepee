-- SQLite schema for Kivy app database

CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    username TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT,
    price REAL NOT NULL,
    stock_quantity INTEGER NOT NULL,
    image_path TEXT
);

CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    order_date TEXT NOT NULL,
    total REAL NOT NULL,
    FOREIGN KEY(user_id) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS order_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL,
    price REAL NOT NULL,
    FOREIGN KEY(order_id) REFERENCES orders(id),
    FOREIGN KEY(product_id) REFERENCES products(id)
);

-- Insert some sample products
INSERT INTO products (name, description, price, stock_quantity, image_path) VALUES
('Classic T-Shirt', 'A classic white t-shirt', 19.99, 100, '../pup_study_style/static/assets/Classic.jpg'),
('Coqutte Dress', 'Elegant coqutte dress', 49.99, 50, '../pup_study_style/static/assets/Coqutte.jpg'),
('Jeepney Signage', 'Colorful jeepney signage', 29.99, 30, '../pup_study_style/static/assets/Jeepney_Signage.jpg'),
('Mono Chrome Shirt', 'Stylish monochrome shirt', 24.99, 75, '../pup_study_style/static/assets/Mono_Chrome.jpg');
