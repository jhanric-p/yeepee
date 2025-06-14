-- SQL schema to create the "profiles" table for the Kivy app

CREATE TABLE IF NOT EXISTS profiles (
    username TEXT PRIMARY KEY,
    name TEXT,
    address1 TEXT,
    contact1 TEXT,
    address2 TEXT,
    contact2 TEXT
);

-- SQL schema to create the "orders" table

CREATE TABLE IF NOT EXISTS orders (
    ref_no INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    status TEXT,
    quantity INTEGER,
    payment TEXT,
    FOREIGN KEY (username) REFERENCES profiles(username)
);

-- SQL schema to create the "products" table

CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT,
    price REAL,
    stock_quantity INTEGER,
    image_path TEXT
);

-- SQL schema to create the "inventory" table

CREATE TABLE IF NOT EXISTS inventory (
    item_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    quantity INTEGER,
    price REAL
);

-- SQL schema to create the "users" table

CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    email TEXT UNIQUE,
    username TEXT UNIQUE,
    password_hash TEXT
);
