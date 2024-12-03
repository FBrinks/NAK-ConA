from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
    QPushButton, QStackedWidget, QToolTip, QGraphicsDropShadowEffect,
    QLabel, QTextEdit
)
from PyQt5.QtGui import QFont, QColor
from PyQt5.QtCore import Qt

from function_excel import ExcelProcessingWidget
from file_search.file_search_app import FileSearchApp
from image_handler.image_process_app import ImageProcessingWidget
from database_handler.database_view import DatabaseViewWidget
from database_handler.products_db import initialize_database
from widgets.base_widget import BaseProcessingWidget

def handle_exit(app):
    app.quit()

def create_tooltip(widget, text):
    """Create tooltip for widget with specified text."""
    QToolTip.setFont(QFont('SansSerif', 10))
    widget.setToolTip(text)

def clear_layout(layout):
    while layout.count():
        child = layout.takeAt(0)
        if child.widget():
            child.widget().deleteLater()

def apply_custom_style(app):
    """Apply light theme styling to the application."""
    style = """
        QWidget {
            background-color: #f0f0f0;
            color: #000000;
        }
        QPushButton {
            background-color: #ffffff;
            border: 1px solid #c0c0c0;
            padding: 5px;
            font-size: 14px;
        }
        QPushButton:hover {
            background-color: #e0e0e0;
        }
        QLabel {
            font-size: 14px;
            color: #333333;
            border: 1px solid #000000;
        }
        QLineEdit {
            background-color: #ffffff;
            border: 1px solid #c0c0c0;
            padding: 5px;
        }
    """
    app.setStyleSheet(style)

def apply_button_shadow_effect(button, blur_radius=5, offset=(2, 2), color=QColor(63, 63, 63, 180)):
    shadow = QGraphicsDropShadowEffect()
    shadow.setBlurRadius(blur_radius)
    shadow.setOffset(offset[0], offset[1]) # (x, y)
    shadow.setColor(color)
    button.setGraphicsEffect(shadow)

def create_nav_button(text, tooltip, widget, content_area, width=150):
    """Creating a navigation button with standard styling."""
    button = QPushButton(text)
    button.setFixedWidth(width)
    create_tooltip(button, tooltip)
    button.clicked.connect(lambda: content_area.setCurrentWidget(widget))
    return button

def create_start_widget():
    """Creating the welcome/start widget with program information."""
    start_widget = QWidget()
    layout = QVBoxLayout(start_widget)
    
    # Create welcome text
    welcome_text = QTextEdit()
    welcome_text.setReadOnly(True)
    welcome_text.setStyleSheet("""
        QTextEdit {
            border: 1px solid #c0c0c0;
            background-color: #f0f0f0;
            padding: 5px;
        }
    """)
    shadow = QGraphicsDropShadowEffect()
    shadow.setBlurRadius(10)
    shadow.setOffset(3, 3)
    shadow.setColor(QColor(63, 63, 63, 180))
    welcome_text.setGraphicsEffect(shadow)
    
    info_text = """
    Welcome to Content Assistant!

    Any questions or feedback or issues can be sent to: fredde.brink@outlook.com
    You who work within the company can also reach me on Teams.

    This application provides several useful tools:

    1. Excel Processing
       • Export an item-list from pim
       • Use english as language
       • Use the attributes: Product/Item Number, Brand, Product name, Product, Supplier Product No, External color code,
       • Removes duplicates and cleans data
       • Combines supplier product numbers with external color codes for image search in content banks
       • Use TEXTJOIN in the saved Excel for usage in Info Search and Image Search/Processing

    2. Info Search
       • Insert as many search_terms as you like for search in files and extract the information
       • Adds the information to a local database for easy access
       • Generates Product texts for the products in the database

    3. Image Search and Processing
       • Search for images in folders and subfolders and process them
       • Convert and resize images

       NOTE: Cropping and Changing non-white backgrounds to white is not implemented yet. 
       although transparent PNG are handled and converted to white background.

    4. Database View
       • View and manage database entries
       • Get a pop up window with  the information for the selected product, where you also can edit the information
       • Search and filter database content

    Select any function from the buttons above to get started.
    """
    
    welcome_text.setText(info_text)
    layout.addWidget(welcome_text)
    
    return start_widget

def main():
    app = QApplication([])
    window = QWidget()
    window.setWindowTitle('Content Assistant')
    
    # Create layouts
    main_layout = QVBoxLayout(window)
    function_button_area = QHBoxLayout()
    content_area = QStackedWidget()
    
    # Initialize database
    if not initialize_database():
        print("Failed to initialize database.")
        return
    
    # Create start widget and add it to content area
    start_widget = create_start_widget()
    content_area.addWidget(start_widget)
    
    # Create widgets
    widgets = {
        'excel': (ExcelProcessingWidget(), 'Excel processin', 'Process item-worklists'),
        'file_search': (FileSearchApp(), 'Data/Info Search', 'Search in files for information'),
        'image': (ImageProcessingWidget(), 'Image handling', 'Search and process images'),
        'database': (DatabaseViewWidget(), 'Database Viewer', 'View and manage database')
    }
    
    # Add widgets to content area and create buttons
    for widget, text, tooltip in widgets.values():
        content_area.addWidget(widget)
        button = create_nav_button(text, tooltip, widget, content_area)
        function_button_area.addWidget(button)
    
    # Create home button
    home_button = create_nav_button('Home', 'Return to start page', start_widget, content_area)
    function_button_area.insertWidget(0, home_button)  # Add home button at the beginning
    
    # Layout assembly
    main_layout.addLayout(function_button_area)
    main_layout.addWidget(content_area)
    
    # Window setup
    window.setMinimumSize(800, 600)
    window.show()
    
    # Set start widget as default view
    content_area.setCurrentWidget(start_widget)
    
    return app.exec_()

if __name__ == '__main__':
    main()
