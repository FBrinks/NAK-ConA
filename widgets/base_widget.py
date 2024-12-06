from PyQt5.QtWidgets import QWidget, QVBoxLayout

class BaseProcessingWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()
        self.layout.setSpacing(10)
        self.layout.setContentsMargins(20, 20, 20, 20)
        self.setLayout(self.layout)
        self.apply_base_styles()

    def apply_base_styles(self):
        self.setStyleSheet(
            """
            QWidget {
                background-color: #f5f5f5;
                font-family: Arial;
            }
            #title {
                font-size: 18px;
                font-weight: bold;
                color: #2c3e50;
                padding: 10px;
            }
            #info {
                background-color: #ffffff;
                padding: 15px;
                border-radius: 5px;
                border: 1px solid #dcdcdc;
                color: #34495e;
                margin: 10px 0;
            }
            #section-label {
                font-weight: bold;
                color: #2c3e50;
            }
            QLineEdit {
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
            QListWidget, QTextEdit {
                background-color: white;
                border: 1px solid #bdc3c7;
                border-radius: 4px;
            }
        """
        )
