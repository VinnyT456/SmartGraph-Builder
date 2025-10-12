from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QWidget
)

class Code_Section(QWidget):
    def __init__(self):
        super().__init__()

        #Create a small section to display the code and ensure it's drawn on the window
        self.setFixedWidth(620)
        self.setMinimumHeight(100)
        self.setStyleSheet("""
            QWidget{
                background: white;
                border-radius: 24px;
            }
        """)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)