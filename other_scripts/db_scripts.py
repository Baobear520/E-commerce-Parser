import sqlite3
from datetime import datetime


def init_db(db, table_name="products"):
    """Initializes the database and creates a table if it does not exist."""
    try:
        with sqlite3.connect(db) as conn:
            cursor = conn.cursor()

            try:
                cursor.execute(f'''
                    DROP TABLE IF EXISTS {table_name}
                ''')
                print(f"Table '{table_name}' dropped successfully (if it existed).")
            except sqlite3.OperationalError as e:
                print(f"Operational error during table drop: {e}.")
            try:
                cursor.execute(f'''
                    CREATE TABLE IF NOT EXISTS {table_name} (
                        product_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        style_code INT,
                        brand_name TEXT,
                        name TEXT,
                        description TEXT,
                        original_price_USD REAL,
                        discount_price_USD REAL,
                        color TEXT,
                        last_updated DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                conn.commit()
                print(f"Table '{table_name}' initialized successfully.")
            except sqlite3.OperationalError as e:
                print(f"Operational error during table creation: {e}.")
            except sqlite3.DatabaseError as e:
                print(f"Database error during table creation: {e}.")
            except Exception as e:
                print(f"An unexpected error occurred during table creation: {e}.")
    except sqlite3.Error as e:
        print(f"Error connecting to the database '{db}': {e}.")


def save_to_sqlite_db(db, data, table_name="products"):
    """Saves product data to the SQLite database, inserting or updating as needed."""
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')


    try:
        with sqlite3.connect(db) as conn:
            cursor = conn.cursor()

            for product in data:
                if not product:
                    print("Skipped empty product entry.")
                    continue  # Skip empty product entries

                try:
                    # Attempt to insert a new product
                    cursor.execute(f'''
                        INSERT INTO {table_name} (
                            style_code, brand_name, name, description, original_price_USD, discount_price_USD, color, last_updated
                        )
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        product["style_code"],
                        product["brand_name"],
                        product["name"],
                        product["description"],
                        product["original_price_USD"],
                        product["discount_price_USD"],
                        product["color"],
                        current_time
                    ))
                    print(f"Inserted product: {product["style_code"]} {product["name"]}")

                except sqlite3.IntegrityError:
                    # Handle uniqueness constraint violation and update existing record
                    try:
                        cursor.execute(f'''
                            UPDATE {table_name}
                            SET 
                                style_code = ?,
                                brand_name = ?, 
                                description = ?, 
                                original_price_USD = ?, 
                                discount_price_USD = ?, 
                                color = ?, 
                                last_updated = ?
                            WHERE name = ?
                        ''', (
                            product["style_code"],
                            product["brand_name"],
                            product["description"],
                            product["original_price_USD"],
                            product["discount_price_USD"],
                            product["color"],
                            current_time,
                            product["name"]
                        ))
                        print(f"Updated product: {product["style_code"]} {product['name']}")
                    except sqlite3.OperationalError as e:
                        print(f"Operational error during update: {e}.")
                    except sqlite3.DatabaseError as e:
                        print(f"Database error during update: {e}.")
                    except Exception as e:
                        print(f"Unexpected error during update: {e}.")

                except sqlite3.OperationalError as e:
                    print(f"Operational error during insertion: {e}.")
                except sqlite3.DatabaseError as e:
                    print(f"Database error during insertion: {e}.")
                except Exception as e:
                    print(f"An unexpected error occurred during insertion: {e}.")

            conn.commit()
        print(f"Processed {len(data)} products.")

    except sqlite3.Error as e:
        print(f"Error connecting to the database '{db}': {e}.")


def check_sqlite_db(db, table_name="products"):
    """Checks and prints records from a specified table."""
    try:
        with sqlite3.connect(db) as conn:
            cursor = conn.cursor()
            try:
                cursor.execute(f'''
                    SELECT * FROM {table_name}
                ''')
                records = cursor.fetchall()

                if records:
                    for record in records:
                        print(record)
                    print(f"Database check finished. Retrieved {len(records)} records.")
                else:
                    print(f"No records found in table '{table_name}'.")

            except sqlite3.OperationalError as e:
                print(f"Operational error during data retrieval: {e}.")
            except sqlite3.DatabaseError as e:
                print(f"Database error during data retrieval: {e}.")
            except Exception as e:
                print(f"An unexpected error occurred during data retrieval: {e}.")

    except sqlite3.Error as e:
        print(f"Error connecting to the database '{db}': {e}.")

