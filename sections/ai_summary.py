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
        
        #Create a new label with the text AI Menu and format it
        self.label = QLabel("AI Menu")
        self.label.setWordWrap(True)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setStyleSheet("""
            font-family: "SF Pro Display";
            font-weight: 600;
            border-radius: 16px;
        """) 
        self.label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

        #Control the size of the button and text to ensure it fits together
        self.setMinimumHeight(35)
        self.label.setMinimumHeight(25)

        #Put the label onto the button
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

        #Create a new label with the text Summarize Dataset and format it
        self.label = QLabel("Summarize Dataset")
        self.label.setWordWrap(True)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setStyleSheet("""
            font-family: "SF Pro Display";
            font-weight: 600;
            border-radius: 16px;
        """) 
        self.label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

        #Control the size of the button and text to ensure it fits together
        self.setMinimumHeight(35)
        self.label.setMinimumHeight(25)

        #Put the label onto the button
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

        #Create a new label with the text Cleaning Suggestions and format it
        self.label = QLabel("Cleaning Suggestions")
        self.label.setWordWrap(True)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setStyleSheet("""
            font-family: "SF Pro Display";
            font-weight: 600;
            border-radius: 16px;
        """) 
        self.label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

        #Control the size of the button and text to ensure it fits together
        self.setMinimumHeight(35)
        self.label.setMinimumHeight(25)

        #Put the label onto the button
        layout = QVBoxLayout(self)
        layout.addWidget(self.label)
        layout.setContentsMargins(5, 0, 5, 0)  

class AI_Summary_TopBar(QWidget):
    def __init__(self):
        super().__init__()
        
        #Create a horizontal bar to put all the buttons on and equally put it
        layout = QHBoxLayout()
        layout.addWidget(AI_Menu_button(),stretch=1)
        layout.addWidget(Summarize_Dataset_button(),stretch=1)
        layout.addWidget(Cleaning_Suggestions_button(),stretch=1)
        layout.setContentsMargins(5,5,5,5) 
        layout.setSpacing(5)

        #Set the style for the buttons
        self.setStyleSheet("""
            QWidget{
                background: white;
                border-radius: 24px;
            }
            QPushButton{
                border-radius: 16px;
                padding: 2px; 
            }
        """)

        #Control the size of the top bar and format it.
        self.setFixedHeight(50)
        self.setFixedWidth(350)
        self.setLayout(layout)

        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

class AI_Summary(QWidget):
    def __init__(self):
        super().__init__()
        #Format the section and control the size of it
        self.setStyleSheet("""
            background: white;
            border-radius: 24px;
        """)
        self.setFixedWidth(350)

        #Ensure that the widget is drawn on the main window
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

class AI_Summary_Section(QWidget):
    def __init__(self):
        super().__init__()
        self.setFixedWidth(350)

        self.ai_summary_topbar = AI_Summary_TopBar()
        self.ai_summary = AI_Summary()

        layout = QVBoxLayout(self)
        layout.addWidget(self.ai_summary_topbar)
        layout.addSpacing(5)
        layout.addWidget(self.ai_summary)
        layout.setContentsMargins(0,0,0,0) 

        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)