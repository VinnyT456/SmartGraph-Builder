import os
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QKeySequence, QPixmap, QShortcut
from PyQt6.QtWidgets import (
    QDialog, QGridLayout, QHBoxLayout, QHeaderView, QLabel, QPushButton, QScrollArea, QSizePolicy, QTableView, QWidget, QVBoxLayout
)
from sections.buttons import *

graph_module = ''
selected_graph = ''
idx = 0

SEABORN_PLOTS = {
    "Scatter Plot":{
        "Image":"sample_graphs/scatter_plot.png",
        "x-axis_data_type":["float"],
        "y-axis_data_type":["float"],
        "parameters":["x-axis","y-axis","axis title","title",
                    "legend","grid","hue", "style", "size", 
                    "palette","alpha", "marker", "s", "edgecolor"]
    },
    "Line Plot":{
        "Image":"sample_graphs/line_plot.png",
        "x-axis_data_type":["float","int"],
        "y-axis_data_type":["float","int"],
        "parameters":["x-axis","y-axis","axis title","title",
                    "legend","grid","hue","style","size",
                    "palette","alpha","linewidth","marker","linestyle"],
    },
    "Regression Plot":{
        "Image":"sample_graphs/regression_plot.png",
        "x-axis_data_type":["float"],
        "y-axis_data_type":["float"],
        "parameters":["x-axis","y-axis","axis title","title",
                    "legend","grid","color","marker","scatter",
                    "fit_reg","ci","line_kws","scatter_kws","truncate"],
    },
    "Bar Plot":{
        "Image":"sample_graphs/bar_plot.png",
        "x-axis_data_type":["object","category"],
        "y-axis_data_type":["float","int"],
        "parameters":["x-axis","y-axis","axis title","title",
                    "legend","grid","hue","palette","errorbar",
                    "ci","capsize","orient","estimator","width"],
    },
    "Count Plot":{
        "Image":"sample_graphs/count_plot.png",
        "x-axis_data_type":["object","category"],
        "parameters":["x-axis","y-axis","axis title","title",
                    "legend","grid","hue","palette","orient",
                    "order","hue_order","dodge","width","saturation"],
    },
    "Box Plot":{
        "Image":"sample_graphs/box_plot.png",
        "x-axis_data_type":["object","category"],
        "y-axis_data_type":["float","int"],
        "parameters":["x-axis","y-axis","axis title","title",
                    "legend","grid","hue","palette","orient",
                    "order","hue_order","width","fliersize","linewidth"],
    },
    "Violin Plot":{
        "Image":"sample_graphs/violin_plot.png",
        "x-axis_data_type":["object","category"],
        "y-axis_data_type":["float","int"],
        "parameters":["x-axis","y-axis","axis title","title",
                    "legend","grid","hue","palette","orient",
                    "order","hue_order","bw","inner","linewidth"],
    },
    "Swarm Plot":{
        "Image":"sample_graphs/swarm_plot.png",
        "x-axis_data_type":["object","category"],
        "y-axis_data_type":["float","int"],
        "parameters":["x-axis","y-axis","axis title","title",
                    "legend","grid","hue","palette","size",
                    "dodge","orient","marker","alpha","linewidth"],
    },
    "Strip Plot":{
        "Image":"sample_graphs/strip_plot.png",
        "x-axis_data_type":["object","category"],
        "y-axis_data_type":["float","int"],
        "parameters":["x-axis","y-axis","axis title","title",
                    "legend","grid","hue","palette","size",
                    "jitter","dodge","orient","alpha","linewidth"],
    },
    "Histogram":{
        "Image":"sample_graphs/histogram.png",
        "x-axis_data_type":["float","int"],
        "parameters":["x-axis","y-axis","axis title","title",
                    "legend","grid","bins","binwidth","stat",
                    "kde","hue","multiple","element","palette"],
    },
    "KDE Plot":{
        "Image":"sample_graphs/kde_plot.png",
        "x-axis_data_type":["float"],
        "parameters":["x-axis","y-axis","axis title","title",
                    "legend","grid","fill","bw_adjust","cut",
                    "clip","hue","multiple","palette","alpha"],
    },
    "ECDF Plot":{
        "Image":"sample_graphs/ecdf_plot.png",
        "x-axis_data_type":["float","int"],
        "parameters":["x-axis","y-axis","axis title","title",
                    "legend","grid","hue","stat","complementary",
                    "palette","alpha","marker","linewidth","orientation"],
    },
    "Rug Plot":{
        "Image":"sample_graphs/rug_plot.png",
        "x-axis_data_type":["float","int"],
        "parameters":["x-axis","y-axis","axis title","title",
                    "legend","grid","hue","height","expand_margins",
                    "palette","alpha","linewidth","orientation","ax"],
    },
    "Heatmap":{
        "Image":"sample_graphs/heatmap.png",
        "x-axis_data_type":["float","int"],
        "y-axis_data_type":["float","int"],
        "parameters":["x-axis","y-axis","axis title","title",
                    "legend","grid","annot","fmt","cmap",
                    "center","vmin","vmax","linewidths","linecolor"]
    },
    "Pair Plot":{
        "Image":"sample_graphs/pair_plot.png",
        "x-axis_data_type":["float","int"],
        "y-axis_data_type":["float","int"],
        "parameters":["x-axis","y-axis","axis title","title",
                    "legend","grid","hue","palette","kind",
                    "diag_kind","markers","corner","plot_kws","diag_kws"]
    },
    "Joint Plot":{
        "Image":"sample_graphs/joint_plot.png",
        "x-axis_data_type":["float","int"],
        "y-axis_data_type":["float","int"],
        "parameters":["x-axis","y-axis","axis title","title",
                    "legend","grid","hue","kind","palette",
                    "height","ratio","marginal_ticks","space","joint_kws"]
    },
    "Cluster Map":{
        "Image":"sample_graphs/cluster_map.png",
        "x-axis_data_type":["object","category"],
        "y-axis_data_type":["object","category"],
        "parameters":["x-axis","y-axis","axis title","title",
                    "cmap","center","annot","linewidths","figsize",
                    "row_cluster","col_cluster","standard_scale","z_score","dendrogram_ratio"]
    },
}

class graph_parameter_table(QWidget):
    def __init__(self,main_window):
        super().__init__()

        self.main_window = main_window
        self.graph_display = self.main_window.graph_section.display_graph

        #Keep a dictionary of all the possible buttons and the features
        self.button_collections = {
            "x-axis":x_axis_button,
            "y-axis":y_axis_button,
            "axis title":axis_title_button,
            "title":title_button,
            "legend":legend_button,
            "grid":grid_button,
            "hue":hue_button,
            "style":style_button,
        }

        #Customize the parameter table
        self.setStyleSheet("""
            QWidget#ParamTable {
                border-radius: 24px;
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #f5f5ff,
                    stop:0.5 #f7f5fc,
                    stop:1 #f0f0ff
                );
            }
            QPushButton {
                background: qlineargradient(
                    x1:0, y1:0,
                    x2:1, y2:0,
                    stop:0 rgba(94, 255, 234, 1),
                    stop:0.29 rgba(63, 252, 180, 1),
                    stop:0.61 rgba(2, 247, 207, 1),
                    stop:0.89 rgba(0, 212, 255, 1)
                );
                border: 2px solid black;
                border-radius: 16px;
                font-family: "SF Pro Display";
                font-weight: 600;
                font-size: 20px;
                padding: 6px;
                color: black;
            }
            QPushButton:hover {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(255, 0, 255, 255),
                    stop:0.22 rgba(252, 86, 191, 255),
                    stop:0.46 rgba(247, 96, 96, 255),
                    stop:0.71 rgba(255, 180, 82, 255),
                    stop:0.90 rgba(245, 219, 51, 255)
                );
                border: 2px solid black;
                border-radius: 16px;
                font-family: "SF Pro Display";
                font-weight: 600;
                font-size: 20px;
                padding: 6px;
                color: black;
            }
            QPushButton:press {
                background: qlineargradient(
                    x1:0, y1:0,
                    x2:1, y2:0,
                    stop:0 rgba(94, 255, 234, 1),
                    stop:0.29 rgba(63, 252, 180, 1),
                    stop:0.61 rgba(2, 247, 207, 1),
                    stop:0.89 rgba(0, 212, 255, 1)
                );
                border: 2px solid black;
                border-radius: 16px;
                font-family: "SF Pro Display";
                font-weight: 600;
                font-size: 20px;
                padding: 6px;
                color: black;
            }
        """)
        self.setObjectName("ParamTable")
        self.layout = QGridLayout(self)
        self.layout.setContentsMargins(10, 10, 10, 10)
        self.layout.setSpacing(10)

        #Keep track of all the buttons
        self.buttons = []

        #Keep track of all the button dialogs
        self.dialogs = {}

    def update_parameter_buttons(self):

        def handle_button_function(name,function):
            if (name not in self.dialogs.keys()):
                if (name.lower() == "x-axis" or name.lower() == "y-axis"):
                    instance = function(SEABORN_PLOTS,selected_graph,self.graph_display)
                else:
                    instance = function(selected_graph,self.graph_display)
                self.dialogs[name] = instance
            
            instance = self.dialogs.get(name)
            if (isinstance(instance,QDialog)):
                instance.exec()
        
        #Get the parameters based on the selected graph and module
        self.parameters = SEABORN_PLOTS[selected_graph].get("parameters",[])

        #Remove any old buttons from the layout
        for btn in self.buttons:
            self.layout.removeWidget(btn)
            btn.deleteLater()
        self.buttons.clear()

        #Display a total of 14 buttons in 7 rows and 2 columns
        for row in range(7):
            for col in range(2):
                #Get the button name and function then connect it to the button itself
                button_name = self.parameters[row*2+col]
                button_function = self.button_collections.get(button_name,'')
                button = QPushButton(button_name)
                button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
                if (button_function):
                    button.clicked.connect(lambda checked=False, name=button_name, func=button_function: handle_button_function(name,func))

                #Add the button to the layout and keep track of the buttons added
                self.layout.addWidget(button, row, col)
                self.buttons.append(button)

        #Control how much space each button covers
        for row in range(7):
            self.layout.setRowStretch(row, 1)
        for col in range(2):
            self.layout.setColumnStretch(col, 1)

        #Make sure that the table is properly drawn on the main window
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

class select_graph_module(QPushButton):
    def __init__(self):
        super().__init__()
        
        #Customize the button
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

        #Specify the possible modules
        self.graph_module = ["Seaborn","Plotly"]
        self.graph_module_idx = -1

        #Create a label to ensure formatting
        self.label = QLabel("Select Graphing Module")
        self.label.setWordWrap(True)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setStyleSheet("""
            font-family: "SF Pro Display";
            font-weight: 600;
            border-radius: 16px;
        """) 
        self.label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

        #Make sure the height of the button is greater than the label
        self.setMinimumHeight(35)
        self.label.setMinimumHeight(25)

        #Put the label on top of the button
        layout = QVBoxLayout(self)
        layout.addWidget(self.label)
        layout.setContentsMargins(5, 0, 5, 0)  

        #Connect the button with the associated function 
        self.clicked.connect(self.change_module)

    def change_module(self):
        #Don't do anything unless there is something in the dataset
        folder_path = './dataset'
        if (os.listdir(folder_path)):
            #Increase the idx by 1 and mod 2 to ensure it's still in the list
            self.graph_module_idx += 1
            self.graph_module_idx %= 2
            #Display the name of the module selected
            self.label.setText(f"{self.graph_module[self.graph_module_idx]}")
            self.label.setStyleSheet("""
                font-family: "SF Pro Display";
                font-weight: 600;
                font-size: 18px;
                border-radius: 16px;
            """) 

            #Change the graph_module variable
            global graph_module
            graph_module = self.graph_module[self.graph_module_idx]

class select_graph_window(QDialog):
    def __init__(self,available_graphs,graph_images,graph_parameter_table):
        super().__init__()

        self.available_graphs = available_graphs
        self.graph_images = graph_images
        self.graph_parameter_table = graph_parameter_table

        #Initialize the size and title of the window
        self.setWindowTitle("Select Your Graph")
        self.setFixedHeight(600)
        self.setFixedWidth(700)

        #Customized the window
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

        #Create a label for the graph name so it formats properly
        self.graph_label = QLabel(f"{self.available_graphs[idx%len(self.available_graphs)]}")
        self.graph_label.setWordWrap(True)
        self.graph_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.graph_label.setStyleSheet("""
            background: qlineargradient(
                x1:0, y1:0,
                x2:1, y2:0,
                stop:0 rgba(220, 245, 255, 1),
                stop:0.5 rgba(205, 240, 255, 1),
                stop:1 rgba(190, 235, 255, 1)
            );
            font-family: "SF Pro Display";
            font-weight: 600;
            border-radius: 16px;
            font-size: 32px;
        """) 

        #Create a widget to put the graph name on
        self.graph_name = QWidget()
        self.graph_name.setObjectName("Graph_Name")
        self.graph_name.setStyleSheet("""
            QWidget#Graph_Name{
                background: qlineargradient(
                    x1:0, y1:0,
                    x2:1, y2:0,
                    stop:0 rgba(220, 245, 255, 1),
                    stop:0.5 rgba(205, 240, 255, 1),
                    stop:1 rgba(190, 235, 255, 1)
                );
                border: 1px solid black;
                border-radius: 24px;
                font-family: "SF Pro Display";
                font-size: 32px;
                font-weight: 600;
            }
        """)

        #Put the graph label on top of the graph name widget
        graph_name_layout = QVBoxLayout()
        graph_name_layout.addWidget(self.graph_label)
        self.graph_name.setLayout(graph_name_layout)

        #Create a widget to display the image of the sample graph
        self.graph_image = QWidget()
        self.graph_image.setObjectName("Graph_Image")
        self.graph_image.setStyleSheet("""
            QWidget#Graph_Image{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #f5f5ff,
                    stop:0.5 #f7f5fc,
                    stop:1 #f0f0ff
                );
                border: 1px solid black;
                border-radius: 24px;
            }
        """)

        #Get the image from the folder and create a Pixmap for it to display later
        self.image_label = QLabel(self.graph_image)
        image = QPixmap(f"./{self.graph_images[idx]}")
        self.image_label.setPixmap(image)
        self.image_label.setScaledContents(True)

        #Put the sample graph image on the image widget to display it
        layout = QVBoxLayout(self.graph_image)
        layout.addWidget(self.image_label)
        layout.setContentsMargins(0, 0, 0, 0) 
        self.graph_image.setLayout(layout)

        #Create a select button to allow the user to choose the graph
        self.select_button = QPushButton("Select")
        self.select_button.setObjectName("Select_Button")

        #Create a shortcut to let the user choose by pressing enter
        enter_shortcut = QShortcut(QKeySequence("Return"), self) 
        enter_shortcut.activated.connect(self.select_button.click)  

        self.select_button.setStyleSheet("""
            QPushButton#Select_Button{  
                background: qlineargradient(
                    x1:0, y1:0,
                    x2:1, y2:0,
                    stop:0 rgba(160, 255, 230, 1),
                    stop:1 rgba(110, 210, 255, 1)
                );
                border: 1px solid black;
                border-radius: 24px;
                font-family: "SF Pro Display";
                font-size: 32px;
                font-weight: 600;
            }
        """)     

        #Create a label to show ← and to ensure the formatting doesn't go wrong
        self.previous_graph_label = QLabel("←")
        self.previous_graph_label.setObjectName("Previous_Graph_Symbol")
        self.previous_graph_label.setStyleSheet("""
            QWidget#Previous_Graph_Symbol{
                background: transparent;
                border-radius: 24px;
                font-family: "SF Pro Display";
                font-size: 54px;
                font-weight: 600;
            }
        """)

        #Create a button to show the previous graph
        self.previous_graph = QPushButton()
        self.previous_graph.setObjectName("Previous_Graph")

        #Create a shortcut to let the user go to the previous graph with the left key
        left_shortcut = QShortcut(QKeySequence("Left"), self) 
        left_shortcut.activated.connect(self.previous_graph.click)

        self.previous_graph.setStyleSheet("""
            QPushButton#Previous_Graph{  
                background: qlineargradient(
                    x1:0, y1:0,
                    x2:1, y2:0,
                    stop:0 rgba(166, 255, 245, 1),
                    stop:0.5 rgba(132, 235, 255, 1),
                    stop:1 rgba(88, 200, 255, 1)
                );
                border: 1px solid black;
                border-radius: 24px;
                font-family: "SF Pro Display";
                font-size: 54px;
                font-weight: 600;
            }
        """)    

        #Put the previous symbol label on top of the previous button and center it
        previous_graph_layout = QVBoxLayout()
        previous_graph_layout.addWidget(self.previous_graph_label,alignment=Qt.AlignmentFlag.AlignCenter)
        self.previous_graph.setLayout(previous_graph_layout)

        #Create a label to show → and to ensure the formatting doesn't go wrong
        self.next_graph_label = QLabel("→")
        self.next_graph_label.setObjectName("Next_Graph_Symbol")
        self.next_graph_label.setStyleSheet("""
            QWidget#Next_Graph_Symbol{
                background: transparent;
                border-radius: 24px;
                font-family: "SF Pro Display";
                font-size: 54px;
                font-weight: 600;
            }
        """)

        #Create a button to show the next graph
        self.next_graph = QPushButton()

        #Create a shortcut to let the user go to the next graph with the right key
        right_shortcut = QShortcut(QKeySequence("Right"), self) 
        right_shortcut.activated.connect(self.next_graph.click)

        self.next_graph.setObjectName("Next_Graph")
        self.next_graph.setStyleSheet("""
            QPushButton#Next_Graph{  
                background: qlineargradient(
                    x1:0, y1:0,
                    x2:1, y2:0,
                    stop:0 rgba(166, 255, 245, 1),
                    stop:0.5 rgba(132, 235, 255, 1),
                    stop:1 rgba(88, 200, 255, 1)
                );
                border: 1px solid black;
                border-radius: 24px;
                font-family: "SF Pro Display";
                font-size: 54px;
                font-weight: 600;
            }
        """)    

        #Put the next symbol label on top of the next button and center it
        next_graph_layout = QVBoxLayout()
        next_graph_layout.addWidget(self.next_graph_label,alignment=Qt.AlignmentFlag.AlignCenter)
        self.next_graph.setLayout(next_graph_layout)

        #Control the sizes of each button and label on the window
        self.graph_name.setFixedHeight(60)
        self.graph_name.setFixedWidth(500)

        self.graph_image.setFixedHeight(450)
        self.graph_image.setFixedWidth(500)

        self.select_button.setFixedHeight(50)
        self.select_button.setFixedWidth(300)

        self.previous_graph.setFixedHeight(70)
        self.previous_graph.setFixedWidth(70)
        
        self.next_graph.setFixedHeight(70)
        self.next_graph.setFixedWidth(70)

        #Put the graph name, graph image, and select button all together vertically and center them with a vertical layout
        vertical_layout = QVBoxLayout()
        vertical_layout.addWidget(self.graph_name,alignment=Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)
        vertical_layout.addWidget(self.graph_image,alignment=Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignHCenter)
        vertical_layout.addWidget(self.select_button,alignment=Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignBottom)
        vertical_layout.setSpacing(10)

        #Using a horizontal layout put the vertical layout we just created between the previous/next buttons
        main_layout = QHBoxLayout()
        main_layout.addWidget(self.previous_graph,alignment=Qt.AlignmentFlag.AlignLeft)
        main_layout.addLayout(vertical_layout)
        main_layout.addWidget(self.next_graph,alignment=Qt.AlignmentFlag.AlignRight)

        #Control how much of the window they cover
        main_layout.setStretch(0, 1) 
        main_layout.setStretch(1, 0)  
        main_layout.setStretch(2, 1)  

        #Control the margins so that it will look better
        main_layout.setContentsMargins(10,10,10,10)

        #Apply the final layout on to the select graph window
        self.setLayout(main_layout)

        #Connect each button with it's associated function
        self.previous_graph.clicked.connect(self.view_previous_graph)
        self.next_graph.clicked.connect(self.view_next_graph)
        self.select_button.clicked.connect(self.select_graph)

    def view_previous_graph(self):
        #Decrease the index by one and replace the graph name and image with the new graph
        global idx
        idx -= 1
        idx %= len(self.available_graphs)
        self.graph_label.setText(self.available_graphs[idx])
        self.update_graph_image()

    def view_next_graph(self):
        #Decrease the index by one and replace the graph name and image with the new graph
        global idx
        idx += 1
        idx %= len(self.available_graphs)
        self.graph_label.setText(self.available_graphs[idx])
        self.update_graph_image()

    def select_graph(self):
        #Update the selected graph variable, display the associated parameter buttons, and close the window.
        global selected_graph
        selected_graph = self.available_graphs[idx]
        self.graph_parameter_table.update_parameter_buttons()
        self.close() 

    def update_graph_image(self):
        #Changes the current image with the new iamge
        image_path = self.graph_images[idx]
        pixmap = QPixmap(image_path)
        if pixmap.isNull():
            print(f"Failed to load image: {image_path}")
        self.image_label.setPixmap(pixmap)

class select_graph(QPushButton):
    def __init__(self,graph_parameter_table):
        super().__init__()
        #Customize the select graph button to make it look good
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

        self.graph_parameter_table = graph_parameter_table
    
        #Create a seperate label for the text to ensure the format is correct
        self.label = QLabel("Select Type of Graph")
        self.label.setWordWrap(True)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setStyleSheet("""
            font-family: "SF Pro Display";
            font-weight: 600;
            border-radius: 16px;
        """) 
        self.label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

        #Set the height of the button and the label
        #The label must be shorter than the button for it to fit
        self.setMinimumHeight(35)
        self.label.setMinimumHeight(25)

        #Put the label onto the button with a vertical layout and center it.
        layout = QVBoxLayout(self)
        layout.addWidget(self.label)
        layout.setContentsMargins(5, 0, 5, 0)

        #Connect the select graph function to the button
        self.clicked.connect(self.open_select_graph_window)

    def open_select_graph_window(self):
        #Only proceed when the user has already selected a graphing module.
        if (graph_module != ''):
            #Grab the graph images from the dictionary
            graph_images = [i["Image"] for i in list(SEABORN_PLOTS.values())]

            #Open a select graph window for the user to choose what graph they wanna plot
            select_graph_window(list(SEABORN_PLOTS.keys()),graph_images,self.graph_parameter_table).exec()
            #Check if the user selected a graph yet, if yes then replace the label with the graph
            if (selected_graph != ''):
                self.label.setText(selected_graph)
                self.label.setStyleSheet("""
                    font-family: "SF Pro Display";
                    font-weight: 600;
                    font-size: 18px;
                    border-radius: 16px;
                """) 

class GraphParameter_TopBar(QWidget):
    def __init__(self,graph_parameter_table):
        super().__init__()

        #Create a horizontal layout to store all the buttons in
        #Add some spacing and margins to make it look better
        layout = QHBoxLayout()
        layout.addWidget(select_graph_module())
        layout.addWidget(select_graph(graph_parameter_table))
        layout.setContentsMargins(5,5,5,5) 
        layout.setSpacing(5)

        #Give the topbar a name to control what is changed when styling
        self.setObjectName("graph_parameter_topbar")

        #Give the topbar a lighter white and a nice border
        #Control what the buttons look like all at once
        self.setStyleSheet("""
            QWidget#graph_parameter_topbar{
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

        #Control the size of the top bar, make sure it doesn't mess with the other stuff.
        self.setFixedHeight(50)
        self.setFixedWidth(350)

        #Apply the layout to the topbar
        self.setLayout(layout)

        #Make sure that the topbar is properly drawn on the main window
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

class GraphParameter_Table(QWidget):
    def __init__(self,graph_parameters):
        super().__init__()
        #Set the background and border to be a lighter color
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

        #Control the size of the sections
        self.setFixedWidth(350)

        self.graph_parameters = graph_parameters
        
        #Put them in a vertical layout then apply it.
        layout = QVBoxLayout()
        layout.addWidget(self.graph_parameters)
        layout.setContentsMargins(0,0,0,0) 
        layout.setSpacing(5)
        self.setLayout(layout)

        #Makes sure that the widget is properly drawn on the main window
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

class GraphParameter_Section(QWidget):
    def __init__(self,main_window):
        super().__init__()

        self.main_window = main_window

        #Create an instance of the graph_parameters, graph_parameters_topbar, and graph_parameters_table 
        self.graph_parameters = graph_parameter_table(self.main_window)
        self.graph_parameters_topbar = GraphParameter_TopBar(self.graph_parameters)
        self.graph_parameters_table = GraphParameter_Table(self.graph_parameters)

        #Put them in a vertical layout and add a spacing of 5 between them.
        layout = QVBoxLayout(self) 
        layout.addWidget(self.graph_parameters_topbar)
        layout.addSpacing(5)
        layout.addWidget(self.graph_parameters_table)
        layout.setContentsMargins(0,0,0,0) 

        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
