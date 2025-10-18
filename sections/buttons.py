from PyQt6.QtCore import QLine, Qt
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
        "axis title":["",""],
        "title":None,
        "legend":"auto",
        "grid":True,
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

        self.plot_parameters = plot_parameters
        self.selected_graph = selected_graph

        self.plot_manager = PlotManager()
        
        #Set the title of the window
        self.setWindowTitle("Select the x-axis")

        #Read the csv file or data points from the dataset folder
        self.dataset = pd.read_csv("./dataset/user_dataset.csv")

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

        #Generate the usable columns in the dataset
        self.usable_columns = self.find_usable_columns()
        #Create the buttons
        self.create_buttons()
        #Display the column in that dataset
        self.display_dataset()
        #Highlight the selected column in the buttons
        self.highlighted_selected_column()

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
        #Make sure that there is no old buttons in the layout
        for btn in self.buttons:
            self.layout.removeWidget(btn)
            btn.deleteLater()
        self.buttons.clear()

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
        """)

    #Close the window and record the selected column
    def select_x_axis_column(self):
        current_version = self.plot_manager.current_version
        plot_json[self.selected_graph]["x-axis"] = self.column_name
        plot_json[self.selected_graph]['version'] = current_version
        self.plot_manager.insert_x_axis_data(plot_json[self.selected_graph])
        self.close()

class y_axis_button(QDialog):
    def __init__(self,plot_parameters,selected_graph):
        super().__init__()

        self.plot_parameters = plot_parameters
        self.selected_graph = selected_graph

        self.plot_manager = PlotManager()
        
        #Set the title of the window
        self.setWindowTitle("Select the y-axis")

        #Read the csv file or data points from the dataset folder 
        self.dataset = pd.read_csv("./dataset/user_dataset.csv")

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

        #Generate the usable columns in the dataset
        self.usable_columns = self.find_usable_columns()
        #Create the buttons
        self.create_buttons()
        #Display the column in that dataset
        self.display_dataset()
        #Highlight the selected column in the buttons
        self.highlighted_selected_column()

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

        #Make sure that there is no old buttons in the layout
        for btn in self.buttons:
            self.layout.removeWidget(btn)
            btn.deleteLater()
        self.buttons.clear()

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
        """)

    #Close the window and record the selected column
    def select_y_axis_column(self):
        current_version = self.plot_manager.current_version
        plot_json[self.selected_graph]["y-axis"] = self.column_name
        plot_json[self.selected_graph]['version'] = current_version
        self.plot_manager.insert_y_axis_data(plot_json[self.selected_graph])
        self.close()

class axis_title_button(QDialog):
    def __init__(self):
        super().__init__()

        self.plot_manager = PlotManager()

        self.setWindowTitle("Enter the x/y axis titles")
        self.setFixedHeight(150)
        self.setFixedWidth(500)

        self.x_axis_input = False
        self.y_axis_input = False

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
        if (db["axis title"][0] == "" and db["axis title"][1] == "" and not self.x_axis_input):
            db["axis title"][0] = x_axis_title
            self.x_axis_input = True
            self.plot_manager.insert_plot_parameter(db)
        else:
            self.plot_manager.update_x_axis_title(x_axis_title)
        

    def y_axis_update_text(self):
        y_axis_title = self.y_axis_title_section.text().strip()
        db = self.plot_manager.get_db()
        if (db["axis title"][0] == "" and db["axis title"][1] == "" and not self.y_axis_input):
            db["axis title"][1] = y_axis_title
            self.y_axis_input = True
            self.plot_manager.insert_plot_parameter(db)
        else:
            self.plot_manager.update_y_axis_title(y_axis_title)

    def close_application(self):
        self.close()

class title_button(QDialog):
    def __init__(self):
        super().__init__()

        self.plot_manager = PlotManager()

        self.setWindowTitle("Enter the Title for the graph")
        self.setFixedHeight(80)
        self.setFixedWidth(500)

        self.title_input = False

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
        if (db["title"] == None and not self.title_input):
            db["title"] = title
            self.title_input = True
            self.plot_manager.insert_plot_parameter(db)
        else:
            self.plot_manager.update_title(title)

    def close_application(self):
        self.close()

class legend_button(QPushButton):
    def __init__(self):
        super().__init__()

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

class grid_button(QPushButton):
    def __init__(self):
        super().__init__()

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
