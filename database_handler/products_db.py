import sqlite3
import datetime

# Adding root directory to sys.path
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database_handler.database_config import get_create_table_query, get_table_columns


def initialize_database():
    try:
        conn = sqlite3.connect("products.db")
        cursor = conn.cursor()
        create_table_query = get_create_table_query()
        print(f"Executing query: {create_table_query}")  # Debug print
        cursor.execute(create_table_query)
        conn.commit()
        conn.close()
        return True
    except sqlite3.Error as e:
        print(f"Error initializing database: {e}")
        return False


def add_mock_values():
    user_input = (
        input("Do you want to add mock values to the database? (Y/N): ").strip().upper()
    )
    if user_input != "Y":
        return

    try:
        num_values = int(input("How many mock values do you want to add?: ").strip())
    except ValueError:
        print("Invalid number. Exiting.")
        return

    try:
        conn = sqlite3.connect("products.db")
        cursor = conn.cursor()
        timestamp = datetime.datetime.now().strftime("%y%m%d")
        columns = [
            col for col in get_table_columns() if col not in ["id", "created_at"]
        ]
        placeholders = ",".join(["?" for _ in columns])
        insert_query = (
            f"INSERT INTO products ({','.join(columns)}) VALUES ({placeholders})"
        )

        for i in range(1, num_values + 1):
            values = [
                f"MOCK_{i}_{timestamp}"
                if col == "search_term"
                else f"Mock Product {i}"
                if col == "product_name"
                else f"Mock {col.replace('_', ' ').title()}"
                if col != "product_no"
                else i
                for col in columns
            ]
            cursor.execute(insert_query, values)

        conn.commit()
        print(f"{num_values} mock values added to the database.")
    except sqlite3.Error as e:
        print(f"Database error: {e}")
    finally:
        conn.close()


def get_connection():
    return sqlite3.connect("products.db")


if __name__ == "__main__":
    if initialize_database():
        print("Database initialized successfully.")
        add_mock_values()
    else:
        print("Failed to initialize database.")
