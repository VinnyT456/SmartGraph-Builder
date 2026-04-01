import os
from PyQt6.QtCore import QEasingCurve, QPoint, QPropertyAnimation, Qt
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import (
    QDialog, QGraphicsOpacityEffect, QGridLayout, QHBoxLayout, QLabel, QPushButton, QSizePolicy, QStackedWidget, QWidget, QVBoxLayout
)
from matplotlib.backend_bases import button_press_handler
from sections import graph
from sections.buttons import *


graph_module = ''
selected_graph = ''

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
    "Relational Plot": {
        "Image": "sample_graphs/relational_plot.png",
        "x-axis_data_type": ["float", "int"],
        "y-axis_data_type": ["float", "int"],
        "parameters": [
            "x-axis", "y-axis", "axis title", "title",
            "legend", "grid", "hue", "style", "size",
            "palette", "alpha", "marker", "kind", "col"
        ]
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
            "size":size_button,
            "palette":palette_button,
            "alpha":alpha_button,
            "marker":marker_button,
            "s":s_button,
            "edgecolor":edgecolor_button
        }

        #Set the object name for the widget
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
                button.setObjectName(button_name)
                button.setFixedSize(160,45)

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
        
        self.setObjectName("select_graph_module")
        self.setProperty("class","topbar_button")

        #Specify the possible modules
        self.graph_module = ["Seaborn","Plotly"]
        self.graph_module_idx = -1

        #Create a label to ensure formatting
        self.label = QLabel("Select Graphing Module")
        self.label.setProperty("class","topbar_button_label")
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
    def __init__(self,available_graphs,graph_parameter_table,select_graph_button):
        super().__init__()

        self.available_graphs = available_graphs
        self.graph_parameter_table = graph_parameter_table
        self.select_graph_button = select_graph_button

        #List for representing the dots (pages)
        self.dots = []

        #List for representing the graph button labels
        self.button_labels = []

        #Dot Index representing the current page for the graphs
        self.dot_idx = 0

        #Initialize the size and title of the window
        self.setWindowTitle("Select Your Graph")
        self.setFixedHeight(650)
        self.setFixedWidth(650)

        #Set the object name for the window 
        self.setObjectName("select_graph_window")

        #Create a dictionary to store the images for the sample graphs
        self.get_graph_images()

        #Create a containers for the widgets that sits on top of the QDialog Window
        self.container_widget = QWidget(self)
        self.container_widget.setObjectName("container_widget")
        self.container_widget.setStyleSheet("""
            QWidget#container_widget{
                background-color: transparent;
                border: none;
            }
        """)
        container_widget_layout = QVBoxLayout(self.container_widget)

        self.select_graph_section = QWidget()
        self.select_graph_section.setObjectName("select_graph_section")
        self.select_graph_section.setStyleSheet("""
            QWidget#select_graph_section{
                border-radius: 16px;
            }
        """)
        self.create_select_graph_widget()

        self.graph_pages_section = self.create_pages_section()

        self.graph_image_section = QWidget()
        self.graph_image_section.setProperty("class","graph_window_widget")

        self.graph_image = QLabel()
        self.graph_image.setPixmap(self.sample_graphs["SCATTER PLOT"])
        self.graph_image.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.graph_image.setScaledContents(True)

        self.opacity_effect = QGraphicsOpacityEffect()
        self.graph_image.setGraphicsEffect(self.opacity_effect)
        self.opacity_effect.setOpacity(1)
    
        graph_image_section_layout = QVBoxLayout(self.graph_image_section)
        graph_image_section_layout.addWidget(self.graph_image)
        graph_image_section_layout.setContentsMargins(10,10,10,10)

        container_widget_layout.addWidget(self.select_graph_section)
        container_widget_layout.addSpacing(2)
        container_widget_layout.addWidget(self.graph_pages_section,alignment=Qt.AlignmentFlag.AlignCenter)
        container_widget_layout.addSpacing(10)
        container_widget_layout.addWidget(self.graph_image_section)
        container_widget_layout.setContentsMargins(20,15,20,20)
        container_widget_layout.setSpacing(0)

        main_layout = QVBoxLayout(self)
        main_layout.addWidget(self.container_widget)
        main_layout.setContentsMargins(0,0,0,0)

    def create_select_graph_widget(self):
        select_graph_section_layout = QHBoxLayout(self.select_graph_section)

        self.select_graph_widget = QWidget()
        self.select_graph_widget.setProperty("class","graph_window_widget")
        self.select_graph_widget.setMinimumHeight(55)
        self.add_graph_buttons()

        self.previous_graph_button = self.create_switch_graph_button(direction="left")
        self.next_graph_button = self.create_switch_graph_button(direction="right")

        self.previous_graph_button.clicked.connect(lambda: self.change_graphs_shown(-1))
        self.next_graph_button.clicked.connect(lambda: self.change_graphs_shown(1))

        select_graph_section_layout.addWidget(self.previous_graph_button)
        select_graph_section_layout.addWidget(self.select_graph_widget)
        select_graph_section_layout.addWidget(self.next_graph_button)
        select_graph_section_layout.setContentsMargins(0,0,0,0)
        select_graph_section_layout.setSpacing(10)

    def create_switch_graph_button(self,direction):
        switch_graph_label = QLabel("<" if direction == "left" else ">")
        switch_graph_label.setProperty("class","graph_label")
        switch_graph_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        switch_graph_label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

        switch_graph_button = QPushButton()
        switch_graph_button.setProperty("class","graph_button")
        switch_graph_button.setFixedSize(55,55)

        switch_graph_button_layout = QVBoxLayout(switch_graph_button)
        switch_graph_button_layout.addWidget(switch_graph_label)
        switch_graph_button_layout.setContentsMargins(0,0,0,0)
        switch_graph_button_layout.setSpacing(0)

        return switch_graph_button

    def create_pages_section(self):
        graph_pages_section = QWidget()
        graph_pages_section.setProperty("class","graph_window_widget")
        graph_pages_section.setFixedHeight(32)

        graph_pages_section_layout = QHBoxLayout(graph_pages_section)
        graph_pages_section_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        graph_pages_section_layout.setContentsMargins(5, 5, 5, 5)
        graph_pages_section_layout.setSpacing(5)

        for i in range(int(len(self.available_graphs) / 3)):
            dot = QLabel("●" if i == 0 else "○")
            dot.setStyleSheet("color: black;")
            dot.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.dots.append(dot)
            graph_pages_section_layout.addWidget(dot)

        return graph_pages_section

    def add_graph_buttons(self):
        graph_button_pages = QStackedWidget(self.select_graph_widget)

        self.select_graph_widget_layout = QVBoxLayout(self.select_graph_widget)
        self.select_graph_widget_layout.addWidget(graph_button_pages)
        self.select_graph_widget_layout.setContentsMargins(0,0,0,0)
        self.select_graph_widget_layout.setSpacing(0)

        def create_page():
            page = QWidget()
            page.setObjectName("page")
            page.setStyleSheet("""
                QWidget#page{
                    background: transparent;
                    border: none;
                }
            """)
            layout = QHBoxLayout(page)
            layout.setContentsMargins(10,0,10,0)
            layout.setSpacing(10)
            return page, layout

        page, page_layout = create_page()

        for i in range(len(self.available_graphs)):
            if (i % 3 == 0 and i != 0):
                graph_button_pages.addWidget(page)

                page, page_layout = create_page()

            graph_label = QLabel(self.available_graphs[i])
            graph_label.setProperty("class","graph_label")
            graph_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            graph_label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
            graph_label.setStyleSheet("font-size: 16pt;")

            graph_button = QPushButton()
            graph_button.setProperty("class","graph_button")
            graph_button.setFixedHeight(35)
            graph_button.clicked.connect(lambda checked, b=graph_button: self.update_graph_image(b))

            graph_button_layout = QVBoxLayout(graph_button)
            graph_button_layout.addWidget(graph_label,alignment=Qt.AlignmentFlag.AlignCenter)
            graph_button_layout.setContentsMargins(0,0,0,0)
            graph_button_layout.setSpacing(0)

            page_layout.addWidget(graph_button,alignment=Qt.AlignmentFlag.AlignVCenter)

            self.button_labels.append(graph_label)

        graph_button_pages.addWidget(page)

    def get_graph_images(self):
        self.sample_graphs = dict()
        for img in os.listdir("./sample_graphs"):
            image = QPixmap(f"./sample_graphs/{img}")

            img_name = img.replace("_"," ")
            img_name = img_name.upper()
            img_name = img_name[:-4]

            self.sample_graphs[img_name] = image

    def change_graphs_shown(self,direction): 
        self.dot_idx = (self.dot_idx + direction) % len(self.dots)
        self.update_dots()
        self.update_buttons()

    def select_graph(self):
        #Update the selected graph variable, display the associated parameter buttons, and close the window.
        global selected_graph
        selected_graph = self.available_graphs[idx]
        self.select_graph_button.label.setText(selected_graph)
        self.select_graph_button.label.setStyleSheet("""
            font-family: "SF Pro Display";
            font-weight: 600;
            font-size: 18px;
            border-radius: 16px;
        """)
        self.graph_parameter_table.update_parameter_buttons()
        self.close() 

    def update_buttons(self):
        start = self.dot_idx * 3
        end = start + 3

        for graph_name, button_label in zip(self.available_graphs[start:end],self.button_labels):
            button_label.setText(graph_name)

    def update_dots(self):
        for idx, dot in enumerate(self.dots):
            dot.setText("●" if idx == self.dot_idx else "○")
    
    def update_graph_image(self,button):
        graph_label = button.findChild(QLabel)
        new_graph = self.sample_graphs[graph_label.text().upper()] 

        self.fade_out = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.fade_out.setDuration(300)  # ms
        self.fade_out.setStartValue(1)
        self.fade_out.setEndValue(0)

        self.fade_out.setEasingCurve(QEasingCurve.Type.InOutQuad)

        # When fade out finishes → change image → fade in
        def on_fade_out_finished():
            self.graph_image.setPixmap(new_graph)

            self.fade_in = QPropertyAnimation(self.opacity_effect, b"opacity")
            self.fade_in.setDuration(300)
            self.fade_in.setStartValue(0)
            self.fade_in.setEndValue(1)

            self.fade_in.setEasingCurve(QEasingCurve.Type.InOutQuad)

            self.fade_in.start()

        self.fade_out.finished.connect(on_fade_out_finished)
        self.fade_out.start()

    def showEvent(self, event):
        super().showEvent(event)

        # Fade animation
        self.fade_anim = QPropertyAnimation(self, b"windowOpacity")
        self.fade_anim.setDuration(200)
        self.fade_anim.setStartValue(0)
        self.fade_anim.setEndValue(1)
        self.fade_anim.setEasingCurve(QEasingCurve.Type.InOutQuad)

        # Slight scale effect (resize)
        start_rect = self.geometry()
        self.setGeometry(
            start_rect.adjusted(20, 20, -20, -20)  # slightly smaller
        )

        self.scale_anim = QPropertyAnimation(self, b"geometry")  # noqa: F405
        self.scale_anim.setDuration(200)
        self.scale_anim.setStartValue(self.geometry())
        self.scale_anim.setEndValue(start_rect)
        self.scale_anim.setEasingCurve(QEasingCurve.Type.OutBack)

        # Start animations
        self.fade_anim.start()
        self.scale_anim.start()
        
class select_graph(QPushButton):
    def __init__(self,graph_parameter_table):
        super().__init__()

        self.graph_parameter_table = graph_parameter_table

        self.setObjectName("select_graph")
        self.setProperty("class","topbar_button")
    
        #Create a seperate label for the text to ensure the format is correct
        self.label = QLabel("Select Type of Graph")
        self.label.setProperty("class","topbar_button_label")
        self.label.setWordWrap(True)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
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
            #Open a select graph window for the user to choose what graph they wanna plot
            self.graph_window = select_graph_window(
                list(SEABORN_PLOTS.keys()),
                self.graph_parameter_table,
                self
            )
            self.graph_window.setModal(True)   
            self.graph_window.show() 

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

        #Give the topbar a name and property
        self.setObjectName("graph_parameter_topbar")
        self.setProperty("class","topbar")

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

        self.setObjectName("GraphParameter_Table")
        self.setProperty("class","adjustment_section")

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