import os
import sqlite3
import pandas as pd
from PyQt5.QtWidgets import (QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, 
                            QHeaderView, QFileDialog, QMessageBox, QScrollArea, QMainWindow, 
                            QHBoxLayout, QTextEdit, QWidget, QVBoxLayout, QApplication, QSizePolicy)
from PyQt5.QtCore import Qt

from widgets.base_widget import BaseProcessingWidget

# Imports from other files in my project
from database_handler.products_db import initialize_database
from openai_handler.openaiProductTexts import ProductDescriptionGenerator
from database_handler.database_config import get_table_columns, get_column_display_widths, get_select_query

# Ensure the database is initialized
initialize_database()

class DatabaseQueryHandler:
    def __init__(self):
        self.conn = sqlite3.connect('products.db')
        self.cursor = self.conn.cursor()

    def fetch_products_for_view(self):
        columns = ["search_term", 
                        "brand", 
                        "product_name", 
                        "product_no", 
                        "headline", 
                        "short_text", 
                        "long_text", 
                        "bullet_points", 
                        "weight", 
                        "material", 
                        "sustainability", 
                        "dimensions"
        ]
        query = f"SELECT {', '.join(columns)} FROM products"
        try:
            self.cursor.execute(query)
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Database error during fetch: {e}")
            return []

    def fetch_product_info(self, search_term):
        columns = get_table_columns()
        self.cursor.execute(f"SELECT {', '.join(columns)} FROM products WHERE search_term = ?", (search_term,))
        return self.cursor.fetchone()

    def search_products(self, keyword):
        columns = get_table_columns()
        conditions = " OR ".join([f"{column} LIKE ?" for column in columns])
        query = f"SELECT {', '.join(columns)} FROM products WHERE {conditions}"
        params = ['%' + keyword + '%'] * len(columns)
        
        try:
            self.cursor.execute(query, params)
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Database error during search: {e}")
            return []

    def export_to_excel(self, path):
        self.cursor.execute("SELECT * FROM products")
        rows = self.cursor.fetchall()
        columns = [desc[0] for desc in self.cursor.description]
        df = pd.DataFrame(rows, columns=columns)
        df.to_excel(path, index=False)
        print(f"Database exported to {path}")

    def import_from_excel(self, path):
        df = pd.read_excel(path)
        df.to_sql('products', self.conn, if_exists='replace', index=False)
        print(f"Database imported from {path}")

    def fetch_multiple_products(self, search_terms):
        columns = get_table_columns()
        placeholders = ','.join(['?' for _ in search_terms])
        query = f"SELECT {', '.join(columns)} FROM products WHERE search_term IN ({placeholders})"
        
        try:
            self.cursor.execute(query, search_terms)
            return self.cursor.fetchall(), columns
        except sqlite3.Error as e:
            print(f"Database error during fetch: {e}")
            return [], []

    def __del__(self):
        self.conn.close()

class ProductInfoWindow(QWidget):
    def __init__(self, search_term, db_handler):
        super().__init__()
        self.search_term = search_term
        self.db_handler = db_handler
        self.initUI()
        self.apply_styles()

    def apply_styles(self):
        self.setStyleSheet("""
            QWidget {
                background-color: #f5f5f5;
                font-family: Arial;
            }
            QLabel {
                color: #2c3e50;
                font-weight: bold;
            }
            QLineEdit, QTextEdit {
                padding: 8px;
                border: 1px solid #bdc3c7;
                border-radius: 4px;
                background-color: white;
            }
            QPushButton {
                padding: 8px 15px;
                border-radius: 4px;
                border: none;
                color: white;
                font-weight: bold;
                background-color: #3498db;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)

    def initUI(self):
        self.setWindowTitle(f"Product Information: {self.search_term}")
        self.setGeometry(100, 100, 800, 600)

        product_info = self.db_handler.fetch_product_info(self.search_term)

        main_layout = QVBoxLayout()
        self.left_layout = QVBoxLayout()
        self.right_layout = QVBoxLayout()
        self.fields = {}

        if product_info:
            for idx, value in enumerate(product_info):
                header = self.db_handler.cursor.description[idx][0]
                if header in ["headline", "short_text", "long_text", "bullet_points"]:
                    widget = QTextEdit()
                    widget.setPlainText(str(value))
                    widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
                    widget.setWordWrapMode(True)
                else:
                    widget = QLineEdit()
                    widget.setText(str(value))
                    widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

                label = QLabel(f"{header}:")
                label.setBuddy(widget)
                self.fields[header] = widget

                h_layout = QHBoxLayout()
                h_layout.addWidget(label)
                h_layout.addWidget(widget)

                if header in ["headline", "short_text", "long_text", "bullet_points"]:
                    self.left_layout.addLayout(h_layout)
                else:
                    self.right_layout.addLayout(h_layout)
        else:
            self.left_layout.addWidget(QLabel("No product information found for this search term."))

        # Combine left and right layouts into a single horizontal layout
        combined_layout = QHBoxLayout()
        combined_layout.addLayout(self.left_layout)
        combined_layout.addLayout(self.right_layout)
        main_layout.addLayout(combined_layout)

        self.save_button = QPushButton("Save Product Info")
        self.save_button.clicked.connect(self.save_product_info)
        main_layout.addWidget(self.save_button)

        self.setLayout(main_layout)

    def save_product_info(self):
        data = {header: widget.toPlainText() if isinstance(widget, QTextEdit) else widget.text() for header, widget in self.fields.items()}
        existing_product = self.db_handler.fetch_product_info(self.search_term)
        placeholders = ", ".join([f"{header} = ?" for header in data.keys()])
        values = list(data.values()) + [self.search_term] if existing_product else list(data.values())
        query = f"UPDATE products SET {placeholders} WHERE search_term = ?" if existing_product else f"INSERT INTO products ({', '.join(data.keys())}) VALUES ({', '.join(['?' for _ in data.keys()])})"

        self.db_handler.cursor.execute(query, values)
        self.db_handler.conn.commit()
        QMessageBox.information(self, "Save Successful", "Product information saved successfully.")

class DatabaseViewWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.db_handler = DatabaseQueryHandler()
        self.columns = ["search_term", 
                        "brand", 
                        "product_name", 
                        "product_no", 
                        "headline", 
                        "short_text", 
                        "long_text", 
                        "bullet_points", 
                        "weight", 
                        "material", 
                        "sustainability", 
                        "dimensions"]
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Enter search keyword...")
        search_button = QPushButton("Search")
        search_button.clicked.connect(self.search_database)
        
        search_layout = QHBoxLayout()
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(search_button)
        
        layout.addLayout(search_layout)
        
        self.table = QTableWidget()
        self.table.setColumnCount(len(self.columns))
        self.table.setHorizontalHeaderLabels(self.columns)
        layout.addWidget(self.table)
        self.create_buttons(layout)
        self.load_database_view()
        
        button_layout = QHBoxLayout()
        show_info_button = QPushButton("Show product info")
        show_info_button.clicked.connect(self.show_product_info_sepWindow)
        export_button = QPushButton("Export Excel-file")
        export_button.clicked.connect(self.export_database)
        import_button = QPushButton("Import Excel-file")
        import_button.clicked.connect(self.import_database)
        
        button_layout.addWidget(show_info_button)
        button_layout.addWidget(export_button)
        button_layout.addWidget(import_button)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)

    def create_buttons(self, layout):
        button_layout = QHBoxLayout()
        refresh_button = QPushButton('Refresh')
        refresh_button.clicked.connect(self.load_database_view)
        button_layout.addWidget(refresh_button)
        layout.addLayout(button_layout)

    def load_database_view(self):
        products = self.db_handler.fetch_products_for_view()
        self.table.setRowCount(len(products))
        for row_idx, row_data in enumerate(products):
            for col_idx, col_data in enumerate(row_data):
                item = QTableWidgetItem(str(col_data))
                if col_idx < len(self.columns) and self.columns[col_idx] == 'search_term':
                    item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                self.table.setItem(row_idx, col_idx, item)

    def show_product_info_sepWindow(self):
        selected_row = self.table.currentRow()
        if selected_row >= 0:
            search_term = self.table.item(selected_row, 0).text()
            self.product_info_window = ProductInfoWindow(search_term, self.db_handler)
            self.product_info_window.show()

    def search_database(self):
        keyword = self.search_input.text().strip()
        if not keyword:
            self.load_database_view()
            return
            
        try:
            products = self.db_handler.search_products(keyword)
            self.table.setRowCount(len(products))
            for row_idx, product in enumerate(products):
                for col_idx, value in enumerate(product):
                    item = QTableWidgetItem(str(value))
                    if col_idx == 0:
                        item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                    self.table.setItem(row_idx, col_idx, item)
            
            if not products:
                QMessageBox.information(self, "Search Results", "No products found matching your search.")
        except Exception as e:
            print(f"Error during search: {e}")
            QMessageBox.warning(self, "Search Error", f"An error occurred while searching: {str(e)}")

    def export_database(self):
        selected_rows = set(item.row() for item in self.table.selectedItems())
        if not selected_rows:
            QMessageBox.warning(self, "No Selection", "Please select at least one row to export.")
            return

        try:
            search_terms = [self.table.item(row, 0).text() for row in selected_rows]
            products, columns = self.db_handler.fetch_multiple_products(search_terms)
            
            if not products:
                QMessageBox.warning(self, "No Data", "No data found for the selected rows.")
                return

            df = pd.DataFrame(products, columns=columns)
            path, _ = QFileDialog.getSaveFileName(self, "Save File", "", "Excel Files (*.xlsx);;CSV Files (*.csv)")
            
            if path:
                df.to_excel(path, index=False) if path.endswith('.xlsx') else df.to_csv(path, index=False)
                QMessageBox.information(self, "Export Successful", f"Successfully exported {len(products)} products to {path}")
        except Exception as e:
            print(f"Export error: {e}")
            QMessageBox.critical(self, "Export Error", f"Failed to export data: {str(e)}")

    def import_database(self):
        path, _ = QFileDialog.getOpenFileName(self, "Open File", "", "Excel Files (*.xlsx)")
        try:
            if path:
                self.db_handler.import_from_excel(path)
                self.load_database_view()
                QMessageBox.information(self, "Import Successful", "Database imported successfully.")
        except Exception as e:
            print(f"Failed to import database. Error: {e}")

if __name__ == "__main__":
    app = QApplication([])
    db_handler = DatabaseQueryHandler()
    window = ProductInfoWindow("example_search_term", db_handler)
    window.show()
    app.exec_()