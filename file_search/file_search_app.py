import os
import sys
import json
import pandas as pd
import pdfplumber
from docx import Document
import fitz

# Imports for the GUI elements (PyQt5)
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QWidget, QLabel, QLineEdit, QPushButton, QTextEdit, 
                             QFileDialog, QMessageBox, QVBoxLayout, QListWidget)

# Add the project root to the python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Imports from other files in my project
from file_search.search_excel import search_excel
from file_search.search_pdf import search_pdf_advanced
from file_search.search_word import search_word
from utils import SaveToFile
from openai_handler.openaiDataBaseHandler import OpenAIAnalyzer, DatabaseHandler, DatabaseSearch
from widgets.base_widget import BaseProcessingWidget

class FileSearchApp(BaseProcessingWidget):
    def __init__(self):
        super().__init__()
        # Initialize handlers
        self.analyzer = OpenAIAnalyzer()
        self.db_handler = DatabaseHandler()
        self.db_datasearch = DatabaseSearch()
        self.save_search_to_excel = SaveToFile()

        # Set search functions
        self.search_excel = search_excel
        self.search_pdf_advanced = search_pdf_advanced
        self.search_word = search_word

        # Initialize variables
        self.inserted_brand = None
        self.inserted_productname = None
        
        self.init_ui()

    def init_ui(self):
        # Add title
        title = QLabel("Document Search and Analysis")
        title.setObjectName("title")
        self.layout.addWidget(title)

        # Add info section
        info_text = """
        Document Search Features:
        • Search Excel, PDF, and Word documents
        • AI-powered content analysis
        • Automatic database updates
        • Export search results
        • Multiple search terms support
        """
        info_label = QLabel(info_text)
        info_label.setObjectName("info")
        info_label.setWordWrap(True)
        self.layout.addWidget(info_label)

        # Create search section
        self.create_search_section()
        
        # Create metadata section
        self.create_metadata_section()
        
        # Create action buttons
        self.create_buttons()
        
        # Create results section
        self.create_results_section()

    def create_search_section(self):
        search_label = QLabel("Search Terms (comma-separated):")
        search_label.setObjectName("section-label")
        self.layout.addWidget(search_label)
        
        self.search_group_entry = QLineEdit()
        self.search_group_entry.setPlaceholderText("Enter search terms...")
        self.layout.addWidget(self.search_group_entry)

    def create_metadata_section(self):
        # Brand input
        brand_label = QLabel("Brand Name:")
        brand_label.setObjectName("section-label")
        self.layout.addWidget(brand_label)
        
        self.brand_entry = QLineEdit()
        self.brand_entry.setPlaceholderText("Enter brand name (optional)")
        self.layout.addWidget(self.brand_entry)

        # Product input
        product_label = QLabel("Product Name:")
        product_label.setObjectName("section-label")
        self.layout.addWidget(product_label)
        
        self.product_name_entry = QLineEdit()
        self.product_name_entry.setPlaceholderText("Enter product name (optional)")
        self.layout.addWidget(self.product_name_entry)

    def create_buttons(self):
        search_button = QPushButton("Search Documents")
        search_button.clicked.connect(self.open_file)
        self.layout.addWidget(search_button)

        export_button = QPushButton("Export Results")
        export_button.clicked.connect(self.handle_save_to_file)
        self.layout.addWidget(export_button)

    def create_results_section(self):
        results_label = QLabel("Search Results:")
        results_label.setObjectName("section-label")
        self.layout.addWidget(results_label)
        
        self.result_listbox = QListWidget()
        self.layout.addWidget(self.result_listbox)

        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        self.result_text.setPlaceholderText("Detailed results will appear here...")
        self.layout.addWidget(self.result_text)

    def update_listbox(self, text):
        self.result_listbox.addItem(text)
        self.result_listbox.scrollToBottom()

    def open_file(self):
        search_group = self.search_group_entry.text()
        if not search_group:
            self.update_listbox("Please enter search terms.")
            return
        file_path, _ = QFileDialog.getOpenFileName(self, "Select file", "", "Files (*.xlsx *.xls *.pdf *.docx *.doc)")
        if not file_path:
            self.update_listbox("No file selected.")
            return        
        self.inserted_brand = self.brand_entry.text().strip() or None
        self.inserted_productname = self.product_name_entry.text().strip() or None

        extension = file_path.split('.')[-1].lower()
        search_term_results = []

        try:
            if extension in ['xlsx', 'xls']:
                df = pd.read_excel(file_path, engine='openpyxl', na_filter=False)
                for search_term in search_group.split(','):
                    search_term_result = self.search_excel(df, search_term.strip())
                    print(f"FileSearchApp open app recieved search_term_result from search_excel: {search_term_result}")
                    self.analyze_and_update_db(search_term.strip(), search_term_result)
                    print(f"FilesearchApp parsed and updated database for search_term: {search_term.strip()}")
                    search_term_results.append((search_term.strip(), search_term_result))
                    self.update_listbox(f"Search completed for {search_term.strip()} in Excel")

            elif extension == 'pdf':
                with pdfplumber.open(file_path) as pdf:
                    doc = fitz.open(file_path)
                    for search_term in search_group.split(','):
                        search_term_result = self.search_pdf_advanced(pdf, doc, search_term.strip())
                        print(f"FileSearchApp open app recieved search_term_result from search_pdf_advanced: {search_term_result}")
                        search_term_results.append((search_term.strip(), search_term_result))
                        print(f"FilesearchApp parsed and updated database for search_term: {search_term.strip()}")
                        self.update_listbox(f"Search completed for {search_term.strip()} in PDF")

            elif extension in ['docx', 'doc']:
                doc = Document(file_path)
                for search_term in search_group.split(','):
                    search_term_result = self.search_word(doc, search_term.strip())
                    print(f"FileSearchApp open app received search_term_result from search_word: {search_term_result}")
                    self.analyze_and_update_db(search_term.strip(), search_term_result)
                    print(f"FilesearchApp parsed and updated database for search_term: {search_term.strip()}")
                    search_term_results.append((search_term.strip(), search_term_result))
                    self.update_listbox(f"Search completed for {search_term.strip()} in Word")

        except Exception as e:
            self.update_listbox(f"Error searching file: {str(e)}")
            print(f"Error searching file: {str(e)}")

    def analyze_and_update_db(self, search_term, search_term_result):
        print(f"Attempting to analyze and update database for search term: {search_term}")

        # Analyze the search term result and update the database
        analysis = self.analyzer.analyze_text(search_term_result)
        
        if self.inserted_brand:
            analysis.brand = self.inserted_brand
        if self.inserted_productname:
            analysis.product_name = self.inserted_productname

        self.db_handler.update_database(search_term, analysis)
        self.update_listbox(f"Database updated for {search_term}")

    def handle_save_to_file(self):
        search_group = self.search_group_entry.text()
        if not search_group:
            self.update_listbox("Please enter search terms.")
            return
        
        search_terms = [term.strip() for term in search_group.split(',')]
        data = []
        for search_term in search_terms:
            results = self.db_datasearch.search_database(search_term)
            data.extend(results)
            
        if data:
            file_path, _ = QFileDialog.getSaveFileName(self, "Save file", "", "Excel files (*.xlsx)")
            if file_path:
                self.save_search_to_excel.save_search_to_excel(data, file_path)
        else:
            print("file_search_app.handle_save_to_file: No data found to save.")