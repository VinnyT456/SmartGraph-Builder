from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QDialog, QHBoxLayout, QLabel, QPushButton, QSizePolicy, QWidget, QVBoxLayout
)

graph_module = ''

SEABORN_PLOTS = {
    "Scatter Plot":{},
    "Line Plot":{},
    "Regression Plot":{},
    "Bar Plot":{},
    "Count Plot":{},
    "Box Plot":{},
    "Violin Plot":{},
    "Swarm Plot":{},
    "Strip Plot":{},
    "Histogram":{},
    "KDE Plot":{},
    "ECDF Plot":{},
    "Rug Plot":{},
    "Heatmap":{},
    "Pair Plot":{},
    "Joint Plot":{},
    "Cluster Map":{},
}

class select_graph_module(QPushButton):
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

        self.graph_module = ["Seaborn","Plotly"]
        self.graph_module_idx = -1

        self.label = QLabel("Select Graphing Module")
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

        self.clicked.connect(self.change_module)

    def change_module(self):
        self.graph_module_idx += 1
        self.graph_module_idx %= 2
        self.label.setText(f"{self.graph_module[self.graph_module_idx]}")
        self.label.setStyleSheet("""
            font-family: "SF Pro Display";
            font-weight: 600;
            font-size: 18px;
            border-radius: 16px;
        """) 

        global graph_module
        graph_module = self.graph_module[self.graph_module_idx]

class select_graph_window(QDialog):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Select Your Graph")
        self.setFixedHeight(500)
        self.setFixedWidth(600)

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

        self.graph_label = QLabel("Graph Name")
        self.graph_label.setWordWrap(True)
        self.graph_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.graph_label.setStyleSheet("""
            background: white;
            font-family: "SF Pro Display";
            font-weight: 600;
            border-radius: 16px;
            font-size: 32px;
        """) 

        self.graph_name = QWidget()
        self.graph_name.setObjectName("Graph_Name")
        self.graph_name.setStyleSheet("""
            QWidget#Graph_Name{
                background: white;
                border: 1px solid black;
                border-radius: 24px;
                font-family: "SF Pro Display";
                font-size: 32px;
                font-weight: 600;
            }
        """)

        graph_name_layout = QVBoxLayout()
        graph_name_layout.addWidget(self.graph_label)
        self.graph_name.setLayout(graph_name_layout)

        self.graph_image = QWidget()
        self.graph_image.setObjectName("Graph_Image")
        self.graph_image.setStyleSheet("""
            QWidget#Graph_Image{
                background: white;
                border: 1px solid black;
                border-radius: 24px;
            }
        """)

        self.select_button = QPushButton("Select")
        self.select_button.setObjectName("Select_Button")
        self.select_button.setStyleSheet("""
            QPushButton#Select_Button{  
                background: white;
                border: 1px solid black;
                border-radius: 24px;
                font-family: "SF Pro Display";
                font-size: 32px;
                font-weight: 600;
            }
        """)     

        self.previous_graph_label = QLabel("←")
        self.previous_graph_label.setObjectName("Previous_Graph_Symbol")
        self.previous_graph_label.setStyleSheet("""
            QWidget#Previous_Graph_Symbol{
                background: transparent;
                border-radius: 24px;
                font-family: "SF Pro Display";
                font-size: 32px;
                font-weight: 600;
            }
        """)

        self.previous_graph = QPushButton()
        self.previous_graph.setObjectName("Previous_Graph")
        self.previous_graph.setStyleSheet("""
            QPushButton#Previous_Graph{  
                background: white;
                border: 1px solid black;
                border-radius: 24px;
                font-family: "SF Pro Display";
                font-size: 32px;
                font-weight: 600;
            }
        """)    

        previous_graph_layout = QVBoxLayout()
        previous_graph_layout.addWidget(self.previous_graph_label,alignment=Qt.AlignmentFlag.AlignCenter)
        self.previous_graph.setLayout(previous_graph_layout)

        self.next_graph_label = QLabel("→")
        self.next_graph_label.setObjectName("Next_Graph_Symbol")
        self.next_graph_label.setStyleSheet("""
            QWidget#Next_Graph_Symbol{
                background: transparent;
                border-radius: 24px;
                font-family: "SF Pro Display";
                font-size: 32px;
                font-weight: 600;
            }
        """)

        self.next_graph = QPushButton()
        self.next_graph.setObjectName("Next_Graph")
        self.next_graph.setStyleSheet("""
            QPushButton#Next_Graph{  
                background: white;
                border: 1px solid black;
                border-radius: 24px;
                font-family: "SF Pro Display";
                font-size: 32px;
                font-weight: 600;
            }
        """)    

        next_graph_layout = QVBoxLayout()
        next_graph_layout.addWidget(self.next_graph_label,alignment=Qt.AlignmentFlag.AlignCenter)
        self.next_graph.setLayout(next_graph_layout)

        self.graph_name.setFixedHeight(60)
        self.graph_name.setFixedWidth(400)

        self.graph_image.setFixedHeight(350)
        self.graph_image.setFixedWidth(400)

        self.select_button.setFixedHeight(50)
        self.select_button.setFixedWidth(200)

        self.previous_graph.setFixedHeight(60)
        self.previous_graph.setFixedWidth(60)
        
        self.next_graph.setFixedHeight(60)
        self.next_graph.setFixedWidth(60)

        vertical_layout = QVBoxLayout()
        vertical_layout.addWidget(self.graph_name,alignment=Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)
        vertical_layout.addWidget(self.graph_image,alignment=Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignHCenter)
        vertical_layout.addWidget(self.select_button,alignment=Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignBottom)
        vertical_layout.setSpacing(10)

        main_layout = QHBoxLayout()
        main_layout.addWidget(self.previous_graph,alignment=Qt.AlignmentFlag.AlignLeft)
        main_layout.addLayout(vertical_layout)
        main_layout.addWidget(self.next_graph,alignment=Qt.AlignmentFlag.AlignRight)

        main_layout.setStretch(0, 1) 
        main_layout.setStretch(1, 0)  
        main_layout.setStretch(2, 1)  

        main_layout.setContentsMargins(10,10,10,10)

        self.setLayout(main_layout)

class select_graph(QPushButton):
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

        self.label = QLabel("Select Type of Graph")
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

        self.clicked.connect(self.open_select_graph_window)

    def open_select_graph_window(self):
        if (graph_module != ''):
            select_graph_window().exec()

class GraphParameter_TopBar(QWidget):
    def __init__(self):
        super().__init__()

        layout = QHBoxLayout()
        layout.addWidget(select_graph_module())
        layout.addWidget(select_graph())
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

class GraphParameter_Section(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("""
            background: white;
            border-radius: 24px;
        """)

        self.setFixedWidth(350)
        
        layout = QVBoxLayout()
        layout.addWidget(GraphParameter_TopBar())
        layout.addStretch()
        layout.setContentsMargins(0,0,0,0) 
        layout.setSpacing(0)

        self.setLayout(layout)

        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)