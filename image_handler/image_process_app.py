from PyQt5.QtWidgets import (
    QWidget,
    QLabel,
    QLineEdit,
    QPushButton,
    QListWidget,
    QFileDialog,
    QMessageBox,
    QVBoxLayout,
    QApplication,
    QScrollArea,
    QSizePolicy,
)
from PyQt5.QtCore import Qt  # Add this import
import os
from widgets.base_widget import BaseProcessingWidget
from image_handler.image_processing_handler import (
    ImageProcessingHandler,
)  # Import the new handler class


class ImageProcessingWidget(BaseProcessingWidget):
    """A PyQt widget for processing and organizing image files.
    This widget is a subclass of QWidget and provides a GUI interface for processing images.

    This widget provides a GUI interface for:
    1. Processing images by search terms:
        - Search for images using multiple search terms
        - Group images by search criteria
        - Process multiple product groups simultaneously
        - Support for comma-separated search terms within groups
        - Support for semicolon-separated groups

    2. Batch processing of image folders:
        - Process all images in a selected folder and subfolders
        - Supports .jpg, .jpeg, .png, .tiff, and .webp formats
        - Maintains folder structure in destination
        - Handles color profiles and transparency
        - Resizes large images (300 dpi and >2500px) automatically
        - Flags low resolution images (<800x600px)

    3. Image processing features:
        - Color mode conversion to RGB
        - ICC profile handling
        - Transparency handling
        - Image resizing
        - Unique filename generation
        - Error handling and logging

    The widget includes:
        - Search term input field
        - Processing start button
        - Folder processing button
        - Status listbox for progress and error messages
        - File dialogs for folder selection
        - Message boxes for warnings and errors

    Usage:
        widget = ImageProcessingWidget()
        widget.show()  # Display the widget in a PyQt application
    """

    def __init__(self):
        super().__init__()
        self.not_found_list = []  # Initialize the list for search terms not found
        self.image_handler = ImageProcessingHandler(
            self
        )  # Initialize the image handler
        self.init_ui()

    def init_ui(self):
        # Create main layout with proper spacing
        self.layout.setSpacing(10)
        self.layout.setContentsMargins(10, 10, 10, 10)

        # Add title
        title = QLabel("Image Processing Tool")
        title.setObjectName("title")
        self.layout.addWidget(title)
        self.layout.addSpacing(10)

        # Add info section
        info_text = """
        Welcome to the Image Processing Tool!

        Features:
        - Search for images using multiple search terms.
        - Group images by search criteria.
        - Process multiple product groups simultaneously.
        - Support for comma-separated search terms within groups.
        - Support for semicolon-separated groups.
        - Process all images in a selected folder and its subfolders.
        - Supports .jpg, .jpeg, .png, .tiff, and .webp formats.
        - Maintains folder structure in the destination.
        - Handles color profiles and transparency.
        - Automatically resizes large images (300 dpi and >2500px).
        - Flags low resolution images (<800x600px).
        - Converts color mode to RGB.
        - Handles ICC profiles.
        - Manages transparency.
        - Generates unique filenames.
        - Provides error handling and logging.

        How to Use:
        1. Select the folder containing the images you want to process.
        2. Enter your search terms, separated by commas for multiple terms within a group.
        3. Use semicolons to separate different groups of search terms.
        4. Click the 'Process' button to start processing the images.
        5. The tool will process the images and display the results in the listboxes.
        6. Click 'Show images not found' to see a list of images that were not found.

        Enjoy using the Image Processing Tool!
        """
        info_label = QLabel(info_text)
        info_label.setObjectName("info")
        info_label.setWordWrap(True)

        # Configure scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidget(info_label)
        scroll_area.setWidgetResizable(True)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setMinimumHeight(100)  # Reduced minimum height
        scroll_area.setMaximumHeight(200)  # Reduced maximum height
        self.layout.addWidget(scroll_area)
        self.layout.addSpacing(15)

        # Create search section with spacing
        self.create_search_section()
        self.layout.addSpacing(15)

        # Create action buttons
        self.create_buttons()
        self.layout.addSpacing(15)

        # Create results section
        self.create_results_section()

    def create_search_section(self):
        label = QLabel(
            "Product Search \nEnter one or more search terms separated by commas (,)\n"
            "For multiple products, separate them with semicolons (;)"
        )
        label.setObjectName("section-label")
        label.setWordWrap(True)  # Add this line to enable word wrapping
        self.layout.addWidget(label)

        self.entry = QLineEdit(self)
        self.entry.setPlaceholderText("Enter search terms...")
        self.layout.addWidget(self.entry)

    def create_buttons(self):
        start_button = QPushButton("Start Search and Processing", self)
        start_button.clicked.connect(self.start_processing)
        self.layout.addWidget(start_button)

        folder_button = QPushButton(
            "Process Folder Images\nClick to select folder", self
        )
        folder_button.clicked.connect(self.process_folder_images)
        self.layout.addWidget(folder_button)

        show_not_found_button = QPushButton("Show images not found", self)
        show_not_found_button.clicked.connect(self.show_not_found_popup)
        self.layout.addWidget(show_not_found_button)

    def create_results_section(self):
        results_label = QLabel("Processing Results:")
        results_label.setObjectName("section-label")
        self.layout.addWidget(results_label)

        # Remove fixed height from file_listbox and use sizePolicy instead
        self.file_listbox = QListWidget(self)
        self.file_listbox.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.file_listbox.setMinimumHeight(100)
        self.layout.addWidget(self.file_listbox)

        self.layout.addSpacing(10)

        # Remove fixed height from not_found_listbox and use sizePolicy instead
        self.not_found_listbox = QListWidget(self)
        self.not_found_listbox.setSizePolicy(
            QSizePolicy.Expanding, QSizePolicy.Expanding
        )
        self.not_found_listbox.setMinimumHeight(100)
        self.layout.addWidget(self.not_found_listbox)

    def add_to_listbox(self, message):
        """Add a message to the appropriate listbox view."""
        message = self.shorten_path_in_message(message)
        if "not found" in message.lower():
            self.not_found_listbox.addItem(message)
            self.not_found_list.append(message)  # Add to the not found list
            print(f"Not found: {message}")  # Print statement for not found images
        else:
            self.file_listbox.addItem(message)
            print(f"Processed: {message}")  # Print statement for processed images

    def clear_listbox(self):
        """Clear both listbox views and reset the not found list."""
        self.file_listbox.clear()
        self.not_found_listbox.clear()
        self.not_found_list = []  # Reset the not found list

    def show_message_box(self, title, message, icon=QMessageBox.Information):
        """Show a message box, usually critical, with the specified title, message, and icon."""
        message = self.shorten_path_in_message(message)
        msg_box = QMessageBox()
        msg_box.setIcon(icon)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.exec_()

    def shorten_path_in_message(self, message):
        """Shorten the path in a message to show only the last part of the path."""
        parts = message.split(os.sep)
        if len(parts) >= 3:
            return os.sep.join(parts[-3:])
        return message

    def show_not_found_popup(self):
        """Show a pop-up window with the list of search terms not found."""
        if not self.not_found_list:
            self.show_message_box("Images Not Found", "No images were not found.")
        else:
            not_found_str = "\n".join(self.not_found_list)
            self.show_message_box("Images Not Found", not_found_str)

    def start_processing(self):
        """Start the image processing based on the search terms entered by the user."""
        self.clear_listbox()
        search_terms = self.entry.text()
        if not self.validate_search_terms(search_terms):
            return

        search_groups = [group.strip() for group in search_terms.split(";")]

        folder_to_search = QFileDialog.getExistingDirectory(
            self, "Välj mapp att söka i"
        )
        destination_folder = QFileDialog.getExistingDirectory(self, "Välj målplats")

        if not folder_to_search or not destination_folder:
            self.show_message_box("Warning", "No folder selected.", QMessageBox.Warning)
            return

        for group in search_groups:
            search_terms_list = [term.strip() for term in group.split(",")]
            print(
                f"Processing group: {search_terms_list}"
            )  # Debugging to check which group is being processed
            group_folder_name = search_terms_list[
                0
            ]  # Use the first search term as the group folder name
            group_destination_folder = os.path.join(
                destination_folder, group_folder_name
            )

            if not os.path.exists(group_destination_folder):
                os.makedirs(group_destination_folder)

            # Process images using the search terms and folders
            self.image_handler.process_images_by_search_terms(
                search_terms_list, folder_to_search, group_destination_folder
            )

    def process_folder_images(self):
        """Process all images in a selected folder and subfolders."""
        self.clear_listbox()
        folder_path = QFileDialog.getExistingDirectory(self, "Välj mapp med bilder")
        if not folder_path:
            self.show_message_box("Warning", "No folder selected.", QMessageBox.Warning)
            return

        destination_folder = QFileDialog.getExistingDirectory(self, "Välj målplats")
        if not destination_folder:
            self.show_message_box(
                "Warning", "No destination folder selected.", QMessageBox.Warning
            )
            return
        self.file_listbox.addItem(f"Processing folder: {folder_path}")

        try:
            for root, dirs, files in os.walk(folder_path):
                for file in files:
                    if file.lower().endswith(
                        (".jpg", ".jpeg", ".png", ".tiff", ".tif", ".webp")
                    ):
                        image_path = os.path.join(root, file)
                        relative_path = os.path.relpath(root, folder_path)
                        destination_dir = os.path.join(
                            destination_folder, relative_path
                        )
                        os.makedirs(destination_dir, exist_ok=True)

                        self.file_listbox.addItem(f"Processing image: {image_path}")
                        self.image_handler.process_and_save_image(
                            image_path, destination_dir
                        )
                        self.file_listbox.addItem("Processing complete")
            self.add_to_listbox("All images processed")
        except Exception as e:
            self.add_to_listbox(
                f"Error processing folder: {str(e)}"
            )  # Add error message to the listbox
            self.show_message_box(
                "Error", f"Error processing folder: {str(e)}", QMessageBox.Critical
            )  # Show error message box

    def validate_search_terms(self, search_terms):
        """Validate the search terms entered by the user."""
        if not search_terms:
            self.show_message_box(
                "Warning", "No search terms entered.", QMessageBox.Warning
            )  # Show warning message box
            return False
        return True

    def generate_unique_filename(self, destination_folder, filename, suffix):
        """Generate a unique filename by adding a suffix and incrementing a counter if needed."""
        return self.image_handler.generate_unique_filename(
            destination_folder, filename, suffix
        )

    def delete_empty_group_folder(self, folder_path):
        """Delete the group folder if it is empty."""
        self.image_handler.delete_empty_group_folder(folder_path)

    def resize_image_if_needed(self, img, filename):
        """Resize image if it is larger than 2500 pixels in width or height and with a dpi higher than 150. Or flag low resolution images.
        Keep the aspect ratio and use Lanczos resampling for resizing. And keep the original DPI.
        """
        return self.image_handler.resize_image_if_needed(img, filename)

    def convert_image_mode(self, img, file_path):
        """Convert the image mode to RGB if needed.
        Using ICC profile if available and handling transparency."""
        return self.image_handler.convert_image_mode(img, file_path)

    def process_image(self, img, file_path):
        """Handle all image processing steps."""
        return self.image_handler.process_image(img, file_path)
