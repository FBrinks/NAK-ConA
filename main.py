from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QStackedWidget,
    QToolTip,
    QGraphicsDropShadowEffect,
    QLabel,
    QTextEdit,
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
    QToolTip.setFont(QFont("SansSerif", 10))
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


def apply_button_shadow_effect(
    button, blur_radius=5, offset=(2, 2), color=QColor(63, 63, 63, 180)
):
    shadow = QGraphicsDropShadowEffect()
    shadow.setBlurRadius(blur_radius)
    shadow.setOffset(offset[0], offset[1])  # (x, y)
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
    welcome_text.setStyleSheet(
        """
        QTextEdit {
            border: 1px solid #c0c0c0;
            background-color: #f0f0f0;
            padding: 5px;
        }
    """
    )
    shadow = QGraphicsDropShadowEffect()
    shadow.setBlurRadius(10)
    shadow.setOffset(3, 3)
    shadow.setColor(QColor(63, 63, 63, 180))
    welcome_text.setGraphicsEffect(shadow)

    # Set welcome text, and i kept a class for the logo image but i removed it for now but kept the style
    info_text = """
        <style>
        .logo-image {
            width: 50px;
            height: auto;
            margin-left: 10px;
            vertical-align: middle;
        }
        </style>
        <table>
            <tr>
                <td>
                    <br>
                    <br>
                    <h2>Welcome to <b>Conrad</b></h2>
                </td>
            </tr>
        </table>
        
        <p style="font-size:14px;">
            Conrad is your <b>content organizer</b> and <b>research assistant</b> for product enrichment.
        </p>
        <p style="font-size:13px;">
            If you have any <b>questions</b>, <b>feedback</b>, or <b>issues</b>, feel free to reach out to:
            <br><b>Email:</b> <a href='mailto:fredde.brink@outlook.com'>fredde.brink@outlook.com</a>
            <br><b>Teams:</b> Contact me directly within the company.
        </p>
        
        <h3 style="color:#2c3e50;">Key Features</h3>
        
        <h4>1. Excel Processing</h4>
        <ul style="font-size:13px;">
            <li>Export an item list from PIM using <b>English</b> as the language.</li>
            <li>Supports attributes: Product/Item Number, Brand, Product Name, Product, Supplier Product No, External Color Code.</li>
            <li>Removes duplicates and cleans data automatically.</li>
            <li>Combines supplier product numbers with external color codes for image searches in content banks.</li>
            <li>Utilizes <b>TEXTJOIN</b> in Excel for seamless Info Search and Image Search/Processing.</li>
        </ul>
        
        <h4>2. Info Search</h4>
        <ul style="font-size:13px;">
            <li>Insert multiple <b>search terms</b> to scan files and extract information.</li>
            <li>Adds information to a local database for easy access.</li>
            <li>Generates SEO-optimized <b>product texts</b> for database entries.</li>
        </ul>
        
        <h4>3. Image Search and Processing</h4>
        <ul style="font-size:13px;">
            <li>Search for images in folders and subfolders and process them effortlessly.</li>
            <li>Convert and resize images to meet your needs.</li>
            <li style="color:#e74c3c;"><b>Note:</b> Cropping and background color changes are not yet implemented, but transparent PNGs are supported and converted to white backgrounds.</li>
        </ul>
        
        <h4>4. Database View</h4>
        <ul style="font-size:13px;">
            <li>View and manage database entries seamlessly.</li>
            <li>Pop-up windows for editing and viewing product information in detail.</li>
            <li>Search and filter content to find what you need quickly.</li>
        </ul>
        
        <p style="font-size:14px; font-weight:bold; color:#3498db;">
            Select a function from the buttons above to get started.
        </p>
    """

    welcome_text.setHtml(info_text)
    layout.addWidget(welcome_text)

    return start_widget


def main():
    app = QApplication([])
    window = QWidget()
    window.setWindowTitle("Conrad - Content assistant")

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
        "excel": (ExcelProcessingWidget(), "Excel processin", "Process item-worklists"),
        "file_search": (
            FileSearchApp(),
            "Data/Info Search",
            "Search in files for information",
        ),
        "image": (
            ImageProcessingWidget(),
            "Image handling",
            "Search and process images",
        ),
        "database": (
            DatabaseViewWidget(),
            "Database Viewer",
            "View and manage database",
        ),
    }

    # Add widgets to content area and create buttons
    for widget, text, tooltip in widgets.values():
        content_area.addWidget(widget)
        button = create_nav_button(text, tooltip, widget, content_area)
        function_button_area.addWidget(button)

    # Create home button
    home_button = create_nav_button(
        "Home", "Return to start page", start_widget, content_area
    )
    function_button_area.insertWidget(
        0, home_button
    )  # Add home button at the beginning

    # Layout assembly
    main_layout.addLayout(function_button_area)
    main_layout.addWidget(content_area)

    # Window setup
    window.setMinimumSize(800, 600)
    window.show()

    # Set start widget as default view
    content_area.setCurrentWidget(start_widget)

    return app.exec_()


if __name__ == "__main__":
    main()
