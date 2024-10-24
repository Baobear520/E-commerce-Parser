# from pymongo import MongoClient
#
# def check_db(db_name="products",collection_name="men_products"):
#     client = MongoClient('mongodb://localhost:27017/')
#     db = client[db_name]
#     collection = db[collection_name]
#
#     product = collection.find_one({"product_id": "1"})
#     print(product)


import sqlite3
from datetime import datetime

# Путь к файлу базы данных SQLite
DB_PATH = 'products.db'


def init_db():
    """Инициализирует базу данных и создает таблицу, если она не существует."""

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    # cursor.execute('''
    #     DROP TABLE IF EXISTS products
    # ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            product_id INTEGER PRIMARY KEY AUTOINCREMENT,
            brand_name TEXT,
            name TEXT UNIQUE,
            description TEXT,
            original_price REAL,
            discount_price REAL,
            color TEXT,
            last_updated DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()


def save_to_sqlite_db(products):
    """Saves product data to the SQLite database, inserting or updating as needed."""
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # Standard datetime format

    # Use a context manager to ensure the connection is closed automatically
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()

        for product in products:
            if not product:
                continue  # Skip empty product entries

            try:
                # Attempt to insert a new product
                cursor.execute('''
                    INSERT INTO products (
                    brand_name, name, description, original_price, discount_price, color, last_updated
                )
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    product["brand_name"],
                    product["name"],
                    product["description"],
                    product["original_price"],
                    product["discount_price"],
                    product["color"],
                    current_time
                ))
                print(f"Inserted product: {product['name']}")

            except sqlite3.IntegrityError:
                # If the `name` already exists, update the existing record

                cursor.execute('''
                    UPDATE products 
                    SET 
                        brand_name = ?, 
                        description = ?, 
                        original_price = ?, 
                        discount_price = ?, 
                        color = ?, 
                        last_updated = ?
                    WHERE name = ?
                ''', (
                    product["brand_name"],
                    product["description"],
                    product["original_price"],
                    product["discount_price"],
                    product["color"],
                    current_time,
                    product["name"]
                ))
                print(f"Updated product: {product['name']}")

        conn.commit()
    print(f"Processed {len(products)} products.")

def check_sqlite_db():
    # Connect to the SQLite database (or create it if it doesn't exist)
    conn = sqlite3.connect(DB_PATH)

    # Create a cursor object to execute SQL queries
    cursor = conn.cursor()

    # Execute a query to select records from a table (replace 'your_table' with your table name)
    cursor.execute("SELECT * FROM products")

    # Fetch all records from the query result
    records = cursor.fetchall()

    # Print out each record
    for record in records:
        print(record)
    print("Database check finished")

    # Close the connection
    conn.close()
