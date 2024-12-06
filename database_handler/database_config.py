def get_table_schema():
    """Return complete table schema definition."""
    return {
        "id": "INTEGER PRIMARY KEY AUTOINCREMENT",
        "search_term": "TEXT NOT NULL",
        "brand": "TEXT",
        "product_name": "TEXT NOT NULL",
        "product_no": "TEXT",
        "headline": "TEXT",
        "short_text": "TEXT",
        "long_text": "TEXT",
        "bullet_points": "TEXT",
        "weight": "TEXT",
        "material": "TEXT",
        "sustainability": "TEXT",
        "dimensions": "TEXT",
        "color": "TEXT",
        "other_info": "TEXT",
        "created_at": "TIMESTAMP DEFAULT CURRENT_TIMESTAMP",
    }


def get_table_columns():
    """Return list of column names for the products table."""
    return list(get_table_schema().keys())


def get_column_display_widths():
    """Return dictionary of column widths for display purposes."""
    return {
        "id": 50,
        "search_term": 150,
        "brand": 100,
        "product_name": 200,
        "headline": 200,
        "long_text": 300,
        "bullet_points": 300,
        "short_text": 300,
        "weight": 100,
        "material": 150,
        "sustainability": 200,
        "dimensions": 150,
        "other_info": 200,
    }


def get_create_table_query():
    """Return CREATE TABLE query string."""
    schema = get_table_schema()
    columns = [f"{col} {dtype}" for col, dtype in schema.items()]
    return f"CREATE TABLE IF NOT EXISTS products ({', '.join(columns)})"


def get_select_query(columns=None):
    """Return the SELECT query string using the specified columns or all columns if none are specified."""
    if columns is None:
        columns = get_table_columns()
    else:
        # Validate columns
        valid_columns = get_table_columns()
        columns = [col for col in columns if col in valid_columns]
        if not columns:
            raise ValueError("No valid columns specified for SELECT query.")

    return f"SELECT {', '.join(columns)} FROM products"


def get_required_columns():
    """Return list of required columns for data validation."""
    return ["search_term", "product_name"]
