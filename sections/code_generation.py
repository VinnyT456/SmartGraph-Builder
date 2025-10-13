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
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #f5f5ff,
                    stop:0.5 #f7f5fc,
                    stop:1 #f0f0ff
                );
                border: 2px solid #d0d0ff;
                border-radius: 24px;
            }
        """)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)