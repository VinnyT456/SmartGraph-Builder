from ctypes import alignment
from io import BytesIO
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QImage, QPainter, QPainterPath, QPixmap
from PyQt6.QtWidgets import (
    QHBoxLayout, QLabel, QPushButton, QSizePolicy, QStackedLayout, QWidget, QVBoxLayout
)
from sections.plot_manager import PlotManager
import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

class graph_generator(QWidget):
    def __init__(self):
        super().__init__()

        self.plot_manager = PlotManager()

    def prepare_plotting(self):
        self.current_graph_parameters = self.plot_manager.get_db()
        self.default_config_plot_manager = PlotManager("./default_plot_config.json")

        self.dataset = pd.read_csv(self.current_graph_parameters.get("data"))

        self.graph_type = self.current_graph_parameters["type"]
        self.available_graphs = {
            "Scatter Plot":sns.scatterplot
        }

        self.graph_axis_titles = self.current_graph_parameters.get("axis-title")
        self.graph_title = self.current_graph_parameters.get("title")
        self.graph_grid = self.current_graph_parameters.get("grid")

        self.graph_legend_parameters = self.current_graph_parameters.get("legend")

        for key in ["legend","version","type","grid","axis-title","title"]:
            self.current_graph_parameters.pop(key,None)

        self.graph_parameters = self.current_graph_parameters.copy()
        self.graph_parameters["data"] = self.dataset

    def create_graph(self,parent=None):
        self.prepare_plotting()

        widget = QWidget(parent)
        widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        # make the matplotlib figure
        graph = self.available_graphs.get(self.graph_type)(**self.graph_parameters)
        fig = graph.get_figure()
        buf = BytesIO()
        fig.savefig(buf, format="png")
        buf.seek(0)
        plt.close(fig)

        #Draw the pixmap with the round corners
        image = QImage.fromData(buf.getvalue())
        pixmap = QPixmap.fromImage(image)
        mask = QPixmap(pixmap.size())
        mask.fill(Qt.GlobalColor.transparent)

        painter = QPainter(mask)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        path = QPainterPath()
        path.addRoundedRect(0, 0, pixmap.width(), pixmap.height(), 20, 20)
        painter.fillPath(path, Qt.GlobalColor.white)
        painter.end()

        pixmap.setMask(mask.createMaskFromColor(Qt.GlobalColor.transparent))

        # check the QImage conversion
        label = QLabel()
        label.setObjectName("image_label")
        label.setStyleSheet("""
            QLabel#image_label {
                border-radius: 16px;
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #f5f5ff,
                    stop:0.5 #f7f5fc,
                    stop:1 #f0f0ff
                );
                padding: 0px;
            }
        """)
        label.setScaledContents(True)
        label.setPixmap(pixmap)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        image_layout = QVBoxLayout(widget)
        image_layout.addWidget(label)
        image_layout.setContentsMargins(0,0,0,0)
        image_layout.setSpacing(0)

        return widget

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
        self.setObjectName("graph_display_main_screen")
        self.setStyleSheet("""
            QWidget#graph_display_main_screen{
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

        self.setFixedWidth(620)

        self.graph_generator = graph_generator()

        self.graph_widget = QWidget()
        self.graph_widget.setObjectName("graph_widget")
        self.graph_widget.setStyleSheet("""
            QWidget{
                background: transparent;
                border-radius: 24px;
            }
        """)

        # This layout is correct
        self.graph_display_layout = QStackedLayout(self)
        self.graph_display_layout.setContentsMargins(0,0,0,0)
        self.graph_display_layout.setSpacing(0)

        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

    def show_graph(self):
        try:
            graph_widget = self.graph_generator.create_graph()
            self.graph_display_layout.addWidget(graph_widget)
            self.graph_display_layout.setCurrentWidget(graph_widget)
        except:
            pass

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
