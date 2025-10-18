from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QHBoxLayout, QLabel, QPushButton, QSizePolicy, QWidget, QVBoxLayout
)

class new_graph_button(QPushButton):
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
            color: #c8f7ff;
        """)

        #Create a new label with the text New Graph and format it
        self.label = QLabel("New Graph")
        self.label.setWordWrap(True)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setStyleSheet("""
            font-family: "SF Pro Display";
            font-weight: 600;
            border-radius: 16px;
        """) 
        self.label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

        #Control the size of the button and the label to ensure they fit together
        self.setMinimumHeight(35)
        self.label.setMinimumHeight(25)

        #Add the text onto the button and format it in order for it to fit
        layout = QVBoxLayout(self)
        layout.addWidget(self.label)
        layout.setContentsMargins(5, 0, 5, 0)  

class undo_button(QPushButton):
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
            color: #c8f7ff;
            
        """)

        #Create a new label with the text Undo and format it
        self.label = QLabel("Undo")
        self.label.setWordWrap(True)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setStyleSheet("""
            font-family: "SF Pro Display";
            font-weight: 600;
            border-radius: 16px;
        """) 
        self.label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

        #Control the size of the button and the label to ensure they fit together
        self.setMinimumHeight(35)
        self.label.setMinimumHeight(25)

        #Add the text onto the button and format it in order for it to fit
        layout = QVBoxLayout(self)
        layout.addWidget(self.label)
        layout.setContentsMargins(5, 0, 5, 0)  

class clear_button(QPushButton):
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
            color: #c8f7ff;
            
        """)

        #Create a new label with the text Clear and format it
        self.label = QLabel("Clear")
        self.label.setWordWrap(True)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setStyleSheet("""
            font-family: "SF Pro Display";
            font-weight: 600;
            border-radius: 16px;
        """) 
        self.label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

        #Control the size of the button and the label to ensure they fit together
        self.setMinimumHeight(35)
        self.label.setMinimumHeight(25)

        #Add the text onto the button and format it in order for it to fit
        layout = QVBoxLayout(self)
        layout.addWidget(self.label)
        layout.setContentsMargins(5, 0, 5, 0)  

class previous_graph_button(QPushButton):
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
            color: #c8f7ff;
            
        """)

        #Create a new label with the text Previous Graph and format it
        self.label = QLabel("Previous Graph")
        self.label.setWordWrap(True)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setStyleSheet("""
            font-family: "SF Pro Display";
            font-weight: 600;
            border-radius: 16px;
        """) 
        self.label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

        #Control the size of the button and the label to ensure they fit together
        self.setMinimumHeight(35)
        self.label.setMinimumHeight(25)

        #Add the text onto the button and format it in order for it to fit
        layout = QVBoxLayout(self)
        layout.addWidget(self.label)
        layout.setContentsMargins(5, 0, 5, 0)  
    
class zoom_in_button(QPushButton):
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
            color: #c8f7ff;
            
        """)

        #Create a new label with the text Zoom In and format it
        self.label = QLabel("Zoom In")
        self.label.setWordWrap(True)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setStyleSheet("""
            font-family: "SF Pro Display";
            font-weight: 600;
            border-radius: 16px;
        """) 
        self.label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

        #Control the size of the button and the label to ensure they fit together
        self.setMinimumHeight(35)
        self.label.setMinimumHeight(25)

        #Add the text onto the button and format it in order for it to fit
        layout = QVBoxLayout(self)
        layout.addWidget(self.label)
        layout.setContentsMargins(5, 0, 5, 0)  

class zoom_out_button(QPushButton):
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
            color: #c8f7ff;
            
        """)

        #Create a new label with the text Zoom Out and format it
        self.label = QLabel("Zoom Out")
        self.label.setWordWrap(True)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setStyleSheet("""
            font-family: "SF Pro Display";
            font-weight: 600;
            border-radius: 16px;
        """) 
        self.label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

        #Control the size of the button and the label to ensure they fit together
        self.setMinimumHeight(35)
        self.label.setMinimumHeight(25)

        #Add the text onto the button and format it in order for it to fit
        layout = QVBoxLayout(self)
        layout.addWidget(self.label)
        layout.setContentsMargins(5, 0, 5, 0)  

class copy_code_button(QPushButton):
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
            color: #c8f7ff;
            
        """)

        #Create a new label with the text Copy Code and format it
        self.label = QLabel("Copy Code")
        self.label.setWordWrap(True)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setStyleSheet("""
            font-family: "SF Pro Display";
            font-weight: 600;
            border-radius: 16px;
        """) 
        self.label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

        #Control the size of the button and the label to ensure they fit together
        self.setMinimumHeight(35)
        self.label.setMinimumHeight(25)

        #Add the text onto the button and format it in order for it to fit
        layout = QVBoxLayout(self)
        layout.addWidget(self.label)
        layout.setContentsMargins(5, 0, 5, 0)  

class export_graph_button(QPushButton):
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
            color: #c8f7ff;
            
        """)

        #Create a new label with the text Export Graph and format it
        self.label = QLabel("Export Graph")
        self.label.setWordWrap(True)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setStyleSheet("""
            font-family: "SF Pro Display";
            font-weight: 600;
            border-radius: 16px;
        """) 
        self.label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

        #Control the size of the button and the label to ensure they fit together
        self.setMinimumHeight(35)
        self.label.setMinimumHeight(25)

        #Add the text onto the button and format it in order for it to fit
        layout = QVBoxLayout(self)
        layout.addWidget(self.label)
        layout.setContentsMargins(5, 0, 5, 0)  

class Graph_TopBar(QWidget):
    def __init__(self):
        super().__init__()
        
        #Put all the buttons together in a horizontal box and format
        layout = QHBoxLayout()
        layout.addWidget(new_graph_button(),stretch=1)
        layout.addWidget(undo_button(),stretch=1)
        layout.addWidget(clear_button(),stretch=1)
        layout.addWidget(previous_graph_button(),stretch=1)
        layout.addWidget(zoom_in_button(),stretch=1)
        layout.addWidget(zoom_out_button(),stretch=1)
        layout.addWidget(copy_code_button(),stretch=1)
        layout.addWidget(export_graph_button(),stretch=1)
        
        layout.setContentsMargins(5,5,5,5) 
        layout.setSpacing(5)

        #Control the size of the box and apply the layout to the Top Bar
        self.setFixedHeight(50)
        self.setFixedWidth(620)
        self.setLayout(layout)

        self.setObjectName("graph_topbar")

        #Format the Top bar and the buttons on it
        self.setStyleSheet("""
            QWidget#graph_topbar{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #f5f5ff,
                    stop:0.5 #f7f5fc,
                    stop:1 #f0f0ff
                );
                border: 2px solid #c0c0ff;
                border-radius: 24px;
            }
            QPushButton{
                border-radius: 16px;
                padding: 2px; 
            }
        """)

        #Ensure the everything is properly drawn on the main window
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        
class Graph_Display(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("""
            background: qlineargradient(
                x1:0, y1:0, x2:1, y2:0,
                stop:0 #f5f5ff,
                stop:0.5 #f7f5fc,
                stop:1 #f0f0ff
            );
            border: 2px solid #d0d0ff;
            border-radius: 24px;
        """)

        #Control the size of the section
        self.setFixedWidth(620)

        #Ensure that everything is properly drawn onto the main window
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

class Graph_Section(QWidget):
    def __init__(self):
        super().__init__()
        self.setFixedWidth(620)

        self.graph_topbar = Graph_TopBar()
        self.display_graph = Graph_Display()

        layout = QVBoxLayout(self)
        layout.addWidget(self.graph_topbar)
        layout.addSpacing(5)
        layout.addWidget(self.display_graph)
        layout.setContentsMargins(0,0,0,0) 

        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
