from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QHBoxLayout, QLabel, QPushButton, QSizePolicy, QWidget, QVBoxLayout
)

class AI_Menu_button(QPushButton):
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
        
        self.label = QLabel("AI Menu")
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

class Summarize_Dataset_button(QPushButton):
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

        self.label = QLabel("Summarize Dataset")
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

class Cleaning_Suggestions_button(QPushButton):
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

        self.label = QLabel("Cleaning Suggestions")
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

class AI_Summary_TopBar(QWidget):
    def __init__(self):
        super().__init__()
        
        layout = QHBoxLayout()
        layout.addWidget(AI_Menu_button(),stretch=1)
        layout.addWidget(Summarize_Dataset_button(),stretch=1)
        layout.addWidget(Cleaning_Suggestions_button(),stretch=1)
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

class AI_Summary_section(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("""
            background: white;
            border-radius: 24px;
        """)
        self.setFixedWidth(350)

        layout = QVBoxLayout()
        layout.addWidget(AI_Summary_TopBar())
        layout.addStretch()
        layout.setContentsMargins(0,0,0,0) 
        layout.setSpacing(0)

        self.setLayout(layout)

        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)