from PyQt6.QtCore import QSortFilterProxyModel, QStringListModel, Qt
from PyQt6.QtGui import QFont, QKeySequence, QPixmap, QShortcut
from PyQt6.QtWidgets import (
    QDialog, QHBoxLayout, QHeaderView, QLabel, QLineEdit, QListView, QPushButton, QScrollArea, 
    QSizePolicy, QTableView, QWidget, QVBoxLayout, QStyledItemDelegate
)
from sections.dataset import PrepareDataset
from sections.plot_manager import PlotManager
import matplotlib.colors as mcolors
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

        #Store the loc buttons created in a list and list out the possible positions
        self.available_loc_arguments = ["best","upper right","upper left","lower left",
                                    "lower right","right","center left","center right",
                                    "lower center","upper center","center"]

        #Use a index to control the current location of the legend
        self.loc_argument_name = self.available_loc_arguments[0]

        #Create the loc parameter section
        self.create_loc_parameter_section()

        #Add the legend loc adjustment section to the main widget to display on the other QDialog
        main_layout = QVBoxLayout(self)
        main_layout.addWidget(self.loc_adjustment_section)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0,0,0,0)

        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

    def create_loc_parameter_section(self):
        loc_parameter_layout = QVBoxLayout(self.loc_adjustment_section)

        self.loc_search_bar = QLineEdit()
        self.loc_search_bar.setObjectName("search_bar")
        self.loc_search_bar.setPlaceholderText("Search: ")
        self.loc_search_bar.setStyleSheet("""
            QLineEdit#search_bar{
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
        self.loc_search_bar.setMinimumHeight(60)
        loc_parameter_layout.addWidget(self.loc_search_bar)
        loc_parameter_layout.addSpacing(15)
    
        self.loc_list_view = QListView()
        self.loc_position_model = QStringListModel(self.available_loc_arguments)

        self.filter_proxy = QSortFilterProxyModel()
        self.filter_proxy.setSourceModel(self.loc_position_model)
        self.filter_proxy.setFilterCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive) 
        self.filter_proxy.setFilterKeyColumn(0)  

        self.loc_search_bar.textChanged.connect(self.filter_proxy.setFilterFixedString)

        self.loc_list_view.setModel(self.filter_proxy)
        self.loc_list_view.setObjectName("loc_list_view")

        class CustomDelegate(QStyledItemDelegate):
            def paint(self, painter, option, index):
                option.displayAlignment = Qt.AlignmentFlag.AlignCenter
                font = QFont("SF Pro Display", 24)
                font.setWeight(600)
                option.font = font
                super().paint(painter, option, index)
        
        self.loc_list_view.setItemDelegate(CustomDelegate())

        self.loc_list_view.setStyleSheet("""
            QListView#loc_list_view{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #f5f5ff,
                    stop:0.5 #f7f5fc,
                    stop:1 #f0f0ff
                );
                border: transparent;
                border-radius: 24px;
            }
            QListView#loc_list_view::item {
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
                color: black;
                min-height: 41px;
            }
            QListView#loc_list_view::item:selected {
                background: qlineargradient(
                    x1:0, y1:0,
                    x2:1, y2:0,
                    stop:0 rgba(94, 255, 234, 1),
                    stop:0.5 rgba(171, 156, 255, 1),
                    stop:1 rgba(255, 203, 255, 1)
                );
                border: 2px solid black;
                border-radius: 16px;
                color: black;
                min-height: 41px;
            }
            QListView#loc_list_view::item:hover {
                background: qlineargradient(
                    x1:0, y1:0,
                    x2:1, y2:0,
                    stop:0 rgba(94, 255, 234, 1),
                    stop:0.5 rgba(171, 156, 255, 1),
                    stop:1 rgba(255, 203, 255, 1)
                );
                border: 2px solid black;
                border-radius: 16px;
                color: black;
                min-height: 41px;
            }
        """)

        self.loc_list_view.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.loc_list_view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.loc_list_view.setSpacing(3)

        self.loc_list_view.clicked.connect(self.change_loc_position)

        loc_parameter_layout.addWidget(self.loc_list_view)

        # Add margins and spacing to make it look good and push content to the top
        loc_parameter_layout.setContentsMargins(10, 10, 10, 10)

    def change_loc_position(self,index):
        self.loc_argument_name = self.loc_position_model.data(index,Qt.ItemDataRole.DisplayRole)
        self.update_parameter_argument()

    def update_parameter_argument(self):
        db = self.plot_manager.get_db()
        if (db != []):
            self.plot_manager.update_legend("loc",self.loc_argument_name)
        else:
            plot_parameters = plot_json[self.selected_graph].copy()
            plot_parameters["legend"]["loc"] = self.loc_argument_name
            self.plot_manager.insert_plot_parameter(plot_parameters)

    def mousePressEvent(self, event):
        if not self.loc_search_bar.geometry().contains(event.position().toPoint()):
            self.loc_search_bar.clearFocus()
        super().mousePressEvent(event)
        
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

        #Initialize the values for the bbox anchor parameter
        self.x_value = 0
        self.y_value = 0
        self.width_value = 0
        self.height_value = 0

        #Create a line edit widget for each of the parameters
        self.x_input = QLineEdit()
        self.x_input.setPlaceholderText("X: ")

        self.y_input = QLineEdit()
        self.y_input.setPlaceholderText("Y: ")

        self.width_input = QLineEdit()
        self.width_input.setPlaceholderText("Width: ")
        
        self.height_input = QLineEdit()
        self.height_input.setPlaceholderText("Height: ")

        #Set the sizes of each line edit widget for consistency
        self.x_input.setFixedHeight(60)
        self.y_input.setFixedHeight(60)
        self.width_input.setFixedHeight(60)
        self.height_input.setFixedHeight(60)

        #Create two widget to display valid and invalid inputs
        self.valid_input_widget = QWidget()
        self.valid_input_widget.setObjectName("valid_input")
        self.valid_input_widget.setStyleSheet("""
            QWidget#valid_input{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(94, 255, 234, 1),   
                    stop:0.3 rgba(63, 252, 180, 1), 
                    stop:0.6 rgba(150, 220, 255, 1)
                    stop:1 rgba(180, 200, 255, 1)  
                );
                border: 2px solid black;
                border-radius: 16px;
            }
        """)

        self.valid_input_label = QLabel("Valid Input")
        self.valid_input_label.setWordWrap(True)
        self.valid_input_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.valid_input_label.setObjectName("valid_input_label")
        self.valid_input_label.setStyleSheet("""
            QLabel#valid_input_label{
                font-family: "SF Pro Display";
                font-weight: 600;
                font-size: 24px;
                padding: 6px;
                color: black;
                border: none;
                background: transparent;
            }
        """)

        valid_input_layout = QVBoxLayout(self.valid_input_widget)
        valid_input_layout.addWidget(self.valid_input_label)
        valid_input_layout.setSpacing(0)
        valid_input_layout.setContentsMargins(0,0,0,0)

        self.invalid_input_widget = QWidget()
        self.invalid_input_widget.setObjectName("invalid_input")
        self.invalid_input_widget.setStyleSheet("""
            QWidget#invalid_input{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(255, 100, 100, 1),   
                    stop:0.4 rgba(255, 130, 120, 1), 
                    stop:0.7 rgba(200, 90, 150, 1), 
                    stop:1 rgba(180, 60, 140, 1)     
                );
                border: 2px solid black;
                border-radius: 16px;
            }
        """)

        self.invalid_input_label = QLabel("Invalid Input")
        self.invalid_input_label.setWordWrap(True)
        self.invalid_input_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.invalid_input_label.setObjectName("invalid_input_label")
        self.invalid_input_label.setStyleSheet("""
            QLabel#invalid_input_label{
                font-family: "SF Pro Display";
                font-weight: 600;
                font-size: 24px;
                padding: 6px;
                color: black;
                border: none;
                background: transparent;
            }
        """)

        invalid_input_layout = QVBoxLayout(self.invalid_input_widget)
        invalid_input_layout.addWidget(self.invalid_input_label)
        invalid_input_layout.setSpacing(0)
        invalid_input_layout.setContentsMargins(0,0,0,0)

        self.valid_input_widget.setMaximumHeight(50)
        self.invalid_input_widget.setMaximumHeight(50)

        self.valid_input_widget.hide()
        self.invalid_input_widget.hide()

        #Connect each line edit to update whenever the user inputs something
        self.x_input.textChanged.connect(self.update_x)
        self.y_input.textChanged.connect(self.update_y)
        self.width_input.textChanged.connect(self.update_width)
        self.height_input.textChanged.connect(self.update_height)

        #Create a layout on the bbox adjustment section
        bbox_section_layout = QVBoxLayout(self.bbox_adjustment_section)

        #Add the 4 line edit widgets to the layout and the 2 valid/invalid widgets
        bbox_section_layout.addWidget(self.x_input)
        bbox_section_layout.addWidget(self.y_input)
        bbox_section_layout.addWidget(self.width_input)
        bbox_section_layout.addWidget(self.height_input)
        bbox_section_layout.addWidget(self.valid_input_widget)
        bbox_section_layout.addWidget(self.invalid_input_widget)

        #Add margins, spacing, and stretch to make it look good
        bbox_section_layout.setContentsMargins(10,10,10,10)
        bbox_section_layout.setSpacing(10)
        bbox_section_layout.addStretch()

        #Add the bbox adjustment sections onto the main widget
        main_layout = QVBoxLayout(self)
        main_layout.addWidget(self.bbox_adjustment_section)
        
        #Add the margins and spacings to make sure that it fits nicely
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0,0,0,0)

        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
    
    def update_x(self):
        #Get the text input of x from the user and remove any excess spaces
        x_input = self.x_input.text().strip()

        #Check if the input is valid and only update if it's valid
        try:
            self.x_value = float(x_input)
            self.valid_input_widget.show()
            self.invalid_input_widget.hide()
        except:
            self.valid_input_widget.hide()
            self.invalid_input_widget.show()
        else:
            self.update_bbox_anchor()
        
    def update_y(self):
        #Get the text input of y from the user and remove any excess spaces
        y_input = self.y_input.text().strip()

        #Check if the input is valid and only update if it's valid
        try:
            self.y_value = float(y_input)
            self.valid_input_widget.show()
            self.invalid_input_widget.hide()
        except:
            self.valid_input_widget.hide()
            self.invalid_input_widget.show()
        else:
            self.update_bbox_anchor()

    def update_width(self):
        #Get the text input of the width from the user and remove any excess spaces
        width_input = self.width_input.text().strip()

        #Check if the input is valid and only update if it's valid
        try:
            self.width_value = float(width_input)
            self.valid_input_widget.show()
            self.invalid_input_widget.hide()
        except:
            self.valid_input_widget.hide()
            self.invalid_input_widget.show()
        else:
            self.update_bbox_anchor()

    def update_height(self):
        #Get the text input of the height input from the user and remove any excess spaces
        height_input = self.height_input.text().strip()
        
        #Check if the input is valid and only update if it's valid
        try:
            self.height_value = float(height_input)
            self.valid_input_widget.show()
            self.invalid_input_widget.hide()
        except:
            self.valid_input_widget.hide()
            self.invalid_input_widget.show()
        else:
            self.update_bbox_anchor()

    def update_bbox_anchor(self):
        #Get the newest json file if it exist
        db = self.plot_manager.get_db()
        new_bbox_anchor = (self.x_value,self.y_value,self.width_value,self.height_value)
        #If the json file is not empty then update it and if it is empty then create one with the new bbox anchor with it.
        if (db != []):
            self.plot_manager.update_legend("bbox_to_anchor",new_bbox_anchor)
        else:
            plot_parameters = plot_json[self.selected_graph].copy()
            plot_parameters["legend"]["bbox_to_anchor"] = new_bbox_anchor
            self.plot_manager.insert_plot_parameter(plot_parameters)

    def mousePressEvent(self, event):
        if not self.x_input.geometry().contains(event.position().toPoint()):
            self.x_input.clearFocus()
        if not self.y_input.geometry().contains(event.position().toPoint()):
            self.y_input.clearFocus()
        if not self.width_input.geometry().contains(event.position().toPoint()):
            self.width_input.clearFocus()
        if not self.height_input.geometry().contains(event.position().toPoint()):
            self.height_input.clearFocus()
        super().mousePressEvent(event)

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

        #Initialize the ncol value to be 0
        self.ncol_value = 0

        #Create a line edit object for the user to input the ncol
        self.ncol_input = QLineEdit()
        self.ncol_input.setPlaceholderText("ncol: ")

        #Set the height of the line edit object to make it look good
        self.ncol_input.setFixedHeight(60)

        #Connect any changes with the text to an update function
        self.ncol_input.textChanged.connect(self.change_ncol)

        #Create two widget to display valid and invalid inputs
        self.valid_input_widget = QWidget()
        self.valid_input_widget.setObjectName("valid_input")
        self.valid_input_widget.setStyleSheet("""
            QWidget#valid_input{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(94, 255, 234, 1),   
                    stop:0.3 rgba(63, 252, 180, 1), 
                    stop:0.6 rgba(150, 220, 255, 1)
                    stop:1 rgba(180, 200, 255, 1)  
                );
                border: 2px solid black;
                border-radius: 16px;
            }
        """)

        self.valid_input_label = QLabel("Valid Input")
        self.valid_input_label.setWordWrap(True)
        self.valid_input_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.valid_input_label.setObjectName("valid_input_label")
        self.valid_input_label.setStyleSheet("""
            QLabel#valid_input_label{
                font-family: "SF Pro Display";
                font-weight: 600;
                font-size: 24px;
                padding: 6px;
                color: black;
                border: none;
                background: transparent;
            }
        """)

        valid_input_layout = QVBoxLayout(self.valid_input_widget)
        valid_input_layout.addWidget(self.valid_input_label)
        valid_input_layout.setSpacing(0)
        valid_input_layout.setContentsMargins(0,0,0,0)

        self.invalid_input_widget = QWidget()
        self.invalid_input_widget.setObjectName("invalid_input")
        self.invalid_input_widget.setStyleSheet("""
            QWidget#invalid_input{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(255, 100, 100, 1),   
                    stop:0.4 rgba(255, 130, 120, 1), 
                    stop:0.7 rgba(200, 90, 150, 1), 
                    stop:1 rgba(180, 60, 140, 1)     
                );
                border: 2px solid black;
                border-radius: 16px;
            }
        """)

        self.invalid_input_label = QLabel("Invalid Input")
        self.invalid_input_label.setWordWrap(True)
        self.invalid_input_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.invalid_input_label.setObjectName("invalid_input_label")
        self.invalid_input_label.setStyleSheet("""
            QLabel#invalid_input_label{
                font-family: "SF Pro Display";
                font-weight: 600;
                font-size: 24px;
                padding: 6px;
                color: black;
                border: none;
                background: transparent;
            }
        """)

        invalid_input_layout = QVBoxLayout(self.invalid_input_widget)
        invalid_input_layout.addWidget(self.invalid_input_label)
        invalid_input_layout.setSpacing(0)
        invalid_input_layout.setContentsMargins(0,0,0,0)

        self.valid_input_widget.setMaximumHeight(50)
        self.invalid_input_widget.setMaximumHeight(50)

        self.valid_input_widget.hide()
        self.invalid_input_widget.hide()

        #Create a layout for the ncol adjustment section and add the line edit object to it
        ncol_section_layout = QVBoxLayout(self.ncol_adjustment_section)
        ncol_section_layout.addWidget(self.ncol_input)
        ncol_section_layout.addWidget(self.valid_input_widget)
        ncol_section_layout.addWidget(self.invalid_input_widget)
    
        #Add the margins, spacing, and stretch to the layout to make it look good
        ncol_section_layout.setContentsMargins(10,10,10,10)
        ncol_section_layout.setSpacing(10)
        ncol_section_layout.addStretch()

        #Add the ncol adjustment section to the main widget
        main_layout = QVBoxLayout(self)
        main_layout.addWidget(self.ncol_adjustment_section)
        
        #Set both the spacing and margins for the main widget to make sure it fits nicely
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0,0,0,0)

        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
    
    def change_ncol(self):
        #Extract the ncol input from the user and remove any excess text from it
        ncol_input = self.ncol_input.text().strip()

        #Only update the ncol value in the json file if the input is valid
        try:
            self.ncol_value = int(ncol_input)
            self.valid_input_widget.show()
            self.invalid_input_widget.hide()
        except:
            self.valid_input_widget.hide()
            self.invalid_input_widget.show()
        else:
            self.update_ncol()

    def update_ncol(self):
        #Get the newest json entries from the plot manager
        db = self.plot_manager.get_db()

        #Check if db is empty or not. If it is empty then create a new entry with the ncol value
        #If the db isn't empty then update the db with the new ncol value.
        if (db != []):
            self.plot_manager.update_legend("ncol",self.ncol_value)
        else:
            plot_parameters = plot_json[self.selected_graph].copy()
            plot_parameters["legend"]["ncol"] = self.ncol_value
            self.plot_manager.insert_plot_parameter(plot_parameters)

    def mousePressEvent(self, event):
        if not self.ncol_input.geometry().contains(event.position().toPoint()):
            self.ncol_input.clearFocus()
        super().mousePressEvent(event)

class fontsize_adjustment_section(QWidget):
    def __init__(self,selected_graph):
        super().__init__()
        
        self.plot_manager = PlotManager()

        self.selected_graph = selected_graph

        #Initialize the options for the fixed fontsize
        self.fixed_fontsizes = ["xx-small", "x-small", "small", "medium", "large", "x-large", "xx-large"]
        
        #Set the initial fontsize to be none
        self.current_fontsize = None
    
        #Use current page to control going back and forth on pages and idx to control which font size is chosen
        self.current_page = 0

        #Create a new widget for the fontsize adjustment section and style it to match the other ones
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

        #Create a button for getting to the screen to input the custom fontsize and customize the button
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

        #Create a button for getting to the screen for selecting the fixed fontsizes and customize the button
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

        #Connect both the custom and fixed fontsize buttons to their associated function
        self.custom_fontsize_button.clicked.connect(self.change_to_custom_fontsize_screen)
        self.fixed_fontsize_button.clicked.connect(self.change_to_fixed_fontsize_screen)

        #Create a layout to store all the buttons in
        button_layout = QVBoxLayout(self.fontsize_adjustment_section)
        button_layout.addWidget(self.custom_fontsize_button)
        button_layout.addWidget(self.fixed_fontsize_button)

        #Add margins, spacing, and stretch to make the layout look nice.
        button_layout.setContentsMargins(10,10,10,10)
        button_layout.setSpacing(5)
        button_layout.addStretch()

        #Create the custom fontsize adjustment screen
        self.custom_fontsize_screen = QWidget()
        self.custom_fontsize_screen.setObjectName("custom_fontsize_screen")
        self.custom_fontsize_screen.setStyleSheet("""
            QWidget#custom_fontsize_screen{
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
        self.create_custom_fontsize_screen()
        self.custom_fontsize_screen.hide()

        #Create the fixed fontsize adjustment screen
        self.fixed_fontsize_screen = QWidget()
        self.fixed_fontsize_screen.setObjectName("fixed_fontsize_screen")
        self.fixed_fontsize_screen.setStyleSheet("""
            QWidget#fixed_fontsize_screen{
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
        self.create_fixed_fontsize_screen()
        self.fixed_fontsize_screen.hide()

        self.available_screen = [self.fontsize_adjustment_section,self.custom_fontsize_screen,self.fixed_fontsize_screen]

        #Create a layout for the main widget and add the adjustment section to it
        main_layout = QVBoxLayout(self)
        main_layout.addWidget(self.fontsize_adjustment_section)
        main_layout.addWidget(self.custom_fontsize_screen)
        main_layout.addWidget(self.fixed_fontsize_screen)

        #Add the spacing and margin to ensure the section fits nicely with the main widget
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0,0,0,0)

        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

        #Create shortcuts to go back and forth between the screens.
        go_back_shortcut = QShortcut(QKeySequence("left"), self) 
        go_back_shortcut.activated.connect(self.change_to_original_screen)

    def create_custom_fontsize_screen(self):
        custom_fontsize_layout = QVBoxLayout(self.custom_fontsize_screen)

        #Create a QLineEdit object to allow the user input the custom fontsize
        #Give it a placeholder text to make sure that the user knows what to input and style the button
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

        #Set the height for the QLineEdit for consistency
        self.custom_fontsize_input.setFixedHeight(60) 
        
        #Connect the QLineEdit object with a update to automatically update the user inputs
        self.custom_fontsize_input.textChanged.connect(self.change_custom_fontsize)

        #Create two widget to display valid and invalid inputs
        self.valid_input_widget = QWidget()
        self.valid_input_widget.setObjectName("valid_input")
        self.valid_input_widget.setStyleSheet("""
            QWidget#valid_input{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(94, 255, 234, 1),   
                    stop:0.3 rgba(63, 252, 180, 1), 
                    stop:0.6 rgba(150, 220, 255, 1)
                    stop:1 rgba(180, 200, 255, 1)  
                );
                border: 2px solid black;
                border-radius: 16px;
            }
        """)

        self.valid_input_label = QLabel("Valid Input")
        self.valid_input_label.setWordWrap(True)
        self.valid_input_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.valid_input_label.setObjectName("valid_input_label")
        self.valid_input_label.setStyleSheet("""
            QLabel#valid_input_label{
                font-family: "SF Pro Display";
                font-weight: 600;
                font-size: 24px;
                padding: 6px;
                color: black;
                border: none;
                background: transparent;
            }
        """)

        valid_input_layout = QVBoxLayout(self.valid_input_widget)
        valid_input_layout.addWidget(self.valid_input_label)
        valid_input_layout.setSpacing(0)
        valid_input_layout.setContentsMargins(0,0,0,0)

        self.invalid_input_widget = QWidget()
        self.invalid_input_widget.setObjectName("invalid_input")
        self.invalid_input_widget.setStyleSheet("""
            QWidget#invalid_input{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(255, 100, 100, 1),   
                    stop:0.4 rgba(255, 130, 120, 1), 
                    stop:0.7 rgba(200, 90, 150, 1), 
                    stop:1 rgba(180, 60, 140, 1)     
                );
                border: 2px solid black;
                border-radius: 16px;
            }
        """)

        self.invalid_input_label = QLabel("Invalid Input")
        self.invalid_input_label.setWordWrap(True)
        self.invalid_input_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.invalid_input_label.setObjectName("invalid_input_label")
        self.invalid_input_label.setStyleSheet("""
            QLabel#invalid_input_label{
                font-family: "SF Pro Display";
                font-weight: 600;
                font-size: 24px;
                padding: 6px;
                color: black;
                border: none;
                background: transparent;
            }
        """)

        invalid_input_layout = QVBoxLayout(self.invalid_input_widget)
        invalid_input_layout.addWidget(self.invalid_input_label)
        invalid_input_layout.setSpacing(0)
        invalid_input_layout.setContentsMargins(0,0,0,0)

        self.valid_input_widget.setMaximumHeight(50)
        self.invalid_input_widget.setMaximumHeight(50)

        self.valid_input_widget.hide()
        self.invalid_input_widget.hide()

        #Add the QLineEdit object to the layout and add the margins, spacing, and stretch to make it look good
        custom_fontsize_layout.addWidget(self.custom_fontsize_input)
        custom_fontsize_layout.addWidget(self.valid_input_widget)
        custom_fontsize_layout.addWidget(self.invalid_input_widget)
        custom_fontsize_layout.setContentsMargins(10,10,10,10)
        custom_fontsize_layout.setSpacing(10)
        custom_fontsize_layout.addStretch()

    def create_fixed_fontsize_screen(self):
        fixed_fontsize_screen_layout = QVBoxLayout(self.fixed_fontsize_screen)
    
        self.fixed_fontsize_list_view = QListView()
        self.fixed_fontsize_model = QStringListModel(self.fixed_fontsizes)

        self.fixed_fontsize_list_view.setModel(self.fixed_fontsize_model)
        self.fixed_fontsize_list_view.setObjectName("fixed_fontsize_list_view")
        class CustomDelegate(QStyledItemDelegate):
            def paint(self, painter, option, index):
                option.displayAlignment = Qt.AlignmentFlag.AlignCenter
                font = QFont("SF Pro Display", 24)
                font.setWeight(600)
                option.font = font
                super().paint(painter, option, index)
        
        self.fixed_fontsize_list_view.setItemDelegate(CustomDelegate())

        self.fixed_fontsize_list_view.setStyleSheet("""
            QListView#fixed_fontsize_list_view{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #f5f5ff,
                    stop:0.5 #f7f5fc,
                    stop:1 #f0f0ff
                );
                border: transparent;
                border-radius: 24px;
            }
            QListView#fixed_fontsize_list_view::item {
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
                color: black;
                min-height: 41px;
            }
            QListView#fixed_fontsize_list_view::item:selected {
                background: qlineargradient(
                    x1:0, y1:0,
                    x2:1, y2:0,
                    stop:0 rgba(94, 255, 234, 1),
                    stop:0.5 rgba(171, 156, 255, 1),
                    stop:1 rgba(255, 203, 255, 1)
                );
                border: 2px solid black;
                border-radius: 16px;
                color: black;
                min-height: 41px;
            }
            QListView#fixed_fontsize_list_view::item:hover {
                background: qlineargradient(
                    x1:0, y1:0,
                    x2:1, y2:0,
                    stop:0 rgba(94, 255, 234, 1),
                    stop:0.5 rgba(171, 156, 255, 1),
                    stop:1 rgba(255, 203, 255, 1)
                );
                border: 2px solid black;
                border-radius: 16px;
                color: black;
                min-height: 41px;
            }
        """)

        self.fixed_fontsize_list_view.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.fixed_fontsize_list_view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.fixed_fontsize_list_view.setSpacing(3)

        self.fixed_fontsize_list_view.clicked.connect(self.change_fixed_fontsize)

        fixed_fontsize_screen_layout.addWidget(self.fixed_fontsize_list_view)

        # Add margins and spacing to make it look good and push content to the top
        fixed_fontsize_screen_layout.setContentsMargins(10, 10, 10, 10)

    def change_to_original_screen(self):
        self.available_screen[self.current_page].hide()
        self.current_page = 0
        self.fontsize_adjustment_section.show()

    def change_to_custom_fontsize_screen(self):
        self.available_screen[self.current_page].hide()
        self.current_page = 1
        self.custom_fontsize_screen.show()

    def change_to_fixed_fontsize_screen(self):
        self.available_screen[self.current_page].hide()
        self.current_page = 2
        self.fixed_fontsize_screen.show()

    def change_custom_fontsize(self):
        custom_fontsize_input = self.custom_fontsize_input.text().strip()

        if (custom_fontsize_input == ""):
            self.valid_input_widget.hide()
            self.invalid_input_widget.hide()
            self.current_fontsize = None
            return

        try:
            custom_fontsize_value = int(custom_fontsize_input)
            if (0 >= custom_fontsize_value):
                raise Exception
            self.valid_input_widget.show()
            self.invalid_input_widget.hide()
        except:
            self.valid_input_widget.hide()
            self.invalid_input_widget.show()
        else:
            self.current_fontsize = custom_fontsize_value
            self.update_fontsize()

    def change_fixed_fontsize(self,index):
        self.current_fontsize = self.fixed_fontsize_model.data(index,Qt.ItemDataRole.DisplayRole)
        self.update_fontsize()

    def update_fontsize(self):
        #Get the newest entry from the json file
        db = self.plot_manager.get_db()

        #Check if the entry is empty or not.
        #If the entry is empty then create one with the new fontsize else update the newest one with the new fontsize
        if (db != []):
            self.plot_manager.update_legend("fontsize",self.current_fontsize)
        else:
            plot_parameters = plot_json[self.selected_graph].copy()
            plot_parameters["legend"]["fontsize"] = self.current_fontsize
            self.plot_manager.insert_plot_parameter(plot_parameters)

    def mousePressEvent(self, event):
        if not self.custom_fontsize_input.geometry().contains(event.position().toPoint()):
            self.custom_fontsize_input.clearFocus()
        super().mousePressEvent(event)

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

        #Initialize the value for the title
        self.title_value = ""

        #Create a QLineEdit to allow the user to input the title and add a placeholder text to it
        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("title: ")
        
        #Set the height of the object for consistency
        self.title_input.setFixedHeight(60)

        #Connect the object to a function to allow it to update automatically
        self.title_input.textChanged.connect(self.update_title)

        #Create a layout for the title section and add the line edit object to the layout
        title_section_layout = QVBoxLayout(self.title_adjustment_section)
        title_section_layout.addWidget(self.title_input)

        #Add the margins, spacing, and stretch to the layout to make it look good
        title_section_layout.setContentsMargins(10,10,10,10)
        title_section_layout.setSpacing(10)
        title_section_layout.addStretch()

        #Create a main layout for the main widget and add the title adjustment section to it
        main_layout = QVBoxLayout(self)
        main_layout.addWidget(self.title_adjustment_section)
        
        #Add the spacing and margin to the main widget to ensure it fits nicely
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0,0,0,0)
    
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

    def update_title(self):
        #Extract the title from the user input and remove any excess spaces.
        self.title_value = self.title_input.text().strip()

        #Change the title to None if it's an empty string
        if (self.title_value == ""):
            self.title_value = None

        #Update it in the json file
        self.update_json()

    def update_json(self):
        #Get the new entry in the json file
        db = self.plot_manager.get_db()
        
        #Check if the db is empty or not and update it if it's empty
        #If the db is empty then create a new entry in the json file with the new title
        if (db != []):
            self.plot_manager.update_legend("title",self.title_value)
        else:
            plot_parameters = plot_json[self.selected_graph].copy()
            plot_parameters["legend"]["title"] = self.title_value
            self.plot_manager.insert_plot_parameter(plot_parameters)

class legend_title_fontsize_adjustment_section(QWidget):
    def __init__(self,selected_graph):
        super().__init__()
        
        self.plot_manager = PlotManager()

        self.selected_graph = selected_graph
        
        #Initialize the custom title fontsize and the fixed fontsizes
        self.custom_title_fontsize = 0
        self.fixed_title_fontsizes = ["xx-small", "x-small", "small", "medium", "large", "x-large", "xx-large"]
        
        #Initialize the fontsize to be None in the beginning
        self.current_title_fontsize = None

        #Initialize the current page to be 0 and the index to be 0
        self.current_page = 0
        self.title_font_idx = 0

        #Store the fontsize buttons created in a list
        self.title_fontsize_buttons = []

        #Create a widget for the title fontsize adjustment section and style it.
        self.title_fontsize_adjustment_section = QWidget()
        self.title_fontsize_adjustment_section.setObjectName("adjust_title_fontsize_section")
        self.title_fontsize_adjustment_section.setStyleSheet("""
            QWidget#adjust_title_fontsize_section{
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

        #Create a QPushButton for switching to the custom title fontsize screen and customize it
        self.custom_title_fontsize_button = QPushButton("Custom Title Fontsize")
        self.custom_title_fontsize_button.setObjectName("custom_title_fontsize")
        self.custom_title_fontsize_button.setStyleSheet("""
            QPushButton#custom_title_fontsize{
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
            QPushButton#custom_title_fontsize:hover{
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

        #Create a QPushButton for switching to the fixed fontsize screen and customize it
        self.fixed_title_fontsize_button = QPushButton("Fixed Title Fontsize")
        self.fixed_title_fontsize_button.setObjectName("fixed_title_fontsize")
        self.fixed_title_fontsize_button.setStyleSheet("""
            QPushButton#fixed_title_fontsize{
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
            QPushButton#fixed_title_fontsize:hover{
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

        #Connect the two buttons to a button that will switch to the associated screen either custom or fixed fontsize
        self.custom_title_fontsize_button.clicked.connect(self.change_to_custom_title_fontsize)
        self.fixed_title_fontsize_button.clicked.connect(self.change_to_fixed_title_fontsize)

        #Create a layout for the title fontsize adjustment section
        button_layout = QVBoxLayout(self.title_fontsize_adjustment_section)

        #Add all the buttons to the layout which will be added to the title fontsize adjustment section
        button_layout.addWidget(self.custom_title_fontsize_button)
        button_layout.addWidget(self.fixed_title_fontsize_button)

        #Add the margins, spacing, and stretch to the layout so that the buttons will look good on the widget
        button_layout.setContentsMargins(10,10,10,10)
        button_layout.setSpacing(5)
        button_layout.addStretch()

        #Create a layout for the main wdiget and add the title fontsize adjustment section to it
        main_layout = QVBoxLayout(self)
        main_layout.addWidget(self.title_fontsize_adjustment_section)

        #Add the spacing and margins to make sure that the section fits nicely to the main widget
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0,0,0,0)

        #Create two shortcuts to allow the user to switch between screens
        go_back_shortcut = QShortcut(QKeySequence("left"), self) 
        go_back_shortcut.activated.connect(self.change_to_original_screen)

        go_to_previous_screen_shortcut = QShortcut(QKeySequence("right"), self) 
        go_to_previous_screen_shortcut.activated.connect(self.change_to_old_page) 

        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

    def clear_layout(self):
        #Clear every widget on the layout
        layout = self.title_fontsize_adjustment_section.layout()
        if layout:
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget:
                    widget.setParent(None)

    def change_to_original_screen(self):
        #Make sure that the layout is completely empty and we're working with a empty widget
        self.clear_layout()

        #Grab the layout that is used for the title_fontsize_adjustment_section
        button_layout = self.title_fontsize_adjustment_section.layout()

        #Add the buttons needed back to it so that it goes back to the original screen
        button_layout.addWidget(self.custom_title_fontsize_button)
        button_layout.addWidget(self.fixed_title_fontsize_button)

        #Add the margins, spacing, and stretch to replicate what the original screen was like
        button_layout.setContentsMargins(10,10,10,10)
        button_layout.setSpacing(5)
        button_layout.addStretch()

        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

    def change_to_old_page(self):
        #Check if the user has been to any other screen
        if (self.current_page != 0):
            #Change the screen based on the last screen the user has been to
            self.clear_layout()
            if (self.current_page == 1):
                self.change_to_custom_title_fontsize()
            elif (self.current_page == 2):
                self.change_to_fixed_title_fontsize()

    def change_to_custom_title_fontsize(self):
        #Make sure that the layout is completely empty and we're working with a empty widget
        self.clear_layout()

        #Set the current page variable to 1 for the user to go back to this screen later
        self.current_page = 1

        #Create QLineEdit object to allow the user to input the custom fontsize they want
        #Add a placeholder text to ensure the user knows what to input and style it to make it look good
        self.custom_title_fontsize_input = QLineEdit()
        self.custom_title_fontsize_input.setPlaceholderText("Title Fontsize:")
        self.custom_title_fontsize_input.setObjectName("custom_title_fontsize_input")
        self.custom_title_fontsize_input.setStyleSheet("""
            QLineEdit#custom_title_fontsize_input{
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
        
        #Set the size of the QLineEdit object for consistency
        self.custom_title_fontsize_input.setFixedHeight(60) 
        
        #Connect the QLineEdit object to a function that will automatically update whenever the user inputs something
        self.custom_title_fontsize_input.textChanged.connect(self.process_custom_title_fontsize)

        #Grab the layout of the title_fontsize_adjustment_section so that the final result is applied onto the main widget
        custom_fontsize_layout = self.title_fontsize_adjustment_section.layout()

        #Add the QLineEdit Object to the layout
        custom_fontsize_layout.addWidget(self.custom_title_fontsize_input)

        #Add the margins, spacing, and stretch to make it look nicer
        custom_fontsize_layout.setContentsMargins(10,10,10,10)
        custom_fontsize_layout.setSpacing(0)
        custom_fontsize_layout.addStretch()

    def change_to_fixed_title_fontsize(self):
        #Make sure that the layout is completely empty and we're working with a empty widget
        self.clear_layout()

        #Set the current page variable to 2 to allow the user to go back to this page later
        self.current_page = 2 

        #Make sure that there is no old buttons in the layout
        self.title_fontsize_buttons.clear()
        self.current_title_fontsize = self.fixed_title_fontsizes[self.title_font_idx]

        #Create a vertical box to put the buttons in. Make sure they are positioned vertically.
        button_layout = self.title_fontsize_adjustment_section.layout()
        #Go through each parameter in the list and create a button for each of them
        for size in self.fixed_title_fontsizes:

            #Make a copy of the current fontsize name
            fontsize = str(size)

            #Create the button with the fontsize name, give it an object name, and give it a fixedHeight for consistency
            fontsize_button = QPushButton(size)
            fontsize_button.setObjectName("not_selected")
            fontsize_button.setFixedHeight(45)

            #Connect each button to the change parameter feature to ensure that dataset being displayed changes with the button
            fontsize_button.clicked.connect(lambda checked=False, fontsize=fontsize: self.change_fontsize(fontsize))

            #Add the button to the list and the layout
            self.title_fontsize_buttons.append(fontsize_button)
            button_layout.addWidget(fontsize_button)

        #Add margins and spacing to make it look and push all the buttons to the top
        button_layout.setContentsMargins(10,10,10,10)
        button_layout.setSpacing(5) 
        button_layout.addStretch()

        self.highlighted_selected_button()

    def change_fontsize(self,fontsize):
        #Keep track of the old idx and change both the column name and new idx
        old_idx = self.title_font_idx
        self.current_title_fontsize = fontsize
        self.title_font_idx = self.fixed_title_fontsizes.index(self.current_title_fontsize)

        #Change the current button that's being displayed and highlight the selected button
        self.highlighted_selected_button(old_idx)

    def highlighted_selected_button(self,old_idx=-1):
        self.update_fontsize()
        #Set the current button selected to be called selected
        self.title_fontsize_buttons[self.title_font_idx].setObjectName("selected")
        #If there is a old_idx then change the old button to be not selected
        if (old_idx != -1):
            self.title_fontsize_buttons[old_idx].setObjectName("not_selected")

        #Customize the dialog window and each button selected and not selected
        self.setStyleSheet("""
            QWidget#adjust_title_fontsize_section{
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

    def process_custom_title_fontsize(self):
        #Extract the fontsize from the user input
        self.current_title_fontsize = self.custom_title_fontsize_input.text().strip()
        #Check if the input is valid and only update if it's valid
        try:
            self.current_title_fontsize = int(self.custom_title_fontsize_input)
        except:
            pass
        else:
            self.update_fontsize()

    def update_fontsize(self):
        #Grab the newest entry in the json file
        db = self.plot_manager.get_db()
        #Check if the entry is empty or not and update if not empty and add if empty
        if (db != []):
            self.plot_manager.update_legend("fontsize",self.current_title_fontsize)
        else:
            plot_parameters = plot_json[self.selected_graph].copy()
            plot_parameters["legend"]["title_fontsize"] = self.current_title_fontsize
            self.plot_manager.insert_plot_parameter(plot_parameters)

class frameon_adjustment_section(QWidget):
    def __init__(self,selected_graph):
        super().__init__()
        
        self.plot_manager = PlotManager()

        self.selected_graph = selected_graph
        
        #Initialize the frameon state
        self.frameon_state = True
        
        #Create a widget to display the frameon adjustment section and style it for consistency
        self.frameon_adjustment_section = QWidget()
        self.frameon_adjustment_section.setObjectName("frameon_adjustment_section")
        self.frameon_adjustment_section.setStyleSheet("""
            QWidget#frameon_adjustment_section{
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
    
        #Create a button to allow the user to switch between Frameon
        self.frameon_button = QPushButton("Frameon")
        self.frameon_button.setObjectName("frameon_button")
        self.frameon_button.setStyleSheet("""
            QPushButton#frameon_button{
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
            QPushButton#frameon_button:hover{
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

        #Connect the frameon button to a function to switch between the two states
        self.frameon_button.clicked.connect(self.switch_on_frameon)

        #Create a button layout for the frameon adjustment section
        button_layout = QVBoxLayout(self.frameon_adjustment_section)

        #Add the frameon button to the layout
        button_layout.addWidget(self.frameon_button)

        #Set the spacing, margins, and stretch to make it look good
        button_layout.setSpacing(0)
        button_layout.setContentsMargins(10,10,10,10)
        button_layout.addStretch()

        #Create a layout for the main widget and store the frameon adjustment section in
        main_layout = QVBoxLayout(self)
        main_layout.addWidget(self.frameon_adjustment_section)

        #Add the spacing and margins to make sure that the section fits nicely
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0,0,0,0)

        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

    def switch_on_frameon(self):
        #Change the frameon_state to be the opposite of the current state and update it in the json
        self.frameon_state = not self.frameon_state
        self.update_frameon()

    def update_frameon(self):
        #Grab the newest entry in the json
        db = self.plot_manager.get_db()
        #Check if the entry is empty or not and update if it's not empty and create one with the state if it's empty
        if (db != []):
            self.plot_manager.update_legend("frameon",self.frameon_state)
        else:
            plot_parameters = plot_json[self.selected_graph].copy()
            plot_parameters["legend"]["frameon"] = self.frameon_state
            self.plot_manager.insert_plot_parameter(plot_parameters)

class face_color_adjustment_section(QWidget):
    def __init__(self,selected_graph):
        super().__init__()

        self.plot_manager = PlotManager()
        self.selected_graph = selected_graph
        self.named_colors = list(mcolors.get_named_colors_mapping().keys())
        self.short_code_colors = self.named_colors[-8:]
        self.named_colors = [c.replace("xkcd:","") for c in self.named_colors]
        self.named_colors = [c.replace("tab:","") for c in self.named_colors]
        self.named_colors = self.named_colors[:-8]

        self.current_facecolor = ""

        #-----Home Screen-----

        self.face_color_adjustment_homescreen = QWidget()
        self.face_color_adjustment_homescreen.setObjectName("face_color_adjustment")
        self.face_color_adjustment_homescreen.setStyleSheet("""
            QWidget#face_color_adjustment{
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

        self.named_color_button = QPushButton("Named Colors")
        self.named_color_button.setObjectName("named_color")
        self.named_color_button.setStyleSheet("""
            QPushButton#named_color{
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
            QPushButton#named_color:hover{
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

        self.hex_code_button = QPushButton("Hex Code Color")
        self.hex_code_button.setObjectName("hex_code")
        self.hex_code_button.setStyleSheet("""
            QPushButton#hex_code{
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
            QPushButton#hex_code:hover{
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

        self.rgba_color_button = QPushButton("RGBA Color")
        self.rgba_color_button.setObjectName("rgba_color")
        self.rgba_color_button.setStyleSheet("""
            QPushButton#rgba_color{
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
            QPushButton#rgba_color:hover{
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

        self.grayscale_color_button = QPushButton("Grayscale Color")
        self.grayscale_color_button.setObjectName("grayscale")
        self.grayscale_color_button.setStyleSheet("""
            QPushButton#grayscale{
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
            QPushButton#grayscale:hover{
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

        self.short_code_color_button = QPushButton("Short Code Color")
        self.short_code_color_button.setObjectName("short_code_color")
        self.short_code_color_button.setStyleSheet("""
            QPushButton#short_code_color{
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
            QPushButton#short_code_color:hover{
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

        self.none_button = QPushButton("None")
        self.none_button.setObjectName("none")
        self.none_button.setStyleSheet("""
            QPushButton#none{
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
            QPushButton#none:hover{
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

        self.named_color_button.clicked.connect(self.change_to_named_color_screen)
        self.hex_code_button.clicked.connect(self.change_to_hex_code_screen)
        self.rgba_color_button.clicked.connect(self.change_to_rgba_color_screen)
        self.grayscale_color_button.clicked.connect(self.change_to_grayscale_colors_screen)
        self.short_code_color_button.clicked.connect(self.change_to_short_code_color_screen)
        self.none_button.clicked.connect(self.set_color_to_none)

        button_layout = QVBoxLayout(self.face_color_adjustment_homescreen)
        button_layout.addWidget(self.named_color_button)
        button_layout.addWidget(self.hex_code_button)
        button_layout.addWidget(self.rgba_color_button)
        button_layout.addWidget(self.grayscale_color_button)
        button_layout.addWidget(self.short_code_color_button)
        button_layout.addWidget(self.none_button)
        button_layout.setContentsMargins(10,10,10,10)
        button_layout.setSpacing(5)
        button_layout.addStretch()

        #-----Named Color Screen-----

        self.named_color_screen = QWidget()
        self.named_color_screen.setObjectName("named_color_screen")
        self.named_color_screen.setStyleSheet("""
            QWidget#named_color_screen{
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
        self.create_named_color_screen()
        self.named_color_screen.hide()

        #-----Hex Code Color Screen-----

        self.hex_code_color_screen = QWidget()
        self.hex_code_color_screen.setObjectName("hex_code_color_screen")
        self.hex_code_color_screen.setStyleSheet("""
            QWidget#hex_code_color_screen{
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
        self.create_hex_code_screen()
        self.hex_code_color_screen.hide()

        #------RGBA Color Screen-----

        self.rgba_color_screen = QWidget()
        self.rgba_color_screen.setObjectName("rgba_color_screen")
        self.rgba_color_screen.setStyleSheet("""
            QWidget#rgba_color_screen{
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
        self.create_rgba_color_screen()
        self.rgba_color_screen.hide()

        self.initial_rgba = [0,0,0,1]

        #------Grayscale Color Screen-----

        self.grayscale_color_screen = QWidget()
        self.grayscale_color_screen.setObjectName("grayscale_color_screen")
        self.grayscale_color_screen.setStyleSheet("""
            QWidget#grayscale_color_screen{
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
        self.create_grayscale_color_screen()
        self.grayscale_color_screen.hide()

        #-----Short Code Colors-----

        self.short_code_color_screen = QWidget()
        self.short_code_color_screen.setObjectName("short_code_color")
        self.short_code_color_screen.setStyleSheet("""
            QWidget#short_code_color{
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
        self.create_short_code_color_screen()
        self.short_code_color_screen.hide()

        #-----Initialize Screen Value-----

        self.available_screens = [self.face_color_adjustment_homescreen,self.named_color_screen,
                                self.hex_code_color_screen,self.rgba_color_screen,
                                self.grayscale_color_screen,self.short_code_color_screen]
        self.previous_screen_idx = 0
        self.current_screen_idx = 0

        #-----Main Screen-----
        main_layout = QVBoxLayout(self)
        main_layout.addWidget(self.face_color_adjustment_homescreen)
        main_layout.addWidget(self.named_color_screen)
        main_layout.addWidget(self.hex_code_color_screen)
        main_layout.addWidget(self.rgba_color_screen)
        main_layout.addWidget(self.grayscale_color_screen)
        main_layout.addWidget(self.short_code_color_screen)
        main_layout.setContentsMargins(0,0,0,0)
        main_layout.setSpacing(0)

        #-----Shortcuts-----
        original_screen_shortcut = QShortcut(QKeySequence("left"),self)
        original_screen_shortcut.activated.connect(self.change_to_original_screen)

        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

    def create_named_color_screen(self):
        named_color_screen_layout = QVBoxLayout(self.named_color_screen)

        self.color_search_bar = QLineEdit()
        self.color_search_bar.setObjectName("search_bar")
        self.color_search_bar.setPlaceholderText("Search: ")
        self.color_search_bar.setStyleSheet("""
            QLineEdit#search_bar{
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
        self.color_search_bar.setMinimumHeight(60)
        named_color_screen_layout.addWidget(self.color_search_bar)
        named_color_screen_layout.addSpacing(15)
    
        self.named_color_list_view = QListView()
        self.named_color_model = QStringListModel(self.named_colors)

        self.filter_proxy = QSortFilterProxyModel()
        self.filter_proxy.setSourceModel(self.named_color_model)
        self.filter_proxy.setFilterCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive) 
        self.filter_proxy.setFilterKeyColumn(0)  

        self.color_search_bar.textChanged.connect(self.filter_proxy.setFilterFixedString)

        self.named_color_list_view.setModel(self.filter_proxy)
        self.named_color_list_view.setObjectName("named_color_list_view")

        class CustomDelegate(QStyledItemDelegate):
            def paint(self, painter, option, index):
                option.displayAlignment = Qt.AlignmentFlag.AlignCenter
                font = QFont("SF Pro Display", 24)
                font.setWeight(600)
                option.font = font
                super().paint(painter, option, index)
        
        self.named_color_list_view.setItemDelegate(CustomDelegate())

        self.named_color_list_view.setStyleSheet("""
            QListView#named_color_list_view{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #f5f5ff,
                    stop:0.5 #f7f5fc,
                    stop:1 #f0f0ff
                );
                border: transparent;
                border-radius: 24px;
            }
            QListView#named_color_list_view::item {
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
                color: black;
                min-height: 41px;
            }
            QListView#named_color_list_view::item:selected {
                background: qlineargradient(
                    x1:0, y1:0,
                    x2:1, y2:0,
                    stop:0 rgba(94, 255, 234, 1),
                    stop:0.5 rgba(171, 156, 255, 1),
                    stop:1 rgba(255, 203, 255, 1)
                );
                border: 2px solid black;
                border-radius: 16px;
                color: black;
                min-height: 41px;
            }
            QListView#named_color_list_view::item:hover {
                background: qlineargradient(
                    x1:0, y1:0,
                    x2:1, y2:0,
                    stop:0 rgba(94, 255, 234, 1),
                    stop:0.5 rgba(171, 156, 255, 1),
                    stop:1 rgba(255, 203, 255, 1)
                );
                border: 2px solid black;
                border-radius: 16px;
                color: black;
                min-height: 41px;
            }
        """)

        self.named_color_list_view.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.named_color_list_view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.named_color_list_view.setSpacing(3)

        self.named_color_list_view.clicked.connect(self.change_named_color)

        named_color_screen_layout.addWidget(self.named_color_list_view)

        # Add margins and spacing to make it look good and push content to the top
        named_color_screen_layout.setContentsMargins(10, 10, 10, 10)

    def create_hex_code_screen(self):
        hex_code_color_screen_layout = QVBoxLayout(self.hex_code_color_screen)

        self.hex_code_input = QLineEdit()
        self.hex_code_input.setObjectName("hex_code")
        self.hex_code_input.setPlaceholderText("Hex Code:")
        self.hex_code_input.setStyleSheet("""
            QLineEdit#hex_code{
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
        self.hex_code_input.setMinimumHeight(60)

        self.hex_code_input.textChanged.connect(self.change_hex_code_color)

        self.hex_valid_input_widget = QWidget()
        self.hex_valid_input_widget.setObjectName("hex_valid_input")
        self.hex_valid_input_widget.setStyleSheet("""
            QWidget#hex_valid_input{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(94, 255, 234, 1),   
                    stop:0.3 rgba(63, 252, 180, 1), 
                    stop:0.6 rgba(150, 220, 255, 1)
                    stop:1 rgba(180, 200, 255, 1)  
                );
                border: 2px solid black;
                border-radius: 16px;
            }
        """)

        self.hex_valid_input_label = QLabel("Valid Input")
        self.hex_valid_input_label.setWordWrap(True)
        self.hex_valid_input_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.hex_valid_input_label.setObjectName("hex_valid_input_label")
        self.hex_valid_input_label.setStyleSheet("""
            QLabel#hex_valid_input_label{
                font-family: "SF Pro Display";
                font-weight: 600;
                font-size: 24px;
                padding: 6px;
                color: black;
                border: none;
                background: transparent;
            }
        """)

        hex_valid_input_layout = QVBoxLayout(self.hex_valid_input_widget)
        hex_valid_input_layout.addWidget(self.hex_valid_input_label)
        hex_valid_input_layout.setSpacing(0)
        hex_valid_input_layout.setContentsMargins(0,0,0,0)

        self.hex_invalid_input_widget = QWidget()
        self.hex_invalid_input_widget.setObjectName("hex_invalid_input")
        self.hex_invalid_input_widget.setStyleSheet("""
            QWidget#hex_invalid_input{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(255, 100, 100, 1),   
                    stop:0.4 rgba(255, 130, 120, 1), 
                    stop:0.7 rgba(200, 90, 150, 1), 
                    stop:1 rgba(180, 60, 140, 1)     
                );
                border: 2px solid black;
                border-radius: 16px;
            }
        """)

        self.hex_invalid_input_label = QLabel("Invalid Input")
        self.hex_invalid_input_label.setWordWrap(True)
        self.hex_invalid_input_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.hex_invalid_input_label.setObjectName("hex_invalid_input_label")
        self.hex_invalid_input_label.setStyleSheet("""
            QLabel#hex_invalid_input_label{
                font-family: "SF Pro Display";
                font-weight: 600;
                font-size: 24px;
                padding: 6px;
                color: black;
                border: none;
                background: transparent;
            }
        """)

        hex_invalid_input_layout = QVBoxLayout(self.hex_invalid_input_widget)
        hex_invalid_input_layout.addWidget(self.hex_invalid_input_label)
        hex_invalid_input_layout.setSpacing(0)
        hex_invalid_input_layout.setContentsMargins(0,0,0,0)

        self.hex_valid_input_widget.setMaximumHeight(50)
        self.hex_invalid_input_widget.setMaximumHeight(50)

        self.hex_valid_input_widget.hide()
        self.hex_invalid_input_widget.hide()

        hex_code_color_screen_layout.addWidget(self.hex_code_input)
        hex_code_color_screen_layout.addWidget(self.hex_valid_input_widget)
        hex_code_color_screen_layout.addWidget(self.hex_invalid_input_widget)
        hex_code_color_screen_layout.setContentsMargins(10,10,10,10)
        hex_code_color_screen_layout.setSpacing(10)
        hex_code_color_screen_layout.addStretch()

    def create_rgba_color_screen(self):
        rgba_color_screen_layout = QVBoxLayout(self.rgba_color_screen)

        self.r_input = QLineEdit()
        self.r_input.setObjectName("r_input")
        self.r_input.setPlaceholderText("r:")
        self.r_input.setStyleSheet("""
            QLineEdit#r_input{
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

        self.g_input = QLineEdit()
        self.g_input.setObjectName("g_input")
        self.g_input.setPlaceholderText("g:")
        self.g_input.setStyleSheet("""
            QLineEdit#g_input{
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

        self.b_input = QLineEdit()
        self.b_input.setObjectName("b_input")
        self.b_input.setPlaceholderText("b:")
        self.b_input.setStyleSheet("""
            QLineEdit#b_input{
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

        self.a_input = QLineEdit()
        self.a_input.setObjectName("a_input")
        self.a_input.setPlaceholderText("a:")
        self.a_input.setStyleSheet("""
            QLineEdit#a_input{
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

        self.r_input.setMinimumHeight(60)
        self.g_input.setMinimumHeight(60)
        self.b_input.setMinimumHeight(60)
        self.a_input.setMinimumHeight(60)

        self.r_input.textChanged.connect(self.change_rgba_color)
        self.g_input.textChanged.connect(self.change_rgba_color)
        self.b_input.textChanged.connect(self.change_rgba_color)
        self.a_input.textChanged.connect(self.change_rgba_color)

        self.rgba_valid_input_widget = QWidget()
        self.rgba_valid_input_widget.setObjectName("rgba_valid_input")
        self.rgba_valid_input_widget.setStyleSheet("""
            QWidget#rgba_valid_input{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(94, 255, 234, 1),   
                    stop:0.3 rgba(63, 252, 180, 1), 
                    stop:0.6 rgba(150, 220, 255, 1)
                    stop:1 rgba(180, 200, 255, 1)  
                );
                border: 2px solid black;
                border-radius: 16px;
            }
        """)

        self.rgba_valid_input_label = QLabel("Valid Input")
        self.rgba_valid_input_label.setWordWrap(True)
        self.rgba_valid_input_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.rgba_valid_input_label.setObjectName("rgba_valid_input_label")
        self.rgba_valid_input_label.setStyleSheet("""
            QLabel#rgba_valid_input_label{
                font-family: "SF Pro Display";
                font-weight: 600;
                font-size: 24px;
                padding: 6px;
                color: black;
                border: none;
                background: transparent;
            }
        """)

        rgba_valid_input_layout = QVBoxLayout(self.rgba_valid_input_widget)
        rgba_valid_input_layout.addWidget(self.rgba_valid_input_label)
        rgba_valid_input_layout.setSpacing(0)
        rgba_valid_input_layout.setContentsMargins(0,0,0,0)

        self.rgba_invalid_input_widget = QWidget()
        self.rgba_invalid_input_widget.setObjectName("rgba_invalid_input")
        self.rgba_invalid_input_widget.setStyleSheet("""
            QWidget#rgba_invalid_input{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(255, 100, 100, 1),   
                    stop:0.4 rgba(255, 130, 120, 1), 
                    stop:0.7 rgba(200, 90, 150, 1), 
                    stop:1 rgba(180, 60, 140, 1)     
                );
                border: 2px solid black;
                border-radius: 16px;
            }
        """)

        self.rgba_invalid_input_label = QLabel("Invalid Input")
        self.rgba_invalid_input_label.setWordWrap(True)
        self.rgba_invalid_input_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.rgba_invalid_input_label.setObjectName("rgba_invalid_input_label")
        self.rgba_invalid_input_label.setStyleSheet("""
            QLabel#rgba_invalid_input_label{
                font-family: "SF Pro Display";
                font-weight: 600;
                font-size: 24px;
                padding: 6px;
                color: black;
                border: none;
                background: transparent;
            }
        """)

        rgba_invalid_input_layout = QVBoxLayout(self.rgba_invalid_input_widget)
        rgba_invalid_input_layout.addWidget(self.rgba_invalid_input_label)
        rgba_invalid_input_layout.setSpacing(0)
        rgba_invalid_input_layout.setContentsMargins(0,0,0,0)

        self.rgba_valid_input_widget.setMaximumHeight(50)
        self.rgba_invalid_input_widget.setMaximumHeight(50)

        self.rgba_valid_input_widget.hide()
        self.rgba_invalid_input_widget.hide()
    
        rgba_color_screen_layout.addWidget(self.r_input)
        rgba_color_screen_layout.addWidget(self.g_input)
        rgba_color_screen_layout.addWidget(self.b_input)
        rgba_color_screen_layout.addWidget(self.a_input)
        rgba_color_screen_layout.addWidget(self.rgba_valid_input_widget)
        rgba_color_screen_layout.addWidget(self.rgba_invalid_input_widget)

        rgba_color_screen_layout.setContentsMargins(10,10,10,10)
        rgba_color_screen_layout.setSpacing(10)
        rgba_color_screen_layout.addStretch()

    def create_grayscale_color_screen(self):
        grayscale_color_screen_layout = QVBoxLayout(self.grayscale_color_screen)

        self.grayscale_input = QLineEdit()
        self.grayscale_input.setObjectName("grayscale")
        self.grayscale_input.setPlaceholderText("Grayscale:")
        self.grayscale_input.setStyleSheet("""
            QLineEdit#grayscale{
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
        self.grayscale_input.setMinimumHeight(60)

        self.grayscale_input.textChanged.connect(self.change_grayscale_color)

        self.grayscale_valid_input_widget = QWidget()
        self.grayscale_valid_input_widget.setObjectName("grayscale_valid_input")
        self.grayscale_valid_input_widget.setStyleSheet("""
            QWidget#grayscale_valid_input{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(94, 255, 234, 1),   
                    stop:0.3 rgba(63, 252, 180, 1), 
                    stop:0.6 rgba(150, 220, 255, 1)
                    stop:1 rgba(180, 200, 255, 1)  
                );
                border: 2px solid black;
                border-radius: 16px;
            }
        """)

        self.grayscale_valid_input_label = QLabel("Valid Input")
        self.grayscale_valid_input_label.setWordWrap(True)
        self.grayscale_valid_input_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.grayscale_valid_input_label.setObjectName("grayscale_valid_input_label")
        self.grayscale_valid_input_label.setStyleSheet("""
            QLabel#grayscale_valid_input_label{
                font-family: "SF Pro Display";
                font-weight: 600;
                font-size: 24px;
                padding: 6px;
                color: black;
                border: none;
                background: transparent;
            }
        """)

        grayscale_valid_input_layout = QVBoxLayout(self.grayscale_valid_input_widget)
        grayscale_valid_input_layout.addWidget(self.grayscale_valid_input_label)
        grayscale_valid_input_layout.setSpacing(0)
        grayscale_valid_input_layout.setContentsMargins(0,0,0,0)

        self.grayscale_invalid_input_widget = QWidget()
        self.grayscale_invalid_input_widget.setObjectName("grayscale_invalid_input")
        self.grayscale_invalid_input_widget.setStyleSheet("""
            QWidget#grayscale_invalid_input{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(255, 100, 100, 1),   
                    stop:0.4 rgba(255, 130, 120, 1), 
                    stop:0.7 rgba(200, 90, 150, 1), 
                    stop:1 rgba(180, 60, 140, 1)     
                );
                border: 2px solid black;
                border-radius: 16px;
            }
        """)

        self.grayscale_invalid_input_label = QLabel("Invalid Input")
        self.grayscale_invalid_input_label.setWordWrap(True)
        self.grayscale_invalid_input_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.grayscale_invalid_input_label.setObjectName("grayscale_invalid_input_label")
        self.grayscale_invalid_input_label.setStyleSheet("""
            QLabel#grayscale_invalid_input_label{
                font-family: "SF Pro Display";
                font-weight: 600;
                font-size: 24px;
                padding: 6px;
                color: black;
                border: none;
                background: transparent;
            }
        """)

        grayscale_invalid_input_layout = QVBoxLayout(self.grayscale_invalid_input_widget)
        grayscale_invalid_input_layout.addWidget(self.grayscale_invalid_input_label)
        grayscale_invalid_input_layout.setSpacing(0)
        grayscale_invalid_input_layout.setContentsMargins(0,0,0,0)

        self.grayscale_valid_input_widget.setMaximumHeight(50)
        self.grayscale_invalid_input_widget.setMaximumHeight(50)

        self.grayscale_valid_input_widget.hide()
        self.grayscale_invalid_input_widget.hide()

        grayscale_color_screen_layout.addWidget(self.grayscale_input)
        grayscale_color_screen_layout.addWidget(self.grayscale_valid_input_widget)
        grayscale_color_screen_layout.addWidget(self.grayscale_invalid_input_widget)
        grayscale_color_screen_layout.setContentsMargins(10,10,10,10)
        grayscale_color_screen_layout.setSpacing(10)
        grayscale_color_screen_layout.addStretch()

    def create_short_code_color_screen(self):
        short_code_color_screen_layout = QVBoxLayout(self.short_code_color_screen)
    
        self.short_code_color_list_view = QListView()
        self.short_code_color_model = QStringListModel(self.short_code_colors)
        self.short_code_color_list_view.setModel(self.short_code_color_model)
        class CustomDelegate(QStyledItemDelegate):
            def paint(self, painter, option, index):
                option.displayAlignment = Qt.AlignmentFlag.AlignCenter
                font = QFont("SF Pro Display", 24)
                font.setWeight(600)
                option.font = font
                super().paint(painter, option, index)
        
        self.short_code_color_list_view.setItemDelegate(CustomDelegate())

        self.short_code_color_list_view.setObjectName("short_code_color_list_view")
        self.short_code_color_list_view.setStyleSheet("""
            QListView#short_code_color_list_view{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #f5f5ff,
                    stop:0.5 #f7f5fc,
                    stop:1 #f0f0ff
                );
                border: transparent;
                border-radius: 24px;
            }
            QListView#short_code_color_list_view::item {
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
                color: black;
                min-height: 41px;
            }
            QListView#short_code_color_list_view::item:selected {
                background: qlineargradient(
                    x1:0, y1:0,
                    x2:1, y2:0,
                    stop:0 rgba(94, 255, 234, 1),
                    stop:0.5 rgba(171, 156, 255, 1),
                    stop:1 rgba(255, 203, 255, 1)
                );
                border: 2px solid black;
                border-radius: 16px;
                color: black;
                min-height: 41px;
            }
            QListView#short_code_color_list_view::item:hover {
                background: qlineargradient(
                    x1:0, y1:0,
                    x2:1, y2:0,
                    stop:0 rgba(94, 255, 234, 1),
                    stop:0.5 rgba(171, 156, 255, 1),
                    stop:1 rgba(255, 203, 255, 1)
                );
                border: 2px solid black;
                border-radius: 16px;
                color: black;
                min-height: 41px;
            }
        """)
        self.short_code_color_list_view.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.short_code_color_list_view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.short_code_color_list_view.setSpacing(3)

        self.short_code_color_list_view.clicked.connect(self.change_short_code_color)

        short_code_color_screen_layout.addWidget(self.short_code_color_list_view)

        # Add margins and spacing to make it look good and push content to the top
        short_code_color_screen_layout.setContentsMargins(10, 10, 10, 10)

    def change_to_original_screen(self):
        self.available_screens[self.current_screen_idx].hide()
        self.current_screen_idx = 0
        self.face_color_adjustment_homescreen.show()

    def change_to_named_color_screen(self):
        self.available_screens[self.current_screen_idx].hide()
        self.previous_screen_idx = self.current_screen_idx
        self.current_screen_idx = 1
        self.named_color_screen.show()

    def change_to_hex_code_screen(self):
        self.available_screens[self.current_screen_idx].hide()
        self.previous_screen_idx = self.current_screen_idx
        self.current_screen_idx = 2
        self.hex_code_color_screen.show()

    def change_to_rgba_color_screen(self):
        self.available_screens[self.current_screen_idx].hide()
        self.previous_screen_idx = self.current_screen_idx
        self.current_screen_idx = 3
        self.rgba_color_screen.show()

    def change_to_grayscale_colors_screen(self):
        self.available_screens[self.current_screen_idx].hide()
        self.previous_screen_idx = self.current_screen_idx
        self.current_screen_idx = 4
        self.grayscale_color_screen.show()

    def change_to_short_code_color_screen(self):
        self.available_screens[self.current_screen_idx].hide()
        self.previous_screen_idx = self.current_screen_idx
        self.current_screen_idx = 5
        self.short_code_color_screen.show()

    def set_color_to_none(self):
        self.current_facecolor = None
        self.update_color()

    def change_named_color(self,index):
        source_index = self.filter_proxy.mapToSource(index)
        self.current_facecolor = self.named_color_model.data(source_index, Qt.ItemDataRole.DisplayRole)
        self.update_color()

    def change_hex_code_color(self):
        hex_code = self.hex_code_input.text().strip()

        if (hex_code == ""):
            self.hex_valid_input_widget.hide()
            self.hex_invalid_input_widget.hide()
            return

        def check_valid_hex_code(hex_code):
            if (hex_code[0] != "#"):
                new_hex_code = "#" + hex_code
                return check_valid_hex_code(new_hex_code)
            hex_code = hex_code[1:]
            if (len(hex_code) not in [3,6,8]):
                return False
            try:
                int(hex_code,16)
                return True
            except:
                return False
        
        if (hex_code != ""):
            validity = check_valid_hex_code(hex_code)
            if (validity):
                self.hex_valid_input_widget.show()
                self.hex_invalid_input_widget.hide()
                self.current_facecolor = hex_code if hex_code[0] == "#" else "#" + hex_code
                self.update_color()
            else:
                self.hex_valid_input_widget.hide()
                self.hex_invalid_input_widget.show()

    def change_rgba_color(self):
        r_value = self.r_input.text().strip()
        g_value = self.g_input.text().strip()
        b_value = self.b_input.text().strip()
        a_value = self.a_input.text().strip()

        if (not(r_value or g_value or b_value or a_value)):
            self.rgba_valid_input_widget.hide()
            self.rgba_invalid_input_widget.hide()
            return 

        valid = None

        try:
            r_value = int(r_value) if r_value != "" else self.initial_rgba[0]
            g_value = int(g_value) if g_value != "" else self.initial_rgba[1]
            b_value = int(b_value) if b_value != "" else self.initial_rgba[2]
            a_value = int(a_value) if a_value != "" else self.initial_rgba[3]
            valid = True
        except:
            valid = False

        if (valid):
            self.initial_rgba[0] = r_value 
            self.initial_rgba[1] = g_value
            self.initial_rgba[2] = b_value 
            self.initial_rgba[3] = a_value

            self.rgba_valid_input_widget.show()
            self.rgba_invalid_input_widget.hide()

            self.current_facecolor = self.initial_rgba

            self.update_color()
        else:
            self.rgba_valid_input_widget.hide()
            self.rgba_invalid_input_widget.show()

    def change_grayscale_color(self):
        grayscale_value = self.grayscale_input.text().strip()

        if (grayscale_value == ""): 
            self.grayscale_valid_input_widget.hide() 
            self.grayscale_invalid_input_widget.hide()
            return

        try: 
            grayscale_value = float(grayscale_value)
            if (0 > grayscale_value or grayscale_value > 1):
                raise Exception
            self.grayscale_valid_input_widget.show()
            self.grayscale_invalid_input_widget.hide()
        except:
            self.grayscale_valid_input_widget.hide()
            self.grayscale_invalid_input_widget.show()

        self.current_facecolor = grayscale_value
        self.update_color()

    def change_short_code_color(self,index):
        self.current_facecolor = self.short_code_color_model.data(index, Qt.ItemDataRole.DisplayRole)
        self.update_color()

    def update_color(self):
        db = self.plot_manager.get_db()
        if (db != []):
            self.plot_manager.update_legend("facecolor",self.current_facecolor)
        else:
            plot_parameters = plot_json[self.selected_graph].copy()
            plot_parameters["legend"]["facecolor"] = self.current_facecolor
            self.plot_manager.insert_plot_parameter(plot_parameters)

    def mousePressEvent(self, event):
        if not self.hex_code_input.geometry().contains(event.position().toPoint()):
            self.hex_code_input.clearFocus()
        if not self.r_input.geometry().contains(event.position().toPoint()):
            self.r_input.clearFocus()
        if not self.g_input.geometry().contains(event.position().toPoint()):
            self.g_input.clearFocus()
        if not self.b_input.geometry().contains(event.position().toPoint()):
            self.b_input.clearFocus()
        if not self.a_input.geometry().contains(event.position().toPoint()):
            self.a_input.clearFocus()
        if not self.grayscale_input.geometry().contains(event.position().toPoint()):
            self.grayscale_input.clearFocus()
        super().mousePressEvent(event)

class edge_color_adjustment_section(QWidget):
    def __init__(self,selected_graph):
        super().__init__()

        self.plot_manager = PlotManager()
        self.selected_graph = selected_graph
        self.named_colors = list(mcolors.get_named_colors_mapping().keys())
        self.short_code_colors = self.named_colors[-8:]
        self.named_colors = [c.replace("xkcd:","") for c in self.named_colors]
        self.named_colors = [c.replace("tab:","") for c in self.named_colors]
        self.named_colors = self.named_colors[:-8]

        self.current_edge_color = ""

        #-----Home Screen-----

        self.edge_color_adjustment_homescreen = QWidget()
        self.edge_color_adjustment_homescreen.setObjectName("face_color_adjustment")
        self.edge_color_adjustment_homescreen.setStyleSheet("""
            QWidget#face_color_adjustment{
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

        self.named_color_button = QPushButton("Named Colors")
        self.named_color_button.setObjectName("named_color")
        self.named_color_button.setStyleSheet("""
            QPushButton#named_color{
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
            QPushButton#named_color:hover{
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

        self.hex_code_button = QPushButton("Hex Code Color")
        self.hex_code_button.setObjectName("hex_code")
        self.hex_code_button.setStyleSheet("""
            QPushButton#hex_code{
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
            QPushButton#hex_code:hover{
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

        self.rgba_color_button = QPushButton("RGBA Color")
        self.rgba_color_button.setObjectName("rgba_color")
        self.rgba_color_button.setStyleSheet("""
            QPushButton#rgba_color{
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
            QPushButton#rgba_color:hover{
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

        self.grayscale_color_button = QPushButton("Grayscale Color")
        self.grayscale_color_button.setObjectName("grayscale")
        self.grayscale_color_button.setStyleSheet("""
            QPushButton#grayscale{
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
            QPushButton#grayscale:hover{
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

        self.short_code_color_button = QPushButton("Short Code Color")
        self.short_code_color_button.setObjectName("short_code_color")
        self.short_code_color_button.setStyleSheet("""
            QPushButton#short_code_color{
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
            QPushButton#short_code_color:hover{
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

        self.none_button = QPushButton("None")
        self.none_button.setObjectName("none")
        self.none_button.setStyleSheet("""
            QPushButton#none{
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
            QPushButton#none:hover{
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

        self.named_color_button.clicked.connect(self.change_to_named_color_screen)
        self.hex_code_button.clicked.connect(self.change_to_hex_code_screen)
        self.rgba_color_button.clicked.connect(self.change_to_rgba_color_screen)
        self.grayscale_color_button.clicked.connect(self.change_to_grayscale_colors_screen)
        self.short_code_color_button.clicked.connect(self.change_to_short_code_color_screen)
        self.none_button.clicked.connect(self.set_color_to_none)

        button_layout = QVBoxLayout(self.edge_color_adjustment_homescreen)
        button_layout.addWidget(self.named_color_button)
        button_layout.addWidget(self.hex_code_button)
        button_layout.addWidget(self.rgba_color_button)
        button_layout.addWidget(self.grayscale_color_button)
        button_layout.addWidget(self.short_code_color_button)
        button_layout.addWidget(self.none_button)
        button_layout.setContentsMargins(10,10,10,10)
        button_layout.setSpacing(5)
        button_layout.addStretch()

        #-----Named Color Screen-----

        self.named_color_screen = QWidget()
        self.named_color_screen.setObjectName("named_color_screen")
        self.named_color_screen.setStyleSheet("""
            QWidget#named_color_screen{
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
        self.create_named_color_screen()
        self.named_color_screen.hide()

        #-----Hex Code Color Screen-----

        self.hex_code_color_screen = QWidget()
        self.hex_code_color_screen.setObjectName("hex_code_color_screen")
        self.hex_code_color_screen.setStyleSheet("""
            QWidget#hex_code_color_screen{
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
        self.create_hex_code_screen()
        self.hex_code_color_screen.hide()

        #------RGBA Color Screen-----

        self.rgba_color_screen = QWidget()
        self.rgba_color_screen.setObjectName("rgba_color_screen")
        self.rgba_color_screen.setStyleSheet("""
            QWidget#rgba_color_screen{
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
        self.create_rgba_color_screen()
        self.rgba_color_screen.hide()

        self.initial_rgba = [0,0,0,1]

        #------Grayscale Color Screen-----

        self.grayscale_color_screen = QWidget()
        self.grayscale_color_screen.setObjectName("grayscale_color_screen")
        self.grayscale_color_screen.setStyleSheet("""
            QWidget#grayscale_color_screen{
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
        self.create_grayscale_color_screen()
        self.grayscale_color_screen.hide()

        #-----Short Code Colors-----

        self.short_code_color_screen = QWidget()
        self.short_code_color_screen.setObjectName("short_code_color")
        self.short_code_color_screen.setStyleSheet("""
            QWidget#short_code_color{
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
        self.create_short_code_color_screen()
        self.short_code_color_screen.hide()

        #-----Initialize Screen Value-----

        self.available_screens = [self.edge_color_adjustment_homescreen,self.named_color_screen,
                                self.hex_code_color_screen,self.rgba_color_screen,
                                self.grayscale_color_screen,self.short_code_color_screen]
        self.previous_screen_idx = 0
        self.current_screen_idx = 0

        #-----Main Screen-----
        main_layout = QVBoxLayout(self)
        main_layout.addWidget(self.edge_color_adjustment_homescreen)
        main_layout.addWidget(self.named_color_screen)
        main_layout.addWidget(self.hex_code_color_screen)
        main_layout.addWidget(self.rgba_color_screen)
        main_layout.addWidget(self.grayscale_color_screen)
        main_layout.addWidget(self.short_code_color_screen)
        main_layout.setContentsMargins(0,0,0,0)
        main_layout.setSpacing(0)

        #-----Shortcuts-----
        original_screen_shortcut = QShortcut(QKeySequence("left"),self)
        original_screen_shortcut.activated.connect(self.change_to_original_screen)

        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

    def create_named_color_screen(self):
        named_color_screen_layout = QVBoxLayout(self.named_color_screen)

        self.color_search_bar = QLineEdit()
        self.color_search_bar.setObjectName("search_bar")
        self.color_search_bar.setPlaceholderText("Search: ")
        self.color_search_bar.setStyleSheet("""
            QLineEdit#search_bar{
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
        self.color_search_bar.setMinimumHeight(60)
        named_color_screen_layout.addWidget(self.color_search_bar)
        named_color_screen_layout.addSpacing(15)
    
        self.named_color_list_view = QListView()
        self.named_color_model = QStringListModel(self.named_colors)

        self.filter_proxy = QSortFilterProxyModel()
        self.filter_proxy.setSourceModel(self.named_color_model)
        self.filter_proxy.setFilterCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive) 
        self.filter_proxy.setFilterKeyColumn(0)  

        self.color_search_bar.textChanged.connect(self.filter_proxy.setFilterFixedString)

        self.named_color_list_view.setModel(self.filter_proxy)
        self.named_color_list_view.setObjectName("named_color_list_view")

        class CustomDelegate(QStyledItemDelegate):
            def paint(self, painter, option, index):
                option.displayAlignment = Qt.AlignmentFlag.AlignCenter
                font = QFont("SF Pro Display", 24)
                font.setWeight(600)
                option.font = font
                super().paint(painter, option, index)
        
        self.named_color_list_view.setItemDelegate(CustomDelegate())

        self.named_color_list_view.setStyleSheet("""
            QListView#named_color_list_view{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #f5f5ff,
                    stop:0.5 #f7f5fc,
                    stop:1 #f0f0ff
                );
                border: transparent;
                border-radius: 24px;
            }
            QListView#named_color_list_view::item {
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
                color: black;
                min-height: 41px;
            }
            QListView#named_color_list_view::item:selected {
                background: qlineargradient(
                    x1:0, y1:0,
                    x2:1, y2:0,
                    stop:0 rgba(94, 255, 234, 1),
                    stop:0.5 rgba(171, 156, 255, 1),
                    stop:1 rgba(255, 203, 255, 1)
                );
                border: 2px solid black;
                border-radius: 16px;
                color: black;
                min-height: 41px;
            }
            QListView#named_color_list_view::item:hover {
                background: qlineargradient(
                    x1:0, y1:0,
                    x2:1, y2:0,
                    stop:0 rgba(94, 255, 234, 1),
                    stop:0.5 rgba(171, 156, 255, 1),
                    stop:1 rgba(255, 203, 255, 1)
                );
                border: 2px solid black;
                border-radius: 16px;
                color: black;
                min-height: 41px;
            }
        """)

        self.named_color_list_view.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.named_color_list_view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.named_color_list_view.setSpacing(3)

        self.named_color_list_view.clicked.connect(self.change_named_color)

        named_color_screen_layout.addWidget(self.named_color_list_view)

        # Add margins and spacing to make it look good and push content to the top
        named_color_screen_layout.setContentsMargins(10, 10, 10, 10)

    def create_hex_code_screen(self):
        hex_code_color_screen_layout = QVBoxLayout(self.hex_code_color_screen)

        self.hex_code_input = QLineEdit()
        self.hex_code_input.setObjectName("hex_code")
        self.hex_code_input.setPlaceholderText("Hex Code:")
        self.hex_code_input.setStyleSheet("""
            QLineEdit#hex_code{
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
        self.hex_code_input.setMinimumHeight(60)

        self.hex_code_input.textChanged.connect(self.change_hex_code_color)

        self.hex_valid_input_widget = QWidget()
        self.hex_valid_input_widget.setObjectName("hex_valid_input")
        self.hex_valid_input_widget.setStyleSheet("""
            QWidget#hex_valid_input{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(94, 255, 234, 1),   
                    stop:0.3 rgba(63, 252, 180, 1), 
                    stop:0.6 rgba(150, 220, 255, 1)
                    stop:1 rgba(180, 200, 255, 1)  
                );
                border: 2px solid black;
                border-radius: 16px;
            }
        """)

        self.hex_valid_input_label = QLabel("Valid Input")
        self.hex_valid_input_label.setWordWrap(True)
        self.hex_valid_input_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.hex_valid_input_label.setObjectName("hex_valid_input_label")
        self.hex_valid_input_label.setStyleSheet("""
            QLabel#hex_valid_input_label{
                font-family: "SF Pro Display";
                font-weight: 600;
                font-size: 24px;
                padding: 6px;
                color: black;
                border: none;
                background: transparent;
            }
        """)

        hex_valid_input_layout = QVBoxLayout(self.hex_valid_input_widget)
        hex_valid_input_layout.addWidget(self.hex_valid_input_label)
        hex_valid_input_layout.setSpacing(0)
        hex_valid_input_layout.setContentsMargins(0,0,0,0)

        self.hex_invalid_input_widget = QWidget()
        self.hex_invalid_input_widget.setObjectName("hex_invalid_input")
        self.hex_invalid_input_widget.setStyleSheet("""
            QWidget#hex_invalid_input{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(255, 100, 100, 1),   
                    stop:0.4 rgba(255, 130, 120, 1), 
                    stop:0.7 rgba(200, 90, 150, 1), 
                    stop:1 rgba(180, 60, 140, 1)     
                );
                border: 2px solid black;
                border-radius: 16px;
            }
        """)

        self.hex_invalid_input_label = QLabel("Invalid Input")
        self.hex_invalid_input_label.setWordWrap(True)
        self.hex_invalid_input_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.hex_invalid_input_label.setObjectName("hex_invalid_input_label")
        self.hex_invalid_input_label.setStyleSheet("""
            QLabel#hex_invalid_input_label{
                font-family: "SF Pro Display";
                font-weight: 600;
                font-size: 24px;
                padding: 6px;
                color: black;
                border: none;
                background: transparent;
            }
        """)

        hex_invalid_input_layout = QVBoxLayout(self.hex_invalid_input_widget)
        hex_invalid_input_layout.addWidget(self.hex_invalid_input_label)
        hex_invalid_input_layout.setSpacing(0)
        hex_invalid_input_layout.setContentsMargins(0,0,0,0)

        self.hex_valid_input_widget.setMaximumHeight(50)
        self.hex_invalid_input_widget.setMaximumHeight(50)

        self.hex_valid_input_widget.hide()
        self.hex_invalid_input_widget.hide()

        hex_code_color_screen_layout.addWidget(self.hex_code_input)
        hex_code_color_screen_layout.addWidget(self.hex_valid_input_widget)
        hex_code_color_screen_layout.addWidget(self.hex_invalid_input_widget)
        hex_code_color_screen_layout.setContentsMargins(10,10,10,10)
        hex_code_color_screen_layout.setSpacing(10)
        hex_code_color_screen_layout.addStretch()

    def create_rgba_color_screen(self):
        rgba_color_screen_layout = QVBoxLayout(self.rgba_color_screen)

        self.r_input = QLineEdit()
        self.r_input.setObjectName("r_input")
        self.r_input.setPlaceholderText("r:")
        self.r_input.setStyleSheet("""
            QLineEdit#r_input{
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

        self.g_input = QLineEdit()
        self.g_input.setObjectName("g_input")
        self.g_input.setPlaceholderText("g:")
        self.g_input.setStyleSheet("""
            QLineEdit#g_input{
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

        self.b_input = QLineEdit()
        self.b_input.setObjectName("b_input")
        self.b_input.setPlaceholderText("b:")
        self.b_input.setStyleSheet("""
            QLineEdit#b_input{
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

        self.a_input = QLineEdit()
        self.a_input.setObjectName("a_input")
        self.a_input.setPlaceholderText("a:")
        self.a_input.setStyleSheet("""
            QLineEdit#a_input{
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

        self.r_input.setMinimumHeight(60)
        self.g_input.setMinimumHeight(60)
        self.b_input.setMinimumHeight(60)
        self.a_input.setMinimumHeight(60)

        self.r_input.textChanged.connect(self.change_rgba_color)
        self.g_input.textChanged.connect(self.change_rgba_color)
        self.b_input.textChanged.connect(self.change_rgba_color)
        self.a_input.textChanged.connect(self.change_rgba_color)

        self.rgba_valid_input_widget = QWidget()
        self.rgba_valid_input_widget.setObjectName("rgba_valid_input")
        self.rgba_valid_input_widget.setStyleSheet("""
            QWidget#rgba_valid_input{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(94, 255, 234, 1),   
                    stop:0.3 rgba(63, 252, 180, 1), 
                    stop:0.6 rgba(150, 220, 255, 1)
                    stop:1 rgba(180, 200, 255, 1)  
                );
                border: 2px solid black;
                border-radius: 16px;
            }
        """)

        self.rgba_valid_input_label = QLabel("Valid Input")
        self.rgba_valid_input_label.setWordWrap(True)
        self.rgba_valid_input_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.rgba_valid_input_label.setObjectName("rgba_valid_input_label")
        self.rgba_valid_input_label.setStyleSheet("""
            QLabel#rgba_valid_input_label{
                font-family: "SF Pro Display";
                font-weight: 600;
                font-size: 24px;
                padding: 6px;
                color: black;
                border: none;
                background: transparent;
            }
        """)

        rgba_valid_input_layout = QVBoxLayout(self.rgba_valid_input_widget)
        rgba_valid_input_layout.addWidget(self.rgba_valid_input_label)
        rgba_valid_input_layout.setSpacing(0)
        rgba_valid_input_layout.setContentsMargins(0,0,0,0)

        self.rgba_invalid_input_widget = QWidget()
        self.rgba_invalid_input_widget.setObjectName("rgba_invalid_input")
        self.rgba_invalid_input_widget.setStyleSheet("""
            QWidget#rgba_invalid_input{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(255, 100, 100, 1),   
                    stop:0.4 rgba(255, 130, 120, 1), 
                    stop:0.7 rgba(200, 90, 150, 1), 
                    stop:1 rgba(180, 60, 140, 1)     
                );
                border: 2px solid black;
                border-radius: 16px;
            }
        """)

        self.rgba_invalid_input_label = QLabel("Invalid Input")
        self.rgba_invalid_input_label.setWordWrap(True)
        self.rgba_invalid_input_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.rgba_invalid_input_label.setObjectName("rgba_invalid_input_label")
        self.rgba_invalid_input_label.setStyleSheet("""
            QLabel#rgba_invalid_input_label{
                font-family: "SF Pro Display";
                font-weight: 600;
                font-size: 24px;
                padding: 6px;
                color: black;
                border: none;
                background: transparent;
            }
        """)

        rgba_invalid_input_layout = QVBoxLayout(self.rgba_invalid_input_widget)
        rgba_invalid_input_layout.addWidget(self.rgba_invalid_input_label)
        rgba_invalid_input_layout.setSpacing(0)
        rgba_invalid_input_layout.setContentsMargins(0,0,0,0)

        self.rgba_valid_input_widget.setMaximumHeight(50)
        self.rgba_invalid_input_widget.setMaximumHeight(50)

        self.rgba_valid_input_widget.hide()
        self.rgba_invalid_input_widget.hide()
    
        rgba_color_screen_layout.addWidget(self.r_input)
        rgba_color_screen_layout.addWidget(self.g_input)
        rgba_color_screen_layout.addWidget(self.b_input)
        rgba_color_screen_layout.addWidget(self.a_input)
        rgba_color_screen_layout.addWidget(self.rgba_valid_input_widget)
        rgba_color_screen_layout.addWidget(self.rgba_invalid_input_widget)

        rgba_color_screen_layout.setContentsMargins(10,10,10,10)
        rgba_color_screen_layout.setSpacing(10)
        rgba_color_screen_layout.addStretch()

    def create_grayscale_color_screen(self):
        grayscale_color_screen_layout = QVBoxLayout(self.grayscale_color_screen)

        self.grayscale_input = QLineEdit()
        self.grayscale_input.setObjectName("grayscale")
        self.grayscale_input.setPlaceholderText("Grayscale:")
        self.grayscale_input.setStyleSheet("""
            QLineEdit#grayscale{
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
        self.grayscale_input.setMinimumHeight(60)

        self.grayscale_input.textChanged.connect(self.change_grayscale_color)

        self.grayscale_valid_input_widget = QWidget()
        self.grayscale_valid_input_widget.setObjectName("grayscale_valid_input")
        self.grayscale_valid_input_widget.setStyleSheet("""
            QWidget#grayscale_valid_input{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(94, 255, 234, 1),   
                    stop:0.3 rgba(63, 252, 180, 1), 
                    stop:0.6 rgba(150, 220, 255, 1)
                    stop:1 rgba(180, 200, 255, 1)  
                );
                border: 2px solid black;
                border-radius: 16px;
            }
        """)

        self.grayscale_valid_input_label = QLabel("Valid Input")
        self.grayscale_valid_input_label.setWordWrap(True)
        self.grayscale_valid_input_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.grayscale_valid_input_label.setObjectName("grayscale_valid_input_label")
        self.grayscale_valid_input_label.setStyleSheet("""
            QLabel#grayscale_valid_input_label{
                font-family: "SF Pro Display";
                font-weight: 600;
                font-size: 24px;
                padding: 6px;
                color: black;
                border: none;
                background: transparent;
            }
        """)

        grayscale_valid_input_layout = QVBoxLayout(self.grayscale_valid_input_widget)
        grayscale_valid_input_layout.addWidget(self.grayscale_valid_input_label)
        grayscale_valid_input_layout.setSpacing(0)
        grayscale_valid_input_layout.setContentsMargins(0,0,0,0)

        self.grayscale_invalid_input_widget = QWidget()
        self.grayscale_invalid_input_widget.setObjectName("grayscale_invalid_input")
        self.grayscale_invalid_input_widget.setStyleSheet("""
            QWidget#grayscale_invalid_input{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(255, 100, 100, 1),   
                    stop:0.4 rgba(255, 130, 120, 1), 
                    stop:0.7 rgba(200, 90, 150, 1), 
                    stop:1 rgba(180, 60, 140, 1)     
                );
                border: 2px solid black;
                border-radius: 16px;
            }
        """)

        self.grayscale_invalid_input_label = QLabel("Invalid Input")
        self.grayscale_invalid_input_label.setWordWrap(True)
        self.grayscale_invalid_input_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.grayscale_invalid_input_label.setObjectName("grayscale_invalid_input_label")
        self.grayscale_invalid_input_label.setStyleSheet("""
            QLabel#grayscale_invalid_input_label{
                font-family: "SF Pro Display";
                font-weight: 600;
                font-size: 24px;
                padding: 6px;
                color: black;
                border: none;
                background: transparent;
            }
        """)

        grayscale_invalid_input_layout = QVBoxLayout(self.grayscale_invalid_input_widget)
        grayscale_invalid_input_layout.addWidget(self.grayscale_invalid_input_label)
        grayscale_invalid_input_layout.setSpacing(0)
        grayscale_invalid_input_layout.setContentsMargins(0,0,0,0)

        self.grayscale_valid_input_widget.setMaximumHeight(50)
        self.grayscale_invalid_input_widget.setMaximumHeight(50)

        self.grayscale_valid_input_widget.hide()
        self.grayscale_invalid_input_widget.hide()

        grayscale_color_screen_layout.addWidget(self.grayscale_input)
        grayscale_color_screen_layout.addWidget(self.grayscale_valid_input_widget)
        grayscale_color_screen_layout.addWidget(self.grayscale_invalid_input_widget)
        grayscale_color_screen_layout.setContentsMargins(10,10,10,10)
        grayscale_color_screen_layout.setSpacing(10)
        grayscale_color_screen_layout.addStretch()

    def create_short_code_color_screen(self):
        short_code_color_screen_layout = QVBoxLayout(self.short_code_color_screen)
    
        self.short_code_color_list_view = QListView()
        self.short_code_color_model = QStringListModel(self.short_code_colors)
        self.short_code_color_list_view.setModel(self.short_code_color_model)
        class CustomDelegate(QStyledItemDelegate):
            def paint(self, painter, option, index):
                option.displayAlignment = Qt.AlignmentFlag.AlignCenter
                font = QFont("SF Pro Display", 24)
                font.setWeight(600)
                option.font = font
                super().paint(painter, option, index)
        
        self.short_code_color_list_view.setItemDelegate(CustomDelegate())

        self.short_code_color_list_view.setObjectName("short_code_color_list_view")
        self.short_code_color_list_view.setStyleSheet("""
            QListView#short_code_color_list_view{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #f5f5ff,
                    stop:0.5 #f7f5fc,
                    stop:1 #f0f0ff
                );
                border: transparent;
                border-radius: 24px;
            }
            QListView#short_code_color_list_view::item {
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
                color: black;
                min-height: 41px;
            }
            QListView#short_code_color_list_view::item:selected {
                background: qlineargradient(
                    x1:0, y1:0,
                    x2:1, y2:0,
                    stop:0 rgba(94, 255, 234, 1),
                    stop:0.5 rgba(171, 156, 255, 1),
                    stop:1 rgba(255, 203, 255, 1)
                );
                border: 2px solid black;
                border-radius: 16px;
                color: black;
                min-height: 41px;
            }
            QListView#short_code_color_list_view::item:hover {
                background: qlineargradient(
                    x1:0, y1:0,
                    x2:1, y2:0,
                    stop:0 rgba(94, 255, 234, 1),
                    stop:0.5 rgba(171, 156, 255, 1),
                    stop:1 rgba(255, 203, 255, 1)
                );
                border: 2px solid black;
                border-radius: 16px;
                color: black;
                min-height: 41px;
            }
        """)
        self.short_code_color_list_view.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.short_code_color_list_view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.short_code_color_list_view.setSpacing(3)

        self.short_code_color_list_view.clicked.connect(self.change_short_code_color)

        short_code_color_screen_layout.addWidget(self.short_code_color_list_view)

        # Add margins and spacing to make it look good and push content to the top
        short_code_color_screen_layout.setContentsMargins(10, 10, 10, 10)

    def change_to_original_screen(self):
        self.available_screens[self.current_screen_idx].hide()
        self.current_screen_idx = 0
        self.edge_color_adjustment_homescreen.show()

    def change_to_named_color_screen(self):
        self.available_screens[self.current_screen_idx].hide()
        self.previous_screen_idx = self.current_screen_idx
        self.current_screen_idx = 1
        self.named_color_screen.show()

    def change_to_hex_code_screen(self):
        self.available_screens[self.current_screen_idx].hide()
        self.previous_screen_idx = self.current_screen_idx
        self.current_screen_idx = 2
        self.hex_code_color_screen.show()

    def change_to_rgba_color_screen(self):
        self.available_screens[self.current_screen_idx].hide()
        self.previous_screen_idx = self.current_screen_idx
        self.current_screen_idx = 3
        self.rgba_color_screen.show()

    def change_to_grayscale_colors_screen(self):
        self.available_screens[self.current_screen_idx].hide()
        self.previous_screen_idx = self.current_screen_idx
        self.current_screen_idx = 4
        self.grayscale_color_screen.show()

    def change_to_short_code_color_screen(self):
        self.available_screens[self.current_screen_idx].hide()
        self.previous_screen_idx = self.current_screen_idx
        self.current_screen_idx = 5
        self.short_code_color_screen.show()

    def set_color_to_none(self):
        self.current_edge_color = None
        self.update_color()

    def change_named_color(self,index):
        source_index = self.filter_proxy.mapToSource(index)
        self.current_edge_color = self.named_color_model.data(source_index, Qt.ItemDataRole.DisplayRole)
        self.update_color()

    def change_hex_code_color(self):
        hex_code = self.hex_code_input.text().strip()

        if (hex_code == ""):
            self.hex_valid_input_widget.hide()
            self.hex_invalid_input_widget.hide()
            return

        def check_valid_hex_code(hex_code):
            if (hex_code[0] != "#"):
                new_hex_code = "#" + hex_code
                return check_valid_hex_code(new_hex_code)
            hex_code = hex_code[1:]
            if (len(hex_code) not in [3,6,8]):
                return False
            try:
                int(hex_code,16)
                return True
            except:
                return False
        
        if (hex_code != ""):
            validity = check_valid_hex_code(hex_code)
            if (validity):
                self.hex_valid_input_widget.show()
                self.hex_invalid_input_widget.hide()
                self.current_edge_color = hex_code if hex_code[0] == "#" else "#" + hex_code
                self.update_color()
            else:
                self.hex_valid_input_widget.hide()
                self.hex_invalid_input_widget.show()

    def change_rgba_color(self):
        r_value = self.r_input.text().strip()
        g_value = self.g_input.text().strip()
        b_value = self.b_input.text().strip()
        a_value = self.a_input.text().strip()

        if (not(r_value or g_value or b_value or a_value)):
            self.rgba_valid_input_widget.hide()
            self.rgba_invalid_input_widget.hide()
            return 

        valid = None

        try:
            r_value = int(r_value) if r_value != "" else self.initial_rgba[0]
            g_value = int(g_value) if g_value != "" else self.initial_rgba[1]
            b_value = int(b_value) if b_value != "" else self.initial_rgba[2]
            a_value = int(a_value) if a_value != "" else self.initial_rgba[3]
            valid = True
        except:
            valid = False

        if (valid):
            self.initial_rgba[0] = r_value 
            self.initial_rgba[1] = g_value
            self.initial_rgba[2] = b_value 
            self.initial_rgba[3] = a_value

            self.rgba_valid_input_widget.show()
            self.rgba_invalid_input_widget.hide()

            self.current_edge_color = self.initial_rgba

            self.update_color()
        else:
            self.rgba_valid_input_widget.hide()
            self.rgba_invalid_input_widget.show()

    def change_grayscale_color(self):
        grayscale_value = self.grayscale_input.text().strip()

        if (grayscale_value == ""): 
            self.grayscale_valid_input_widget.hide() 
            self.grayscale_invalid_input_widget.hide()
            return

        try: 
            grayscale_value = float(grayscale_value)
            if (0 > grayscale_value or grayscale_value > 1):
                raise Exception
            self.grayscale_valid_input_widget.show()
            self.grayscale_invalid_input_widget.hide()
        except:
            self.grayscale_valid_input_widget.hide()
            self.grayscale_invalid_input_widget.show()

        self.current_edge_color = grayscale_value
        self.update_color()

    def change_short_code_color(self,index):
        self.current_edge_color = self.short_code_color_model.data(index, Qt.ItemDataRole.DisplayRole)
        self.update_color()

    def update_color(self):
        db = self.plot_manager.get_db()
        if (db != []):
            self.plot_manager.update_legend("edgecolor",self.current_edge_color)
        else:
            plot_parameters = plot_json[self.selected_graph].copy()
            plot_parameters["legend"]["edgecolor"] = self.current_edge_color
            self.plot_manager.insert_plot_parameter(plot_parameters)

    def mousePressEvent(self, event):
        if not self.hex_code_input.geometry().contains(event.position().toPoint()):
            self.hex_code_input.clearFocus()
        if not self.r_input.geometry().contains(event.position().toPoint()):
            self.r_input.clearFocus()
        if not self.g_input.geometry().contains(event.position().toPoint()):
            self.g_input.clearFocus()
        if not self.b_input.geometry().contains(event.position().toPoint()):
            self.b_input.clearFocus()
        if not self.a_input.geometry().contains(event.position().toPoint()):
            self.a_input.clearFocus()
        if not self.grayscale_input.geometry().contains(event.position().toPoint()):
            self.grayscale_input.clearFocus()
        super().mousePressEvent(event)

class framealpha_adjustment_section(QWidget):
    def __init__(self,selected_graph):
        super().__init__()
        
        self.plot_manager = PlotManager()
        
        self.selected_graph = selected_graph

        #Create a section to display the loc section and style it
        self.framealpha_adjustment_section = QWidget()
        self.framealpha_adjustment_section.setObjectName("framealpha_adjustment_section")
        self.framealpha_adjustment_section.setStyleSheet("""
            QWidget#framealpha_adjustment_section{
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

        #Initialize the ncol value to be 0
        self.framealpha_value = None

        #Create a line edit object for the user to input the ncol
        self.framealpha_input = QLineEdit()
        self.framealpha_input.setPlaceholderText("framealpha: ")

        #Set the height of the line edit object to make it look good
        self.framealpha_input.setFixedHeight(60)

        #Connect any changes with the text to an update function
        self.framealpha_input.textChanged.connect(self.change_framealpha)

        #Create two widget to display valid and invalid inputs
        self.valid_input_widget = QWidget()
        self.valid_input_widget.setObjectName("valid_input")
        self.valid_input_widget.setStyleSheet("""
            QWidget#valid_input{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(94, 255, 234, 1),   
                    stop:0.3 rgba(63, 252, 180, 1), 
                    stop:0.6 rgba(150, 220, 255, 1)
                    stop:1 rgba(180, 200, 255, 1)  
                );
                border: 2px solid black;
                border-radius: 16px;
            }
        """)

        self.valid_input_label = QLabel("Valid Input")
        self.valid_input_label.setWordWrap(True)
        self.valid_input_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.valid_input_label.setObjectName("valid_input_label")
        self.valid_input_label.setStyleSheet("""
            QLabel#valid_input_label{
                font-family: "SF Pro Display";
                font-weight: 600;
                font-size: 24px;
                padding: 6px;
                color: black;
                border: none;
                background: transparent;
            }
        """)

        valid_input_layout = QVBoxLayout(self.valid_input_widget)
        valid_input_layout.addWidget(self.valid_input_label)
        valid_input_layout.setSpacing(0)
        valid_input_layout.setContentsMargins(0,0,0,0)

        self.invalid_input_widget = QWidget()
        self.invalid_input_widget.setObjectName("invalid_input")
        self.invalid_input_widget.setStyleSheet("""
            QWidget#invalid_input{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(255, 100, 100, 1),   
                    stop:0.4 rgba(255, 130, 120, 1), 
                    stop:0.7 rgba(200, 90, 150, 1), 
                    stop:1 rgba(180, 60, 140, 1)     
                );
                border: 2px solid black;
                border-radius: 16px;
            }
        """)

        self.invalid_input_label = QLabel("Invalid Input")
        self.invalid_input_label.setWordWrap(True)
        self.invalid_input_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.invalid_input_label.setObjectName("invalid_input_label")
        self.invalid_input_label.setStyleSheet("""
            QLabel#invalid_input_label{
                font-family: "SF Pro Display";
                font-weight: 600;
                font-size: 24px;
                padding: 6px;
                color: black;
                border: none;
                background: transparent;
            }
        """)

        invalid_input_layout = QVBoxLayout(self.invalid_input_widget)
        invalid_input_layout.addWidget(self.invalid_input_label)
        invalid_input_layout.setSpacing(0)
        invalid_input_layout.setContentsMargins(0,0,0,0)

        self.valid_input_widget.setMaximumHeight(50)
        self.invalid_input_widget.setMaximumHeight(50)

        self.valid_input_widget.hide()
        self.invalid_input_widget.hide()

        #Create a layout for the ncol adjustment section and add the line edit object to it
        framealpha_section_layout = QVBoxLayout(self.framealpha_adjustment_section)
        framealpha_section_layout.addWidget(self.framealpha_input)
        framealpha_section_layout.addWidget(self.valid_input_widget)
        framealpha_section_layout.addWidget(self.invalid_input_widget)
    
        #Add the margins, spacing, and stretch to the layout to make it look good
        framealpha_section_layout.setContentsMargins(10,10,10,10)
        framealpha_section_layout.setSpacing(10)
        framealpha_section_layout.addStretch()

        #Add the ncol adjustment section to the main widget
        main_layout = QVBoxLayout(self)
        main_layout.addWidget(self.framealpha_adjustment_section)
        
        #Set both the spacing and margins for the main widget to make sure it fits nicely
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0,0,0,0)

        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
    
    def change_framealpha(self):
        #Extract the ncol input from the user and remove any excess text from it
        framealpha_input = self.framealpha_input.text().strip()

        if (framealpha_input == ""):
            self.valid_input_widget.hide()
            self.invalid_input_widget.hide()
            self.framealpha_value = None
            return

        #Only update the ncol value in the json file if the input is valid
        try:
            framealpha_input = float(framealpha_input)
            if (0 > framealpha_input or framealpha_input > 1):
                raise Exception
            self.valid_input_widget.show()
            self.invalid_input_widget.hide()
        except:
            self.valid_input_widget.hide()
            self.invalid_input_widget.show()
        else:
            self.framealpha_value = framealpha_input
            self.update_framealpha()

    def update_framealpha(self):
        db = self.plot_manager.get_db()
        if (db != []):
            self.plot_manager.update_legend("framealpha",self.framealpha_value)
        else:
            plot_parameters = plot_json[self.selected_graph].copy()
            plot_parameters["legend"]["framealpha"] = self.framealpha_value
            self.plot_manager.insert_plot_parameter(plot_parameters)

    def mousePressEvent(self, event):
        if not self.framealpha_input.geometry().contains(event.position().toPoint()):
            self.framealpha_input.clearFocus()
        super().mousePressEvent(event)

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
        self.layout.addWidget(loc_adjustment_section(self.selected_graph),stretch=1)

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
        if (self.buttons[self.idx].objectName() == "selected"):
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
            self.initial_grid_state = not self.initial_grid_state
            self.plot_manager.update_legend("grid",self.initial_grid_state)
        else:
            plot_parameter = plot_json[self.selected_graph].copy()
            plot_parameter["grid"] = self.initial_grid_state
            self.plot_manager.insert_plot_parameter(plot_parameter) 