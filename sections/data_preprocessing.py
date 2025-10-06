from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QSizePolicy, QWidget, QGridLayout, QVBoxLayout
)

class DataPreprocessing_Section(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("""
            background: white;
        """)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)