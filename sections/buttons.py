from PyQt6.QtCore import Qt
from PyQt6.QtGui import QKeySequence, QPixmap, QShortcut
from PyQt6.QtWidgets import (
    QDialog, QGridLayout, QHBoxLayout, QHeaderView, QLabel, QLineEdit, QPushButton, QScrollArea, QSizePolicy, QTableView, QWidget, QVBoxLayout
)
from sections.dataset import PrepareDataset
from sections.plot_manager import PlotManager
import pandas as pd
import os

plot_json = {
    "Scatter Plot":{
        "version":1,
        "type":"Scatter Plot",
        "data":"./user_dataset.csv",
        "x-axis":None,
        "y-axis":None,
        "axis title":{
            "x-axis":"",
            "y-axis":"",
        },
        "title":None,
        "legend":{
            "loc":"best",
            "bbox_to_anchor":None,
            "ncol":1,
            "fontsize":None,
            "title":None,
            "title_fontsize":None,
            "frameon":True,
            "facecolor":None,
            "edgecolor":None,
            "framealpha":None,
            "shadow":False,
            "fancybox":True,
            "borderpad":0.4,
            "labelcolor":"none",
            "alignment":"center",
            "columnspacing":2.0,
            "handletextpad":0.8,
            "borderaxespad":0.5,
            "handlelength":2.0,
            "handleheight":0.7,
            "markerfirst":True,
        },
        "grid":False,
        "hue":None,
        "style":None,
        "size":None,
        "palette":None,
        "alpha":1.0,
        "marker":"o",
        "s":36,
        "edgecolor":"w"
    }
}

if os.path.exists("plot_config.json"):
    os.remove("plot_config.json")

class x_axis_button(QDialog):
    def __init__(self,plot_parameters,selected_graph):
        super().__init__()

        self.plot_manager = PlotManager()

        self.plot_parameters = plot_parameters
        self.selected_graph = selected_graph
        
        #Set the title of the window
        self.setWindowTitle("Select the x-axis")

        #Keep track of the current column and index
        self.column_name = ''
        self.idx = 0
    
        #Store all the buttons in a list for highlighting the selected one
        self.buttons = []
        
        #Style the Dialog window for selecting the x-axis
        self.setStyleSheet("""
            QDialog{
               background: qlineargradient(
                    x1: 0, y1: 1, 
                    x2: 0, y2: 0,
                    stop: 0 rgba(25, 191, 188, 1),
                    stop: 0.28 rgba(27, 154, 166, 1),
                    stop: 0.65 rgba(78, 160, 242, 1),
                    stop: 0.89 rgba(33, 218, 255, 1)
                );
            }
        """)

        #Control the size of the dialog window
        self.setFixedWidth(600)
        self.setFixedHeight(500)

        #Create a section to store all the buttons and style it
        self.button_section = QWidget()
        self.button_section.setObjectName("button_section")
        self.button_section.setStyleSheet("""
            QWidget#button_section{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #f5f5ff,
                    stop:0.5 #f7f5fc,
                    stop:1 #f0f0ff
                );
                border: 2px solid black;
                border-radius: 24px;
            }
        """)

        #Create a section to display the dataset and style it
        self.data_section = QWidget()
        self.data_section.setObjectName("data_section")
        self.data_section.setStyleSheet("""
            QWidget#data_section{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #f5f5ff,
                    stop:0.5 #f7f5fc,
                    stop:1 #f0f0ff
                );
                border: 2px solid black;
                border-radius: 24px;
            }
        """)

        #Create a QTableView instance to display the dataset
        self.dataset_table = QTableView()
        self.dataset_table.setObjectName("dataset_table")
        header = self.dataset_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.dataset_table.setStyleSheet("""
            QTableView#dataset_table {
                border-radius: 24px;
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #f5f5ff,
                    stop:0.5 #f7f5fc,
                    stop:1 #f0f0ff
                );
                font-family: "SF Pro Display";
                font-size: 11pt;
                color: black;
                margin: 5px;
                padding: 10px;           
            }
            QHeaderView::section {
                background-color: white;
                color: black;
                font-size: 16pt;
                font-family: "SF Pro Display";
                font-weight: bold;
                border-radius: 24px;
                border: 2px solid black;
            }
        """)

        #Create a scrollable area to allow the user to scroll through the buttons
        self.scroll_section = QScrollArea()
        self.scroll_section.setFrameShape(QScrollArea.Shape.NoFrame)
        self.scroll_section.setWidgetResizable(True)

        #Place the scrollable area on the button section
        self.scroll_section.setWidget(self.button_section)
        self.scroll_section.setStyleSheet("""
            QScrollArea{
                background: transparent;
                border: none;
                border-radius: 24px;
            }
        """)
        #Hide the handle
        self.scroll_section.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        #Place the dataset table on top of the dataset section
        layout = QVBoxLayout(self.data_section)
        layout.addWidget(self.dataset_table)
        layout.setContentsMargins(0,0,0,0)
        layout.setSpacing(0)

        #Allow the dataset to take up all the space
        self.dataset_table.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        #Place the buttons and the dataset next to each other side by side
        self.layout = QHBoxLayout(self)
        self.layout.addWidget(self.scroll_section,stretch=1)
        self.layout.addSpacing(10)
        self.layout.addWidget(self.data_section,stretch=1)

        #Create a shortcut for the user to go to the previous column by press up
        up_shortcut = QShortcut(QKeySequence("up"), self) 
        up_shortcut.activated.connect(self.columns_go_up)  

        #Create a shortcut for the user to go to the next column by press down
        down_shortcut = QShortcut(QKeySequence("down"), self) 
        down_shortcut.activated.connect(self.columns_go_down)

        #Create a shortcut for the user to select the column by pressing enter/return
        enter_shortcut = QShortcut(QKeySequence("Return"), self) 
        enter_shortcut.activated.connect(self.select_x_axis_column) 

        #Make sure this gets drawn.
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

    def find_usable_columns(self):
        #Get the needed data type from the dictionary
        x_axis_data_type = self.plot_parameters[self.selected_graph].get("x-axis_data_type")
        if (x_axis_data_type):
            #Return the columns in the dataset that match the data type and set the column name with the first column
            columns = self.dataset.select_dtypes(include=x_axis_data_type).columns
            if (not columns.empty):
                self.column_name = columns[0]
                return columns.tolist()
        return []

    def create_buttons(self):  
        if (self.usable_columns == []):
            return

        def remove_layout(widget):
            layout = widget.layout()
            if layout is not None:
                while layout.count():
                    item = layout.takeAt(0)
                    child = item.widget()
                    if child is not None:
                        child.setParent(None)
                QWidget().setLayout(layout)
        
        #Make sure that there is no old buttons in the layout
        for btn in self.buttons:
            self.layout.removeWidget(btn)
            btn.deleteLater()
        self.buttons.clear()
        remove_layout(self.button_section)

        #Create a vertical box to put the buttons in. Make sure they are positioned vertically.
        button_layout = QVBoxLayout(self.button_section)

        #Go through each column in the list and create a button for each of them
        for column in self.usable_columns:

            #Make a copy of the current column name
            column_name = str(column)

            #Create the button with the column name, give it an object name, and give it a fixedHeight for consistency
            column_button = QPushButton(column_name)
            column_button.setObjectName("not_selected")
            column_button.setFixedHeight(45)

            #Connect each button to the change column feature to ensure that dataset being displayed changes with the button
            column_button.clicked.connect(lambda checked=False, col=column_name: self.change_column(col))

            #Add the button to the list and the layout
            self.buttons.append(column_button)
            button_layout.addWidget(column_button)

        #Add margins and spacing to make it look and push all the buttons to the top
        button_layout.setContentsMargins(10,10,10,10)
        button_layout.setSpacing(5) 
        button_layout.addStretch()

    def get_dataset(self):
        self.dataset = pd.read_csv("./dataset/user_dataset.csv")

    def display_dataset(self):
        if (self.usable_columns == []):
            return
        self.model = PrepareDataset(self.dataset[[self.column_name]])
        self.dataset_table.setModel(self.model)
        self.dataset_table.verticalHeader().setVisible(False)
        self.dataset_table.setShowGrid(True)
        self.dataset_table.setSortingEnabled(False)

    def change_column(self,column):
        if (self.usable_columns == []):
            return
        #Keep track of the old idx and change both the column name and new idx
        old_idx = self.idx
        self.column_name = column
        self.idx = self.usable_columns.index(self.column_name)

        if (old_idx != self.idx):
            #Change the current column that's being displayed and highlight the selected button
            self.display_dataset()
            self.highlighted_selected_column(old_idx)

    def columns_go_down(self):
        if (self.usable_columns == []):
            return
        #Keep track of the old idx and change both the column name and idx
        #Change the column display and the button selected
        old_idx = self.idx
        self.idx += 1
        self.idx %= len(self.usable_columns)
        self.highlighted_selected_column(old_idx)
        self.column_name = self.usable_columns[self.idx]
        self.display_dataset()

        vertical_scroll_bar = self.scroll_section.verticalScrollBar()
        if (old_idx == len(self.usable_columns)-1 and self.idx == 0):
            vertical_scroll_bar.setValue(0)
        elif (self.idx == len(self.usable_columns)-1):
            vertical_scroll_bar.setValue(vertical_scroll_bar.maximum())
        elif (self.idx > 8 and self.idx < len(self.usable_columns)):
            scroll_value = min(vertical_scroll_bar.maximum(), vertical_scroll_bar.value() + 50)
            vertical_scroll_bar.setValue(scroll_value)

    def columns_go_up(self):
        if (self.usable_columns == []):
            return
        #Keep track of the old idx and change both the column name and idx
        #Change the column display and the button selected
        old_idx = self.idx
        self.idx -= 1
        self.idx %= len(self.usable_columns)
        self.highlighted_selected_column(old_idx)
        self.column_name = self.usable_columns[self.idx]
        self.display_dataset()

        vertical_scroll_bar = self.scroll_section.verticalScrollBar()
        if (old_idx == 0 and self.idx == len(self.usable_columns)-1):
            max_scroll_value = vertical_scroll_bar.maximum()
            vertical_scroll_bar.setValue(max_scroll_value)
        elif (self.idx == 0):
            vertical_scroll_bar.setValue(0)
        elif (self.idx < len(self.usable_columns) - 9):
            scroll_value = max(0, vertical_scroll_bar.value() - 50)
            vertical_scroll_bar.setValue(scroll_value)

    def highlighted_selected_column(self,old_idx=-1):
        if (self.usable_columns == []):
            return
        #Set the current button selected to be called selected
        self.buttons[self.idx].setObjectName("selected")
        #If there is a old_idx then change the old button to be not selected
        if (old_idx != -1):
            self.buttons[old_idx].setObjectName("not_selected")

        #Customize the dialog window and each button selected and not selected
        self.setStyleSheet("""
            QDialog{
                background: qlineargradient(
                    x1: 0, y1: 1, 
                    x2: 0, y2: 0,
                    stop: 0 rgba(25, 191, 188, 1),
                    stop: 0.28 rgba(27, 154, 166, 1),
                    stop: 0.65 rgba(78, 160, 242, 1),
                    stop: 0.89 rgba(33, 218, 255, 1)
                );
            }
            QPushButton#selected{
                background: qlineargradient(
                    x1:0, y1:0,
                    x2:1, y2:0,
                    stop:0 rgba(94, 255, 234, 1),
                    stop:0.5 rgba(171, 156, 255, 1),
                    stop:1 rgba(255, 203, 255, 1)
                );
                border: 2px solid black;
                border-radius: 16px;
                font-family: "SF Pro Display";
                font-weight: 600;
                font-size: 24px;
                padding: 6px;
                color: black;
            }
            QPushButton#not_selected{
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
                font-size: 24px;
                padding: 6px;
                color: black;
            }
            QPushButton#not_selected:hover{
                background: qlineargradient(
                    x1:0, y1:0,
                    x2:1, y2:0,
                    stop:0 rgba(94, 255, 234, 1),
                    stop:0.5 rgba(171, 156, 255, 1),
                    stop:1 rgba(255, 203, 255, 1)
                );
                border: 2px solid black;
                border-radius: 16px;
                font-family: "SF Pro Display";
                font-weight: 600;
                font-size: 24px;
                padding: 6px;
                color: black;
            }
        """)

    #Close the window and record the selected column
    def select_x_axis_column(self):
        db = self.plot_manager.get_db()
        if (db != []):
            plot_parameters = db.copy()
            plot_parameters["x-axis"] = self.column_name
        else:
            plot_parameters = plot_json[self.selected_graph].copy()
            plot_parameters["x-axis"] = self.column_name
        self.plot_manager.insert_x_axis_data(plot_parameters)
        self.close()

    def showEvent(self, event):
        super().showEvent(event)
        self.get_dataset()
        #Generate the usable columns in the dataset
        self.usable_columns = self.find_usable_columns()
        #Create the buttons
        self.create_buttons()
        #Display the column in that dataset
        self.display_dataset()
        #Highlight the selected column in the buttons
        self.highlighted_selected_column()

class y_axis_button(QDialog):
    def __init__(self,plot_parameters,selected_graph):
        super().__init__()

        self.plot_parameters = plot_parameters
        self.selected_graph = selected_graph

        self.plot_manager = PlotManager()
        
        #Set the title of the window
        self.setWindowTitle("Select the y-axis")

        #Keep track of the current column and index
        self.column_name = ''
        self.idx = 0

        #Store all the buttons in a list for highlighting the selected one
        self.buttons = []
        
        #Style the Dialog window for selecting the y-axis
        self.setStyleSheet("""
            QDialog{
               background: qlineargradient(
                    x1: 0, y1: 1, 
                    x2: 0, y2: 0,
                    stop: 0 rgba(25, 191, 188, 1),
                    stop: 0.28 rgba(27, 154, 166, 1),
                    stop: 0.65 rgba(78, 160, 242, 1),
                    stop: 0.89 rgba(33, 218, 255, 1)
                );
            }
        """)

        #Control the size of the dialog window
        self.setFixedWidth(600)
        self.setFixedHeight(500)

        #Create a section to store all the buttons and style it
        self.button_section = QWidget()
        self.button_section.setObjectName("button_section")
        self.button_section.setStyleSheet("""
            QWidget#button_section{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #f5f5ff,
                    stop:0.5 #f7f5fc,
                    stop:1 #f0f0ff
                );
                border: 2px solid black;
                border-radius: 24px;
            }
        """)

        #Create a section to display the dataset and style it
        self.data_section = QWidget()
        self.data_section.setObjectName("data_section")
        self.data_section.setStyleSheet("""
            QWidget#data_section{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #f5f5ff,
                    stop:0.5 #f7f5fc,
                    stop:1 #f0f0ff
                );
                border: 2px solid black;
                border-radius: 24px;
            }
        """)

        #Create a QTableView instance to display the dataset
        self.dataset_table = QTableView()
        self.dataset_table.setObjectName("dataset_table")
        header = self.dataset_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.dataset_table.setStyleSheet("""
            QTableView#dataset_table {
                border-radius: 24px;
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #f5f5ff,
                    stop:0.5 #f7f5fc,
                    stop:1 #f0f0ff
                );
                font-family: "SF Pro Display";
                font-size: 11pt;
                color: black;
                margin: 5px;
                padding: 10px;           
            }
            QHeaderView::section {
                background-color: white;
                color: black;
                font-size: 16pt;
                font-family: "SF Pro Display";
                font-weight: bold;
                border-radius: 24px;
                border: 2px solid black;
            }
        """)

        #Create a scrollable area to allow the user to scroll through the buttons
        self.scroll_section = QScrollArea()
        self.scroll_section.setFrameShape(QScrollArea.Shape.NoFrame)
        self.scroll_section.setWidgetResizable(True)

        #Place the scrollable area on the button section
        self.scroll_section.setWidget(self.button_section)
        self.scroll_section.setStyleSheet("""
            QScrollArea{
                background: transparent;
                border: none;
                border-radius: 24px;
            }
        """)
        #Hide the handle
        self.scroll_section.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        #Place the dataset table on top of the dataset section
        layout = QVBoxLayout(self.data_section)
        layout.addWidget(self.dataset_table)
        layout.setContentsMargins(0,0,0,0)
        layout.setSpacing(0)

        #Allow the dataset to take up all the space
        self.dataset_table.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        #Place the buttons and the dataset next to each other side by side
        self.layout = QHBoxLayout(self)
        self.layout.addWidget(self.scroll_section,stretch=1)
        self.layout.addSpacing(10)
        self.layout.addWidget(self.data_section,stretch=1)

        #Create a shortcut for the user to go to the previous column by press up
        up_shortcut = QShortcut(QKeySequence("up"), self) 
        up_shortcut.activated.connect(self.columns_go_up)  

        #Create a shortcut for the user to go to the next column by press down
        down_shortcut = QShortcut(QKeySequence("down"), self) 
        down_shortcut.activated.connect(self.columns_go_down)

        #Create a shortcut for the user to select the column by pressing enter/return
        enter_shortcut = QShortcut(QKeySequence("Return"), self) 
        enter_shortcut.activated.connect(self.select_y_axis_column) 

        #Make sure this gets drawn.
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)


    def find_usable_columns(self):
        #Get the needed data type from the dictionary
        y_axis_data_type = self.plot_parameters[self.selected_graph].get("y-axis_data_type")
        if (y_axis_data_type):
            #Return the columns in the dataset that match the data type and set the column name with the first column
            columns = self.dataset.select_dtypes(include=y_axis_data_type).columns
            if (not columns.empty):
                self.column_name = columns[0]
                return columns.tolist()
        return []

    def create_buttons(self):  
        if (self.usable_columns == []):
            return

        def remove_layout(widget):
            layout = widget.layout()
            if layout is not None:
                while layout.count():
                    item = layout.takeAt(0)
                    child = item.widget()
                    if child is not None:
                        child.setParent(None)
                QWidget().setLayout(layout)

        #Make sure that there is no old buttons in the layout
        for btn in self.buttons:
            self.layout.removeWidget(btn)
            btn.deleteLater()
        self.buttons.clear()
        remove_layout(self.button_section)

        #Create a vertical box to put the buttons in. Make sure they are positioned vertically.
        button_layout = QVBoxLayout(self.button_section)
        #Go through each column in the list and create a button for each of them
        for column in self.usable_columns:

            #Make a copy of the current column name
            column_name = str(column)

            #Create the button with the column name, give it an object name, and give it a fixedHeight for consistency
            column_button = QPushButton(column_name)
            column_button.setObjectName("not_selected")
            column_button.setFixedHeight(45)

            #Connect each button to the change column feature to ensure that dataset being displayed changes with the button
            column_button.clicked.connect(lambda checked=False, col=column_name: self.change_column(col))

            #Add the button to the list and the layout
            self.buttons.append(column_button)
            button_layout.addWidget(column_button)

        #Add margins and spacing to make it look and push all the buttons to the top
        button_layout.setContentsMargins(10,10,10,10)
        button_layout.setSpacing(5) 
        button_layout.addStretch()

    def get_dataset(self):
        self.dataset = pd.read_csv("./dataset/user_dataset.csv")

    #Display the dataset and make it look decent
    def display_dataset(self):
        if (self.usable_columns == []):
            return
        self.model = PrepareDataset(self.dataset[[self.column_name]])
        self.dataset_table.setModel(self.model)
        self.dataset_table.verticalHeader().setVisible(False)
        self.dataset_table.setShowGrid(True)
        self.dataset_table.setSortingEnabled(False)

    def change_column(self,column):
        if (self.usable_columns == []):
            return
        #Keep track of the old idx and change both the column name and new idx
        old_idx = self.idx
        self.column_name = column
        self.idx = self.usable_columns.index(self.column_name)

        #Change the current column that's being displayed and highlight the selected button
        self.display_dataset()
        self.highlighted_selected_column(old_idx)

    def columns_go_down(self):
        if (self.usable_columns == []):
            return
        #Keep track of the old idx and change both the column name and idx
        #Change the column display and the button selected
        old_idx = self.idx
        self.idx += 1
        self.idx %= len(self.usable_columns)
        self.highlighted_selected_column(old_idx)
        self.column_name = self.usable_columns[self.idx]
        self.display_dataset()

        vertical_scroll_bar = self.scroll_section.verticalScrollBar()
        if (old_idx == len(self.usable_columns)-1 and self.idx == 0):
            vertical_scroll_bar.setValue(0)
        if self.idx > 8 and self.idx < len(self.usable_columns):
            scroll_value = min(vertical_scroll_bar.maximum(), vertical_scroll_bar.value() + 50)
            vertical_scroll_bar.setValue(scroll_value)

    def columns_go_up(self):
        if (self.usable_columns == []):
            return
        #Keep track of the old idx and change both the column name and idx
        #Change the column display and the button selected
        old_idx = self.idx
        self.idx -= 1
        self.idx %= len(self.usable_columns)
        self.highlighted_selected_column(old_idx)
        self.column_name = self.usable_columns[self.idx]
        self.display_dataset()

        vertical_scroll_bar = self.scroll_section.verticalScrollBar()
        if (old_idx == 0 and self.idx == len(self.usable_columns)-1):
            max_scroll_value = vertical_scroll_bar.maximum()
            vertical_scroll_bar.setValue(max_scroll_value)
        elif self.idx < len(self.usable_columns) - 9:
            scroll_value = max(0, vertical_scroll_bar.value() - 50)
            vertical_scroll_bar.setValue(scroll_value)

    def highlighted_selected_column(self,old_idx=-1):
        if (self.usable_columns == []):
            return
        #Set the current button selected to be called selected
        self.buttons[self.idx].setObjectName("selected")
        #If there is a old_idx then change the old button to be not selected
        if (old_idx != -1):
            self.buttons[old_idx].setObjectName("not_selected")

        #Customize the dialog window and each button selected and not selected
        self.setStyleSheet("""
            QDialog{
                background: qlineargradient(
                    x1: 0, y1: 1, 
                    x2: 0, y2: 0,
                    stop: 0 rgba(25, 191, 188, 1),
                    stop: 0.28 rgba(27, 154, 166, 1),
                    stop: 0.65 rgba(78, 160, 242, 1),
                    stop: 0.89 rgba(33, 218, 255, 1)
                );
            }
            QPushButton#selected{
                background: qlineargradient(
                    x1:0, y1:0,
                    x2:1, y2:0,
                    stop:0 rgba(94, 255, 234, 1),
                    stop:0.5 rgba(171, 156, 255, 1),
                    stop:1 rgba(255, 203, 255, 1)
                );
                border: 2px solid black;
                border-radius: 16px;
                font-family: "SF Pro Display";
                font-weight: 600;
                font-size: 24px;
                padding: 6px;
                color: black;
            }
            QPushButton#not_selected{
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
                font-size: 24px;
                padding: 6px;
                color: black;
            }
            QPushButton#not_selected:hover{
                background: qlineargradient(
                    x1:0, y1:0,
                    x2:1, y2:0,
                    stop:0 rgba(94, 255, 234, 1),
                    stop:0.5 rgba(171, 156, 255, 1),
                    stop:1 rgba(255, 203, 255, 1)
                );
                border: 2px solid black;
                border-radius: 16px;
                font-family: "SF Pro Display";
                font-weight: 600;
                font-size: 24px;
                padding: 6px;
                color: black;
            }
        """)

    #Close the window and record the selected column
    def select_y_axis_column(self):
        db = self.plot_manager.get_db()
        if (db != []):
            plot_parameters = db.copy()
            plot_parameters["y-axis"] = self.column_name
        else:
            plot_parameters = plot_json[self.selected_graph].copy()
            plot_parameters["y-axis"] = self.column_name
        self.plot_manager.insert_y_axis_data(plot_parameters)
        self.close()

    def showEvent(self, event):
        super().showEvent(event)
        self.get_dataset()
        #Generate the usable columns in the dataset
        self.usable_columns = self.find_usable_columns()
        #Create the buttons
        self.create_buttons()
        #Display the column in that dataset
        self.display_dataset()
        #Highlight the selected column in the buttons
        self.highlighted_selected_column()

class axis_title_button(QDialog):
    def __init__(self,selected_graph):
        super().__init__()

        self.plot_manager = PlotManager()
        self.selected_graph = selected_graph
        self.axis_title_created = False

        self.setWindowTitle("Enter the x/y axis titles")
        self.setFixedHeight(150)
        self.setFixedWidth(500)

        self.setStyleSheet("""
            QDialog{
               background: qlineargradient(
                    x1:0, y1:1,
                    x2:0, y2:0,
                    stop:0.02 rgba(131, 125, 255, 1),
                    stop:0.36 rgba(97, 97, 255, 1),
                    stop:0.66 rgba(31, 162, 255, 1),
                    stop:1 rgba(0, 212, 255, 1)
                );
            }
        """)

        self.x_axis_title_section = QLineEdit()
        self.x_axis_title_section.setPlaceholderText("X-Axis Title")
        self.x_axis_title_section.setObjectName("x_axis_title")
        self.x_axis_title_section.setStyleSheet("""
            QLineEdit#x_axis_title{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #f5f5ff,
                    stop:0.5 #f7f5fc,
                    stop:1 #f0f0ff
                );
                color: black;
                font-size: 24pt;
                border: 2px solid black;
                border-radius: 24px;
            }
        """)

        self.y_axis_title_section = QLineEdit() 
        self.y_axis_title_section.setPlaceholderText("Y-Axis Title")
        self.y_axis_title_section.setObjectName("y_axis_title")
        self.y_axis_title_section.setStyleSheet("""
            QLineEdit#y_axis_title{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #f5f5ff,
                    stop:0.5 #f7f5fc,
                    stop:1 #f0f0ff
                );
                color: black;
                font-size: 24pt;
                border: 2px solid black;
                border-radius: 24px;
            }
        """)

        self.x_axis_title_section.setFixedHeight(60)
        self.y_axis_title_section.setFixedHeight(60)

        self.x_axis_title_section.textChanged.connect(self.x_axis_update_text)
        self.y_axis_title_section.textChanged.connect(self.y_axis_update_text)

        layout = QVBoxLayout(self)
        layout.addWidget(self.x_axis_title_section)
        layout.addWidget(self.y_axis_title_section)
        layout.setContentsMargins(10,10,10,10)
        layout.setSpacing(10)

        close_shortcut = QShortcut(QKeySequence("Return"), self) 
        close_shortcut.activated.connect(self.close_application)

    def x_axis_update_text(self):
        x_axis_title = self.x_axis_title_section.text().strip()

        db = self.plot_manager.get_db()
        if (db != []):
            if ((db["axis title"]["x-axis"] == "" and db["axis title"]["y-axis"] == "") or not self.axis_title_created):
                db["axis title"]["x-axis"] = x_axis_title
                self.axis_title_created = True
                self.plot_manager.insert_plot_parameter(db)
            else:
                self.plot_manager.update_x_axis_title(x_axis_title)
        else:
            plot_parameter = plot_json[self.selected_graph].copy()
            plot_parameter["axis title"]["x-axis"] = x_axis_title
            self.axis_title_created = not self.axis_title_created
            self.plot_manager.insert_plot_parameter(plot_parameter)
        

    def y_axis_update_text(self):
        y_axis_title = self.y_axis_title_section.text().strip()
        db = self.plot_manager.get_db()
        if (db != []):
            if ((db["axis title"]["x-axis"] == "" and db["axis title"]["y-axis"] == "") or not self.axis_title_created):
                db["axis title"]["y-axis"] = y_axis_title
                self.plot_manager.insert_plot_parameter(db)
                self.axis_title_created = True
            else:
                self.plot_manager.update_y_axis_title(y_axis_title)
        else:
            plot_parameter = plot_json[self.selected_graph].copy()
            plot_parameter["axis title"]["y-axis"] = y_axis_title
            self.plot_manager.insert_plot_parameter(plot_parameter)
            self.axis_title_created = True

    def close_application(self):
        self.axis_title_created = False
        self.close()

class title_button(QDialog):
    def __init__(self,selected_graph):
        super().__init__()

        self.plot_manager = PlotManager()
        self.selected_graph = selected_graph
        self.title_created = False

        self.setWindowTitle("Enter the Title for the graph")
        self.setFixedHeight(80)
        self.setFixedWidth(500)

        self.setStyleSheet("""
            QDialog{
               background: qlineargradient(
                    x1:0, y1:1,
                    x2:0, y2:0,
                    stop:0.02 rgba(131, 125, 255, 1),
                    stop:0.36 rgba(97, 97, 255, 1),
                    stop:0.66 rgba(31, 162, 255, 1),
                    stop:1 rgba(0, 212, 255, 1)
                );
            }
        """)

        self.title_section = QLineEdit()
        self.title_section.setPlaceholderText("Title")
        self.title_section.setObjectName("title_section")
        self.title_section.setStyleSheet("""
            QLineEdit#title_section{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #f5f5ff,
                    stop:0.5 #f7f5fc,
                    stop:1 #f0f0ff
                );
                color: black;
                font-size: 24pt;
                border: 2px solid black;
                border-radius: 24px;
            }
        """)

        self.title_section.setFixedHeight(60)

        self.title_section.textChanged.connect(self.update_title)

        layout = QVBoxLayout(self)
        layout.addWidget(self.title_section)
        layout.setContentsMargins(10,10,10,10)
        layout.setSpacing(10)

        close_shortcut = QShortcut(QKeySequence("Return"), self) 
        close_shortcut.activated.connect(self.close_application)

    def update_title(self):
        title = self.title_section.text().strip()
        db = self.plot_manager.get_db()
        if (db != []):
            if (db["title"] == None or not self.title_created):
                db["title"] = title
                self.plot_manager.insert_plot_parameter(db)
                self.title_created = True
            else:
                self.plot_manager.update_title(title)
        else:
            plot_parameters = plot_json[self.selected_graph].copy()
            plot_parameters["title"] = title
            self.plot_manager.insert_plot_parameter(plot_parameters)
            self.title_created = True

    def close_application(self):
        self.title_created = False
        self.close()

class loc_adjustment_section(QWidget):
    def __init__(self,selected_graph):
        super().__init__()

        self.plot_manager = PlotManager()

        self.selected_graph = selected_graph

        #Create a section to display the loc section and style it
        self.loc_adjustment_section = QWidget()
        self.loc_adjustment_section.setObjectName("adjust_loc_section")
        self.loc_adjustment_section.setStyleSheet("""
            QWidget#adjust_loc_section{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #f5f5ff,
                    stop:0.5 #f7f5fc,
                    stop:1 #f0f0ff
                );
                border: 2px solid black;
                border-radius: 24px;
            }
        """)

        self.loc_buttons = []
        self.available_loc_arguments = ["best","upper right","upper left","lower left",
                                    "lower right","right","center left","center right",
                                    "lower center","upper center","center"]
        self.loc_idx = 0
        self.loc_argument_name = self.available_loc_arguments[0]
        self.scroll_section = QScrollArea()
        self.scroll_section.setFrameShape(QScrollArea.Shape.NoFrame)
        self.scroll_section.setWidgetResizable(True)

        self.loc_parameter_section()
        self.highlighted_selected_column()

        #Place the scrollable area on the button section
        self.scroll_section.setWidget(self.loc_adjustment_section)
        self.scroll_section.setStyleSheet("""
            QScrollArea{
                background: transparent;
                border: none;
                border-radius: 24px;
            }
        """)
        #Hide the handle
        self.scroll_section.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        main_layout = QVBoxLayout(self)
        main_layout.addWidget(self.scroll_section)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0,0,0,0)

        #Create a shortcut for the user to go to the previous column by press up
        up_shortcut = QShortcut(QKeySequence("left"), self) 
        up_shortcut.activated.connect(self.move_selected_button_up)  

        down_shortcut = QShortcut(QKeySequence("right"),self)
        down_shortcut.activated.connect(self.move_selected_button_down)

        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

    def loc_parameter_section(self):
        #Make sure that there is no old buttons in the layout
        for btn in self.loc_buttons:
            self.layout.removeWidget(btn)
            btn.deleteLater()
        self.loc_buttons.clear()
        self.remove_layout()

        #Create a vertical box to put the buttons in. Make sure they are positioned vertically.
        button_layout = QVBoxLayout(self.loc_adjustment_section)
        #Go through each arugment in the list and create a button for each of them
        for argument in self.available_loc_arguments:

            #Make a copy of the current arugment name
            arugment_name = str(argument)

            #Create the button with the column name, give it an object name, and give it a fixedHeight for consistency
            argument_button = QPushButton(arugment_name)
            argument_button.setObjectName("not_selected")
            argument_button.setFixedHeight(45)

            #Connect each button to the change arugment feature to ensure that dataset being displayed changes with the button
            argument_button.clicked.connect(lambda checked=False, argument=arugment_name: self.change_argument(argument))

            #Add the button to the list and the layout
            self.loc_buttons.append(argument_button)
            button_layout.addWidget(argument_button)

        #Add margins and spacing to make it look and push all the buttons to the top
        button_layout.setContentsMargins(10,10,10,10)
        button_layout.setSpacing(5) 
        button_layout.addStretch()
        
    def change_argument(self, argument_name):
        #Keep track of the old idx and change both the argument name and new idx
        old_idx = self.loc_idx
        self.loc_argument_name = argument_name
        self.loc_idx = self.available_loc_arguments.index(self.loc_argument_name)

        #Change the current arugment that's being displayed and highlights the selected button
        self.highlighted_selected_column(old_idx)

    def move_selected_button_up(self):
        #Keep track of the old idx and change both the column name and idx
        #Change the column display and the button selected
        old_idx = self.loc_idx
        self.loc_idx -= 1

        self.loc_idx %= len(self.available_loc_arguments)
        self.highlighted_selected_column(old_idx)
        self.loc_argument_name = self.available_loc_arguments[self.loc_idx]

        vertical_scroll_bar = self.scroll_section.verticalScrollBar()
        if (old_idx == 0 and self.loc_idx == len(self.available_loc_arguments)-1):
            max_scroll_value = vertical_scroll_bar.maximum()
            vertical_scroll_bar.setValue(max_scroll_value)
        elif (self.loc_idx == 0):
            vertical_scroll_bar.setValue(0)
        elif self.loc_idx < len(self.available_loc_arguments) - 9:
            scroll_value = max(0, vertical_scroll_bar.value() - 50)
            vertical_scroll_bar.setValue(scroll_value)

        self.update_parameter_argument()

    def move_selected_button_down(self):
        old_idx = self.loc_idx
        self.loc_idx += 1
        self.loc_idx %= len(self.available_loc_arguments)
        self.highlighted_selected_column(old_idx)
        self.loc_adjustment_name = self.available_loc_arguments[self.loc_idx]

        vertical_scroll_bar = self.scroll_section.verticalScrollBar()
        if (old_idx == len(self.available_loc_arguments)-1 and self.loc_idx == 0):
            vertical_scroll_bar.setValue(0)
        elif (self.loc_idx == len(self.available_loc_arguments)-1):
            vertical_scroll_bar.setValue(vertical_scroll_bar.maximum())
        elif self.loc_idx > 8 and self.loc_idx < len(self.available_loc_arguments):
            scroll_value = min(vertical_scroll_bar.maximum(), vertical_scroll_bar.value() + 50)
            vertical_scroll_bar.setValue(scroll_value)

        self.update_parameter_argument()

    def remove_layout(self):    
        layout = self.loc_adjustment_section.layout()
        if layout is not None:
            while layout.count():
                item = layout.takeAt(0)
                child = item.widget()
                if child is not None:
                    child.setParent(None)
            QWidget().setLayout(layout)

    def highlighted_selected_column(self,old_idx=-1):
        #Set the current button selected to be called selected
        self.loc_buttons[self.loc_idx].setObjectName("selected")

        #If there is a old_idx then change the old button to be not selected
        if (old_idx != -1):
            self.loc_buttons[old_idx].setObjectName("not_selected")

        #Customize the dialog window and each button selected and not selected
        self.setStyleSheet("""
            QWidget#adjust_loc_section{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #f5f5ff,
                    stop:0.5 #f7f5fc,
                    stop:1 #f0f0ff
                );
                border: 2px solid black;
                border-radius: 24px;
            }
            QPushButton#selected{
                background: qlineargradient(
                    x1:0, y1:0,
                    x2:1, y2:0,
                    stop:0 rgba(94, 255, 234, 1),
                    stop:0.5 rgba(171, 156, 255, 1),
                    stop:1 rgba(255, 203, 255, 1)
                );
                border: 2px solid black;
                border-radius: 16px;
                font-family: "SF Pro Display";
                font-weight: 600;
                font-size: 24px;
                padding: 6px;
                color: black;
            }
            QPushButton#not_selected{
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
                font-size: 24px;
                padding: 6px;
                color: black;
            }
            QPushButton#not_selected:hover{
                background: qlineargradient(
                    x1:0, y1:0,
                    x2:1, y2:0,
                    stop:0 rgba(94, 255, 234, 1),
                    stop:0.5 rgba(171, 156, 255, 1),
                    stop:1 rgba(255, 203, 255, 1)
                );
                border: 2px solid black;
                border-radius: 16px;
                font-family: "SF Pro Display";
                font-weight: 600;
                font-size: 24px;
                padding: 6px;
                color: black;
            }
        """)

    def update_parameter_argument(self):
        db = self.plot_manager.get_db()
        if (db != []):
            if (db["legend"]["loc"] != self.loc_adjustment_name):
                self.plot_manager.update_legend("loc",self.loc_adjustment_name)
        else:
            plot_parameters = plot_json[self.selected_graph].copy()
            plot_parameters["legend"]["loc"] = self.loc_adjustment_name
            self.plot_manager.insert_plot_parameter(plot_parameters)

class bbox_to_anchor_adjustment_section(QWidget):
    def __init__(self,selected_graph):
        super().__init__()
        
        self.plot_manager = PlotManager()
        
        self.selected_graph = selected_graph

        #Create a section to display the loc section and style it
        self.bbox_adjustment_section = QWidget()
        self.bbox_adjustment_section.setObjectName("adjust_bbox_section")
        self.bbox_adjustment_section.setStyleSheet("""
            QWidget#adjust_bbox_section{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #f5f5ff,
                    stop:0.5 #f7f5fc,
                    stop:1 #f0f0ff
                );
                border: 2px solid black;
                border-radius: 24px;
            }
            QLineEdit{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #f5f5ff,
                    stop:0.5 #f7f5fc,
                    stop:1 #f0f0ff
                );
                color: black;
                font-size: 24pt;
                border: 2px solid black;
                border-radius: 24px;
            }
        """)

        self.x_value = 0
        self.y_value = 0
        self.width_value = 0
        self.height_value = 0

        self.x_input = QLineEdit()
        self.x_input.setPlaceholderText("X: ")
        self.y_input = QLineEdit()
        self.y_input.setPlaceholderText("Y: ")
        self.width_input = QLineEdit()
        self.width_input.setPlaceholderText("Width: ")
        self.height_input = QLineEdit()
        self.height_input.setPlaceholderText("Height: ")

        self.x_input.setFixedHeight(60)
        self.y_input.setFixedHeight(60)
        self.width_input.setFixedHeight(60)
        self.height_input.setFixedHeight(60)

        self.x_input.textChanged.connect(self.update_x)
        self.y_input.textChanged.connect(self.update_y)
        self.width_input.textChanged.connect(self.update_width)
        self.height_input.textChanged.connect(self.update_height)

        bbox_section_layout = QVBoxLayout(self.bbox_adjustment_section)

        bbox_section_layout.addWidget(self.x_input)
        bbox_section_layout.addWidget(self.y_input)
        bbox_section_layout.addWidget(self.width_input)
        bbox_section_layout.addWidget(self.height_input)

        bbox_section_layout.setContentsMargins(10,10,10,5)
        bbox_section_layout.setSpacing(10)
        bbox_section_layout.addStretch()

        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

        main_layout = QVBoxLayout(self)
        main_layout.addWidget(self.bbox_adjustment_section)
        
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0,0,0,0)
    
    def update_x(self):
        x_input = self.x_input.text().strip()
        try:
            self.x_value = float(x_input)
        except:
            pass
        else:
            self.update_bbox_anchor()
        

    def update_y(self):
        y_input = self.y_input.text().strip()
        try:
            self.y_value = float(y_input)
        except:
            pass
        else:
            self.update_bbox_anchor()

    def update_width(self):
        width_input = self.width_input.text().strip()
        try:
            self.width_value = float(width_input)
        except:
            pass
        else:
            self.update_bbox_anchor()

    def update_height(self):
        height_input = self.height_input.text().strip()
        try:
            self.height_value = float(height_input)
        except:
            pass
        else:
            self.update_bbox_anchor()

    def update_bbox_anchor(self):
        db = self.plot_manager.get_db()
        if (db != []):
            new_bbox_anchor = [self.x_value,self.y_value,self.width_value,self.height_value]
            self.plot_manager.update_legend("bbox_to_anchor",new_bbox_anchor)
        else:
            plot_parameters = plot_json[self.selected_graph].copy()
            plot_parameters["legend"]["bbox_to_anchor"] = (0,0,0,0)
            self.plot_manager.insert_plot_parameter(plot_parameters)

class ncol_adjustment_section(QWidget):
    def __init__(self,selected_graph):
        super().__init__()
        
        self.plot_manager = PlotManager()
        
        self.selected_graph = selected_graph

        #Create a section to display the loc section and style it
        self.ncol_adjustment_section = QWidget()
        self.ncol_adjustment_section.setObjectName("adjust_ncol_section")
        self.ncol_adjustment_section.setStyleSheet("""
            QWidget#adjust_ncol_section{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #f5f5ff,
                    stop:0.5 #f7f5fc,
                    stop:1 #f0f0ff
                );
                border: 2px solid black;
                border-radius: 24px;
            }
            QLineEdit{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #f5f5ff,
                    stop:0.5 #f7f5fc,
                    stop:1 #f0f0ff
                );
                color: black;
                font-size: 24pt;
                border: 2px solid black;
                border-radius: 24px;
            }
        """)

        self.ncol_value = 0

        self.ncol_input = QLineEdit()
        self.ncol_input.setPlaceholderText("ncol: ")

        self.ncol_input.setFixedHeight(60)

        self.ncol_input.textChanged.connect(self.update_ncol)

        ncol_section_layout = QVBoxLayout(self.ncol_adjustment_section)
        ncol_section_layout.addWidget(self.ncol_input)

        ncol_section_layout.setContentsMargins(10,10,10,5)
        ncol_section_layout.setSpacing(10)
        ncol_section_layout.addStretch()

        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

        main_layout = QVBoxLayout(self)
        main_layout.addWidget(self.ncol_adjustment_section)
        
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0,0,0,0)
    
    def update_ncol(self):
        ncol_input = self.ncol_input.text().strip()
        try:
            self.ncol_value = int(ncol_input)
        except:
            pass
        else:
            self.update_json()

    def update_json(self):
        db = self.plot_manager.get_db()
        if (db != []):
            self.plot_manager.update_legend("ncol",self.ncol_value)
        else:
            plot_parameters = plot_json[self.selected_graph].copy()
            plot_parameters["legend"]["ncol"] = self.ncol_value
            self.plot_manager.insert_plot_parameter(plot_parameters)

class fontsize_adjustment_section(QWidget):
    def __init__(self,selected_graph):
        super().__init__()
        
        self.plot_manager = PlotManager()

        self.selected_graph = selected_graph
        
        self.custom_fontsize = 0
        self.fixed_fontsizes = ["xx-small", "x-small", "small", "medium", "large", "x-large", "xx-large"]
        self.current_fontsize = None

        self.current_page = 0
        self.font_idx = 0

        self.fontsize_buttons = []

        self.fontsize_adjustment_section = QWidget()
        self.fontsize_adjustment_section.setObjectName("adjust_fontsize_section")
        self.fontsize_adjustment_section.setStyleSheet("""
            QWidget#adjust_fontsize_section{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #f5f5ff,
                    stop:0.5 #f7f5fc,
                    stop:1 #f0f0ff
                );
                border: 2px solid black;
                border-radius: 24px;
            }
        """)

        self.custom_fontsize_button = QPushButton("Custom Fontsize")
        self.custom_fontsize_button.setObjectName("custom_fontsize")
        self.custom_fontsize_button.setStyleSheet("""
            QPushButton#custom_fontsize{
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
                font-size: 24px;
                padding: 6px;
                color: black;
            }
            QPushButton#custom_fontsize:hover{
                background: qlineargradient(
                    x1:0, y1:0,
                    x2:1, y2:0,
                    stop:0 rgba(94, 255, 234, 1),
                    stop:0.5 rgba(171, 156, 255, 1),
                    stop:1 rgba(255, 203, 255, 1)
                );
                border: 2px solid black;
                border-radius: 16px;
                font-family: "SF Pro Display";
                font-weight: 600;
                font-size: 24px;
                padding: 6px;
                color: black;
            }
        """)

        self.fixed_fontsize_button = QPushButton("Fixed Fontsize")
        self.fixed_fontsize_button.setObjectName("fixed_fontsize")
        self.fixed_fontsize_button.setStyleSheet("""
            QPushButton#fixed_fontsize{
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
                font-size: 24px;
                padding: 6px;
                color: black;
            }
            QPushButton#fixed_fontsize:hover{
                background: qlineargradient(
                    x1:0, y1:0,
                    x2:1, y2:0,
                    stop:0 rgba(94, 255, 234, 1),
                    stop:0.5 rgba(171, 156, 255, 1),
                    stop:1 rgba(255, 203, 255, 1)
                );
                border: 2px solid black;
                border-radius: 16px;
                font-family: "SF Pro Display";
                font-weight: 600;
                font-size: 24px;
                padding: 6px;
                color: black;
            }
        """)

        self.custom_fontsize_button.clicked.connect(self.change_to_custom_fontsize)
        self.fixed_fontsize_button.clicked.connect(self.change_to_fixed_fontsize)

        button_layout = QVBoxLayout(self.fontsize_adjustment_section)
        button_layout.addWidget(self.custom_fontsize_button)
        button_layout.addWidget(self.fixed_fontsize_button)
        button_layout.setContentsMargins(10,10,10,10)
        button_layout.setSpacing(5)
        button_layout.addStretch()

        main_layout = QVBoxLayout(self)
        main_layout.addWidget(self.fontsize_adjustment_section)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0,0,0,0)

        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

        go_back_shortcut = QShortcut(QKeySequence("left"), self) 
        go_back_shortcut.activated.connect(self.change_to_original_screen)

        go_to_previous_screen_shortcut = QShortcut(QKeySequence("right"), self) 
        go_to_previous_screen_shortcut.activated.connect(self.change_to_old_page)

    def clear_layout(self):
        layout = self.fontsize_adjustment_section.layout()
        if layout:
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget:
                    widget.setParent(None)

    def change_to_original_screen(self):
        self.clear_layout()

        button_layout = self.fontsize_adjustment_section.layout()

        button_layout.addWidget(self.custom_fontsize_button)
        button_layout.addWidget(self.fixed_fontsize_button)
        button_layout.setContentsMargins(10,10,10,10)
        button_layout.setSpacing(5)
        button_layout.addStretch()

        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

    def change_to_old_page(self):
        if (self.current_page != 0):
            self.clear_layout()
            if (self.current_page == 1):
                self.change_to_custom_fontsize()
            elif (self.current_page == 2):
                self.change_to_fixed_fontsize()

    def change_to_custom_fontsize(self):
        self.clear_layout()

        self.current_page = 1

        self.custom_fontsize_input = QLineEdit()
        self.custom_fontsize_input.setPlaceholderText("Fontsize:")
        self.custom_fontsize_input.setObjectName("custom_fontsize_input")
        self.custom_fontsize_input.setStyleSheet("""
            QLineEdit#custom_fontsize_input{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #f5f5ff,
                    stop:0.5 #f7f5fc,
                    stop:1 #f0f0ff
                );
                color: black;
                font-size: 24pt;
                border: 2px solid black;
                border-radius: 24px;
            }
        """)
        self.custom_fontsize_input.setFixedHeight(60) 
        
        self.custom_fontsize_input.textChanged.connect(self.process_custom_fontsize)

        custom_fontsize_layout = self.fontsize_adjustment_section.layout()
        custom_fontsize_layout.addWidget(self.custom_fontsize_input)
        custom_fontsize_layout.setContentsMargins(5,10,5,10)
        custom_fontsize_layout.setSpacing(0)
        custom_fontsize_layout.addStretch()

    def change_to_fixed_fontsize(self):
        self.clear_layout()

        self.current_page = 2 

        #Make sure that there is no old buttons in the layout
        self.fontsize_buttons.clear()
        self.current_fontsize = self.fixed_fontsizes[self.font_idx]

        #Create a vertical box to put the buttons in. Make sure they are positioned vertically.
        button_layout = self.fontsize_adjustment_section.layout()
        #Go through each parameter in the list and create a button for each of them
        for size in self.fixed_fontsizes:

            #Make a copy of the current fontsize name
            fontsize = str(size)

            #Create the button with the fontsize name, give it an object name, and give it a fixedHeight for consistency
            fontsize_button = QPushButton(size)
            fontsize_button.setObjectName("not_selected")
            fontsize_button.setFixedHeight(45)

            #Connect each button to the change parameter feature to ensure that dataset being displayed changes with the button
            fontsize_button.clicked.connect(lambda checked=False, fontsize=fontsize: self.change_fontsize(fontsize))

            #Add the button to the list and the layout
            self.fontsize_buttons.append(fontsize_button)
            button_layout.addWidget(fontsize_button)

        #Add margins and spacing to make it look and push all the buttons to the top
        button_layout.setContentsMargins(10,10,10,10)
        button_layout.setSpacing(5) 
        button_layout.addStretch()

        self.highlighted_selected_button()

    def change_fontsize(self,fontsize):
        #Keep track of the old idx and change both the column name and new idx
        old_idx = self.font_idx
        self.current_fontsize = fontsize
        self.font_idx = self.fixed_fontsizes.index(self.current_fontsize)

        #Change the current button that's being displayed and highlight the selected button
        self.highlighted_selected_button(old_idx)

    def highlighted_selected_button(self,old_idx=-1):
        self.update_fontsize()
        #Set the current button selected to be called selected
        self.fontsize_buttons[self.font_idx].setObjectName("selected")
        #If there is a old_idx then change the old button to be not selected
        if (old_idx != -1):
            self.fontsize_buttons[old_idx].setObjectName("not_selected")

        #Customize the dialog window and each button selected and not selected
        self.setStyleSheet("""
            QWidget#adjust_fontsize_section{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #f5f5ff,
                    stop:0.5 #f7f5fc,
                    stop:1 #f0f0ff
                );
                border: 2px solid black;
                border-radius: 24px;
            }
            QPushButton#selected{
                background: qlineargradient(
                    x1:0, y1:0,
                    x2:1, y2:0,
                    stop:0 rgba(94, 255, 234, 1),
                    stop:0.5 rgba(171, 156, 255, 1),
                    stop:1 rgba(255, 203, 255, 1)
                );
                border: 2px solid black;
                border-radius: 16px;
                font-family: "SF Pro Display";
                font-weight: 600;
                font-size: 24px;
                padding: 6px;
                color: black;
            }
            QPushButton#not_selected{
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
                font-size: 24px;
                padding: 6px;
                color: black;
            }
            QPushButton#not_selected:hover{
                background: qlineargradient(
                    x1:0, y1:0,
                    x2:1, y2:0,
                    stop:0 rgba(94, 255, 234, 1),
                    stop:0.5 rgba(171, 156, 255, 1),
                    stop:1 rgba(255, 203, 255, 1)
                );
                border: 2px solid black;
                border-radius: 16px;
                font-family: "SF Pro Display";
                font-weight: 600;
                font-size: 24px;
                padding: 6px;
                color: black;
            }
        """)

    def process_custom_fontsize(self):
        self.current_fontsize = self.custom_fontsize_input.text().strip()
        try:
            self.current_fontsize = int(self.current_fontsize)
        except:
            pass
        else:
            self.update_fontsize()

    def update_fontsize(self):
        db = self.plot_manager.get_db()
        if (db != []):
            self.plot_manager.update_legend("fontsize",self.current_fontsize)
        else:
            plot_parameters = plot_json[self.selected_graph].copy()
            plot_parameters["legend"]["fontsize"] = self.current_fontsize
            self.plot_manager.insert_plot_parameter(plot_parameters)

class legend_title_adjustment_section(QWidget):
    def __init__(self,selected_graph):
        super().__init__()
        
        self.plot_manager = PlotManager()
        
        self.selected_graph = selected_graph

        #Create a section to display the loc section and style it
        self.title_adjustment_section = QWidget()
        self.title_adjustment_section.setObjectName("adjust_title_section")
        self.title_adjustment_section.setStyleSheet("""
            QWidget#adjust_title_section{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #f5f5ff,
                    stop:0.5 #f7f5fc,
                    stop:1 #f0f0ff
                );
                border: 2px solid black;
                border-radius: 24px;
            }
            QLineEdit{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #f5f5ff,
                    stop:0.5 #f7f5fc,
                    stop:1 #f0f0ff
                );
                color: black;
                font-size: 24pt;
                border: 2px solid black;
                border-radius: 24px;
            }
        """)

        self.title_value = ""

        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("title: ")

        self.title_input.setFixedHeight(60)

        self.title_input.textChanged.connect(self.update_title)

        title_section_layout = QVBoxLayout(self.title_adjustment_section)
        title_section_layout.addWidget(self.title_input)

        title_section_layout.setContentsMargins(10,10,10,5)
        title_section_layout.setSpacing(10)
        title_section_layout.addStretch()

        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

        main_layout = QVBoxLayout(self)
        main_layout.addWidget(self.title_adjustment_section)
        
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0,0,0,0)
    
    def update_title(self):
        self.title_value = self.title_input.text().strip()
        if (self.title_value == ""):
            self.title_value = None
        self.update_json()

    def update_json(self):
        db = self.plot_manager.get_db()
        if (db != []):
            self.plot_manager.update_legend("title",self.title_value)
        else:
            plot_parameters = plot_json[self.selected_graph].copy()
            plot_parameters["legend"]["title"] = self.title_value
            self.plot_manager.insert_plot_parameter(plot_parameters)

class legend_button(QDialog):
    def __init__(self,selected_graph):
        super().__init__()

        self.setWindowTitle("Customize Legend")

        self.selected_graph = selected_graph

        self.legend_parameters = list(plot_json[self.selected_graph]["legend"].keys())
        self.idx = 0

        self.parameter_name = ""

        self.setStyleSheet("""
            QDialog{
               background: qlineargradient(
                    x1: 0, y1: 1, 
                    x2: 0, y2: 0,
                    stop: 0 rgba(25, 191, 188, 1),
                    stop: 0.28 rgba(27, 154, 166, 1),
                    stop: 0.65 rgba(78, 160, 242, 1),
                    stop: 0.89 rgba(33, 218, 255, 1)
                );
            }
        """)

        self.setFixedWidth(600)
        self.setFixedHeight(500)

        self.parameters_section = QWidget()
        self.parameters_section.setObjectName("legend_parameter_section")
        self.parameters_section.setStyleSheet("""
            QWidget#legend_parameter_section{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #f5f5ff,
                    stop:0.5 #f7f5fc,
                    stop:1 #f0f0ff
                );
                border: 2px solid black;
                border-radius: 24px;
            }
        """)

        #Create a section to display the dataset and style it
        self.adjust_parameters_section = QWidget()
        self.adjust_parameters_section.setObjectName("adjust_parameters_section")
        self.adjust_parameters_section.setStyleSheet("""
            QWidget#adjust_parameters_section{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #f5f5ff,
                    stop:0.5 #f7f5fc,
                    stop:1 #f0f0ff
                );
                border: 2px solid black;
                border-radius: 24px;
            }
        """)

        #Create a scrollable area to allow the user to scroll through the buttons
        self.scroll_section = QScrollArea()
        self.scroll_section.setFrameShape(QScrollArea.Shape.NoFrame)
        self.scroll_section.setWidgetResizable(True)

        #Place the scrollable area on the button section
        self.scroll_section.setWidget(self.parameters_section)
        self.scroll_section.setStyleSheet("""
            QScrollArea{
                background: transparent;
                border: none;
                border-radius: 24px;
            }
        """)
        #Hide the handle
        self.scroll_section.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        #Store the buttons created
        self.buttons = []

        #Create the buttons
        self.create_legend_parameter_buttons()
        #Highlight the selected column in the buttons
        self.highlighted_selected_column()

        #Place the buttons and the dataset next to each other side by side
        self.layout = QHBoxLayout(self)
        self.layout.addWidget(self.scroll_section,stretch=1)
        self.layout.addSpacing(10)
        self.layout.addWidget(legend_title_adjustment_section(self.selected_graph),stretch=1)

        #Create a shortcut for the user to go to the previous column by press up
        up_shortcut = QShortcut(QKeySequence("up"), self) 
        up_shortcut.activated.connect(self.columns_go_up)  

        #Create a shortcut for the user to go to the next column by press down
        down_shortcut = QShortcut(QKeySequence("down"), self) 
        down_shortcut.activated.connect(self.columns_go_down)

        #Create a shortcut for the user to close the dialog window
        close_shortcut = QShortcut(QKeySequence("Return"), self) 
        close_shortcut.activated.connect(self.close_application)

        #Make sure this gets drawn.
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        
    def create_legend_parameter_buttons(self):

        #Make sure that there is no old buttons in the layout
        for btn in self.buttons:
            self.layout.removeWidget(btn)
            btn.deleteLater()
        self.buttons.clear()

        #Create a vertical box to put the buttons in. Make sure they are positioned vertically.
        button_layout = QVBoxLayout(self.parameters_section)
        #Go through each parameter in the list and create a button for each of them
        for parameter in self.legend_parameters:

            #Make a copy of the current parameter name
            parameter_name = str(parameter)

            #Create the button with the parameter name, give it an object name, and give it a fixedHeight for consistency
            parameter_button = QPushButton(parameter_name)
            parameter_button.setObjectName("not_selected")
            parameter_button.setFixedHeight(45)

            #Connect each button to the change parameter feature to ensure that dataset being displayed changes with the button
            parameter_button.clicked.connect(lambda checked=False, parameter=parameter_name: self.change_parameter(parameter))

            #Add the button to the list and the layout
            self.buttons.append(parameter_button)
            button_layout.addWidget(parameter_button)

        #Add margins and spacing to make it look and push all the buttons to the top
        button_layout.setContentsMargins(10,10,10,10)
        button_layout.setSpacing(5) 
        button_layout.addStretch()

    def display_current_parameter_adjustment(self):
        pass

    def change_parameter(self,parameter_name):
        #Keep track of the old idx and change both the column name and new idx
        old_idx = self.idx
        self.parameter_name = parameter_name
        self.idx = self.legend_parameters.index(self.parameter_name)

        #Change the current column that's being displayed and highlight the selected button
        self.highlighted_selected_column(old_idx)

    def columns_go_up(self):
        #Keep track of the old idx and change both the column name and idx
        #Change the column display and the button selected
        old_idx = self.idx
        self.idx -= 1
        self.idx %= len(self.legend_parameters)
        self.highlighted_selected_column(old_idx)
        self.parameter_name = self.legend_parameters[self.idx]

        vertical_scroll_bar = self.scroll_section.verticalScrollBar()
        if (old_idx == 0 and self.idx == len(self.legend_parameters)-1):
            max_scroll_value = vertical_scroll_bar.maximum()
            vertical_scroll_bar.setValue(max_scroll_value)
        elif (self.idx == 0):
            vertical_scroll_bar.setValue(0)
        elif self.idx < len(self.legend_parameters) - 9:
            scroll_value = max(0, vertical_scroll_bar.value() - 50)
            vertical_scroll_bar.setValue(scroll_value)

    def columns_go_down(self):
        old_idx = self.idx
        self.idx += 1
        self.idx %= len(self.legend_parameters)
        self.highlighted_selected_column(old_idx)
        self.parameter_name = self.legend_parameters[self.idx]

        vertical_scroll_bar = self.scroll_section.verticalScrollBar()
        if (old_idx == len(self.legend_parameters)-1 and self.idx == 0):
            vertical_scroll_bar.setValue(0)
        elif (self.idx == len(self.legend_parameters)-1):
            vertical_scroll_bar.setValue(vertical_scroll_bar.maximum())
        elif self.idx > 8 and self.idx < len(self.legend_parameters):
            scroll_value = min(vertical_scroll_bar.maximum(), vertical_scroll_bar.value() + 50)
            vertical_scroll_bar.setValue(scroll_value)

    def highlighted_selected_column(self,old_idx=-1):
        #Set the current button selected to be called selected
        self.buttons[self.idx].setObjectName("selected")
        #If there is a old_idx then change the old button to be not selected
        if (old_idx != -1):
            self.buttons[old_idx].setObjectName("not_selected")

        #Customize the dialog window and each button selected and not selected
        self.setStyleSheet("""
            QDialog{
                background: qlineargradient(
                    x1: 0, y1: 1, 
                    x2: 0, y2: 0,
                    stop: 0 rgba(25, 191, 188, 1),
                    stop: 0.28 rgba(27, 154, 166, 1),
                    stop: 0.65 rgba(78, 160, 242, 1),
                    stop: 0.89 rgba(33, 218, 255, 1)
                );
            }
            QPushButton#selected{
                background: qlineargradient(
                    x1:0, y1:0,
                    x2:1, y2:0,
                    stop:0 rgba(94, 255, 234, 1),
                    stop:0.5 rgba(171, 156, 255, 1),
                    stop:1 rgba(255, 203, 255, 1)
                );
                border: 2px solid black;
                border-radius: 16px;
                font-family: "SF Pro Display";
                font-weight: 600;
                font-size: 24px;
                padding: 6px;
                color: black;
            }
            QPushButton#not_selected{
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
                font-size: 24px;
                padding: 6px;
                color: black;
            }
            QPushButton#not_selected:hover{
                background: qlineargradient(
                    x1:0, y1:0,
                    x2:1, y2:0,
                    stop:0 rgba(94, 255, 234, 1),
                    stop:0.5 rgba(171, 156, 255, 1),
                    stop:1 rgba(255, 203, 255, 1)
                );
                border: 2px solid black;
                border-radius: 16px;
                font-family: "SF Pro Display";
                font-weight: 600;
                font-size: 24px;
                padding: 6px;
                color: black;
            }
        """)

    def close_application(self):
        self.close()

class grid_button(QPushButton):
    def __init__(self,selected_graph):
        super().__init__()
        self.plot_manager = PlotManager()
        self.initial_grid_state = True
        self.selected_graph = selected_graph
        self.update_grid()

    def update_grid(self):
        db = self.plot_manager.get_db()
        if (db != []):
            db["grid"] = not db["grid"]
            self.plot_manager.insert_plot_parameter(db)
        else:
            plot_parameter = plot_json[self.selected_graph].copy()
            plot_parameter["grid"] = self.initial_grid_state
            self.plot_manager.insert_plot_parameter(plot_parameter) 

