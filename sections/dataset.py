from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QHBoxLayout, QLabel, QPushButton, QSizePolicy, QWidget, QVBoxLayout
)

class import_replace_dataset_button(QPushButton):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("""
            background: qlineargradient(
                        x1:0, y1:1,
                        x2:0, y2:0,
                        stop:0.02 rgba(131, 125, 255, 1),
                        stop:0.36 rgba(97, 97, 255, 1),
                        stop:0.66 rgba(31, 162, 255, 1),
                        stop:1 rgba(0, 212, 255, 1)
                    );
            color: black;
        """)

        self.label = QLabel("Import Dataset")
        self.label.setWordWrap(True)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setStyleSheet("""
            font-family: "SF Pro Display";
            font-weight: 600;
            border-radius: 16px;
        """) 
        self.label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

        self.setMinimumHeight(35)
        self.label.setMinimumHeight(25)

        layout = QVBoxLayout(self)
        layout.addWidget(self.label)
        layout.setContentsMargins(5, 0, 5, 0)  

class enter_datapoints_button(QPushButton):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("""
            background: qlineargradient(
                        x1:0, y1:1,
                        x2:0, y2:0,
                        stop:0.02 rgba(131, 125, 255, 1),
                        stop:0.36 rgba(97, 97, 255, 1),
                        stop:0.66 rgba(31, 162, 255, 1),
                        stop:1 rgba(0, 212, 255, 1)
                    );
            color: black;
        """)

        self.label = QLabel("Enter Datapoints")
        self.label.setWordWrap(True)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setStyleSheet("""
            font-family: "SF Pro Display";
            font-weight: 600;
            border-radius: 16px;
        """) 
        self.label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

        self.setMinimumHeight(35)
        self.label.setMinimumHeight(25)

        layout = QVBoxLayout(self)
        layout.addWidget(self.label)
        layout.setContentsMargins(5, 0, 5, 0)  

class column_management_button(QPushButton):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("""
            background: qlineargradient(
                        x1:0, y1:1,
                        x2:0, y2:0,
                        stop:0.02 rgba(131, 125, 255, 1),
                        stop:0.36 rgba(97, 97, 255, 1),
                        stop:0.66 rgba(31, 162, 255, 1),
                        stop:1 rgba(0, 212, 255, 1)
                    );
            color: black;
        """)

        self.label = QLabel("Column Management")
        self.label.setWordWrap(True)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setStyleSheet("""
            font-family: "SF Pro Display";
            font-weight: 600;
            border-radius: 16px;
        """) 
        self.label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

        self.setMinimumHeight(35)
        self.label.setMinimumHeight(25)

        layout = QVBoxLayout(self)
        layout.addWidget(self.label)
        layout.setContentsMargins(5, 0, 5, 0)

class Dataset_TopBar(QWidget):
    def __init__(self):
        super().__init__()
        
        layout = QHBoxLayout()
        layout.addWidget(import_replace_dataset_button())
        layout.addWidget(enter_datapoints_button())
        layout.addWidget(column_management_button())
        layout.setContentsMargins(5,5,5,5) 
        layout.setSpacing(5)

        self.setStyleSheet("""
            QPushButton{
                border-radius: 16px;
                padding: 2px; 
            }
        """)

        self.setFixedHeight(40)
        self.setFixedWidth(350)
        self.setLayout(layout)

class Dataset_Section(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("""
            background: white;
            border-radius: 24px;
        """)
        self.setFixedWidth(350)

        layout = QVBoxLayout()
        layout.addWidget(Dataset_TopBar())
        layout.addStretch()
        layout.setContentsMargins(0,0,0,0) 
        layout.setSpacing(0)

        self.setLayout(layout)

        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)