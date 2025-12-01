from PyQt6.QtCore import QSortFilterProxyModel, QStringListModel, Qt
from PyQt6.QtGui import QFont, QKeySequence, QShortcut, QStandardItem, QStandardItemModel
from PyQt6.QtWidgets import (
    QAbstractItemView, QDialog, QHBoxLayout, QHeaderView, QLabel, QLineEdit, QListView, QListWidget, QListWidgetItem, QPushButton, 
    QSizePolicy, QTableView, QWidget, QVBoxLayout, QStyledItemDelegate, QSizePolicy
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
        "data":"./dataset/user_dataset.csv",
        "x":None,
        "y":None,
        "axis-title":{
            "x-axis-title":"",
            "y-axis-title":"",
        },
        "title":None,
        "legend":{
            "visible":False,
            "label":"__nolegend__",
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
            "labelcolor":"k",
            "alignment":"center",
            "columnspacing":2.0,
            "handletextpad":0.8,
            "borderaxespad":0.5,
            "handlelength":2.0,
            "handleheight":0.7,
            "markerfirst":True,
            "seaborn_legends":{
                "legend":"brief",
                "legend_out":False,
                "markers":True,
                "dashes":True,
                "size_order":None,
                "hue_order":None,
                "style_order":None,
            }
        },
        "grid":{
            "visible":None,
            "which":"major",
            "axis":"both",
            "color":"black",
            "linestyle":"-",
            "linewidth":0.8,
            "alpha":None,
            "zorder":2,
            "dashes":[None,None],
            "snap":None
        },
        "hue":[None,{True:"True",False:"False"}],
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
    def __init__(self,plot_parameters,selected_graph,graph_display):
        super().__init__()

        self.plot_manager = PlotManager()

        self.plot_parameters = plot_parameters
        self.selected_graph = selected_graph
        self.graph_display = graph_display

        #Keep track of the current column and index
        self.column_name = ''
        self.current_column_index = 0
        self.get_dataset()
        self.usable_columns = self.find_usable_columns()
        
        #Set the title of the window
        self.setWindowTitle("Select the x-axis")
        
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
                border-radius: 16px;
            }
        """)
        self.create_button_section()
        self.update_x_axis()

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
                border-radius: 16px;
            }
        """)

        #Create a QTableView instance to display the dataset
        self.dataset_table = QTableView()
        self.dataset_table.setObjectName("dataset_table")
        header = self.dataset_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.dataset_table.setStyleSheet("""
            QTableView#dataset_table {
                border-radius: 16px;
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

        #Place the dataset table on top of the dataset section
        layout = QVBoxLayout(self.data_section)
        layout.addWidget(self.dataset_table)
        layout.setContentsMargins(0,0,0,0)
        layout.setSpacing(0)

        #Allow the dataset to take up all the space
        self.dataset_table.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        #Place the buttons and the dataset next to each other side by side
        self.layout = QHBoxLayout(self)
        self.layout.addWidget(self.button_section,stretch=1)
        self.layout.addSpacing(10)
        self.layout.addWidget(self.data_section,stretch=1)

        #Create a shortcut for the user to go to the previous column by press up
        up_shortcut = QShortcut(QKeySequence("up"), self) 
        up_shortcut.activated.connect(self.columns_go_up)  

        #Create a shortcut for the user to go to the next column by press down
        down_shortcut = QShortcut(QKeySequence("down"), self) 
        down_shortcut.activated.connect(self.columns_go_down)

        return_shortcut = QShortcut(QKeySequence("Return"),self)
        return_shortcut.activated.connect(self.exit_dialog)

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

    def create_button_section(self):  
        column_button_layout = QVBoxLayout(self.button_section)
    
        self.column_button_list_view = QListView()
        self.column_button_model = QStringListModel(self.usable_columns)

        self.column_button_list_view.setModel(self.column_button_model)
        self.column_button_list_view.setObjectName("column_button_list_view")
        self.column_button_list_view.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)

        column_index = self.column_button_model.index(self.current_column_index)  
        self.column_button_list_view.setCurrentIndex(column_index)

        class CustomDelegate(QStyledItemDelegate):
            def paint(self, painter, option, index):
                option.displayAlignment = Qt.AlignmentFlag.AlignCenter
                font = QFont("SF Pro Display", 24)
                font.setWeight(600)
                option.font = font
                super().paint(painter, option, index)
        
        self.column_button_list_view.setItemDelegate(CustomDelegate())

        self.column_button_list_view.setStyleSheet("""
            QListView#column_button_list_view{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #f5f5ff,
                    stop:0.5 #f7f5fc,
                    stop:1 #f0f0ff
                );
                border: transparent;
                border-radius: 16px;
            }
            QListView#column_button_list_view::item {
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
            QListView#column_button_list_view::item:selected {
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
            QListView#column_button_list_view::item:hover {
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

        self.column_button_list_view.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.column_button_list_view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.column_button_list_view.setSpacing(3)

        self.column_button_list_view.clicked.connect(self.change_current_column)

        column_button_layout.addWidget(self.column_button_list_view)

        # Add margins and spacing to make it look good and push content to the top
        column_button_layout.setContentsMargins(10, 10, 10, 10)

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

    def change_current_column(self,index):
        self.column_name = self.column_button_model.data(index, Qt.ItemDataRole.DisplayRole)
        self.current_column_index = index.row()
        self.display_dataset()
        self.update_x_axis()

    def columns_go_down(self):
        self.current_column_index += 1
        self.current_column_index %= len(self.usable_columns)
        new_screen_index = self.column_button_model.index(self.current_column_index)
        self.column_button_list_view.setCurrentIndex(new_screen_index)
        self.column_button_list_view.scrollTo(new_screen_index,QAbstractItemView.ScrollHint.PositionAtCenter)
        self.column_name = self.usable_columns[self.current_column_index]
        self.display_dataset()
        self.update_x_axis()

    def columns_go_up(self):
        self.current_column_index -= 1
        self.current_column_index %= len(self.usable_columns)
        new_screen_index = self.column_button_model.index(self.current_column_index)
        self.column_button_list_view.setCurrentIndex(new_screen_index)
        self.column_button_list_view.scrollTo(new_screen_index,QAbstractItemView.ScrollHint.PositionAtCenter)
        self.column_name = self.usable_columns[self.current_column_index]
        self.display_dataset()
        self.update_x_axis()

    def update_x_axis(self):
        db = self.plot_manager.get_db()
        if (db != []):
            plot_parameters = db.copy()
            plot_parameters["x"] = self.column_name
        else:
            plot_parameters = plot_json[self.selected_graph].copy()
            plot_parameters["x"] = self.column_name
        self.plot_manager.insert_x_axis_data(plot_parameters)
        self.graph_display.show_graph()

    def exit_dialog(self):
        self.close()

    def showEvent(self, event):
        super().showEvent(event)
        self.get_dataset()
        self.usable_columns = self.find_usable_columns()
        self.current_column_index = 0

        if self.usable_columns:
            self.display_dataset()

            self.column_button_model.setStringList(self.usable_columns)
            column_index = self.column_button_model.index(self.current_column_index)  
            self.column_button_list_view.setCurrentIndex(column_index)

        self.update_x_axis()
        
class y_axis_button(QDialog):
    def __init__(self,plot_parameters,selected_graph,graph_display):
        super().__init__()

        self.plot_manager = PlotManager()

        self.plot_parameters = plot_parameters
        self.selected_graph = selected_graph
        self.graph_display = graph_display
        
        #Set the title of the window
        self.setWindowTitle("Select the y-axis")

        #Keep track of the current column and index
        self.column_name = ''
        self.current_column_index = 0
        self.get_dataset()
        self.usable_columns = self.find_usable_columns()
        
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
                border-radius: 16px;
            }
        """)
        self.create_button_section()
        self.update_y_axis()

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
                border-radius: 16px;
            }
        """)

        #Create a QTableView instance to display the dataset
        self.dataset_table = QTableView()
        self.dataset_table.setObjectName("dataset_table")
        header = self.dataset_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.dataset_table.setStyleSheet("""
            QTableView#dataset_table {
                border-radius: 16px;
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

        self.display_dataset()

        #Place the dataset table on top of the dataset section
        layout = QVBoxLayout(self.data_section)
        layout.addWidget(self.dataset_table)
        layout.setContentsMargins(0,0,0,0)
        layout.setSpacing(0)

        #Allow the dataset to take up all the space
        self.dataset_table.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        #Place the buttons and the dataset next to each other side by side
        self.layout = QHBoxLayout(self)
        self.layout.addWidget(self.button_section,stretch=1)
        self.layout.addSpacing(10)
        self.layout.addWidget(self.data_section,stretch=1)

        #Create a shortcut for the user to go to the previous column by press up
        up_shortcut = QShortcut(QKeySequence("up"), self) 
        up_shortcut.activated.connect(self.columns_go_up)  

        #Create a shortcut for the user to go to the next column by press down
        down_shortcut = QShortcut(QKeySequence("down"), self) 
        down_shortcut.activated.connect(self.columns_go_down)

        return_shortcut = QShortcut(QKeySequence("Return"),self)
        return_shortcut.activated.connect(self.exit_dialog)

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

    def create_button_section(self):  
        column_button_layout = QVBoxLayout(self.button_section)

        self.column_button_list_view = QListView()
        self.column_button_model = QStringListModel(self.usable_columns)

        self.column_button_list_view.setModel(self.column_button_model)
        self.column_button_list_view.setObjectName("column_button_list_view")
        self.column_button_list_view.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)

        column_index = self.column_button_model.index(self.current_column_index)  
        self.column_button_list_view.setCurrentIndex(column_index)

        class CustomDelegate(QStyledItemDelegate):
            def paint(self, painter, option, index):
                option.displayAlignment = Qt.AlignmentFlag.AlignCenter
                font = QFont("SF Pro Display", 24)
                font.setWeight(600)
                option.font = font
                super().paint(painter, option, index)
        
        self.column_button_list_view.setItemDelegate(CustomDelegate())

        self.column_button_list_view.setStyleSheet("""
            QListView#column_button_list_view{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #f5f5ff,
                    stop:0.5 #f7f5fc,
                    stop:1 #f0f0ff
                );
                border: transparent;
                border-radius: 16px;
            }
            QListView#column_button_list_view::item {
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
            QListView#column_button_list_view::item:selected {
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
            QListView#column_button_list_view::item:hover {
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

        self.column_button_list_view.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.column_button_list_view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.column_button_list_view.setSpacing(3)

        self.column_button_list_view.clicked.connect(self.change_current_column)

        column_button_layout.addWidget(self.column_button_list_view)

        # Add margins and spacing to make it look good and push content to the top
        column_button_layout.setContentsMargins(10, 10, 10, 10)

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

    def change_current_column(self,index):
        self.column_name = self.column_button_model.data(index, Qt.ItemDataRole.DisplayRole)
        self.current_column_index = index.row()
        self.display_dataset()
        self.update_y_axis()

    def columns_go_down(self):
        self.current_column_index += 1
        self.current_column_index %= len(self.usable_columns)
        new_screen_index = self.column_button_model.index(self.current_column_index)
        self.column_button_list_view.setCurrentIndex(new_screen_index)
        self.column_button_list_view.scrollTo(new_screen_index,QAbstractItemView.ScrollHint.PositionAtCenter)
        self.column_name = self.usable_columns[self.current_column_index]
        self.display_dataset()
        self.update_y_axis()

    def columns_go_up(self):
        self.current_column_index -= 1
        self.current_column_index %= len(self.usable_columns)
        new_screen_index = self.column_button_model.index(self.current_column_index)
        self.column_button_list_view.setCurrentIndex(new_screen_index)
        self.column_button_list_view.scrollTo(new_screen_index,QAbstractItemView.ScrollHint.PositionAtCenter)
        self.column_name = self.usable_columns[self.current_column_index]
        self.display_dataset()
        self.update_y_axis()

    def update_y_axis(self):
        db = self.plot_manager.get_db()
        if (db != []):
            plot_parameters = db.copy()
            plot_parameters["y"] = self.column_name
        else:
            plot_parameters = plot_json[self.selected_graph].copy()
            plot_parameters["y"] = self.column_name
        self.plot_manager.insert_y_axis_data(plot_parameters)
        self.graph_display.show_graph()

    def exit_dialog(self):
        self.close()

    def showEvent(self, event):
        super().showEvent(event)
        self.get_dataset()
        self.usable_columns = self.find_usable_columns()

        if self.usable_columns:
            self.column_name = self.usable_columns[0]
            self.current_column_index = 0
            self.display_dataset()

            self.column_button_model.setStringList(self.usable_columns)
            column_index = self.column_button_model.index(self.current_column_index)  
            self.column_button_list_view.setCurrentIndex(column_index)

class axis_title_button(QDialog):
    def __init__(self,selected_graph,graph_display):
        super().__init__()

        self.plot_manager = PlotManager()
        self.selected_graph = selected_graph
        self.graph_display = graph_display
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
                border-radius: 16px;
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
                border-radius: 16px;
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
            if ((db["axis-title"]["x-axis-title"] == "" and db["axis-title"]["y-axis-title"] == "") or not self.axis_title_created):
                db["axis-title"]["x-axis-title"] = x_axis_title
                self.axis_title_created = True
                self.plot_manager.insert_plot_parameter(db)
            else:
                self.plot_manager.update_x_axis_title(x_axis_title)
        else:
            plot_parameter = plot_json[self.selected_graph].copy()
            plot_parameter["axis title"]["x-axis-title"] = x_axis_title
            self.axis_title_created = not self.axis_title_created
            self.plot_manager.insert_plot_parameter(plot_parameter)
        self.graph_display.show_graph()

    def y_axis_update_text(self):
        y_axis_title = self.y_axis_title_section.text().strip()
        db = self.plot_manager.get_db()
        if (db != []):
            if ((db["axis-title"]["x-axis-title"] == "" and db["axis-title"]["y-axis-title"] == "") or not self.axis_title_created):
                db["axis-title"]["y-axis-title"] = y_axis_title
                self.plot_manager.insert_plot_parameter(db)
                self.axis_title_created = True
            else:
                self.plot_manager.update_y_axis_title(y_axis_title)
        else:
            plot_parameter = plot_json[self.selected_graph].copy()
            plot_parameter["axis title"]["y-axis-title"] = y_axis_title
            self.plot_manager.insert_plot_parameter(plot_parameter)
            self.axis_title_created = True
        self.graph_display.show_graph()

    def close_application(self):
        self.axis_title_created = False
        self.close()

class title_button(QDialog):
    def __init__(self,selected_graph,graph_display):
        super().__init__()

        self.plot_manager = PlotManager()
        self.selected_graph = selected_graph
        self.title_created = False

        self.graph_display = graph_display

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
                border-radius: 16px;
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
        self.graph_display.show_graph()

    def close_application(self):
        self.title_created = False
        self.close()

class legend_visible_adjustment_section(QWidget):
    def __init__(self,selected_graph,graph_display):
        super().__init__()
        
        self.selected_graph = selected_graph
        self.graph_display = graph_display
        self.plot_manager = PlotManager()

        self.legend_visible_state = False

        #Create a widget to display the grid visibility adjustment section and style it for consistency
        self.legend_visibility_adjustment_section = QWidget()
        self.legend_visibility_adjustment_section.setObjectName("legend_visibility_adjustment_section")
        self.legend_visibility_adjustment_section.setStyleSheet("""
            QWidget#legend_visibility_adjustment_section{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #f5f5ff,
                    stop:0.5 #f7f5fc,
                    stop:1 #f0f0ff
                );
                border: 2px solid black;
                border-radius: 16px;
            }
        """)

        #Create a label to put on top of the QPushButton
        self.legend_visibility_label = QLabel("Legend On")
        self.legend_visibility_label.setWordWrap(True)
        self.legend_visibility_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.legend_visibility_label.setObjectName("legend_visibility_label")
        self.legend_visibility_label.setStyleSheet("""
            QLabel#legend_visibility_label{
                font-family: "SF Pro Display";
                font-weight: 600;
                font-size: 24px;
                padding: 6px;
                color: black;
                border: none;
                background: transparent;
            }
        """)
        self.legend_visibility_label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
    
        #Create a button to allow the user to switch grid visibility
        self.legend_visibility_button = QPushButton()
        self.legend_visibility_button.setObjectName("legend_visibility_button")
        self.legend_visibility_button.setStyleSheet("""
            QPushButton#legend_visibility_button{
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
                font-size: 16px;
                padding: 6px;
                color: black;
            }
            QPushButton#legend_visibility_button:hover{
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
        self.legend_visibility_button.setMinimumHeight(50)
        
        #Put the label on top of the button we created for control grid visibility
        legend_visibility_button_layout = QVBoxLayout(self.legend_visibility_button)
        legend_visibility_button_layout.addWidget(self.legend_visibility_label)
        legend_visibility_button_layout.setContentsMargins(0,0,0,0)
        legend_visibility_button_layout.setSpacing(0)

        #Connect the grid visibility button to a function to switch between the two states
        self.legend_visibility_button.clicked.connect(self.switch_legend_visibility)

        #Create a button layout for the grid visibility adjustment section
        button_layout = QVBoxLayout(self.legend_visibility_adjustment_section)

        #Add the grid visibility button to the layout
        button_layout.addWidget(self.legend_visibility_button)

        #Set the spacing, margins, and stretch to make it look good
        button_layout.setContentsMargins(10,10,10,10)
        button_layout.addStretch()

        #Create a layout for the main widget and store the frameon adjustment section in
        main_layout = QVBoxLayout(self)
        main_layout.addWidget(self.legend_visibility_adjustment_section)

        #Add the spacing and margins to make sure that the section fits nicely
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0,0,0,0)

        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

    def switch_legend_visibility(self):
        self.legend_visible_state = not self.legend_visible_state
        if (self.legend_visible_state == False):
            self.legend_visibility_label.setText("Legend On")
        else:
            self.legend_visibility_label.setText("Legend Off")

        self.update_legend_visibility()

    def update_legend_visibility(self):
        db = self.plot_manager.get_db()
        if (db != []):
            self.plot_manager.update_legend("visible",self.legend_visible_state)
        else:
            plot_parameters = plot_json[self.selected_graph].copy()
            plot_parameters["legend"]["visible"] = self.legend_visible_state
            self.plot_manager.insert_plot_parameter(plot_parameters)
        self.graph_display.show_graph()

class legend_label_adjustment_section(QWidget):
    def __init__(self,selected_graph,graph_display):
        super().__init__()
        
        self.plot_manager = PlotManager()
        
        self.selected_graph = selected_graph
        self.graph_display = graph_display

        #Create a section to display the ncol section and style it
        self.legend_label_adjustment_section = QWidget()
        self.legend_label_adjustment_section.setObjectName("legend_label_adjustment_section")
        self.legend_label_adjustment_section.setStyleSheet("""
            QWidget#legend_label_adjustment_section{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #f5f5ff,
                    stop:0.5 #f7f5fc,
                    stop:1 #f0f0ff
                );
                border: 2px solid black;
                border-radius: 16px;
            }
        """)

        #Initialize the ncol value to be 0
        self.label_value = "__nolegend__"

        #Create a line edit object for the user to input the ncol
        self.label_input = QLineEdit()
        self.label_input.setObjectName("label_input")
        self.label_input.setStyleSheet("""
            QLineEdit#label_input{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #f5f5ff,
                    stop:0.5 #f7f5fc,
                    stop:1 #f0f0ff
                );
                color: black;
                font-size: 24pt;
                border: 2px solid black;
                border-radius: 16px;
            }
        """)
        self.label_input.setPlaceholderText("Label: ")

        #Set the height of the line edit object to make it look good
        self.label_input.setFixedHeight(60)

        #Connect any changes with the text to an update function
        self.label_input.textChanged.connect(self.change_label)

        #Create a layout for the label adjustment section and add the line edit object to it
        legend_label_section_layout = QVBoxLayout(self.legend_label_adjustment_section)
        legend_label_section_layout.addWidget(self.label_input)
    
        #Add the margins, spacing, and stretch to the layout to make it look good
        legend_label_section_layout.setContentsMargins(10,10,10,10)
        legend_label_section_layout.setSpacing(10)
        legend_label_section_layout.addStretch()

        #Add the label adjustment section to the main widget
        main_layout = QVBoxLayout(self)
        main_layout.addWidget(self.legend_label_adjustment_section)
        
        #Set both the spacing and margins for the main widget to make sure it fits nicely
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0,0,0,0)

        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
    
    def change_label(self):
        #Extract the ncol input from the user and remove any excess text from it
        self.label_value = self.label_input.text().strip()
        if (self.label_value == ""):
            self.label_value = "__nolegend__"
        self.update_label()

    def update_label(self):
        #Get the newest json entries from the plot manager
        db = self.plot_manager.get_db()

        #Check if db is empty or not. If it is empty then create a new entry with the ncol value
        #If the db isn't empty then update the db with the new ncol value.
        if (db != []):
            self.plot_manager.update_legend("label",self.label_value)
        else:
            plot_parameters = plot_json[self.selected_graph].copy()
            plot_parameters["legend"]["label"] = self.label_value
            self.plot_manager.insert_plot_parameter(plot_parameters)
        self.graph_display.show_graph()

    def mousePressEvent(self, event):
        if not self.label_input.geometry().contains(event.position().toPoint()):
            self.label_input.clearFocus()
        super().mousePressEvent(event)

class legend_loc_adjustment_section(QWidget):
    def __init__(self,selected_graph,graph_display):
        super().__init__()

        self.plot_manager = PlotManager()

        self.selected_graph = selected_graph
        self.graph_display = graph_display

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
                border-radius: 16px;
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
                border-radius: 16px;
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
        self.loc_list_view.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)

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
                border-radius: 16px;
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
        self.graph_display.show_graph()

    def mousePressEvent(self, event):
        if not self.loc_search_bar.geometry().contains(event.position().toPoint()):
            self.loc_search_bar.clearFocus()
        super().mousePressEvent(event)

class legend_bbox_to_anchor_adjustment_section(QWidget):
    def __init__(self,selected_graph,graph_display):
        super().__init__()
        
        self.plot_manager = PlotManager()
        
        self.selected_graph = selected_graph
        self.graph_display = graph_display

        #Create a section to display the bbox section and style it
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
                border-radius: 16px;
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
                border-radius: 16px;
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

        if (x_input == ""):
            self.valid_input_widget.hide()
            self.invalid_input_widget.hide()
            self.x_value = ""
            self.update_bbox_anchor()
            return

        #Check if the input is valid and only update if it's valid
        try:
            self.x_value = float(x_input)
            self.valid_input_label.setText("Valid X")
            self.valid_input_widget.show()
            self.invalid_input_widget.hide()
        except:
            self.invalid_input_label.setText("Invalid X")
            self.valid_input_widget.hide()
            self.invalid_input_widget.show()
        else:
            self.update_bbox_anchor()
        
    def update_y(self):
        #Get the text input of y from the user and remove any excess spaces
        y_input = self.y_input.text().strip()

        if (y_input == ""):
            self.valid_input_widget.hide()
            self.invalid_input_widget.hide()
            self.y_value = ""
            self.update_bbox_anchor()
            return

        #Check if the input is valid and only update if it's valid
        try:
            self.y_value = float(y_input)
            self.valid_input_label.setText("Valid Y")
            self.valid_input_widget.show()
            self.invalid_input_widget.hide()
        except:
            self.invalid_input_label.setText("Invalid Y")
            self.valid_input_widget.hide()
            self.invalid_input_widget.show()
        else:
            self.update_bbox_anchor()

    def update_width(self):
        #Get the text input of the width from the user and remove any excess spaces
        width_input = self.width_input.text().strip()

        if (width_input == ""):
            self.valid_input_widget.hide()
            self.invalid_input_widget.hide()
            self.width_value = ""
            self.update_bbox_anchor()
            return

        #Check if the input is valid and only update if it's valid
        try:
            self.width_value = float(width_input)
            self.valid_input_label.setText("Valid Width")
            self.valid_input_widget.show()
            self.invalid_input_widget.hide()
        except:
            self.invalid_input_label.setText("Invalid Width")
            self.valid_input_widget.hide()
            self.invalid_input_widget.show()
        else:
            self.update_bbox_anchor()

    def update_height(self):
        #Get the text input of the height input from the user and remove any excess spaces
        height_input = self.height_input.text().strip()

        if (height_input == ""):
            self.valid_input_widget.hide()
            self.invalid_input_widget.hide()
            self.height_value = ""
            self.update_bbox_anchor()
            return
        
        #Check if the input is valid and only update if it's valid
        try:
            self.height_value = float(height_input)
            self.valid_input_label.setText("Valid Height")
            self.valid_input_widget.show()
            self.invalid_input_widget.hide()
        except:
            self.invalid_input_label.setText("Invalid Height")
            self.valid_input_widget.hide()
            self.invalid_input_widget.show()
        else:
            self.update_bbox_anchor()

    def update_bbox_anchor(self):
        #Get the newest json file if it exist
        db = self.plot_manager.get_db()

        #Reset the values that are empty to be the default again
        if (self.x_value or self.y_value or self.width_value or self.height_value):
            if (self.x_value == ""):
                self.x_value = 0
            if (self.y_value == ""):
                self.y_value = 0
            if (self.width_value == ""):
                self.width_value = 1
            if (self.height_value == ""):
                self.height_value = 1
            #Create the new_bbox_anchor with the current x,y,width,height values
            new_bbox_anchor = (self.x_value,self.y_value,self.width_value,self.height_value)
        else:
            new_bbox_anchor = None

        #If the json file is not empty then update it and if it is empty then create one with the new bbox anchor with it.
        if (db != []):
            self.plot_manager.update_legend("bbox_to_anchor",new_bbox_anchor)
        else:
            plot_parameters = plot_json[self.selected_graph].copy()
            plot_parameters["legend"]["bbox_to_anchor"] = new_bbox_anchor
            self.plot_manager.insert_plot_parameter(plot_parameters)
        self.graph_display.show_graph()

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

class legend_ncol_adjustment_section(QWidget):
    def __init__(self,selected_graph,graph_display):
        super().__init__()
        
        self.plot_manager = PlotManager()
        
        self.selected_graph = selected_graph
        self.graph_display = graph_display

        #Create a section to display the ncol section and style it
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
                border-radius: 16px;
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
                border-radius: 16px;
            }
        """)

        #Initialize the ncol value to be 0
        self.ncol_value = 1

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

        if (ncol_input == ""):
            self.valid_input_widget.hide()
            self.invalid_input_widget.hide()
            self.ncol_value = 1
            self.update_ncol()
            return 

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
        self.graph_display.show_graph()

    def mousePressEvent(self, event):
        if not self.ncol_input.geometry().contains(event.position().toPoint()):
            self.ncol_input.clearFocus()
        super().mousePressEvent(event)

class legend_fontsize_adjustment_section(QWidget):
    def __init__(self,selected_graph,graph_display):
        super().__init__()
        
        self.plot_manager = PlotManager()

        self.selected_graph = selected_graph
        self.graph_display = graph_display

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
                border-radius: 16px;
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
                border-radius: 16px;
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
                border-radius: 16px;
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
                border-radius: 16px;
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
        self.fixed_fontsize_list_view.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
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
                border-radius: 16px;
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
            self.update_fontsize()
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
        self.graph_display.show_graph()

    def mousePressEvent(self, event):
        if not self.custom_fontsize_input.geometry().contains(event.position().toPoint()):
            self.custom_fontsize_input.clearFocus()
        super().mousePressEvent(event)

class legend_title_adjustment_section(QWidget):
    def __init__(self,selected_graph,graph_display):
        super().__init__()
        
        self.plot_manager = PlotManager()
        
        self.selected_graph = selected_graph
        self.graph_display = graph_display

        #Create a section to display the legend title section and style it
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
                border-radius: 16px;
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
                border-radius: 16px;
            }
        """)

        #Initialize the value for the title
        self.title_value = None

        #Create a QLineEdit to allow the user to input the title and add a placeholder text to it
        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("title: ")
        
        #Set the height of the object for consistency
        self.title_input.setFixedHeight(60)

        #Connect the object to a function to allow it to update automatically
        self.title_input.textChanged.connect(self.change_title)

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

    def change_title(self):
        #Extract the title from the user input and remove any excess spaces.
        self.title_value = self.title_input.text().strip()

        #Change the title to None if it's an empty string
        if (self.title_value == ""):
            self.title_value = None

        #Update it in the json file
        self.update_title()

    def update_title(self):
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
        self.graph_display.show_graph()

class legend_title_fontsize_adjustment_section(QWidget):
    def __init__(self,selected_graph,graph_display):
        super().__init__()
        
        self.plot_manager = PlotManager()

        self.selected_graph = selected_graph
        self.graph_display = graph_display
        
        #Initialize the fixed fontsizes
        self.fixed_title_fontsizes = ["xx-small", "x-small", "small", "medium", "large", "x-large", "xx-large"]
        
        #Initialize the fontsize to be None in the beginning
        self.current_title_fontsize = None

        #Initialize the current page to be 0 and the index to be 0
        self.current_page = 0

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
                border-radius: 16px;
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

        #Create the Custom Title Fontsize Screen
        self.custom_title_fontsize_screen = QWidget()
        self.custom_title_fontsize_screen.setObjectName("custom_title_fontsize_screen")
        self.custom_title_fontsize_screen.setStyleSheet("""
            QWidget#custom_title_fontsize_screen{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #f5f5ff,
                    stop:0.5 #f7f5fc,
                    stop:1 #f0f0ff
                );
                border: 2px solid black;
                border-radius: 16px;
            }
        """)
        self.create_custom_title_fontsize_screen()
        self.custom_title_fontsize_screen.hide()

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

        #Create the Fixed Title Fontsize Screen
        self.fixed_title_fontsize_screen = QWidget()
        self.fixed_title_fontsize_screen.setObjectName("fixed_title_fontsize_screen")
        self.fixed_title_fontsize_screen.setStyleSheet("""
            QWidget#fixed_title_fontsize_screen{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #f5f5ff,
                    stop:0.5 #f7f5fc,
                    stop:1 #f0f0ff
                );
                border: 2px solid black;
                border-radius: 16px;
            }
        """)
        self.create_fixed_title_fontsize_screen()
        self.fixed_title_fontsize_screen.hide()

        #Store all the available screens in a list
        self.available_screens = [self.title_fontsize_adjustment_section,self.custom_title_fontsize_screen,self.fixed_title_fontsize_screen]

        #Connect the two buttons to a button that will switch to the associated screen either custom or fixed fontsize
        self.custom_title_fontsize_button.clicked.connect(self.change_to_custom_title_fontsize)
        self.fixed_title_fontsize_button.clicked.connect(self.change_to_fixed_title_fontsize)

        #Create a layout for the title fontsize adjustment section
        title_fontsize_layout = QVBoxLayout(self.title_fontsize_adjustment_section)

        #Add all the buttons to the layout which will be added to the title fontsize adjustment section
        title_fontsize_layout.addWidget(self.custom_title_fontsize_button)
        title_fontsize_layout.addWidget(self.fixed_title_fontsize_button)

        #Add the margins, spacing, and stretch to the layout so that the buttons will look good on the widget
        title_fontsize_layout.setContentsMargins(10,10,10,10)
        title_fontsize_layout.setSpacing(5)
        title_fontsize_layout.addStretch()

        #Create a layout for the main wdiget and add the title fontsize adjustment section to it
        main_layout = QVBoxLayout(self)
        main_layout.addWidget(self.title_fontsize_adjustment_section)
        main_layout.addWidget(self.custom_title_fontsize_screen)
        main_layout.addWidget(self.fixed_title_fontsize_screen)

        #Add the spacing and margins to make sure that the section fits nicely to the main widget
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0,0,0,0)

        #Create two shortcuts to allow the user to switch between screens
        go_back_shortcut = QShortcut(QKeySequence("left"), self) 
        go_back_shortcut.activated.connect(self.change_to_original_screen)

        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

    def create_custom_title_fontsize_screen(self):
        custom_title_fontsize_layout = QVBoxLayout(self.custom_title_fontsize_screen)

        #Create a QLineEdit object to allow the user input the custom fontsize
        #Give it a placeholder text to make sure that the user knows what to input and style the button
        self.custom_title_fontsize_input = QLineEdit()
        self.custom_title_fontsize_input.setPlaceholderText("Fontsize:")
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
                border-radius: 16px;
            }
        """)

        #Set the height for the QLineEdit for consistency
        self.custom_title_fontsize_input.setFixedHeight(60) 
        
        #Connect the QLineEdit object with a update to automatically update the user inputs
        self.custom_title_fontsize_input.textChanged.connect(self.change_custom_title_fontsize)

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
        custom_title_fontsize_layout.addWidget(self.custom_title_fontsize_input)
        custom_title_fontsize_layout.addWidget(self.valid_input_widget)
        custom_title_fontsize_layout.addWidget(self.invalid_input_widget)
        custom_title_fontsize_layout.setContentsMargins(10,10,10,10)
        custom_title_fontsize_layout.setSpacing(10)
        custom_title_fontsize_layout.addStretch()

    def create_fixed_title_fontsize_screen(self):
        fixed_title_fontsize_screen_layout = QVBoxLayout(self.fixed_title_fontsize_screen)
    
        self.fixed_title_fontsize_list_view = QListView()
        self.fixed_title_fontsize_model = QStringListModel(self.fixed_title_fontsizes)

        self.fixed_title_fontsize_list_view.setModel(self.fixed_title_fontsize_model)
        self.fixed_title_fontsize_list_view.setObjectName("fixed_title_fontsize_list_view")
        self.fixed_title_fontsize_list_view.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        class CustomDelegate(QStyledItemDelegate):
            def paint(self, painter, option, index):
                option.displayAlignment = Qt.AlignmentFlag.AlignCenter
                font = QFont("SF Pro Display", 24)
                font.setWeight(600)
                option.font = font
                super().paint(painter, option, index)
        
        self.fixed_title_fontsize_list_view.setItemDelegate(CustomDelegate())

        self.fixed_title_fontsize_list_view.setStyleSheet("""
            QListView#fixed_title_fontsize_list_view{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #f5f5ff,
                    stop:0.5 #f7f5fc,
                    stop:1 #f0f0ff
                );
                border: transparent;
                border-radius: 16px;
            }
            QListView#fixed_title_fontsize_list_view::item {
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
            QListView#fixed_title_fontsize_list_view::item:selected {
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
            QListView#fixed_title_fontsize_list_view::item:hover {
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

        self.fixed_title_fontsize_list_view.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.fixed_title_fontsize_list_view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.fixed_title_fontsize_list_view.setSpacing(3)

        self.fixed_title_fontsize_list_view.clicked.connect(self.change_fixed_title_fontsize)

        fixed_title_fontsize_screen_layout.addWidget(self.fixed_title_fontsize_list_view)

        # Add margins and spacing to make it look good and push content to the top
        fixed_title_fontsize_screen_layout.setContentsMargins(10, 10, 10, 10)

    def change_to_original_screen(self):
        self.available_screens[self.current_page].hide()
        self.current_page = 0
        self.title_fontsize_adjustment_section.show()

    def change_to_custom_title_fontsize(self):
        self.available_screens[self.current_page].hide()
        self.current_page = 1
        self.custom_title_fontsize_screen.show()

    def change_to_fixed_title_fontsize(self):
        self.available_screens[self.current_page].hide()
        self.current_page = 2
        self.fixed_title_fontsize_screen.show()

    def change_custom_title_fontsize(self):
        #Extract the fontsize from the user input
        current_title_fontsize_value = self.custom_title_fontsize_input.text().strip()

        if (current_title_fontsize_value == ""):
            self.valid_input_widget.hide()
            self.invalid_input_widget.hide()
            self.current_title_fontsize = None
            self.update_title_fontsize()
            return 

        #Check if the input is valid and only update if it's valid
        try:
            current_title_fontsize_value = int(current_title_fontsize_value)
            if (current_title_fontsize_value <= 0):
                raise Exception
            self.valid_input_widget.show()
            self.invalid_input_widget.hide()
            self.current_title_fontsize = current_title_fontsize_value
            self.update_title_fontsize()
        except:
            self.valid_input_widget.hide()
            self.invalid_input_widget.show()

    def change_fixed_title_fontsize(self,index):
        self.current_title_fontsize = self.fixed_title_fontsize_model.data(index, Qt.ItemDataRole.DisplayRole)
        self.update_title_fontsize()

    def update_title_fontsize(self):
        #Grab the newest entry in the json file
        db = self.plot_manager.get_db()
        #Check if the entry is empty or not and update if not empty and add if empty
        if (db != []):
            self.plot_manager.update_legend("title_fontsize",self.current_title_fontsize)
        else:
            plot_parameters = plot_json[self.selected_graph].copy()
            plot_parameters["legend"]["title_fontsize"] = self.current_title_fontsize
            self.plot_manager.insert_plot_parameter(plot_parameters)
        self.graph_display.show_graph()

    def mousePressEvent(self, event):
        if not self.custom_title_fontsize_input.geometry().contains(event.position().toPoint()):
            self.custom_title_fontsize_input.clearFocus()
        super().mousePressEvent(event)

    def showEvent(self, event):
        super().showEvent(event)
        self.change_to_original_screen()

class legend_frameon_adjustment_section(QWidget):
    def __init__(self,selected_graph,graph_display):
        super().__init__()
        
        self.plot_manager = PlotManager()

        self.selected_graph = selected_graph
        self.graph_display = graph_display
        
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
                border-radius: 16px;
            }
        """)

        #Create a label to put on top of the QPushButton
        self.frameon_label = QLabel("Frameon")
        self.frameon_label.setWordWrap(True)
        self.frameon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.frameon_label.setObjectName("frameon_label")
        self.frameon_label.setStyleSheet("""
            QLabel#frameon_label{
                font-family: "SF Pro Display";
                font-weight: 600;
                font-size: 24px;
                padding: 6px;
                color: black;
                border: none;
                background: transparent;
            }
        """)
        self.frameon_label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
    
        #Create a button to allow the user to switch between Frameon
        self.frameon_button = QPushButton()
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
                font-size: 16px;
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
        self.frameon_button.setMinimumHeight(45)
        
        #Put the label on top of the button we created for control frameon
        frameon_button_layout = QVBoxLayout(self.frameon_button)
        frameon_button_layout.addWidget(self.frameon_label)
        frameon_button_layout.setContentsMargins(0,0,0,0)
        frameon_button_layout.setSpacing(0)

        #Connect the frameon button to a function to switch between the two states
        self.frameon_button.clicked.connect(self.switch_frameon_state)

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

    def switch_frameon_state(self):
        #Change the frameon_state to be the opposite of the current state and update it in the json
        self.frameon_state = not self.frameon_state
        if (self.frameon_state):
            self.frameon_label.setText("Frameon")
        else:
            self.frameon_label.setText("Frameoff")
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
        self.graph_display.show_graph()

class legend_face_color_adjustment_section(QWidget):
    def __init__(self,selected_graph,graph_display):
        super().__init__()

        self.graph_display = graph_display

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
                border-radius: 16px;
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
                border-radius: 16px;
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
                border-radius: 16px;
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
                border-radius: 16px;
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
                border-radius: 16px;
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
                border-radius: 16px;
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
                border-radius: 16px;
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
                border-radius: 16px;
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
                border-radius: 16px;
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
                border-radius: 16px;
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
                border-radius: 16px;
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
                border-radius: 16px;
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
                border-radius: 16px;
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
                border-radius: 16px;
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
        self.short_code_color_list_view.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
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
                border-radius: 16px;
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
            self.current_facecolor = None
            self.update_color()
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
            self.current_facecolor = None
            self.update_color()
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
            self.current_facecolor = None
            self.update_color()
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
        self.graph_display.show_graph()

    def mousePressEvent(self, event):
        if not self.color_search_bar.geometry().contains(event.position().toPoint()):
            self.color_search_bar.clearFocus()
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

class legend_edge_color_adjustment_section(QWidget):
    def __init__(self,selected_graph,graph_display):
        super().__init__()

        self.graph_display = graph_display

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
                border-radius: 16px;
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
                border-radius: 16px;
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
                border-radius: 16px;
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
                border-radius: 16px;
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
                border-radius: 16px;
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
                border-radius: 16px;
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
                border-radius: 16px;
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
        self.named_color_list_view.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)

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
                border-radius: 16px;
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
                border-radius: 16px;
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
                border-radius: 16px;
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
                border-radius: 16px;
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
                border-radius: 16px;
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
                border-radius: 16px;
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
                border-radius: 16px;
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
        self.short_code_color_list_view.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)

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
                border-radius: 16px;
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
            self.current_edge_color = None
            self.update_color
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
            self.current_edge_color = None
            self.update_color()
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
            self.current_edge_color = None
            self.update_color()
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
        self.graph_display.show_graph()

    def mousePressEvent(self, event):
        if not self.color_search_bar.geometry().contains(event.position().toPoint()):
            self.color_search_bar.clearFocus()
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

class legend_framealpha_adjustment_section(QWidget):
    def __init__(self,selected_graph,graph_display):
        super().__init__()
        
        self.graph_display = graph_display

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
                border-radius: 16px;
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
                border-radius: 16px;
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
            self.update_framealpha()
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
        self.graph_display.show_graph()

    def mousePressEvent(self, event):
        if not self.framealpha_input.geometry().contains(event.position().toPoint()):
            self.framealpha_input.clearFocus()
        super().mousePressEvent(event)

class legend_shadow_adjustment_section(QWidget):
    def __init__(self,selected_graph,graph_display):
        super().__init__()

        self.graph_display = graph_display

        self.plot_manager = PlotManager()
        
        self.selected_graph = selected_graph
        
        #Initialize the shadow state
        self.shadow_state = False
        
        #Create a widget to display the shadow adjustment section and style it for consistency
        self.shadow_adjustment_section = QWidget()
        self.shadow_adjustment_section.setObjectName("shadow_adjustment_section")
        self.shadow_adjustment_section.setStyleSheet("""
            QWidget#shadow_adjustment_section{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #f5f5ff,
                    stop:0.5 #f7f5fc,
                    stop:1 #f0f0ff
                );
                border: 2px solid black;
                border-radius: 16px;
            }
        """)

        #Create a label to put on top of the QPushButton
        self.shadow_label = QLabel("Shadow Off")
        self.shadow_label.setWordWrap(True)
        self.shadow_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.shadow_label.setObjectName("shadow_label")
        self.shadow_label.setStyleSheet("""
            QLabel#shadow_label{
                font-family: "SF Pro Display";
                font-weight: 600;
                font-size: 24px;
                padding: 6px;
                color: black;
                border: none;
                background: transparent;
            }
        """)
        self.shadow_label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
    
        #Create a button to allow the user to switch between shadow
        self.shadow_button = QPushButton()
        self.shadow_button.setObjectName("shadow_button")
        self.shadow_button.setStyleSheet("""
            QPushButton#shadow_button{
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
                font-size: 16px;
                padding: 6px;
                color: black;
            }
            QPushButton#shadow_button:hover{
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
        self.shadow_button.setMinimumHeight(45)
        
        #Put the label on top of the button we created for control frameon
        shadow_button_layout = QVBoxLayout(self.shadow_button)
        shadow_button_layout.addWidget(self.shadow_label)
        shadow_button_layout.setContentsMargins(0,0,0,0)
        shadow_button_layout.setSpacing(0)

        #Connect the frameon button to a function to switch between the two states
        self.shadow_button.clicked.connect(self.switch_shadow_state)

        #Create a button layout for the frameon adjustment section
        button_layout = QVBoxLayout(self.shadow_adjustment_section)

        #Add the frameon button to the layout
        button_layout.addWidget(self.shadow_button)

        #Set the spacing, margins, and stretch to make it look good
        button_layout.setSpacing(0)
        button_layout.setContentsMargins(10,10,10,10)
        button_layout.addStretch()

        #Create a layout for the main widget and store the frameon adjustment section in
        main_layout = QVBoxLayout(self)
        main_layout.addWidget(self.shadow_adjustment_section)

        #Add the spacing and margins to make sure that the section fits nicely
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0,0,0,0)

        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

    def switch_shadow_state(self):
        #Change the frameon_state to be the opposite of the current state and update it in the json
        self.shadow_state = not self.shadow_state
        if (self.shadow_state):
            self.shadow_label.setText("Shadow On")
        else:
            self.shadow_label.setText("Shadow Off")
        self.update_shadow()

    def update_shadow(self):
        #Grab the newest entry in the json
        db = self.plot_manager.get_db()
        #Check if the entry is empty or not and update if it's not empty and create one with the state if it's empty
        if (db != []):
            self.plot_manager.update_legend("shadow",self.shadow_state)
        else:
            plot_parameters = plot_json[self.selected_graph].copy()
            plot_parameters["legend"]["shadow"] = self.shadow_state
            self.plot_manager.insert_plot_parameter(plot_parameters)
        self.graph_display.show_graph()

class legend_fancybox_adjustment_section(QWidget):
    def __init__(self,selected_graph,graph_display):
        super().__init__()

        self.graph_display = graph_display

        self.plot_manager = PlotManager()
        
        self.selected_graph = selected_graph
        
        #Initialize the fancybox state
        self.fancybox_state = True
        
        #Create a widget to display the fancybox adjustment section and style it for consistency
        self.fancybox_adjustment_section = QWidget()
        self.fancybox_adjustment_section.setObjectName("fancybox_adjustment_section")
        self.fancybox_adjustment_section.setStyleSheet("""
            QWidget#fancybox_adjustment_section{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #f5f5ff,
                    stop:0.5 #f7f5fc,
                    stop:1 #f0f0ff
                );
                border: 2px solid black;
                border-radius: 16px;
            }
        """)

        #Create a label to put on top of the QPushButton
        self.fancybox_label = QLabel("Fancybox On")
        self.fancybox_label.setWordWrap(True)
        self.fancybox_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.fancybox_label.setObjectName("fancybox_label")
        self.fancybox_label.setStyleSheet("""
            QLabel#fancybox_label{
                font-family: "SF Pro Display";
                font-weight: 600;
                font-size: 24px;
                padding: 6px;
                color: black;
                border: none;
                background: transparent;
            }
        """)
        self.fancybox_label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
    
        #Create a button to allow the user to switch between shadow
        self.fancybox_button = QPushButton()
        self.fancybox_button.setObjectName("fancybox_button")
        self.fancybox_button.setStyleSheet("""
            QPushButton#fancybox_button{
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
                font-size: 16px;
                padding: 6px;
                color: black;
            }
            QPushButton#fancybox_button:hover{
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
        self.fancybox_button.setMinimumHeight(45)
        
        #Put the label on top of the button we created for control frameon
        fancybox_button_layout = QVBoxLayout(self.fancybox_button)
        fancybox_button_layout.addWidget(self.fancybox_label)
        fancybox_button_layout.setContentsMargins(0,0,0,0)
        fancybox_button_layout.setSpacing(0)

        #Connect the frameon button to a function to switch between the two states
        self.fancybox_button.clicked.connect(self.switch_fancybox_state)

        #Create a button layout for the frameon adjustment section
        button_layout = QVBoxLayout(self.fancybox_adjustment_section)

        #Add the frameon button to the layout
        button_layout.addWidget(self.fancybox_button)

        #Set the spacing, margins, and stretch to make it look good
        button_layout.setSpacing(0)
        button_layout.setContentsMargins(10,10,10,10)
        button_layout.addStretch()

        #Create a layout for the main widget and store the frameon adjustment section in
        main_layout = QVBoxLayout(self)
        main_layout.addWidget(self.fancybox_adjustment_section)

        #Add the spacing and margins to make sure that the section fits nicely
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0,0,0,0)

        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

    def switch_fancybox_state(self):
        #Change the frameon_state to be the opposite of the current state and update it in the json
        self.fancybox_state = not self.fancybox_state
        if (self.fancybox_state):
            self.fancybox_label.setText("Fancybox On")
        else:
            self.fancybox_label.setText("Fancybox Off")
        self.update_fancybox()

    def update_fancybox(self):
        #Grab the newest entry in the json
        db = self.plot_manager.get_db()
        #Check if the entry is empty or not and update if it's not empty and create one with the state if it's empty
        if (db != []):
            self.plot_manager.update_legend("fancybox",self.fancybox_state)
        else:
            plot_parameters = plot_json[self.selected_graph].copy()
            plot_parameters["legend"]["fancybox"] = self.fancybox_state
            self.plot_manager.insert_plot_parameter(plot_parameters)
        self.graph_display.show_graph()

class legend_borderpad_adjustment_section(QWidget):
    def __init__(self, selected_graph,graph_display):
        super().__init__()

        self.graph_display = graph_display

        self.plot_manager = PlotManager()
        
        self.selected_graph = selected_graph

        #Create a section to display the borderpad section and style it
        self.borderpad_adjustment_section = QWidget()
        self.borderpad_adjustment_section.setObjectName("borderpad_adjustment_section")
        self.borderpad_adjustment_section.setStyleSheet("""
            QWidget#borderpad_adjustment_section{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #f5f5ff,
                    stop:0.5 #f7f5fc,
                    stop:1 #f0f0ff
                );
                border: 2px solid black;
                border-radius: 16px;
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
                border-radius: 16px;
            }
        """)

        #Initialize the bordpad value to be 0.4
        self.borderpad_value = 0.4

        #Create a line edit object for the user to input the borderpad
        self.borderpad_input = QLineEdit()
        self.borderpad_input.setPlaceholderText("borderpad: ")

        #Set the height of the line edit object to make it look good
        self.borderpad_input.setFixedHeight(60)

        #Connect any changes with the text to an update function
        self.borderpad_input.textChanged.connect(self.change_borderpad)

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
        borderpad_section_layout = QVBoxLayout(self.borderpad_adjustment_section)
        borderpad_section_layout.addWidget(self.borderpad_input)
        borderpad_section_layout.addWidget(self.valid_input_widget)
        borderpad_section_layout.addWidget(self.invalid_input_widget)
    
        #Add the margins, spacing, and stretch to the layout to make it look good
        borderpad_section_layout.setContentsMargins(10,10,10,10)
        borderpad_section_layout.setSpacing(10)
        borderpad_section_layout.addStretch()

        #Add the borderpad adjustment section to the main widget
        main_layout = QVBoxLayout(self)
        main_layout.addWidget(self.borderpad_adjustment_section)
        
        #Set both the spacing and margins for the main widget to make sure it fits nicely
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0,0,0,0)

        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
    
    def change_borderpad(self):
        #Extract the borderpad input from the user and remove any excess text from it
        borderpad_input = self.borderpad_input.text().strip()

        if (borderpad_input == ""):
            self.valid_input_widget.hide()
            self.invalid_input_widget.hide()
            self.borderpad_value = 0.4
            self.update_borderpad()
            return 

        #Only update the borderpad value in the json file if the input is valid
        try:
            self.borderpad_value = float(borderpad_input)
            self.valid_input_widget.show()
            self.invalid_input_widget.hide()
        except:
            self.valid_input_widget.hide()
            self.invalid_input_widget.show()
        else:
            self.update_borderpad()

    def update_borderpad(self):
        #Get the newest json entries from the plot manager
        db = self.plot_manager.get_db()

        #Check if db is empty or not. If it is empty then create a new entry with the ncol value
        #If the db isn't empty then update the db with the new ncol value.
        if (db != []):
            self.plot_manager.update_legend("borderpad",self.borderpad_value)
        else:
            plot_parameters = plot_json[self.selected_graph].copy()
            plot_parameters["legend"]["borderpad"] = self.borderpad_value
            self.plot_manager.insert_plot_parameter(plot_parameters)
        self.graph_display.show_graph()

    def mousePressEvent(self, event):
        if not self.borderpad_input.geometry().contains(event.position().toPoint()):
            self.borderpad_input.clearFocus()
        super().mousePressEvent(event)

class legend_label_color_adjustment_section(QWidget):
    def __init__(self,selected_graph,graph_display):
        super().__init__()

        self.graph_display = graph_display

        self.plot_manager = PlotManager()
        self.selected_graph = selected_graph
        self.named_colors = list(mcolors.get_named_colors_mapping().keys())
        self.short_code_colors = self.named_colors[-8:]
        self.named_colors = [c.replace("xkcd:","") for c in self.named_colors]
        self.named_colors = [c.replace("tab:","") for c in self.named_colors]
        self.named_colors = self.named_colors[:-8]

        self.current_label_color = ""

        #-----Home Screen-----

        self.label_color_adjustment_homescreen = QWidget()
        self.label_color_adjustment_homescreen.setObjectName("label_color_adjustment")
        self.label_color_adjustment_homescreen.setStyleSheet("""
            QWidget#label_color_adjustment{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #f5f5ff,
                    stop:0.5 #f7f5fc,
                    stop:1 #f0f0ff
                );
                border: 2px solid black;
                border-radius: 16px;
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

        button_layout = QVBoxLayout(self.label_color_adjustment_homescreen)
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
                border-radius: 16px;
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
                border-radius: 16px;
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
                border-radius: 16px;
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
                border-radius: 16px;
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
                border-radius: 16px;
            }  
        """)
        self.create_short_code_color_screen()
        self.short_code_color_screen.hide()

        #-----Initialize Screen Value-----

        self.available_screens = [self.label_color_adjustment_homescreen,self.named_color_screen,
                                self.hex_code_color_screen,self.rgba_color_screen,
                                self.grayscale_color_screen,self.short_code_color_screen]
        self.current_screen_idx = 0

        #-----Main Screen-----
        main_layout = QVBoxLayout(self)
        main_layout.addWidget(self.label_color_adjustment_homescreen)
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
                border-radius: 16px;
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
        self.named_color_list_view.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)

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
                border-radius: 16px;
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
                border-radius: 16px;
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
                border-radius: 16px;
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
                border-radius: 16px;
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
                border-radius: 16px;
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
                border-radius: 16px;
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
                border-radius: 16px;
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
        self.short_code_color_list_view.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
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
                border-radius: 16px;
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
        self.label_color_adjustment_homescreen.show()

    def change_to_named_color_screen(self):
        self.available_screens[self.current_screen_idx].hide()
        self.current_screen_idx = 1
        self.named_color_screen.show()

    def change_to_hex_code_screen(self):
        self.available_screens[self.current_screen_idx].hide()
        self.current_screen_idx = 2
        self.hex_code_color_screen.show()

    def change_to_rgba_color_screen(self):
        self.available_screens[self.current_screen_idx].hide()
        self.current_screen_idx = 3
        self.rgba_color_screen.show()

    def change_to_grayscale_colors_screen(self):
        self.available_screens[self.current_screen_idx].hide()
        self.current_screen_idx = 4
        self.grayscale_color_screen.show()

    def change_to_short_code_color_screen(self):
        self.available_screens[self.current_screen_idx].hide()
        self.current_screen_idx = 5
        self.short_code_color_screen.show()

    def set_color_to_none(self):
        self.current_label_color = None
        self.update_color()

    def change_named_color(self,index):
        source_index = self.filter_proxy.mapToSource(index)
        self.current_label_color = self.named_color_model.data(source_index, Qt.ItemDataRole.DisplayRole)
        self.update_color()

    def change_hex_code_color(self):
        hex_code = self.hex_code_input.text().strip()

        if (hex_code == ""):
            self.hex_valid_input_widget.hide()
            self.hex_invalid_input_widget.hide()
            self.current_label_color = "k"
            self.update_color()
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
                self.current_label_color = hex_code if hex_code[0] == "#" else "#" + hex_code
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
            self.current_label_color = "k"
            self.update_color()
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

            self.current_label_color = self.initial_rgba

            self.update_color()
        else:
            self.rgba_valid_input_widget.hide()
            self.rgba_invalid_input_widget.show()

    def change_grayscale_color(self):
        grayscale_value = self.grayscale_input.text().strip()

        if (grayscale_value == ""): 
            self.grayscale_valid_input_widget.hide() 
            self.grayscale_invalid_input_widget.hide()
            self.current_label_color = "k"
            self.update_color()
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

        self.current_label_color = grayscale_value
        self.update_color()

    def change_short_code_color(self,index):
        self.current_label_color = self.short_code_color_model.data(index, Qt.ItemDataRole.DisplayRole)
        self.update_color()

    def update_color(self):
        db = self.plot_manager.get_db()
        if (db != []):
            self.plot_manager.update_legend("labelcolor",self.current_label_color)
        else:
            plot_parameters = plot_json[self.selected_graph].copy()
            plot_parameters["legend"]["labelcolor"] = self.current_label_color
            self.plot_manager.insert_plot_parameter(plot_parameters)
        self.graph_display.show_graph()

    def mousePressEvent(self, event):
        if not self.color_search_bar.geometry().contains(event.position().toPoint()):
            self.color_search_bar.clearFocus()
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

class legend_alignment_adjustment_section(QWidget):
    def __init__(self,selected_graph,graph_display):
        super().__init__()

        self.graph_display = graph_display
        
        self.plot_manager = PlotManager()
        self.selected_graph = selected_graph

        self.available_alignments = ["left","center","right"]
        self.current_alignment = "center"

        self.alignment_adjustment_screen = QWidget()
        self.alignment_adjustment_screen.setObjectName("alignment_adjustment_screen")
        self.alignment_adjustment_screen.setStyleSheet("""
            QWidget#alignment_adjustment_screen{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #f5f5ff,
                    stop:0.5 #f7f5fc,
                    stop:1 #f0f0ff
                );
                border: 2px solid black;
                border-radius: 16px;
            }
        """)
        self.create_alignment_adjustment_screen()

        main_layout = QVBoxLayout(self)
        main_layout.addWidget(self.alignment_adjustment_screen)
        main_layout.setContentsMargins(0,0,0,0)
        main_layout.setSpacing(0)

        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground,True)

    def create_alignment_adjustment_screen(self):
        alignment_adjustment_screen_layout = QVBoxLayout(self.alignment_adjustment_screen)
    
        self.alignment_list_view = QListView()
        self.alignment_model = QStringListModel(self.available_alignments)

        self.alignment_list_view.setModel(self.alignment_model)
        self.alignment_list_view.setObjectName("alignment_list_view")
        self.alignment_list_view.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        class CustomDelegate(QStyledItemDelegate):
            def paint(self, painter, option, index):
                option.displayAlignment = Qt.AlignmentFlag.AlignCenter
                font = QFont("SF Pro Display", 24)
                font.setWeight(600)
                option.font = font
                super().paint(painter, option, index)
        
        self.alignment_list_view.setItemDelegate(CustomDelegate())

        self.alignment_list_view.setStyleSheet("""
            QListView#alignment_list_view{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #f5f5ff,
                    stop:0.5 #f7f5fc,
                    stop:1 #f0f0ff
                );
                border: transparent;
                border-radius: 16px;
            }
            QListView#alignment_list_view::item {
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
            QListView#alignment_list_view::item:selected {
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
            QListView#alignment_list_view::item:hover {
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

        self.alignment_list_view.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.alignment_list_view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.alignment_list_view.setSpacing(3)

        self.alignment_list_view.clicked.connect(self.change_alignment)

        alignment_adjustment_screen_layout.addWidget(self.alignment_list_view)

        # Add margins and spacing to make it look good and push content to the top
        alignment_adjustment_screen_layout.setContentsMargins(10, 10, 10, 10)

    def change_alignment(self,index):
        self.current_alignment = self.alignment_model.data(index,Qt.ItemDataRole.DisplayRole)
        self.update_alignment()

    def update_alignment(self): 
        db = self.plot_manager.get_db()
        if (db != []):
            self.plot_manager.update_legend("alignment",self.current_alignment)
        else:
            plot_parameters = plot_json[self.selected_graph].copy()
            plot_parameters["legend"]["alignment"] = self.current_alignment
            self.plot_manager.insert_plot_parameter(plot_parameters)
        self.graph_display.show_graph()

class legend_columnspacing_adjustment_section(QWidget):
    def __init__(self, selected_graph,graph_display):
        super().__init__()

        self.graph_display = graph_display

        self.plot_manager = PlotManager()
        
        self.selected_graph = selected_graph

        #Create a section to display the loc section and style it
        self.columnspacing_adjustment_section = QWidget()
        self.columnspacing_adjustment_section.setObjectName("columnspacing_adjustment_section")
        self.columnspacing_adjustment_section.setStyleSheet("""
            QWidget#columnspacing_adjustment_section{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #f5f5ff,
                    stop:0.5 #f7f5fc,
                    stop:1 #f0f0ff
                );
                border: 2px solid black;
                border-radius: 16px;
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
                border-radius: 16px;
            }
        """)

        #Initialize the ncol value to be 0
        self.columnspacing_value = 0

        #Create a line edit object for the user to input the ncol
        self.columnspacing_input = QLineEdit()
        self.columnspacing_input.setPlaceholderText("columnspacing: ")

        #Set the height of the line edit object to make it look good
        self.columnspacing_input.setFixedHeight(60)

        #Connect any changes with the text to an update function
        self.columnspacing_input.textChanged.connect(self.change_columnspacing)

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
        columnspacing_section_layout = QVBoxLayout(self.columnspacing_adjustment_section)
        columnspacing_section_layout.addWidget(self.columnspacing_input)
        columnspacing_section_layout.addWidget(self.valid_input_widget)
        columnspacing_section_layout.addWidget(self.invalid_input_widget)
    
        #Add the margins, spacing, and stretch to the layout to make it look good
        columnspacing_section_layout.setContentsMargins(10,10,10,10)
        columnspacing_section_layout.setSpacing(10)
        columnspacing_section_layout.addStretch()

        #Add the ncol adjustment section to the main widget
        main_layout = QVBoxLayout(self)
        main_layout.addWidget(self.columnspacing_adjustment_section)
        
        #Set both the spacing and margins for the main widget to make sure it fits nicely
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0,0,0,0)

        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
    
    def change_columnspacing(self):
        #Extract the ncol input from the user and remove any excess text from it
        columnspacing_input = self.columnspacing_input.text().strip()

        if (columnspacing_input == ""):
            self.valid_input_widget.hide()
            self.invalid_input_widget.hide()
            self.columnspacing_value = 2.0
            self.update_columnspacing()
            return 

        #Only update the ncol value in the json file if the input is valid
        try:
            self.columnspacing_value = float(columnspacing_input)
            self.valid_input_widget.show()
            self.invalid_input_widget.hide()
        except:
            self.valid_input_widget.hide()
            self.invalid_input_widget.show()
        else:
            self.update_columnspacing()

    def update_columnspacing(self):
        #Get the newest json entries from the plot manager
        db = self.plot_manager.get_db()

        #Check if db is empty or not. If it is empty then create a new entry with the ncol value
        #If the db isn't empty then update the db with the new ncol value.
        if (db != []):
            self.plot_manager.update_legend("columnspacing",self.columnspacing_value)
        else:
            plot_parameters = plot_json[self.selected_graph].copy()
            plot_parameters["legend"]["columnspacing"] = self.columnspacing_value
            self.plot_manager.insert_plot_parameter(plot_parameters)
        self.graph_display.show_graph()

    def mousePressEvent(self, event):
        if not self.columnspacing_input.geometry().contains(event.position().toPoint()):
            self.columnspacing_input.clearFocus()
        super().mousePressEvent(event)

class legend_handletextpad_adjustment_section(QWidget):
    def __init__(self, selected_graph,graph_display):
        super().__init__()

        self.graph_display = graph_display

        self.plot_manager = PlotManager()
        
        self.selected_graph = selected_graph

        #Create a section to display the loc section and style it
        self.handletextpad_adjustment_section = QWidget()
        self.handletextpad_adjustment_section.setObjectName("handletextpad_adjustment_section")
        self.handletextpad_adjustment_section.setStyleSheet("""
            QWidget#handletextpad_adjustment_section{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #f5f5ff,
                    stop:0.5 #f7f5fc,
                    stop:1 #f0f0ff
                );
                border: 2px solid black;
                border-radius: 16px;
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
                border-radius: 16px;
            }
        """)

        #Initialize the ncol value to be 0
        self.handletextpad_value = 0

        #Create a line edit object for the user to input the ncol
        self.handletextpad_input = QLineEdit()
        self.handletextpad_input.setPlaceholderText("handletextpad: ")

        #Set the height of the line edit object to make it look good
        self.handletextpad_input.setFixedHeight(60)

        #Connect any changes with the text to an update function
        self.handletextpad_input.textChanged.connect(self.change_handletextpad)

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
        handletextpad_section_layout = QVBoxLayout(self.handletextpad_adjustment_section)
        handletextpad_section_layout.addWidget(self.handletextpad_input)
        handletextpad_section_layout.addWidget(self.valid_input_widget)
        handletextpad_section_layout.addWidget(self.invalid_input_widget)
    
        #Add the margins, spacing, and stretch to the layout to make it look good
        handletextpad_section_layout.setContentsMargins(10,10,10,10)
        handletextpad_section_layout.setSpacing(10)
        handletextpad_section_layout.addStretch()

        #Add the ncol adjustment section to the main widget
        main_layout = QVBoxLayout(self)
        main_layout.addWidget(self.handletextpad_adjustment_section)
        
        #Set both the spacing and margins for the main widget to make sure it fits nicely
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0,0,0,0)

        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
    
    def change_handletextpad(self):
        #Extract the ncol input from the user and remove any excess text from it
        handletextpad_input = self.handletextpad_input.text().strip()

        if (handletextpad_input == ""):
            self.valid_input_widget.hide()
            self.invalid_input_widget.hide()
            self.handletextpad_value = 0.8
            self.update_handletextpad()
            return 

        #Only update the ncol value in the json file if the input is valid
        try:
            self.handletextpad_value = float(handletextpad_input)
            self.valid_input_widget.show()
            self.invalid_input_widget.hide()
        except:
            self.valid_input_widget.hide()
            self.invalid_input_widget.show()
        else:
            self.update_handletextpad()

    def update_handletextpad(self):
        #Get the newest json entries from the plot manager
        db = self.plot_manager.get_db()

        #Check if db is empty or not. If it is empty then create a new entry with the ncol value
        #If the db isn't empty then update the db with the new ncol value.
        if (db != []):
            self.plot_manager.update_legend("handletextpad",self.handletextpad_value)
        else:
            plot_parameters = plot_json[self.selected_graph].copy()
            plot_parameters["legend"]["handletextpad"] = self.handletextpad_value
            self.plot_manager.insert_plot_parameter(plot_parameters)
        self.graph_display.show_graph()

    def mousePressEvent(self, event):
        if not self.handletextpad_input.geometry().contains(event.position().toPoint()):
            self.handletextpad_input.clearFocus()
        super().mousePressEvent(event)

class legend_borderaxespad_adjustment_section(QWidget):
    def __init__(self, selected_graph,graph_display):
        super().__init__()

        self.graph_display = graph_display

        self.plot_manager = PlotManager()
        
        self.selected_graph = selected_graph

        #Create a section to display the loc section and style it
        self.borderaxespad_adjustment_section = QWidget()
        self.borderaxespad_adjustment_section.setObjectName("borderaxespad_adjustment_section")
        self.borderaxespad_adjustment_section.setStyleSheet("""
            QWidget#borderaxespad_adjustment_section{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #f5f5ff,
                    stop:0.5 #f7f5fc,
                    stop:1 #f0f0ff
                );
                border: 2px solid black;
                border-radius: 16px;
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
                border-radius: 16px;
            }
        """)

        #Initialize the ncol value to be 0
        self.borderaxespad_value = 0

        #Create a line edit object for the user to input the ncol
        self.borderaxespad_input = QLineEdit()
        self.borderaxespad_input.setPlaceholderText("borderaxespad: ")

        #Set the height of the line edit object to make it look good
        self.borderaxespad_input.setFixedHeight(60)

        #Connect any changes with the text to an update function
        self.borderaxespad_input.textChanged.connect(self.change_borderaxespad)

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
        borderaxespad_section_layout = QVBoxLayout(self.borderaxespad_adjustment_section)
        borderaxespad_section_layout.addWidget(self.borderaxespad_input)
        borderaxespad_section_layout.addWidget(self.valid_input_widget)
        borderaxespad_section_layout.addWidget(self.invalid_input_widget)
    
        #Add the margins, spacing, and stretch to the layout to make it look good
        borderaxespad_section_layout.setContentsMargins(10,10,10,10)
        borderaxespad_section_layout.setSpacing(10)
        borderaxespad_section_layout.addStretch()

        #Add the ncol adjustment section to the main widget
        main_layout = QVBoxLayout(self)
        main_layout.addWidget(self.borderaxespad_adjustment_section)
        
        #Set both the spacing and margins for the main widget to make sure it fits nicely
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0,0,0,0)

        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
    
    def change_borderaxespad(self):
        #Extract the ncol input from the user and remove any excess text from it
        borderaxespad_input = self.borderaxespad_input.text().strip()

        if (borderaxespad_input == ""):
            self.valid_input_widget.hide()
            self.invalid_input_widget.hide()
            self.borderaxespad_value = 0.5
            self.update_borderaxespad()
            return 

        #Only update the ncol value in the json file if the input is valid
        try:
            self.borderaxespad_value = float(borderaxespad_input)
            self.valid_input_widget.show()
            self.invalid_input_widget.hide()
        except:
            self.valid_input_widget.hide()
            self.invalid_input_widget.show()
        else:
            self.update_borderaxespad()

    def update_borderaxespad(self):
        #Get the newest json entries from the plot manager
        db = self.plot_manager.get_db()

        #Check if db is empty or not. If it is empty then create a new entry with the ncol value
        #If the db isn't empty then update the db with the new ncol value.
        if (db != []):
            self.plot_manager.update_legend("borderaxespad",self.borderaxespad_value)
        else:
            plot_parameters = plot_json[self.selected_graph].copy()
            plot_parameters["legend"]["borderaxespad"] = self.borderaxespad_value
            self.plot_manager.insert_plot_parameter(plot_parameters)
        self.graph_display.show_graph()

    def mousePressEvent(self, event):
        if not self.borderaxespad_input.geometry().contains(event.position().toPoint()):
            self.borderaxespad_input.clearFocus()
        super().mousePressEvent(event)

class legend_handlelength_adjustment_section(QWidget):
    def __init__(self, selected_graph, graph_display):
        super().__init__()

        self.graph_display = graph_display

        self.plot_manager = PlotManager()
        
        self.selected_graph = selected_graph

        #Create a section to display the loc section and style it
        self.handlelength_adjustment_section = QWidget()
        self.handlelength_adjustment_section.setObjectName("handlelength_adjustment_section")
        self.handlelength_adjustment_section.setStyleSheet("""
            QWidget#handlelength_adjustment_section{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #f5f5ff,
                    stop:0.5 #f7f5fc,
                    stop:1 #f0f0ff
                );
                border: 2px solid black;
                border-radius: 16px;
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
                border-radius: 16px;
            }
        """)

        #Initialize the handlelength value to be 2.0
        self.handlelength_value = 2.0

        #Create a line edit object for the user to input the ncol
        self.handlelength_input = QLineEdit()
        self.handlelength_input.setPlaceholderText("handlelength: ")

        #Set the height of the line edit object to make it look good
        self.handlelength_input.setFixedHeight(60)

        #Connect any changes with the text to an update function
        self.handlelength_input.textChanged.connect(self.change_handlelength)

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
        handlelength_section_layout = QVBoxLayout(self.handlelength_adjustment_section)
        handlelength_section_layout.addWidget(self.handlelength_input)
        handlelength_section_layout.addWidget(self.valid_input_widget)
        handlelength_section_layout.addWidget(self.invalid_input_widget)
    
        #Add the margins, spacing, and stretch to the layout to make it look good
        handlelength_section_layout.setContentsMargins(10,10,10,10)
        handlelength_section_layout.setSpacing(10)
        handlelength_section_layout.addStretch()

        #Add the ncol adjustment section to the main widget
        main_layout = QVBoxLayout(self)
        main_layout.addWidget(self.handlelength_adjustment_section)
        
        #Set both the spacing and margins for the main widget to make sure it fits nicely
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0,0,0,0)

        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
    
    def change_handlelength(self):
        #Extract the ncol input from the user and remove any excess text from it
        handlelength_input = self.handlelength_input.text().strip()

        if (handlelength_input == ""):
            self.valid_input_widget.hide()
            self.invalid_input_widget.hide()
            self.handlelength_value = 2.0
            self.update_handlelength()
            return 

        #Only update the ncol value in the json file if the input is valid
        try:
            self.handlelength_value = float(handlelength_input)
            self.valid_input_widget.show()
            self.invalid_input_widget.hide()
        except:
            self.valid_input_widget.hide()
            self.invalid_input_widget.show()
        else:
            self.update_handlelength()

    def update_handlelength(self):
        #Get the newest json entries from the plot manager
        db = self.plot_manager.get_db()

        #Check if db is empty or not. If it is empty then create a new entry with the ncol value
        #If the db isn't empty then update the db with the new ncol value.
        if (db != []):
            self.plot_manager.update_legend("handlelength",self.handlelength_value)
        else:
            plot_parameters = plot_json[self.selected_graph].copy()
            plot_parameters["legend"]["handlelength"] = self.handlelength_value
            self.plot_manager.insert_plot_parameter(plot_parameters)
        self.graph_display.show_graph()

    def mousePressEvent(self, event):
        if not self.handlelength_input.geometry().contains(event.position().toPoint()):
            self.handlelength_input.clearFocus()
        super().mousePressEvent(event)

class legend_handleheight_adjustment_section(QWidget):
    def __init__(self, selected_graph, graph_display):
        super().__init__()

        self.graph_display = graph_display

        self.plot_manager = PlotManager()
        
        self.selected_graph = selected_graph

        #Create a section to display the loc section and style it
        self.handleheight_adjustment_section = QWidget()
        self.handleheight_adjustment_section.setObjectName("handleheight_adjustment_section")
        self.handleheight_adjustment_section.setStyleSheet("""
            QWidget#handleheight_adjustment_section{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #f5f5ff,
                    stop:0.5 #f7f5fc,
                    stop:1 #f0f0ff
                );
                border: 2px solid black;
                border-radius: 16px;
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
                border-radius: 16px;
            }
        """)

        #Initialize the ncol value to be 0
        self.handleheight_value = 0

        #Create a line edit object for the user to input the ncol
        self.handleheight_input = QLineEdit()
        self.handleheight_input.setPlaceholderText("handleheight_input: ")

        #Set the height of the line edit object to make it look good
        self.handleheight_input.setFixedHeight(60)

        #Connect any changes with the text to an update function
        self.handleheight_input.textChanged.connect(self.change_handleheight)

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
        handleheight_section_layout = QVBoxLayout(self.handleheight_adjustment_section)
        handleheight_section_layout.addWidget(self.handleheight_input)
        handleheight_section_layout.addWidget(self.valid_input_widget)
        handleheight_section_layout.addWidget(self.invalid_input_widget)
    
        #Add the margins, spacing, and stretch to the layout to make it look good
        handleheight_section_layout.setContentsMargins(10,10,10,10)
        handleheight_section_layout.setSpacing(10)
        handleheight_section_layout.addStretch()

        #Add the ncol adjustment section to the main widget
        main_layout = QVBoxLayout(self)
        main_layout.addWidget(self.handleheight_adjustment_section)
        
        #Set both the spacing and margins for the main widget to make sure it fits nicely
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0,0,0,0)

        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
    
    def change_handleheight(self):
        #Extract the ncol input from the user and remove any excess text from it
        handleheight_input = self.handleheight_input.text().strip()

        if (handleheight_input == ""):
            self.valid_input_widget.hide()
            self.invalid_input_widget.hide()
            self.handleheight_value = 0.7
            self.update_handleheight()
            return 

        #Only update the ncol value in the json file if the input is valid
        try:
            self.handleheight_value = float(handleheight_input)
            self.valid_input_widget.show()
            self.invalid_input_widget.hide()
        except:
            self.valid_input_widget.hide()
            self.invalid_input_widget.show()
        else:
            self.update_handleheight()

    def update_handleheight(self):
        #Get the newest json entries from the plot manager
        db = self.plot_manager.get_db()

        #Check if db is empty or not. If it is empty then create a new entry with the ncol value
        #If the db isn't empty then update the db with the new ncol value.
        if (db != []):
            self.plot_manager.update_legend("handleheight",self.handleheight_value)
        else:
            plot_parameters = plot_json[self.selected_graph].copy()
            plot_parameters["legend"]["handleheight"] = self.handleheight_value
            self.plot_manager.insert_plot_parameter(plot_parameters)
        self.graph_display.show_graph()

    def mousePressEvent(self, event):
        if not self.handleheight_input.geometry().contains(event.position().toPoint()):
            self.handleheight_input.clearFocus()
        super().mousePressEvent(event)

class legend_markerfirst_adjustment_section(QWidget):
    def __init__(self,selected_graph,graph_display):
        super().__init__()

        self.graph_display = graph_display

        self.plot_manager = PlotManager()
        
        self.selected_graph = selected_graph
        
        #Initialize the frameon state
        self.markerfirst_state = True
        
        #Create a widget to display the frameon adjustment section and style it for consistency
        self.markerfirst_adjustment_section = QWidget()
        self.markerfirst_adjustment_section.setObjectName("markerfirst_adjustment_section")
        self.markerfirst_adjustment_section.setStyleSheet("""
            QWidget#markerfirst_adjustment_section{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #f5f5ff,
                    stop:0.5 #f7f5fc,
                    stop:1 #f0f0ff
                );
                border: 2px solid black;
                border-radius: 16px;
            }
        """)

        #Create a label to put on top of the QPushButton
        self.markerfirst_label = QLabel("Markerfirst On")
        self.markerfirst_label.setWordWrap(True)
        self.markerfirst_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.markerfirst_label.setObjectName("markerfirst_label")
        self.markerfirst_label.setStyleSheet("""
            QLabel#markerfirst_label{
                font-family: "SF Pro Display";
                font-weight: 600;
                font-size: 24px;
                padding: 6px;
                color: black;
                border: none;
                background: transparent;
            }
        """)
        self.markerfirst_label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
    
        #Create a button to allow the user to switch between shadow
        self.markerfirst_button = QPushButton()
        self.markerfirst_button.setObjectName("markerfirst_button")
        self.markerfirst_button.setStyleSheet("""
            QPushButton#markerfirst_button{
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
                font-size: 16px;
                padding: 6px;
                color: black;
            }
            QPushButton#markerfirst_button:hover{
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
        self.markerfirst_button.setMinimumHeight(45)
        
        #Put the label on top of the button we created for control frameon
        markerfirst_button_layout = QVBoxLayout(self.markerfirst_button)
        markerfirst_button_layout.addWidget(self.markerfirst_label)
        markerfirst_button_layout.setContentsMargins(0,0,0,0)
        markerfirst_button_layout.setSpacing(0)

        #Connect the frameon button to a function to switch between the two states
        self.markerfirst_button.clicked.connect(self.switch_markerfirst_state)

        #Create a button layout for the frameon adjustment section
        button_layout = QVBoxLayout(self.markerfirst_adjustment_section)

        #Add the frameon button to the layout
        button_layout.addWidget(self.markerfirst_button)

        #Set the spacing, margins, and stretch to make it look good
        button_layout.setSpacing(0)
        button_layout.setContentsMargins(10,10,10,10)
        button_layout.addStretch()

        #Create a layout for the main widget and store the frameon adjustment section in
        main_layout = QVBoxLayout(self)
        main_layout.addWidget(self.markerfirst_adjustment_section)

        #Add the spacing and margins to make sure that the section fits nicely
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0,0,0,0)

        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

    def switch_markerfirst_state(self):
        #Change the frameon_state to be the opposite of the current state and update it in the json
        self.markerfirst_state = not self.markerfirst_state
        if (self.markerfirst_state):
            self.markerfirst_label.setText("Markerfirst On")
        else:
            self.markerfirst_label.setText("Markerfirst Off")
        self.update_markerfirst()

    def update_markerfirst(self):
        #Grab the newest entry in the json
        db = self.plot_manager.get_db()
        #Check if the entry is empty or not and update if it's not empty and create one with the state if it's empty
        if (db != []):
            self.plot_manager.update_legend("markerfirst",self.markerfirst_state)
        else:
            plot_parameters = plot_json[self.selected_graph].copy()
            plot_parameters["legend"]["markerfirst"] = self.markerfirst_state
            self.plot_manager.insert_plot_parameter(plot_parameters)
        self.graph_display.show_graph()

class seaborn_legend_adjustment_section(QWidget):
    def __init__(self,selected_graph,graph_display): 
        super().__init__()

        self.plot_manager = PlotManager()

        self.selected_graph = selected_graph
        self.graph_display = graph_display

        #Create a section to display the seaborn legend section and style it
        self.sns_legend_adjustment_section = QWidget()
        self.sns_legend_adjustment_section.setObjectName("sns_legend_adjustment_section")
        self.sns_legend_adjustment_section.setStyleSheet("""
            QWidget#sns_legend_adjustment_section{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #f5f5ff,
                    stop:0.5 #f7f5fc,
                    stop:1 #f0f0ff
                );
                border: 2px solid black;
                border-radius: 16px;
            }
        """)

        #Store the loc buttons created in a list and list out the possible positions
        self.available_sns_legend_arguments = ["brief","full","True","False"]

        #Use a index to control the current location of the legend
        self.sns_legend_argument_name = self.available_sns_legend_arguments[0]

        #Create the seaborn legend parameter section
        self.create_sns_legend_parameter_section()

        #Add the legend loc adjustment section to the main widget to display on the other QDialog
        main_layout = QVBoxLayout(self)
        main_layout.addWidget(self.sns_legend_adjustment_section)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0,0,0,0)

        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

    def create_sns_legend_parameter_section(self):
        sns_legend_parameter_layout = QVBoxLayout(self.sns_legend_adjustment_section)
    
        self.sns_legend_list_view = QListView()
        self.sns_legend_parameter_model = QStringListModel(self.available_sns_legend_arguments)

        self.sns_legend_list_view.setModel(self.sns_legend_parameter_model)
        self.sns_legend_list_view.setObjectName("sns_legend_list_view")
        self.sns_legend_list_view.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        class CustomDelegate(QStyledItemDelegate):
            def paint(self, painter, option, index):
                option.displayAlignment = Qt.AlignmentFlag.AlignCenter
                font = QFont("SF Pro Display", 24)
                font.setWeight(600)
                option.font = font
                super().paint(painter, option, index)
        
        self.sns_legend_list_view.setItemDelegate(CustomDelegate())

        self.sns_legend_list_view.setStyleSheet("""
            QListView#sns_legend_list_view{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #f5f5ff,
                    stop:0.5 #f7f5fc,
                    stop:1 #f0f0ff
                );
                border: transparent;
                border-radius: 16px;
            }
            QListView#sns_legend_list_view::item {
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
            QListView#sns_legend_list_view::item:selected {
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
            QListView#sns_legend_list_view::item:hover {
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

        self.sns_legend_list_view.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.sns_legend_list_view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.sns_legend_list_view.setSpacing(3)

        self.sns_legend_list_view.clicked.connect(self.change_sns_legend_parameter)

        sns_legend_parameter_layout.addWidget(self.sns_legend_list_view)

        # Add margins and spacing to make it look good and push content to the top
        sns_legend_parameter_layout.setContentsMargins(10, 10, 10, 10)

    def change_sns_legend_parameter(self,index):
        self.sns_legend_argument_name = self.sns_legend_parameter_model.data(index,Qt.ItemDataRole.DisplayRole)
        
        if (self.sns_legend_argument_name == "True"):
            self.sns_legend_argument_name = True
        if (self.sns_legend_argument_name == "False"):
            self.sns_legend_argument_name = False

        self.update_legend_argument()

    def update_legend_argument(self):
        db = self.plot_manager.get_db()
        if (db != []):
            self.plot_manager.update_seaborn_legend("legend",self.sns_legend_argument_name)
        else:
            plot_parameters = plot_json[self.selected_graph].copy()
            plot_parameters["legend"]["seaborn_legends"]["legend"] = self.sns_legend_argument_name
            self.plot_manager.insert_plot_parameter(plot_parameters)
        self.graph_display.show_graph()

class seaborn_legend_off_adjustment_section(QWidget):
    def __init__(self,selected_graph,graph_display):
        super().__init__()
        
        self.selected_graph = selected_graph
        self.plot_manager = PlotManager()
        self.graph_display = graph_display

        #Initialize the frameon state
        self.sns_legend_off_state = True
        
        #Create a widget to display the frameon adjustment section and style it for consistency
        self.sns_legend_off_adjustment_section = QWidget()
        self.sns_legend_off_adjustment_section.setObjectName("sns_legend_off_adjustment_section")
        self.sns_legend_off_adjustment_section.setStyleSheet("""
            QWidget#sns_legend_off_adjustment_section{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #f5f5ff,
                    stop:0.5 #f7f5fc,
                    stop:1 #f0f0ff
                );
                border: 2px solid black;
                border-radius: 16px;
            }
        """)

        #Create a label to put on top of the QPushButton
        self.sns_legend_off_label = QLabel("Legend Off")
        self.sns_legend_off_label.setWordWrap(True)
        self.sns_legend_off_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.sns_legend_off_label.setObjectName("legend_off_label")
        self.sns_legend_off_label.setStyleSheet("""
            QLabel#legend_off_label{
                font-family: "SF Pro Display";
                font-weight: 600;
                font-size: 24px;
                padding: 6px;
                color: black;
                border: none;
                background: transparent;
            }
        """)
        self.sns_legend_off_label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
    
        #Create a button to allow the user to switch between Frameon
        self.sns_legend_off_button = QPushButton()
        self.sns_legend_off_button.setObjectName("sns_legend_off_button")
        self.sns_legend_off_button.setStyleSheet("""
            QPushButton#sns_legend_off_button{
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
                font-size: 16px;
                padding: 6px;
                color: black;
            }
            QPushButton#sns_legend_off_button:hover{
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
        self.sns_legend_off_button.setMinimumHeight(45)
        
        #Put the label on top of the button we created for control frameon
        sns_legend_off_button_layout = QVBoxLayout(self.sns_legend_off_button)
        sns_legend_off_button_layout.addWidget(self.sns_legend_off_label)
        sns_legend_off_button_layout.setContentsMargins(0,0,0,0)
        sns_legend_off_button_layout.setSpacing(0)

        #Connect the frameon button to a function to switch between the two states
        self.sns_legend_off_button.clicked.connect(self.switch_sns_legend_off_state)

        #Create a button layout for the frameon adjustment section
        button_layout = QVBoxLayout(self.sns_legend_off_adjustment_section)

        #Add the frameon button to the layout
        button_layout.addWidget(self.sns_legend_off_button)

        #Set the spacing, margins, and stretch to make it look good
        button_layout.setSpacing(0)
        button_layout.setContentsMargins(10,10,10,10)
        button_layout.addStretch()

        #Create a layout for the main widget and store the frameon adjustment section in
        main_layout = QVBoxLayout(self)
        main_layout.addWidget(self.sns_legend_off_adjustment_section)

        #Add the spacing and margins to make sure that the section fits nicely
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0,0,0,0)

        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

    def switch_sns_legend_off_state(self):
        #Change the frameon_state to be the opposite of the current state and update it in the json
        self.sns_legend_off_state = not self.sns_legend_off_state
        if (self.sns_legend_off_state):
            self.sns_legend_off_label.setText("Legend Off")
        else:
            self.sns_legend_off_label.setText("Legend On")
        self.update_sns_legend_off()

    def update_sns_legend_off(self):
        #Grab the newest entry in the json
        db = self.plot_manager.get_db()
        #Check if the entry is empty or not and update if it's not empty and create one with the state if it's empty
        if (db != []):
            self.plot_manager.update_seaborn_legend("legend_off",self.sns_legend_off_state)
        else:
            plot_parameters = plot_json[self.selected_graph].copy()
            plot_parameters["legend"]["seaborn_legends"]["legend_off"] = self.sns_legend_off_state
            self.plot_manager.insert_plot_parameter(plot_parameters)
        self.graph_display.show_graph()

class seaborn_legend_markers_adjustment_section(QWidget):
    def __init__(self,selected_graph,graph_display):
        super().__init__()
        self.selected_graph = selected_graph
        self.graph_display = graph_display
        self.plot_manager = PlotManager()

        self.available_markers = [".", ",", "o", "v", "^", "<", ">", "1", "2", "3", "4",
                                "8", "s", "p", "P", "*", "h", "H", "+", "x", "X",
                                "D", "d", "|", "_"]

        self.markers = ""
        self.markers_dictionary = dict()
        self.markers_dictionary_key = ""
        self.markers_dictionary_value = ""
        self.initial_markers_argument = True

        #-----Seaborn Legend Markers Screen-----
        self.sns_legend_markers_screen = QWidget()
        self.sns_legend_markers_screen.setObjectName("sns_legend_markers_screen")
        self.sns_legend_markers_screen.setStyleSheet("""
            QWidget#sns_legend_markers_screen{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #f5f5ff,
                    stop:0.5 #f7f5fc,
                    stop:1 #f0f0ff
                );
                border: 2px solid black;
                border-radius: 16px;
            }       
        """)

        #-----Markers Instruction Widget-----
        self.markers_instruction_widget = QWidget()
        self.markers_instruction_widget.setObjectName("markers_instruction_widget")
        self.markers_instruction_widget.setStyleSheet("""
            QWidget#markers_instruction_widget{
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

        self.markers_instruction_label = QLabel("Select the hue or style first")
        self.markers_instruction_label.setObjectName("markers_instruction_label")
        self.markers_instruction_label.setWordWrap(True)
        self.markers_instruction_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.markers_instruction_label.setStyleSheet("""
            QLabel#markers_instruction_label{
                font-family: "SF Pro Display";
                font-weight: 600;
                font-size: 24px;
                padding: 6px;
                color: black;
                border: none;
                background: transparent; 
            }
        """)

        markers_instruction_widget_layout = QVBoxLayout(self.markers_instruction_widget)
        markers_instruction_widget_layout.addWidget(self.markers_instruction_label)
        markers_instruction_widget_layout.setContentsMargins(0,0,0,0)
        markers_instruction_widget_layout.setSpacing(0)

        #-----Turn Markers on/off Button-----
        self.turn_markers_on_off_button = QPushButton()
        self.turn_markers_on_off_button.setObjectName("turn_markers_on_off_button")
        self.turn_markers_on_off_button.setStyleSheet("""
            QPushButton#turn_markers_on_off_button{
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
                font-size: 16px;
                padding: 6px;
                color: black;
            }
            QPushButton#turn_markers_on_off_button:hover{
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

        self.turn_markers_on_off_label = QLabel("Turn Markers Off")
        self.turn_markers_on_off_label.setObjectName("turn_markers_on_off_label")
        self.turn_markers_on_off_label.setWordWrap(True)
        self.turn_markers_on_off_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.turn_markers_on_off_label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.turn_markers_on_off_label.setStyleSheet("""
            QLabel#turn_markers_on_off_label{
                font-family: "SF Pro Display";
                font-weight: 600;
                font-size: 24px;
                padding: 6px;
                color: black;
                border: none;
                background: transparent;
            }
        """)

        turn_markers_on_off_layout = QVBoxLayout(self.turn_markers_on_off_button)
        turn_markers_on_off_layout.addWidget(self.turn_markers_on_off_label)
        turn_markers_on_off_layout.setContentsMargins(0,0,0,0)
        turn_markers_on_off_layout.setSpacing(0)

        #-----Select Single Marker Button-----
        self.select_single_markers_button = QPushButton()
        self.select_single_markers_button.setObjectName("select_single_markers_button")
        self.select_single_markers_button.setStyleSheet("""
            QPushButton#select_single_markers_button{
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
                font-size: 16px;
                padding: 6px;
                color: black;
            }
            QPushButton#select_single_markers_button:hover{
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

        self.select_single_markers_label = QLabel("Select Single Marker")
        self.select_single_markers_label.setObjectName("select_single_markers_label")
        self.select_single_markers_label.setWordWrap(True)
        self.select_single_markers_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.select_single_markers_label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.select_single_markers_label.setStyleSheet("""
            QLabel#select_single_markers_label{
                font-family: "SF Pro Display";
                font-weight: 600;
                font-size: 24px;
                padding: 6px;
                color: black;
                border: none;
                background: transparent;
            }
        """)

        select_single_markers_button_layout = QVBoxLayout(self.select_single_markers_button)
        select_single_markers_button_layout.addWidget(self.select_single_markers_label)
        select_single_markers_button_layout.setContentsMargins(0,0,0,0)
        select_single_markers_button_layout.setSpacing(0)

        #-----Select Multiple Marker Button-----
        self.select_multiple_markers_button = QPushButton()
        self.select_multiple_markers_button.setObjectName("select_multiple_markers_button")
        self.select_multiple_markers_button.setStyleSheet("""
            QPushButton#select_multiple_markers_button{
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
                font-size: 16px;
                padding: 6px;
                color: black;
            }
            QPushButton#select_multiple_markers_button:hover{
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

        self.select_multiple_markers_label = QLabel("Select Multiple Marker")
        self.select_multiple_markers_label.setObjectName("select_multiple_markers_label")
        self.select_multiple_markers_label.setWordWrap(True)
        self.select_multiple_markers_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.select_multiple_markers_label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.select_multiple_markers_label.setStyleSheet("""
            QLabel#select_multiple_markers_label{
                font-family: "SF Pro Display";
                font-weight: 600;
                font-size: 24px;
                padding: 6px;
                color: black;
                border: none;
                background: transparent;
            }
        """)

        select_multiple_markers_button_layout = QVBoxLayout(self.select_multiple_markers_button)
        select_multiple_markers_button_layout.addWidget(self.select_multiple_markers_label)
        select_multiple_markers_button_layout.setContentsMargins(0,0,0,0)
        select_multiple_markers_button_layout.setSpacing(0)

        #-----Select Dictionary Markers Button-----
        self.select_dictionary_markers_button = QPushButton()
        self.select_dictionary_markers_button.setObjectName("select_dictionary_markers_button")
        self.select_dictionary_markers_button.setStyleSheet("""
            QPushButton#select_dictionary_markers_button{
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
                font-size: 16px;
                padding: 6px;
                color: black;
            }
            QPushButton#select_dictionary_markers_button:hover{
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

        self.select_dictionary_markers_label = QLabel("Select Dictionay Marker")
        self.select_dictionary_markers_label.setObjectName("select_dictionary_markers_label")
        self.select_dictionary_markers_label.setWordWrap(True)
        self.select_dictionary_markers_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.select_dictionary_markers_label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.select_dictionary_markers_label.setStyleSheet("""
            QLabel#select_dictionary_markers_label{
                font-family: "SF Pro Display";
                font-weight: 600;
                font-size: 24px;
                padding: 6px;
                color: black;
                border: none;
                background: transparent;
            }
        """)

        select_dictionary_markers_button_layout = QVBoxLayout(self.select_dictionary_markers_button)
        select_dictionary_markers_button_layout.addWidget(self.select_dictionary_markers_label)
        select_dictionary_markers_button_layout.setContentsMargins(0,0,0,0)
        select_dictionary_markers_button_layout.setSpacing(0)

        #-----Set the size of each button-----
        self.turn_markers_on_off_button.setMinimumHeight(70)
        self.select_single_markers_button.setMinimumHeight(70)
        self.select_multiple_markers_button.setMinimumHeight(70)
        self.select_dictionary_markers_button.setMinimumHeight(70)

        #-----Connect cach button to it's associated function-----
        self.turn_markers_on_off_button.clicked.connect(self.turn_markers_on_and_off)
        self.select_single_markers_button.clicked.connect(self.change_to_single_markers_screen)
        self.select_multiple_markers_button.clicked.connect(self.change_to_multiple_markers_screen)
        self.select_dictionary_markers_button.clicked.connect(self.change_to_dictonary_markers_screen)

        #-----Seaborn Legend Markers Screen Layout-----
        sns_legend_markers_screen_layout = QVBoxLayout(self.sns_legend_markers_screen)
        sns_legend_markers_screen_layout.addWidget(self.turn_markers_on_off_button)
        sns_legend_markers_screen_layout.addWidget(self.select_single_markers_button)
        sns_legend_markers_screen_layout.addWidget(self.select_multiple_markers_button)
        sns_legend_markers_screen_layout.addWidget(self.select_dictionary_markers_button)
        sns_legend_markers_screen_layout.setContentsMargins(10,10,10,10)
        sns_legend_markers_screen_layout.setSpacing(10)
        sns_legend_markers_screen_layout.addStretch()

        #-----Seaborn Legend Select Single Markers Screen-----
        self.select_single_markers_screen = QWidget()
        self.select_single_markers_screen.setObjectName("select_single_markers_screen")
        self.select_single_markers_screen.setStyleSheet(""" 
            QWidget#select_single_markers_screen{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #f5f5ff,
                    stop:0.5 #f7f5fc,
                    stop:1 #f0f0ff
                );
                border: 2px solid black;
                border-radius: 16px;
            }     
        """)
        self.create_select_single_markers_screen()
        self.select_single_markers_screen.hide()

        #-----Seaborn Legend Multiple Markers Screen-----
        self.select_multiple_markers_screen = QWidget()
        self.select_multiple_markers_screen.setObjectName("select_multiple_markers_screen")
        self.select_multiple_markers_screen.setStyleSheet("""
            QWidget#select_multiple_markers_screen{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #f5f5ff,
                    stop:0.5 #f7f5fc,
                    stop:1 #f0f0ff
                );
                border: 2px solid black;
                border-radius: 16px;
            }  
        """)
        self.create_select_multiple_markers_screen()
        self.select_multiple_markers_screen.hide()

        #-----Seaborn Legend Dictionary Markers Screen----
        self.select_dictionary_markers_screen = QWidget()
        self.select_dictionary_markers_screen.setObjectName("select_dictionary_markers_screen")
        self.select_dictionary_markers_screen.setStyleSheet("""
            QWidget#select_dictionary_markers_screen{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #f5f5ff,
                    stop:0.5 #f7f5fc,
                    stop:1 #f0f0ff
                );
                border: 2px solid black;
                border-radius: 16px;
            }  
        """)
        self.create_select_dictionary_markers_screen()
        self.select_dictionary_markers_screen.hide()

        #-----All Available Screens-----
        self.current_screen_idx = 0
        self.available_screens = [self.sns_legend_markers_screen,self.select_single_markers_screen,
                                self.select_multiple_markers_screen,self.select_dictionary_markers_screen]

        #-----Add All the Screens to the Main Widget-----
        main_layout = QVBoxLayout(self)
        for screen in self.available_screens:
            main_layout.addWidget(screen)

        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0,0,0,0)

        #-----Keyboard Shortcuts-----
        previous_screen_shortcut = QShortcut(QKeySequence("left"),self)
        previous_screen_shortcut.activated.connect(self.change_to_home_screen)

    def create_select_single_markers_screen(self):
        select_single_markers_screen_layout = QVBoxLayout(self.select_single_markers_screen)

        self.single_select_markers_list_view = QListView()
        self.single_select_markers_model = QStringListModel(self.available_markers)

        self.single_select_markers_list_view.setModel(self.single_select_markers_model)
        self.single_select_markers_list_view.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.single_select_markers_list_view.setObjectName("single_select_markers_list_view")
        self.single_select_markers_list_view.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)

        class CustomDelegate(QStyledItemDelegate):
            def paint(self, painter, option, index):
                option.displayAlignment = Qt.AlignmentFlag.AlignCenter
                font = QFont("SF Pro Display", 24)
                font.setWeight(600)
                option.font = font
                super().paint(painter, option, index)
        
        self.single_select_markers_list_view.setItemDelegate(CustomDelegate())

        self.single_select_markers_list_view.setStyleSheet("""
            QListView#single_select_markers_list_view{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #f5f5ff,
                    stop:0.5 #f7f5fc,
                    stop:1 #f0f0ff
                );
                border: transparent;
                border-radius: 16px;
            }
            QListView#single_select_markers_list_view::item {
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
            QListView#single_select_markers_list_view::item:selected {
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
            QListView#single_select_markers_list_view::item:hover {
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

        self.single_select_markers_list_view.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.single_select_markers_list_view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.single_select_markers_list_view.setSpacing(3)

        self.single_select_markers_list_view.clicked.connect(self.change_single_select_marker)
        select_single_markers_screen_layout.addWidget(self.single_select_markers_list_view)

        # Add margins and spacing to make it look good and push content to the top
        select_single_markers_screen_layout.setContentsMargins(10, 10, 10, 10)

    def create_select_multiple_markers_screen(self):
        select_multiple_markers_screen_layout = QVBoxLayout(self.select_multiple_markers_screen)

        self.multiple_select_markers_list_view = QListView()
        self.multiple_select_markers_list_view.setSelectionMode(QListView.SelectionMode.MultiSelection)
        self.multiple_select_markers_model = QStringListModel(self.available_markers)

        self.multiple_select_markers_list_view.setModel(self.multiple_select_markers_model)
        self.multiple_select_markers_list_view.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.multiple_select_markers_list_view.setObjectName("multiple_select_markers_list_view")
        self.multiple_select_markers_list_view.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)

        class CustomDelegate(QStyledItemDelegate):
            def paint(self, painter, option, index):
                option.displayAlignment = Qt.AlignmentFlag.AlignCenter
                font = QFont("SF Pro Display", 24)
                font.setWeight(600)
                option.font = font
                super().paint(painter, option, index)
        
        self.multiple_select_markers_list_view.setItemDelegate(CustomDelegate())

        self.multiple_select_markers_list_view.setStyleSheet("""
            QListView#multiple_select_markers_list_view{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #f5f5ff,
                    stop:0.5 #f7f5fc,
                    stop:1 #f0f0ff
                );
                border: transparent;
                border-radius: 16px;
            }
            QListView#multiple_select_markers_list_view::item {
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
            QListView#multiple_select_markers_list_view::item:selected {
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
            QListView#multiple_select_markers_list_view::item:hover {
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

        self.multiple_select_markers_list_view.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.multiple_select_markers_list_view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.multiple_select_markers_list_view.setSpacing(3)

        self.multiple_select_markers_list_view.selectionModel().selectionChanged.connect(self.change_multiple_select_marker)
        select_multiple_markers_screen_layout.addWidget(self.multiple_select_markers_list_view)

        # Add margins and spacing to make it look good and push content to the top
        select_multiple_markers_screen_layout.setContentsMargins(10, 10, 10, 10)

    def create_select_dictionary_markers_screen(self):
        select_dictionary_markers_screen_layout = QVBoxLayout(self.select_dictionary_markers_screen) 

        self.select_dictionary_markers_key_input = QLineEdit()
        self.select_dictionary_markers_key_input.setObjectName("select_dictionary_markers_key_input")
        self.select_dictionary_markers_key_input.setPlaceholderText("Key:")
        self.select_dictionary_markers_key_input.setStyleSheet("""
            QLineEdit#select_dictionary_markers_key_input{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #f5f5ff,
                    stop:0.5 #f7f5fc,
                    stop:1 #f0f0ff
                );
                color: black;
                font-size: 24pt;
                border: 2px solid black;
                border-radius: 16px;
            }
        """)
        self.select_dictionary_markers_key_input.textChanged.connect(self.change_dictionary_key_marker)
        self.select_dictionary_markers_key_input.setMinimumHeight(50)
        
        self.dictionary_select_markers_list_view = QListView()
        self.dictionary_select_markers_model = QStringListModel(self.available_markers)

        self.dictionary_select_markers_list_view.setModel(self.multiple_select_markers_model)
        self.dictionary_select_markers_list_view.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.dictionary_select_markers_list_view.setObjectName("dictionary_select_markers_list_view")
        self.dictionary_select_markers_list_view.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)

        class CustomDelegate(QStyledItemDelegate):
            def paint(self, painter, option, index):
                option.displayAlignment = Qt.AlignmentFlag.AlignCenter
                font = QFont("SF Pro Display", 24)
                font.setWeight(600)
                option.font = font
                super().paint(painter, option, index)
        
        self.dictionary_select_markers_list_view.setItemDelegate(CustomDelegate())

        self.dictionary_select_markers_list_view.setStyleSheet("""
            QListView#dictionary_select_markers_list_view{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #f5f5ff,
                    stop:0.5 #f7f5fc,
                    stop:1 #f0f0ff
                );
                border: transparent;
                border-radius: 16px;
            }
            QListView#dictionary_select_markers_list_view::item {
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
            QListView#dictionary_select_markers_list_view::item:selected {
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
            QListView#dictionary_select_markers_list_view::item:hover {
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

        self.dictionary_select_markers_list_view.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.dictionary_select_markers_list_view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.dictionary_select_markers_list_view.setSpacing(3)

        self.dictionary_select_markers_list_view.clicked.connect(self.change_dictionary_value_marker)

        select_dictionary_markers_screen_layout.addWidget(self.select_dictionary_markers_key_input)
        select_dictionary_markers_screen_layout.addWidget(self.dictionary_select_markers_list_view)
        select_dictionary_markers_screen_layout.setContentsMargins(10,10,10,10)
        select_dictionary_markers_screen_layout.setSpacing(10)

    def change_to_home_screen(self):
        self.available_screens[self.current_screen_idx].hide()
        self.current_screen_idx = 0
        self.available_screens[self.current_screen_idx].show()

    def change_to_single_markers_screen(self):
        self.available_screens[self.current_screen_idx].hide()
        self.current_screen_idx = 1
        self.available_screens[self.current_screen_idx].show()

    def change_to_multiple_markers_screen(self):
        self.available_screens[self.current_screen_idx].hide()
        self.current_screen_idx = 2
        self.available_screens[self.current_screen_idx].show()

    def change_to_dictonary_markers_screen(self):
        self.available_screens[self.current_screen_idx].hide()
        self.current_screen_idx = 3
        self.available_screens[self.current_screen_idx].show()

    def turn_markers_on_and_off(self):
        self.initial_markers_argument = not self.initial_markers_argument
        if (self.initial_markers_argument):
            self.turn_markers_on_off_label.setText("Turn Markers Off")
        else:
            self.turn_markers_on_off_label.setText("Turn Markers On")
        self.markers = self.initial_markers_argument
        self.update_markers()

    def change_single_select_marker(self,index):
        self.markers = self.multiple_select_markers_model.data(index, Qt.ItemDataRole.DisplayRole)
        self.update_markers()
    
    def change_multiple_select_marker(self):
        selected_indexes = self.multiple_select_markers_list_view.selectedIndexes()
        self.markers = [index.data() for index in selected_indexes]
        self.update_markers()

    def change_dictionary_key_marker(self):
        self.markers_dictionary_key = self.select_dictionary_markers_key_input.text().strip()
        self.change_dictionary_select_marker()

    def change_dictionary_value_marker(self,index):
        self.markers_dictionary_value = self.dictionary_select_markers_model.data(index,Qt.ItemDataRole.DisplayRole)
        self.change_dictionary_select_marker()
        self.select_dictionary_markers_key_input.clear()

    def change_dictionary_select_marker(self):
        if (self.markers_dictionary_key != "" and self.markers_dictionary_value != ""):
            dictionary_keys = list(self.markers_dictionary.keys())
            dictionary_values = list(self.markers_dictionary.values())
            if (self.markers_dictionary_key not in dictionary_keys and self.markers_dictionary_value not in dictionary_values):
                self.markers_dictionary[self.markers_dictionary_key] = self.markers_dictionary_value
                self.markers = self.markers_dictionary
                self.update_markers()

    def update_markers(self):
        db = self.plot_manager.get_db()
        if (db != []):
            self.plot_manager.update_seaborn_legend("markers",self.markers)
        else:
            plot_parameters = plot_json[self.selected_graph].copy()
            plot_parameters["legend"]["seaborn_legends"]["markers"] = self.markers
            self.plot_manager.insert_plot_parameter(plot_parameters)
        self.graph_display.show_graph()

    def reset_marker_selection(self):
        self.markers = []
        self.markers_dictionary = dict()
        self.markers_dictionary_key = ""
        self.markers_dictionary_value = ""

    def showEvent(self,event):
        super().showEvent(event)
        self.reset_marker_selection()
        self.change_to_home_screen()

class seaborn_legend_dashes_adjustment_section(QWidget):
    def __init__(self,selected_graph,graph_display):
        super().__init__()
        self.selected_graph = selected_graph
        self.graph_display = graph_display
        self.plot_manager = PlotManager()

        self.available_dashes = ["solid (-)","dashed (--)","dashdot (-.)","dotted (:)","None (—)"]
        self.dashes = list(map(lambda x:x[x.index("(")+1:x.index(")")],self.available_dashes))

        self.dashes = ""
        self.dashes_dictionary = dict()
        self.dashes_dictionary_key = ""
        self.dashes_dictionary_value = ""
        self.initial_dashes_argument = True

        #-----Valid Single Custom Dashes Widget and Label-----
        self.valid_single_custom_dashes_widget = QWidget()
        self.valid_single_custom_dashes_widget.setObjectName("valid_single_custom_dashes_widget")
        self.valid_single_custom_dashes_widget.setStyleSheet("""
            QWidget#valid_single_custom_dashes_widget{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(94, 255, 234, 1),   
                    stop:0.3 rgba(63, 252, 180, 1), 
                    stop:0.6 rgba(150, 220, 255, 1),  
                    stop:1 rgba(180, 200, 255, 1)  
                );
                border: 2px solid black;
                border-radius: 16px;
            }
        """)

        self.valid_single_custom_dashes_label = QLabel("Valid Dashes")
        self.valid_single_custom_dashes_label.setObjectName("valid_single_custom_dashes_label")
        self.valid_single_custom_dashes_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.valid_single_custom_dashes_label.setStyleSheet("""
            QLabel#valid_single_custom_dashes_label{
                font-family: "SF Pro Display";
                font-weight: 600;
                font-size: 24px;
                padding: 6px;
                color: black;
                border: none;
                background: transparent;
            }
        """)
        
        valid_single_custom_dashes_widget_layout = QVBoxLayout(self.valid_single_custom_dashes_widget)
        valid_single_custom_dashes_widget_layout.addWidget(self.valid_single_custom_dashes_label)
        valid_single_custom_dashes_widget_layout.setContentsMargins(0,0,0,0)
        valid_single_custom_dashes_widget_layout.setSpacing(0)

        #-----Invalid Custom Dashes Widget and Label-----
        self.invalid_single_custom_dashes_widget = QWidget()
        self.invalid_single_custom_dashes_widget.setObjectName("invalid_single_custom_dashes_widget")
        self.invalid_single_custom_dashes_widget.setStyleSheet("""
            QWidget#invalid_single_custom_dashes_widget{
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

        self.invalid_single_custom_dashes_label = QLabel("Invalid Dashes")
        self.invalid_single_custom_dashes_label.setObjectName("invalid_single_custom_dashes_label")
        self.invalid_single_custom_dashes_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.invalid_single_custom_dashes_label.setStyleSheet("""
            QLabel#invalid_single_custom_dashes_label{
                font-family: "SF Pro Display";
                font-weight: 600;
                font-size: 24px;
                padding: 6px;
                color: black;
                border: none;
                background: transparent;
            }
        """)
        
        invalid_single_custom_dashes_widget_layout = QVBoxLayout(self.invalid_single_custom_dashes_widget)
        invalid_single_custom_dashes_widget_layout.addWidget(self.invalid_single_custom_dashes_label)
        invalid_single_custom_dashes_widget_layout.setContentsMargins(0,0,0,0)
        invalid_single_custom_dashes_widget_layout.setSpacing(0)

        #-----Set the Height of both widgets and hide them-----
        self.valid_single_custom_dashes_widget.setMinimumHeight(50)
        self.invalid_single_custom_dashes_widget.setMinimumHeight(50)
        
        self.valid_single_custom_dashes_widget.hide()
        self.invalid_single_custom_dashes_widget.hide()

        #-----Valid Multiple Custom Dashes Widget and Label-----
        self.valid_multiple_custom_dashes_widget = QWidget()
        self.valid_multiple_custom_dashes_widget.setObjectName("valid_multiple_custom_dashes_widget")
        self.valid_multiple_custom_dashes_widget.setStyleSheet("""
            QWidget#valid_multiple_custom_dashes_widget{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(94, 255, 234, 1),   
                    stop:0.3 rgba(63, 252, 180, 1), 
                    stop:0.6 rgba(150, 220, 255, 1),  
                    stop:1 rgba(180, 200, 255, 1)  
                );
                border: 2px solid black;
                border-radius: 16px;
            }
        """)

        self.valid_multiple_custom_dashes_label = QLabel("Valid Dashes")
        self.valid_multiple_custom_dashes_label.setObjectName("valid_multiple_custom_dashes_label")
        self.valid_multiple_custom_dashes_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.valid_multiple_custom_dashes_label.setStyleSheet("""
            QLabel#valid_multiple_custom_dashes_label{
                font-family: "SF Pro Display";
                font-weight: 600;
                font-size: 24px;
                padding: 6px;
                color: black;
                border: none;
                background: transparent;
            }
        """)
        
        valid_multiple_custom_dashes_widget_layout = QVBoxLayout(self.valid_multiple_custom_dashes_widget)
        valid_multiple_custom_dashes_widget_layout.addWidget(self.valid_multiple_custom_dashes_label)
        valid_multiple_custom_dashes_widget_layout.setContentsMargins(0,0,0,0)
        valid_multiple_custom_dashes_widget_layout.setSpacing(0)

        #-----Invalid Custom Dashes Widget and Label-----
        self.invalid_multiple_custom_dashes_widget = QWidget()
        self.invalid_multiple_custom_dashes_widget.setObjectName("invalid_multiple_custom_dashes_widget")
        self.invalid_multiple_custom_dashes_widget.setStyleSheet("""
            QWidget#invalid_multiple_custom_dashes_widget{
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

        self.invalid_multiple_custom_dashes_label = QLabel("Invalid Dashes")
        self.invalid_multiple_custom_dashes_label.setObjectName("invalid_multiple_custom_dashes_label")
        self.invalid_multiple_custom_dashes_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.invalid_multiple_custom_dashes_label.setStyleSheet("""
            QLabel#invalid_multiple_custom_dashes_label{
                font-family: "SF Pro Display";
                font-weight: 600;
                font-size: 24px;
                padding: 6px;
                color: black;
                border: none;
                background: transparent;
            }
        """)
        
        invalid_multiple_custom_dashes_widget_layout = QVBoxLayout(self.invalid_multiple_custom_dashes_widget)
        invalid_multiple_custom_dashes_widget_layout.addWidget(self.invalid_multiple_custom_dashes_label)
        invalid_multiple_custom_dashes_widget_layout.setContentsMargins(0,0,0,0)
        invalid_multiple_custom_dashes_widget_layout.setSpacing(0)

        #-----Set the Height of both widgets and hide them-----
        self.valid_multiple_custom_dashes_widget.setMinimumHeight(50)
        self.invalid_multiple_custom_dashes_widget.setMinimumHeight(50)
        
        self.valid_multiple_custom_dashes_widget.hide()
        self.invalid_multiple_custom_dashes_widget.hide()

        #-----Valid Dictionary Custom Dashes Widget and Label-----
        self.valid_dictionary_custom_dashes_widget = QWidget()
        self.valid_dictionary_custom_dashes_widget.setObjectName("valid_dictionary_custom_dashes_widget")
        self.valid_dictionary_custom_dashes_widget.setStyleSheet("""
            QWidget#valid_dictionary_custom_dashes_widget{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(94, 255, 234, 1),   
                    stop:0.3 rgba(63, 252, 180, 1), 
                    stop:0.6 rgba(150, 220, 255, 1),  
                    stop:1 rgba(180, 200, 255, 1)  
                );
                border: 2px solid black;
                border-radius: 16px;
            }
        """)

        self.valid_dictionary_custom_dashes_label = QLabel("Valid Dashes")
        self.valid_dictionary_custom_dashes_label.setObjectName("valid_dictionary_custom_dashes_label")
        self.valid_dictionary_custom_dashes_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.valid_dictionary_custom_dashes_label.setStyleSheet("""
            QLabel#valid_dictionary_custom_dashes_label{
                font-family: "SF Pro Display";
                font-weight: 600;
                font-size: 24px;
                padding: 6px;
                color: black;
                border: none;
                background: transparent;
            }
        """)
        
        valid_dictionary_custom_dashes_widget_layout = QVBoxLayout(self.valid_dictionary_custom_dashes_widget)
        valid_dictionary_custom_dashes_widget_layout.addWidget(self.valid_dictionary_custom_dashes_label)
        valid_dictionary_custom_dashes_widget_layout.setContentsMargins(0,0,0,0)
        valid_dictionary_custom_dashes_widget_layout.setSpacing(0)

        #-----Invalid Custom Dashes Widget and Label-----
        self.invalid_dictionary_custom_dashes_widget = QWidget()
        self.invalid_dictionary_custom_dashes_widget.setObjectName("invalid_dictionary_custom_dashes_widget")
        self.invalid_dictionary_custom_dashes_widget.setStyleSheet("""
            QWidget#invalid_dictionary_custom_dashes_widget{
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

        self.invalid_dictionary_custom_dashes_label = QLabel("Invalid Dashes")
        self.invalid_dictionary_custom_dashes_label.setObjectName("invalid_dictionary_custom_dashes_label")
        self.invalid_dictionary_custom_dashes_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.invalid_dictionary_custom_dashes_label.setStyleSheet("""
            QLabel#invalid_dictionary_custom_dashes_label{
                font-family: "SF Pro Display";
                font-weight: 600;
                font-size: 24px;
                padding: 6px;
                color: black;
                border: none;
                background: transparent;
            }
        """)
        
        invalid_dictionary_custom_dashes_widget_layout = QVBoxLayout(self.invalid_dictionary_custom_dashes_widget)
        invalid_dictionary_custom_dashes_widget_layout.addWidget(self.invalid_dictionary_custom_dashes_label)
        invalid_dictionary_custom_dashes_widget_layout.setContentsMargins(0,0,0,0)
        invalid_dictionary_custom_dashes_widget_layout.setSpacing(0)

        #-----Set the Height of both widgets and hide them-----
        self.valid_dictionary_custom_dashes_widget.setMinimumHeight(50)
        self.invalid_dictionary_custom_dashes_widget.setMinimumHeight(50)
        
        self.valid_dictionary_custom_dashes_widget.hide()
        self.invalid_dictionary_custom_dashes_widget.hide()

        #-----Seaborn Legend Dashes Screen-----
        self.sns_legend_dashes_screen = QWidget()
        self.sns_legend_dashes_screen.setObjectName("sns_legend_dashes_screen")
        self.sns_legend_dashes_screen.setStyleSheet("""
            QWidget#sns_legend_dashes_screen{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #f5f5ff,
                    stop:0.5 #f7f5fc,
                    stop:1 #f0f0ff
                );
                border: 2px solid black;
                border-radius: 16px;
            }       
        """)
        self.sns_legend_dashes_screen.hide()

        #----Turn Dashes on/off Button-----
        self.turn_dashes_on_off_button = QPushButton()
        self.turn_dashes_on_off_button.setObjectName("turn_dashes_on_off_button")
        self.turn_dashes_on_off_button.setStyleSheet("""
            QPushButton#turn_dashes_on_off_button{
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
                font-size: 16px;
                padding: 6px;
                color: black;
            }
            QPushButton#turn_dashes_on_off_button:hover{
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

        self.turn_dashes_on_off_label = QLabel("Turn Dashes Off")
        self.turn_dashes_on_off_label.setObjectName("turn_dashes_on_off_label")
        self.turn_dashes_on_off_label.setWordWrap(True)
        self.turn_dashes_on_off_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.turn_dashes_on_off_label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.turn_dashes_on_off_label.setStyleSheet("""
            QLabel#turn_dashes_on_off_label{
                font-family: "SF Pro Display";
                font-weight: 600;
                font-size: 24px;
                padding: 6px;
                color: black;
                border: none;
                background: transparent;
            }
        """)

        turn_dashes_on_off_layout = QVBoxLayout(self.turn_dashes_on_off_button)
        turn_dashes_on_off_layout.addWidget(self.turn_dashes_on_off_label)
        turn_dashes_on_off_layout.setContentsMargins(0,0,0,0)
        turn_dashes_on_off_layout.setSpacing(0)

        #-----Select Single Dashes Button-----
        self.select_single_dashes_button = QPushButton()
        self.select_single_dashes_button.setObjectName("select_single_dashes_button")
        self.select_single_dashes_button.setStyleSheet("""
            QPushButton#select_single_dashes_button{
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
                font-size: 16px;
                padding: 6px;
                color: black;
            }
            QPushButton#select_single_dashes_button:hover{
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

        self.select_single_dashes_label = QLabel("Select Single Dashes")
        self.select_single_dashes_label.setObjectName("select_single_dashes_label")
        self.select_single_dashes_label.setWordWrap(True)
        self.select_single_dashes_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.select_single_dashes_label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.select_single_dashes_label.setStyleSheet("""
            QLabel#select_single_dashes_label{
                font-family: "SF Pro Display";
                font-weight: 600;
                font-size: 24px;
                padding: 6px;
                color: black;
                border: none;
                background: transparent;
            }
        """)

        select_single_dashes_button_layout = QVBoxLayout(self.select_single_dashes_button)
        select_single_dashes_button_layout.addWidget(self.select_single_dashes_label)
        select_single_dashes_button_layout.setContentsMargins(0,0,0,0)
        select_single_dashes_button_layout.setSpacing(0)

        #-----Select Multiple Dashes Button-----
        self.select_multiple_dashes_button = QPushButton()
        self.select_multiple_dashes_button.setObjectName("select_multiple_dashes_button")
        self.select_multiple_dashes_button.setStyleSheet("""
            QPushButton#select_multiple_dashes_button{
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
                font-size: 16px;
                padding: 6px;
                color: black;
            }
            QPushButton#select_multiple_dashes_button:hover{
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

        self.select_multiple_dashes_label = QLabel("Select Multiple Dashes")
        self.select_multiple_dashes_label.setObjectName("select_multiple_dashes_label")
        self.select_multiple_dashes_label.setWordWrap(True)
        self.select_multiple_dashes_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.select_multiple_dashes_label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.select_multiple_dashes_label.setStyleSheet("""
            QLabel#select_multiple_dashes_label{
                font-family: "SF Pro Display";
                font-weight: 600;
                font-size: 24px;
                padding: 6px;
                color: black;
                border: none;
                background: transparent;
            }
        """)

        select_multiple_dashes_button_layout = QVBoxLayout(self.select_multiple_dashes_button)
        select_multiple_dashes_button_layout.addWidget(self.select_multiple_dashes_label)
        select_multiple_dashes_button_layout.setContentsMargins(0,0,0,0)
        select_multiple_dashes_button_layout.setSpacing(0)

        #-----Select Dictionary Dashes Button-----
        self.select_dictionary_dashes_button = QPushButton()
        self.select_dictionary_dashes_button.setObjectName("select_dictionary_dashes_button")
        self.select_dictionary_dashes_button.setStyleSheet("""
            QPushButton#select_dictionary_dashes_button{
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
                font-size: 16px;
                padding: 6px;
                color: black;
            }
            QPushButton#select_dictionary_dashes_button:hover{
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

        self.select_dictionary_dashes_label = QLabel("Select Dictionay Dashes")
        self.select_dictionary_dashes_label.setObjectName("select_dictionary_dashes_label")
        self.select_dictionary_dashes_label.setWordWrap(True)
        self.select_dictionary_dashes_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.select_dictionary_dashes_label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.select_dictionary_dashes_label.setStyleSheet("""
            QLabel#select_dictionary_dashes_label{
                font-family: "SF Pro Display";
                font-weight: 600;
                font-size: 24px;
                padding: 6px;
                color: black;
                border: none;
                background: transparent;
            }
        """)

        select_dictionary_dashes_button_layout = QVBoxLayout(self.select_dictionary_dashes_button)
        select_dictionary_dashes_button_layout.addWidget(self.select_dictionary_dashes_label)
        select_dictionary_dashes_button_layout.setContentsMargins(0,0,0,0)
        select_dictionary_dashes_button_layout.setSpacing(0)

        #-----Set the size of each button-----
        self.turn_dashes_on_off_button.setMinimumHeight(70)
        self.select_single_dashes_button.setMinimumHeight(70)
        self.select_multiple_dashes_button.setMinimumHeight(70)
        self.select_dictionary_dashes_button.setMinimumHeight(70)

        #-----Connect cach button to it's associated function-----
        self.turn_dashes_on_off_button.clicked.connect(self.turn_dashes_on_and_off)
        self.select_single_dashes_button.clicked.connect(self.change_to_single_dashes_screen)
        self.select_multiple_dashes_button.clicked.connect(self.change_to_multiple_dashes_screen)
        self.select_dictionary_dashes_button.clicked.connect(self.change_to_dictionary_dashes_screen)

        #-----Seaborn Legend Dashes Screen Layout-----
        sns_legend_dashes_screen_layout = QVBoxLayout(self.sns_legend_dashes_screen)
        sns_legend_dashes_screen_layout.addWidget(self.turn_dashes_on_off_button)
        sns_legend_dashes_screen_layout.addWidget(self.select_single_dashes_button)
        sns_legend_dashes_screen_layout.addWidget(self.select_multiple_dashes_button)
        sns_legend_dashes_screen_layout.addWidget(self.select_dictionary_dashes_button)
        sns_legend_dashes_screen_layout.setContentsMargins(10,10,10,10)
        sns_legend_dashes_screen_layout.setSpacing(10)
        sns_legend_dashes_screen_layout.addStretch()

        #-----Seaborn Legend Select Single Dashes Screen-----
        self.select_single_dashes_screen = QWidget()
        self.select_single_dashes_screen.setObjectName("select_single_dashes_screen")
        self.select_single_dashes_screen.setStyleSheet("""
            QWidget#select_single_dashes_screen{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #f5f5ff,
                    stop:0.5 #f7f5fc,
                    stop:1 #f0f0ff
                );
                border: 2px solid black;
                border-radius: 16px;
            }
        """)
        self.select_single_dashes_screen.hide()

        #-----Seaborn Legend Select Single Premade Dashes Button-----
        self.select_single_premade_dashes_button = QPushButton()
        self.select_single_premade_dashes_button.setObjectName("select_single_premade_dashes_button")
        self.select_single_premade_dashes_button.setStyleSheet("""
            QPushButton#select_single_premade_dashes_button{
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
                font-size: 16px;
                padding: 6px;
                color: black;
            }
            QPushButton#select_single_premade_dashes_button:hover{
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

        self.select_single_premade_dashes_label = QLabel("Select Premade Dashes")
        self.select_single_premade_dashes_label.setObjectName("select_single_premade_dashes_label")
        self.select_single_premade_dashes_label.setWordWrap(True)
        self.select_single_premade_dashes_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.select_single_premade_dashes_label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.select_single_premade_dashes_label.setStyleSheet("""
            QLabel#select_single_premade_dashes_label{
                font-family: "SF Pro Display";
                font-weight: 600;
                font-size: 24px;
                padding: 6px;
                color: black;
                border: none;
                background: transparent;
            }
        """)

        select_single_premade_dashes_button_layout = QVBoxLayout(self.select_single_premade_dashes_button)
        select_single_premade_dashes_button_layout.addWidget(self.select_single_premade_dashes_label)
        select_single_premade_dashes_button_layout.setContentsMargins(0,0,0,0)
        select_single_premade_dashes_button_layout.setSpacing(0)

        #-----Seaborn Legend Select Single Premade Dashes Screen-----
        self.select_single_premade_dashes_screen = QWidget()
        self.select_single_premade_dashes_screen.setObjectName("select_single_premade_dashes_screen")
        self.select_single_premade_dashes_screen.setStyleSheet(""" 
            QWidget#select_single_premade_dashes_screen{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #f5f5ff,
                    stop:0.5 #f7f5fc,
                    stop:1 #f0f0ff
                );
                border: 2px solid black;
                border-radius: 16px;
            }     
        """)
        self.create_select_single_premade_dashes_screen()
        self.select_single_premade_dashes_screen.hide()

        #-----Seaborn Legend Select Custom Dashes Button-----
        self.select_single_custom_dashes_button = QPushButton()
        self.select_single_custom_dashes_button.setObjectName("select_single_custom_dashes_button")
        self.select_single_custom_dashes_button.setStyleSheet("""
            QPushButton#select_single_custom_dashes_button{
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
                font-size: 16px;
                padding: 6px;
                color: black;
            }
            QPushButton#select_single_custom_dashes_button:hover{
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

        self.select_single_custom_dashes_label = QLabel("Enter Custom Dashes")
        self.select_single_custom_dashes_label.setObjectName("select_single_custom_dashes_label")
        self.select_single_custom_dashes_label.setWordWrap(True)
        self.select_single_custom_dashes_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.select_single_custom_dashes_label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.select_single_custom_dashes_label.setStyleSheet("""
            QLabel#select_single_custom_dashes_label{
                font-family: "SF Pro Display";
                font-weight: 600;
                font-size: 24px;
                padding: 6px;
                color: black;
                border: none;
                background: transparent;
            }
        """)

        select_single_custom_dashes_button_layout = QVBoxLayout(self.select_single_custom_dashes_button)
        select_single_custom_dashes_button_layout.addWidget(self.select_single_custom_dashes_label)
        select_single_custom_dashes_button_layout.setContentsMargins(0,0,0,0)
        select_single_custom_dashes_button_layout.setSpacing(0)

        #-----Seaborn Legend Select Custom Dashes Screen-----
        self.select_single_custom_dashes_screen = QWidget()
        self.select_single_custom_dashes_screen.setObjectName("select_single_custom_dashes_screen")
        self.select_single_custom_dashes_screen.setStyleSheet(""" 
            QWidget#select_single_custom_dashes_screen{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #f5f5ff,
                    stop:0.5 #f7f5fc,
                    stop:1 #f0f0ff
                );
                border: 2px solid black;
                border-radius: 16px;
            }     
        """)
        self.create_select_single_custom_dashes_screen()
        self.select_single_custom_dashes_screen.hide()

        #-----Connect the two buttons to its function-----
        self.select_single_premade_dashes_button.clicked.connect(self.change_to_select_single_premade_dashes_screen)
        self.select_single_custom_dashes_button.clicked.connect(self.change_to_select_single_custom_dashes_screen)

        #-----Control the size of the buttons -----
        self.select_single_premade_dashes_button.setMinimumHeight(60)
        self.select_single_custom_dashes_button.setMinimumHeight(60)

        #-----Seaborn Legend Select Single Dashes Layout-----
        single_dashes_screen_layout = QVBoxLayout(self.select_single_dashes_screen)
        single_dashes_screen_layout.addWidget(self.select_single_premade_dashes_button)
        single_dashes_screen_layout.addWidget(self.select_single_custom_dashes_button)
        single_dashes_screen_layout.setContentsMargins(10,10,10,10)
        single_dashes_screen_layout.setSpacing(5)
        single_dashes_screen_layout.addStretch()

        #-----Seaborn Legend Multiple Dashes Screen-----
        self.select_multiple_dashes_screen = QWidget()
        self.select_multiple_dashes_screen.setObjectName("select_multiple_dashes_screen")
        self.select_multiple_dashes_screen.setStyleSheet("""
            QWidget#select_multiple_dashes_screen{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #f5f5ff,
                    stop:0.5 #f7f5fc,
                    stop:1 #f0f0ff
                );
                border: 2px solid black;
                border-radius: 16px;
            }  
        """)
        self.select_multiple_dashes_screen.hide()

        #-----Seaborn Legend Multiple Premade Dashes Button-----
        self.select_multiple_premade_dashes_button = QPushButton()
        self.select_multiple_premade_dashes_button.setObjectName("select_multiple_premade_dashes_button")
        self.select_multiple_premade_dashes_button.setStyleSheet("""
            QPushButton#select_multiple_premade_dashes_button{
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
                font-size: 16px;
                padding: 6px;
                color: black;
            }
            QPushButton#select_multiple_premade_dashes_button:hover{
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

        self.select_multiple_premade_dashes_label = QLabel("Select Multiple Premade Dashes")
        self.select_multiple_premade_dashes_label.setObjectName("select_multiple_premade_dashes_label")
        self.select_multiple_premade_dashes_label.setWordWrap(True)
        self.select_multiple_premade_dashes_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.select_multiple_premade_dashes_label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.select_multiple_premade_dashes_label.setStyleSheet("""
            QLabel#select_multiple_premade_dashes_label{
                font-family: "SF Pro Display";
                font-weight: 600;
                font-size: 24px;
                padding: 6px;
                color: black;
                border: none;
                background: transparent;
            }
        """)

        select_multiple_premade_dashes_button_layout = QVBoxLayout(self.select_multiple_premade_dashes_button)
        select_multiple_premade_dashes_button_layout.addWidget(self.select_multiple_premade_dashes_label)
        select_multiple_premade_dashes_button_layout.setContentsMargins(0,0,0,0)
        select_multiple_premade_dashes_button_layout.setSpacing(0)

        #-----Seaborn Legend Multiple Premade Dashes Screen-----
        self.select_multiple_premade_dashes_screen = QWidget()
        self.select_multiple_premade_dashes_screen.setObjectName("select_multiple_premade_dashes_screen")
        self.select_multiple_premade_dashes_screen.setStyleSheet("""
            QWidget#select_multiple_premade_dashes_screen{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #f5f5ff,
                    stop:0.5 #f7f5fc,
                    stop:1 #f0f0ff
                );
                border: 2px solid black;
                border-radius: 16px;
            }  
        """)
        self.create_select_multiple_premade_dashes_screen()
        self.select_multiple_premade_dashes_screen.hide()

        #-----Seaborn Legend Multiple Custom Dashes Button-----
        self.select_multiple_custom_dashes_button = QPushButton()
        self.select_multiple_custom_dashes_button.setObjectName("select_multiple_custom_dashes_button")
        self.select_multiple_custom_dashes_button.setStyleSheet("""
            QPushButton#select_multiple_custom_dashes_button{
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
                font-size: 16px;
                padding: 6px;
                color: black;
            }
            QPushButton#select_multiple_custom_dashes_button:hover{
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

        self.select_multiple_custom_dashes_label = QLabel("Enter Multiple Custom Dashes")
        self.select_multiple_custom_dashes_label.setObjectName("select_multiple_custom_dashes_label")
        self.select_multiple_custom_dashes_label.setWordWrap(True)
        self.select_multiple_custom_dashes_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.select_multiple_custom_dashes_label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.select_multiple_custom_dashes_label.setStyleSheet("""
            QLabel#select_multiple_custom_dashes_label{
                font-family: "SF Pro Display";
                font-weight: 600;
                font-size: 24px;
                padding: 6px;
                color: black;
                border: none;
                background: transparent;
            }
        """)

        select_multiple_custom_dashes_button_layout = QVBoxLayout(self.select_multiple_custom_dashes_button)
        select_multiple_custom_dashes_button_layout.addWidget(self.select_multiple_custom_dashes_label)
        select_multiple_custom_dashes_button_layout.setContentsMargins(0,0,0,0)
        select_multiple_custom_dashes_button_layout.setSpacing(0)

        #-----Seaborn Legend Multiple Custom Dashes Screen-----
        self.select_multiple_custom_dashes_screen = QWidget()
        self.select_multiple_custom_dashes_screen.setObjectName("select_multiple_custom_dashes_screen")
        self.select_multiple_custom_dashes_screen.setStyleSheet("""
            QWidget#select_multiple_custom_dashes_screen{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #f5f5ff,
                    stop:0.5 #f7f5fc,
                    stop:1 #f0f0ff
                );
                border: 2px solid black;
                border-radius: 16px;
            }  
        """)
        self.create_select_multiple_custom_dashes_screen()
        self.select_multiple_custom_dashes_screen.hide()

        #-----Connect the two buttons to its function-----
        self.select_multiple_premade_dashes_button.clicked.connect(self.change_to_select_multiple_premade_dashes_screen)
        self.select_multiple_custom_dashes_button.clicked.connect(self.change_to_select_multiple_custom_dashes_screen)

        #-----Control the size of the buttons -----
        self.select_multiple_premade_dashes_button.setMinimumHeight(70)
        self.select_multiple_custom_dashes_button.setMinimumHeight(70)

        #-----Seaborn Legend Select Multiple Dashes Layout-----
        multiple_dashes_screen_layout = QVBoxLayout(self.select_multiple_dashes_screen)
        multiple_dashes_screen_layout.addWidget(self.select_multiple_premade_dashes_button)
        multiple_dashes_screen_layout.addWidget(self.select_multiple_custom_dashes_button)
        multiple_dashes_screen_layout.setContentsMargins(10,10,10,10)
        multiple_dashes_screen_layout.setSpacing(5)
        multiple_dashes_screen_layout.addStretch()

        #-----Seaborn Legend Dictionary Dashes Screen----
        self.select_dictionary_dashes_screen = QWidget()
        self.select_dictionary_dashes_screen.setObjectName("select_dictionary_dashes_screen")
        self.select_dictionary_dashes_screen.setStyleSheet("""
            QWidget#select_dictionary_dashes_screen{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #f5f5ff,
                    stop:0.5 #f7f5fc,
                    stop:1 #f0f0ff
                );
                border: 2px solid black;
                border-radius: 16px;
            }  
        """)
        self.select_dictionary_dashes_screen.hide()

        #-----Seaborn Legend Dictionary Premade Dashes Button-----
        self.select_dictionary_premade_dashes_button = QPushButton()
        self.select_dictionary_premade_dashes_button.setObjectName("select_dictionary_premade_dashes_button")
        self.select_dictionary_premade_dashes_button.setStyleSheet("""
            QPushButton#select_dictionary_premade_dashes_button{
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
                font-size: 16px;
                padding: 6px;
                color: black;
            }
            QPushButton#select_dictionary_premade_dashes_button:hover{
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

        self.select_dictionary_premade_dashes_label = QLabel("Enter Dictionary Premade Dashes")
        self.select_dictionary_premade_dashes_label.setObjectName("select_dictionary_premade_dashes_label")
        self.select_dictionary_premade_dashes_label.setWordWrap(True)
        self.select_dictionary_premade_dashes_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.select_dictionary_premade_dashes_label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.select_dictionary_premade_dashes_label.setStyleSheet("""
            QLabel#select_dictionary_premade_dashes_label{
                font-family: "SF Pro Display";
                font-weight: 600;
                font-size: 24px;
                padding: 6px;
                color: black;
                border: none;
                background: transparent;
            }
        """)

        select_dictionary_premade_dashes_button_layout = QVBoxLayout(self.select_dictionary_premade_dashes_button)
        select_dictionary_premade_dashes_button_layout.addWidget(self.select_dictionary_premade_dashes_label)
        select_dictionary_premade_dashes_button_layout.setContentsMargins(0,0,0,0)
        select_dictionary_premade_dashes_button_layout.setSpacing(0)

        #-----Seaborn Legend Dictionary Premade Dashes Screen----
        self.select_dictionary_premade_dashes_screen = QWidget()
        self.select_dictionary_premade_dashes_screen.setObjectName("select_dictionary_premade_dashes_screen")
        self.select_dictionary_premade_dashes_screen.setStyleSheet("""
            QWidget#select_dictionary_premade_dashes_screen{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #f5f5ff,
                    stop:0.5 #f7f5fc,
                    stop:1 #f0f0ff
                );
                border: 2px solid black;
                border-radius: 16px;
            }  
        """)
        self.create_select_dictionary_premade_dashes_screen()
        self.select_dictionary_premade_dashes_screen.hide()

        #-----Seaborn Legend Dictionary Custom Dashes Button-----
        self.select_dictionary_custom_dashes_button = QPushButton()
        self.select_dictionary_custom_dashes_button.setObjectName("select_dictionary_custom_dashes_button")
        self.select_dictionary_custom_dashes_button.setStyleSheet("""
            QPushButton#select_dictionary_custom_dashes_button{
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
                font-size: 16px;
                padding: 6px;
                color: black;
            }
            QPushButton#select_dictionary_custom_dashes_button:hover{
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

        self.select_dictionary_custom_dashes_label = QLabel("Enter Dictionary Custom Dashes")
        self.select_dictionary_custom_dashes_label.setObjectName("select_dictionary_custom_dashes_label")
        self.select_dictionary_custom_dashes_label.setWordWrap(True)
        self.select_dictionary_custom_dashes_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.select_dictionary_custom_dashes_label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.select_dictionary_custom_dashes_label.setStyleSheet("""
            QLabel#select_dictionary_custom_dashes_label{
                font-family: "SF Pro Display";
                font-weight: 600;
                font-size: 24px;
                padding: 6px;
                color: black;
                border: none;
                background: transparent;
            }
        """)

        select_dictionary_custom_dashes_button_layout = QVBoxLayout(self.select_dictionary_custom_dashes_button)
        select_dictionary_custom_dashes_button_layout.addWidget(self.select_dictionary_custom_dashes_label)
        select_dictionary_custom_dashes_button_layout.setContentsMargins(0,0,0,0)
        select_dictionary_custom_dashes_button_layout.setSpacing(0)

        #-----Seaborn Legend Dictionary Custom Dashes Screen----
        self.select_dictionary_custom_dashes_screen = QWidget()
        self.select_dictionary_custom_dashes_screen.setObjectName("select_dictionary_custom_dashes_screen")
        self.select_dictionary_custom_dashes_screen.setStyleSheet("""
            QWidget#select_dictionary_custom_dashes_screen{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #f5f5ff,
                    stop:0.5 #f7f5fc,
                    stop:1 #f0f0ff
                );
                border: 2px solid black;
                border-radius: 16px;
            }  
        """)
        self.create_select_dictionary_custom_dashes_screen()
        self.select_dictionary_custom_dashes_screen.hide()

        #-----Connect the two buttons to its function-----
        self.select_dictionary_premade_dashes_button.clicked.connect(self.change_to_select_dictionary_premade_dashes_screen)
        self.select_dictionary_custom_dashes_button.clicked.connect(self.change_to_select_dictionary_custom_dashes_screen)

        #-----Control the size of the buttons -----
        self.select_dictionary_premade_dashes_button.setMinimumHeight(70)
        self.select_dictionary_custom_dashes_button.setMinimumHeight(70)

        #-----Seaborn Legend Select Multiple Dashes Layout-----
        dictionary_dashes_screen_layout = QVBoxLayout(self.select_dictionary_dashes_screen)
        dictionary_dashes_screen_layout.addWidget(self.select_dictionary_premade_dashes_button)
        dictionary_dashes_screen_layout.addWidget(self.select_dictionary_custom_dashes_button)
        dictionary_dashes_screen_layout.setContentsMargins(10,10,10,10)
        dictionary_dashes_screen_layout.setSpacing(5)
        dictionary_dashes_screen_layout.addStretch()

        #-----All Available Screens-----
        self.current_screen_idx = 0
        self.available_screens = [self.sns_legend_dashes_screen,self.select_single_dashes_screen,
                                self.select_single_premade_dashes_screen,self.select_single_custom_dashes_screen,
                                self.select_multiple_dashes_screen,self.select_multiple_premade_dashes_screen,
                                self.select_multiple_custom_dashes_screen,self.select_dictionary_dashes_screen,
                                self.select_dictionary_premade_dashes_screen,self.select_dictionary_custom_dashes_screen]
        self.available_screens[self.current_screen_idx].show()

        #-----Add All the Screens to the Main Widget-----
        main_layout = QVBoxLayout(self)
        for screen in self.available_screens:
            main_layout.addWidget(screen)

        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0,0,0,0)

        #-----Keyboard Shortcuts-----
        previous_screen_shortcut = QShortcut(QKeySequence("left"),self)
        previous_screen_shortcut.activated.connect(self.change_to_previous_screen)

        enter_custom_dashes_shortcut = QShortcut(QKeySequence("Return"),self)
        enter_custom_dashes_shortcut.activated.connect(self.add_new_custom_dashes)

    def create_select_single_premade_dashes_screen(self):
        select_single_premade_dashes_screen_layout = QVBoxLayout(self.select_single_premade_dashes_screen)

        self.single_select_premade_dashes_list_view = QListView()
        self.single_select_premade_dashes_model = QStringListModel(self.available_dashes)

        self.single_select_premade_dashes_list_view.setModel(self.single_select_premade_dashes_model)
        self.single_select_premade_dashes_list_view.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.single_select_premade_dashes_list_view.setObjectName("single_select_premade_dashes_list_view")
        self.single_select_premade_dashes_list_view.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)

        class CustomDelegate(QStyledItemDelegate):
            def paint(self, painter, option, index):
                option.displayAlignment = Qt.AlignmentFlag.AlignCenter
                font = QFont("SF Pro Display", 24)
                font.setWeight(600)
                option.font = font
                super().paint(painter, option, index)
        
        self.single_select_premade_dashes_list_view.setItemDelegate(CustomDelegate())

        self.single_select_premade_dashes_list_view.setStyleSheet("""
            QListView#single_select_premade_dashes_list_view{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #f5f5ff,
                    stop:0.5 #f7f5fc,
                    stop:1 #f0f0ff
                );
                border: transparent;
                border-radius: 16px;
            }
            QListView#single_select_premade_dashes_list_view::item {
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
            QListView#single_select_premade_dashes_list_view::item:selected {
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
            QListView#single_select_premade_dashes_list_view::item:hover {
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

        self.single_select_premade_dashes_list_view.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.single_select_premade_dashes_list_view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.single_select_premade_dashes_list_view.setSpacing(3)

        self.single_select_premade_dashes_list_view.clicked.connect(self.change_single_select_premade_dashes)
        select_single_premade_dashes_screen_layout.addWidget(self.single_select_premade_dashes_list_view)

        # Add margins and spacing to make it look good and push content to the top
        select_single_premade_dashes_screen_layout.setContentsMargins(10, 10, 10, 10)

    def create_select_single_custom_dashes_screen(self):
        select_single_custom_dashes_screen_layout = QVBoxLayout(self.select_single_custom_dashes_screen)

        single_custom_dashes_instructions_widget = QWidget()
        single_custom_dashes_instructions_widget.setObjectName("single_custom_dashes_instructions_widget")
        single_custom_dashes_instructions_widget.setStyleSheet("""
            QWidget#single_custom_dashes_instructions_widget{
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
                font-size: 16px;
                padding: 6px;
                color: black;
            }
        """)

        single_custom_dashes_instructions_label = QLabel("Enter the numbers seperated by space")
        single_custom_dashes_instructions_label.setObjectName("single_custom_dashes_instructions_label")
        single_custom_dashes_instructions_label.setWordWrap(True)
        single_custom_dashes_instructions_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        single_custom_dashes_instructions_label.setStyleSheet("""
            QLabel#single_custom_dashes_instructions_label{
                font-family: "SF Pro Display";
                font-weight: 600;
                font-size: 24px;
                padding: 6px;
                color: black;
                border: none;
                background: transparent;
            }
        """)

        single_custom_dashes_instructions_layout = QVBoxLayout(single_custom_dashes_instructions_widget)
        single_custom_dashes_instructions_layout.addWidget(single_custom_dashes_instructions_label)
        single_custom_dashes_instructions_layout.setContentsMargins(0,0,0,0)
        single_custom_dashes_instructions_layout.setSpacing(0)

        self.select_single_custom_dashes_input = QLineEdit()
        self.select_single_custom_dashes_input.setObjectName("select_single_custom_dashes_input")
        self.select_single_custom_dashes_input.setPlaceholderText("Custom Dashes:")
        self.select_single_custom_dashes_input.setStyleSheet("""
            QLineEdit#select_single_custom_dashes_input{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #f5f5ff,
                    stop:0.5 #f7f5fc,
                    stop:1 #f0f0ff
                );
                color: black;
                font-size: 24pt;
                border: 2px solid black;
                border-radius: 16px;
            }
        """)
        self.select_single_custom_dashes_input.textChanged.connect(self.change_single_select_custom_dashes)
        self.select_single_custom_dashes_input.setMinimumHeight(60)

        select_single_custom_dashes_screen_layout.addWidget(single_custom_dashes_instructions_widget)
        select_single_custom_dashes_screen_layout.addWidget(self.select_single_custom_dashes_input)
        select_single_custom_dashes_screen_layout.addWidget(self.valid_single_custom_dashes_widget)
        select_single_custom_dashes_screen_layout.addWidget(self.invalid_single_custom_dashes_widget)
        select_single_custom_dashes_screen_layout.setContentsMargins(10,10,10,10)
        select_single_custom_dashes_screen_layout.setSpacing(10)
        select_single_custom_dashes_screen_layout.addStretch()

    def create_select_multiple_premade_dashes_screen(self):
        select_multiple_premade_dashes_screen_layout = QVBoxLayout(self.select_multiple_premade_dashes_screen)

        self.multiple_select_premade_dashes_list_view = QListView()
        self.multiple_select_premade_dashes_list_view.setSelectionMode(QListView.SelectionMode.MultiSelection)
        self.multiple_select_premade_dashes_model = QStringListModel(self.available_dashes)

        self.multiple_select_premade_dashes_list_view.setModel(self.multiple_select_premade_dashes_model)
        self.multiple_select_premade_dashes_list_view.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.multiple_select_premade_dashes_list_view.setObjectName("multiple_select_premade_dashes_list_view")
        self.multiple_select_premade_dashes_list_view.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)

        class CustomDelegate(QStyledItemDelegate):
            def paint(self, painter, option, index):
                option.displayAlignment = Qt.AlignmentFlag.AlignCenter
                font = QFont("SF Pro Display", 24)
                font.setWeight(600)
                option.font = font
                super().paint(painter, option, index)
        
        self.multiple_select_premade_dashes_list_view.setItemDelegate(CustomDelegate())

        self.multiple_select_premade_dashes_list_view.setStyleSheet("""
            QListView#multiple_select_premade_dashes_list_view{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #f5f5ff,
                    stop:0.5 #f7f5fc,
                    stop:1 #f0f0ff
                );
                border: transparent;
                border-radius: 16px;
            }
            QListView#multiple_select_premade_dashes_list_view::item {
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
            QListView#multiple_select_premade_dashes_list_view::item:selected {
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
            QListView#multiple_select_premade_dashes_list_view::item:hover {
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

        self.multiple_select_premade_dashes_list_view.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.multiple_select_premade_dashes_list_view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.multiple_select_premade_dashes_list_view.setSpacing(3)

        self.multiple_select_premade_dashes_list_view.selectionModel().selectionChanged.connect(self.change_multiple_select_premade_dashes)
        select_multiple_premade_dashes_screen_layout.addWidget(self.multiple_select_premade_dashes_list_view)

        # Add margins and spacing to make it look good and push content to the top
        select_multiple_premade_dashes_screen_layout.setContentsMargins(10, 10, 10, 10)

    def create_select_multiple_custom_dashes_screen(self):
        select_multiple_custom_dashes_screen_layout = QVBoxLayout(self.select_multiple_custom_dashes_screen)

        multiple_custom_dashes_instructions_widget = QWidget()
        multiple_custom_dashes_instructions_widget.setObjectName("multiple_custom_dashes_instructions_widget")
        multiple_custom_dashes_instructions_widget.setStyleSheet("""
            QWidget#multiple_custom_dashes_instructions_widget{
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
                font-size: 16px;
                padding: 6px;
                color: black;
            }
        """)

        multiple_custom_dashes_instructions_label = QLabel("Press Enter to Input More Values")
        multiple_custom_dashes_instructions_label.setObjectName("multiple_custom_dashes_instructions_label")
        multiple_custom_dashes_instructions_label.setWordWrap(True)
        multiple_custom_dashes_instructions_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        multiple_custom_dashes_instructions_label.setStyleSheet("""
            QLabel#multiple_custom_dashes_instructions_label{
                font-family: "SF Pro Display";
                font-weight: 600;
                font-size: 24px;
                padding: 6px;
                color: black;
                border: none;
                background: transparent;
            }
        """)

        multiple_custom_dashes_instructions_layout = QVBoxLayout(multiple_custom_dashes_instructions_widget)
        multiple_custom_dashes_instructions_layout.addWidget(multiple_custom_dashes_instructions_label)
        multiple_custom_dashes_instructions_layout.setContentsMargins(0,0,0,0)
        multiple_custom_dashes_instructions_layout.setSpacing(0)

        self.select_multiple_custom_dashes_input = QLineEdit()
        self.select_multiple_custom_dashes_input.setObjectName("select_multiple_custom_dashes_input")
        self.select_multiple_custom_dashes_input.setPlaceholderText("Custom Dashes:")
        self.select_multiple_custom_dashes_input.setStyleSheet("""
            QLineEdit#select_multiple_custom_dashes_input{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #f5f5ff,
                    stop:0.5 #f7f5fc,
                    stop:1 #f0f0ff
                );
                color: black;
                font-size: 24pt;
                border: 2px solid black;
                border-radius: 16px;
            }
        """)
        self.select_multiple_custom_dashes_input.textChanged.connect(self.check_multiple_select_custom_dashes)
        self.select_multiple_custom_dashes_input.setMinimumHeight(60)

        select_multiple_custom_dashes_screen_layout.addWidget(multiple_custom_dashes_instructions_widget)
        select_multiple_custom_dashes_screen_layout.addWidget(self.select_multiple_custom_dashes_input)
        select_multiple_custom_dashes_screen_layout.addWidget(self.valid_multiple_custom_dashes_widget)
        select_multiple_custom_dashes_screen_layout.addWidget(self.invalid_multiple_custom_dashes_widget)
        select_multiple_custom_dashes_screen_layout.setContentsMargins(10,10,10,10)
        select_multiple_custom_dashes_screen_layout.setSpacing(10)
        select_multiple_custom_dashes_screen_layout.addStretch()

    def create_select_dictionary_premade_dashes_screen(self):
        select_dictionary_premade_dashes_screen_layout = QVBoxLayout(self.select_dictionary_premade_dashes_screen) 

        self.select_dictionary_premade_dashes_key_input = QLineEdit()
        self.select_dictionary_premade_dashes_key_input.setObjectName("select_dictionary_premade_dashes_key_input")
        self.select_dictionary_premade_dashes_key_input.setPlaceholderText("Key:")
        self.select_dictionary_premade_dashes_key_input.setStyleSheet("""
            QLineEdit#select_dictionary_premade_dashes_key_input{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #f5f5ff,
                    stop:0.5 #f7f5fc,
                    stop:1 #f0f0ff
                );
                color: black;
                font-size: 24pt;
                border: 2px solid black;
                border-radius: 16px;
            }
        """)
        self.select_dictionary_premade_dashes_key_input.textChanged.connect(self.change_dictionary_key_dashes)
        self.select_dictionary_premade_dashes_key_input.setMinimumHeight(50)
        
        self.select_dictionary_premade_dashes_list_view = QListView()
        self.select_dictionary_premade_dashes_model = QStringListModel(self.available_dashes)

        self.select_dictionary_premade_dashes_list_view.setModel(self.select_dictionary_premade_dashes_model)
        self.select_dictionary_premade_dashes_list_view.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.select_dictionary_premade_dashes_list_view.setObjectName("select_dictionary_premade_dashes_list_view")
        self.select_dictionary_premade_dashes_list_view.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)

        class CustomDelegate(QStyledItemDelegate):
            def paint(self, painter, option, index):
                option.displayAlignment = Qt.AlignmentFlag.AlignCenter
                font = QFont("SF Pro Display", 24)
                font.setWeight(600)
                option.font = font
                super().paint(painter, option, index)
        
        self.select_dictionary_premade_dashes_list_view.setItemDelegate(CustomDelegate())

        self.select_dictionary_premade_dashes_list_view.setStyleSheet("""
            QListView#select_dictionary_premade_dashes_list_view{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #f5f5ff,
                    stop:0.5 #f7f5fc,
                    stop:1 #f0f0ff
                );
                border: transparent;
                border-radius: 16px;
            }
            QListView#select_dictionary_premade_dashes_list_view::item {
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
            QListView#select_dictionary_premade_dashes_list_view::item:selected {
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
            QListView#select_dictionary_premade_dashes_list_view::item:hover {
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

        self.select_dictionary_premade_dashes_list_view.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.select_dictionary_premade_dashes_list_view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.select_dictionary_premade_dashes_list_view.setSpacing(3)

        self.select_dictionary_premade_dashes_list_view.clicked.connect(self.change_dictionary_value_premade_dashes)

        select_dictionary_premade_dashes_screen_layout.addWidget(self.select_dictionary_premade_dashes_key_input)
        select_dictionary_premade_dashes_screen_layout.addWidget(self.select_dictionary_premade_dashes_list_view)
        select_dictionary_premade_dashes_screen_layout.setContentsMargins(10,10,10,10)
        select_dictionary_premade_dashes_screen_layout.setSpacing(10)

    def create_select_dictionary_custom_dashes_screen(self):
        select_dictionary_custom_dashes_screen_layout = QVBoxLayout(self.select_dictionary_custom_dashes_screen) 

        dictionary_custom_dashes_instructions_widget = QWidget()
        dictionary_custom_dashes_instructions_widget.setObjectName("dictionary_custom_dashes_instructions_widget")
        dictionary_custom_dashes_instructions_widget.setStyleSheet("""
            QWidget#dictionary_custom_dashes_instructions_widget{
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
                font-size: 16px;
                padding: 6px;
                color: black;
            }
        """)

        dictionary_custom_dashes_instructions_label = QLabel("Press Enter to Input More Values")
        dictionary_custom_dashes_instructions_label.setObjectName("dictionary_custom_dashes_instructions_label")
        dictionary_custom_dashes_instructions_label.setWordWrap(True)
        dictionary_custom_dashes_instructions_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        dictionary_custom_dashes_instructions_label.setStyleSheet("""
            QLabel#dictionary_custom_dashes_instructions_label{
                font-family: "SF Pro Display";
                font-weight: 600;
                font-size: 24px;
                padding: 6px;
                color: black;
                border: none;
                background: transparent;
            }
        """)

        dictionary_custom_dashes_instructions_layout = QVBoxLayout(dictionary_custom_dashes_instructions_widget)
        dictionary_custom_dashes_instructions_layout.addWidget(dictionary_custom_dashes_instructions_label)
        dictionary_custom_dashes_instructions_layout.setContentsMargins(0,0,0,0)
        dictionary_custom_dashes_instructions_layout.setSpacing(0)

        self.select_dictionary_custom_dashes_key_input = QLineEdit()
        self.select_dictionary_custom_dashes_key_input.setObjectName("select_dictionary_custom_dashes_key_input")
        self.select_dictionary_custom_dashes_key_input.setPlaceholderText("Key:")
        self.select_dictionary_custom_dashes_key_input.setStyleSheet("""
            QLineEdit#select_dictionary_custom_dashes_key_input{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #f5f5ff,
                    stop:0.5 #f7f5fc,
                    stop:1 #f0f0ff
                );
                color: black;
                font-size: 24pt;
                border: 2px solid black;
                border-radius: 16px;
            }
        """)
        self.select_dictionary_custom_dashes_key_input.textChanged.connect(self.change_dictionary_key_dashes)
        self.select_dictionary_custom_dashes_key_input.setMinimumHeight(50)

        self.select_dictionary_custom_dashes_value_input = QLineEdit()
        self.select_dictionary_custom_dashes_value_input.setObjectName("select_dictionary_custom_dashes_value_input")
        self.select_dictionary_custom_dashes_value_input.setPlaceholderText("Value:")
        self.select_dictionary_custom_dashes_value_input.setStyleSheet("""
            QLineEdit#select_dictionary_custom_dashes_value_input{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #f5f5ff,
                    stop:0.5 #f7f5fc,
                    stop:1 #f0f0ff
                );
                color: black;
                font-size: 24pt;
                border: 2px solid black;
                border-radius: 16px;
            }
        """)
        self.select_dictionary_custom_dashes_value_input.textChanged.connect(self.change_dictionary_value_custom_dashes)
        self.select_dictionary_custom_dashes_value_input.setMinimumHeight(50)

        select_dictionary_custom_dashes_screen_layout.addWidget(dictionary_custom_dashes_instructions_widget)
        select_dictionary_custom_dashes_screen_layout.addWidget(self.select_dictionary_custom_dashes_key_input)
        select_dictionary_custom_dashes_screen_layout.addWidget(self.select_dictionary_custom_dashes_value_input)
        select_dictionary_custom_dashes_screen_layout.addWidget(self.valid_dictionary_custom_dashes_widget)
        select_dictionary_custom_dashes_screen_layout.addWidget(self.invalid_dictionary_custom_dashes_widget)
        select_dictionary_custom_dashes_screen_layout.setContentsMargins(10,10,10,10)
        select_dictionary_custom_dashes_screen_layout.setSpacing(10)
        select_dictionary_custom_dashes_screen_layout.addStretch()

    def change_to_home_screen(self):
        self.available_screens[self.current_screen_idx].hide()
        self.current_screen_idx = 0
        self.available_screens[self.current_screen_idx].show()

    def change_to_previous_screen(self):
        self.hide_validity_widgets()
        if (self.current_screen_idx == 0):
            return

        self.available_screens[self.current_screen_idx].hide()

        if (self.current_screen_idx in [1,4,7]):
            self.current_screen_idx = 0
        if (self.current_screen_idx in [2,3]):
            self.current_screen_idx = 1
            self.select_single_custom_dashes_input.clear()
        if (self.current_screen_idx in [5,6]):
            self.current_screen_idx = 4
            self.select_multiple_custom_dashes_input.clear()
        if (self.current_screen_idx in [8,9]):
            self.current_screen_idx = 7
            self.select_dictionary_premade_dashes_key_input.clear()
            self.select_dictionary_custom_dashes_key_input.clear()
            self.select_dictionary_custom_dashes_value_input.clear()

        self.available_screens[self.current_screen_idx].show()

    def change_to_single_dashes_screen(self):
        self.available_screens[self.current_screen_idx].hide()
        self.current_screen_idx = 1
        self.available_screens[self.current_screen_idx].show()

    def change_to_select_single_premade_dashes_screen(self):
        self.available_screens[self.current_screen_idx].hide()
        self.current_screen_idx = 2
        self.available_screens[self.current_screen_idx].show()

    def change_to_select_single_custom_dashes_screen(self):
        self.available_screens[self.current_screen_idx].hide()
        self.current_screen_idx = 3
        self.available_screens[self.current_screen_idx].show()

    def change_to_multiple_dashes_screen(self):
        self.available_screens[self.current_screen_idx].hide()
        self.current_screen_idx = 4
        self.available_screens[self.current_screen_idx].show()

    def change_to_select_multiple_premade_dashes_screen(self):
        self.available_screens[self.current_screen_idx].hide()
        self.current_screen_idx = 5
        self.available_screens[self.current_screen_idx].show()

    def change_to_select_multiple_custom_dashes_screen(self):
        self.available_screens[self.current_screen_idx].hide()
        self.current_screen_idx = 6
        self.available_screens[self.current_screen_idx].show()

    def change_to_dictionary_dashes_screen(self):
        self.available_screens[self.current_screen_idx].hide()
        self.current_screen_idx = 7
        self.available_screens[self.current_screen_idx].show()

    def change_to_select_dictionary_premade_dashes_screen(self):
        self.available_screens[self.current_screen_idx].hide()
        self.current_screen_idx = 8
        self.available_screens[self.current_screen_idx].show()

    def change_to_select_dictionary_custom_dashes_screen(self):
        self.available_screens[self.current_screen_idx].hide()
        self.current_screen_idx = 9
        self.available_screens[self.current_screen_idx].show()

    def turn_dashes_on_and_off(self):
        self.initial_dashes_argument = not self.initial_dashes_argument
        if (self.initial_dashes_argument):
            self.turn_dashes_on_off_label.setText("Turn Dashes Off")
        else:
            self.turn_dashes_on_off_label.setText("Turn Dashes On")
        self.dashes = self.initial_dashes_argument
        self.update_dashes()

    def change_single_select_premade_dashes(self,index):
        self.dashes = self.single_select_premade_dashes_model.data(index, Qt.ItemDataRole.DisplayRole)
        if ("None" in self.dashes):
            self.dashes = ""
        else:
            self.dashes = self.dashes[self.dashes.index("(")+1:self.dashes.index(")")]
        self.update_dashes()
    
    def change_single_select_custom_dashes(self):
        custom_dashes = self.select_single_custom_dashes_input.text().strip()

        if (custom_dashes == ""):
            self.valid_single_custom_dashes_widget.hide()
            self.invalid_single_custom_dashes_widget.hide()
            self.dashes = ""
            self.update_dashes()
            return
        
        # Split by comma or space
        if "," in custom_dashes:
            custom_dashes = custom_dashes.split(",")
        elif " " in custom_dashes:
            custom_dashes = custom_dashes.split()
        else:
            custom_dashes = [custom_dashes]
        
        try:
            custom_dashes = list(map(float, custom_dashes))
            self.dashes = tuple(custom_dashes)

            if (len(custom_dashes) < 4 or len(custom_dashes) % 2 == 1):
                raise Exception
            
            self.valid_single_custom_dashes_widget.show()
            self.invalid_single_custom_dashes_widget.hide()
            
        except:
            self.valid_single_custom_dashes_widget.setVisible(False)
            self.invalid_single_custom_dashes_widget.setVisible(True)
        
        self.update_dashes()

    def change_multiple_select_premade_dashes(self):
        selected_indexes = self.multiple_select_premade_dashes_list_view.selectedIndexes()
        self.dashes = [index.data() for index in selected_indexes]
        self.dashes = list(map(lambda x:x[x.index("(")+1:x.index(")")],self.dashes))
        self.dashes = [dash if (dash != "\u2014") else "" for dash in self.dashes]
        self.update_dashes()

    def check_multiple_select_custom_dashes(self):
        custom_dashes = self.select_multiple_custom_dashes_input.text().strip()

        if (custom_dashes == ""):
            self.valid_multiple_custom_dashes_widget.hide()
            self.invalid_multiple_custom_dashes_widget.hide()
            return False
        
        # Split by comma or space
        if "," in custom_dashes:
            custom_dashes = custom_dashes.split(",")
        elif " " in custom_dashes:
            custom_dashes = custom_dashes.split()
        else:
            custom_dashes = [custom_dashes]
        
        try:
            custom_dashes = list(map(float, custom_dashes))

            if (len(custom_dashes) < 4 or len(custom_dashes) % 2 == 1):
                raise Exception

            self.valid_multiple_custom_dashes_widget.show()
            self.invalid_multiple_custom_dashes_widget.hide()

            return True
            
        except:
            self.valid_multiple_custom_dashes_widget.hide()
            self.invalid_multiple_custom_dashes_widget.show()
            return False

    def change_dictionary_key_dashes(self):
        if (self.select_dictionary_premade_dashes_key_input.text().strip() != ""):
            self.dashes_dictionary_key = self.select_dictionary_premade_dashes_key_input.text().strip()
        else:
            self.dashes_dictionary_key = self.select_dictionary_custom_dashes_key_input.text().strip()

    def change_dictionary_value_premade_dashes(self,index):
        self.dashes_dictionary_value = self.select_dictionary_premade_dashes_model.data(index,Qt.ItemDataRole.DisplayRole)
        if ("None" in self.dashes_dictionary_value):
            self.dashes_dictionary_value = ""
        else:
            self.dashes_dictionary_value = self.dashes[self.dashes.index("(")+1:self.dashes.index(")")]
        self.change_dictionary_select_dashes()
        self.select_dictionary_premade_dashes_key_input.clear()

    def change_dictionary_value_custom_dashes(self):
        custom_dashes = self.select_dictionary_custom_dashes_value_input.text().strip()

        if (custom_dashes == ""):
            self.valid_dictionary_custom_dashes_widget.hide()
            self.invalid_dictionary_custom_dashes_widget.hide()
            return False
        
        # Split by comma or space
        if "," in custom_dashes:
            custom_dashes = custom_dashes.split(",")
        elif " " in custom_dashes:
            custom_dashes = custom_dashes.split()
        else:
            custom_dashes = [custom_dashes]
        
        try:
            custom_dashes = list(map(float, custom_dashes))

            if (len(custom_dashes) < 4 or len(custom_dashes) % 2 == 1):
                raise Exception

            self.dashes_dictionary_value = custom_dashes

            self.valid_dictionary_custom_dashes_widget.show()
            self.invalid_dictionary_custom_dashes_widget.hide()

            return True
            
        except:
            self.valid_dictionary_custom_dashes_widget.hide()
            self.invalid_dictionary_custom_dashes_widget.show()
            return False

    def change_dictionary_select_dashes(self):
        if (self.dashes_dictionary_key != "" and self.dashes_dictionary_value != ""):
            dictionary_keys = list(self.dashes_dictionary.keys())
            dictionary_values = list(self.dashes_dictionary.values())
            if (self.dashes_dictionary_key not in dictionary_keys and self.dashes_dictionary_value not in dictionary_values):
                self.dashes_dictionary[self.dashes_dictionary_key] = self.dashes_dictionary_value
                self.dashes = self.dashes_dictionary
                self.update_dashes()

    def update_dashes(self):
        db = self.plot_manager.get_db()
        if (db != []):
            self.plot_manager.update_seaborn_legend("dashes",self.dashes)
        else:
            plot_parameters = plot_json[self.selected_graph].copy()
            plot_parameters["legend"]["seaborn_legends"]["dashes"] = self.dashes
            self.plot_manager.insert_plot_parameter(plot_parameters)
        self.graph_display.show_graph()

    def add_new_custom_dashes(self):
        if (not self.available_screens[6].isHidden()):
            if (self.check_multiple_select_custom_dashes()):
                custom_dashes = self.select_multiple_custom_dashes_input.text().strip()
                if "," in custom_dashes:
                    custom_dashes = custom_dashes.split(",")
                elif " " in custom_dashes:
                    custom_dashes = custom_dashes.split()
                else:
                    custom_dashes = [custom_dashes]
                custom_dashes = list(map(float, custom_dashes))
                
                if (isinstance(self.dashes,list)):
                    self.dashes.append(custom_dashes)
                else:
                    self.dashes = [custom_dashes]

                self.select_multiple_custom_dashes_input.clear()

                self.update_dashes()

        if (not self.available_screens[9].isHidden()):
            if (self.change_dictionary_value_custom_dashes()):
                self.change_dictionary_select_dashes()

                self.select_dictionary_custom_dashes_key_input.clear()
                self.select_dictionary_custom_dashes_value_input.clear()

    def reset_dashes_selection(self):
        self.dashes = []
        self.dashes_dictionary = dict()
        self.dashes_dictionary_key = ""
        self.dashes_dictionary_value = ""

    def hide_validity_widgets(self):
        self.valid_single_custom_dashes_widget.hide()
        self.invalid_single_custom_dashes_widget.hide()

    def mousePressEvent(self, event):
        if (not self.select_single_custom_dashes_input.geometry().contains(event.position().toPoint())):
            self.select_single_custom_dashes_input.clearFocus()
        if (not self.select_multiple_custom_dashes_input.geometry().contains(event.position().toPoint())):
            self.select_multiple_custom_dashes_input.clearFocus()
        if (not self.select_dictionary_premade_dashes_key_input.geometry().contains(event.position().toPoint())):
            self.select_dictionary_premade_dashes_key_input.clearFocus()
        if (not self.select_dictionary_custom_dashes_key_input.geometry().contains(event.position().toPoint())):
            self.select_dictionary_custom_dashes_key_input.clearFocus()
        if (not self.select_dictionary_custom_dashes_value_input.geometry().contains(event.position().toPoint())):
            self.select_dictionary_custom_dashes_value_input.clearFocus()
        super().mousePressEvent(event)

    def showEvent(self,event):
        super().showEvent(event)
        self.reset_dashes_selection()
        self.change_to_home_screen()

class seaborn_legend_size_order_adjustment_section(QWidget):
    def __init__(self,selected_graph,graph_display):
        super().__init__()
        self.selected_graph = selected_graph
        self.graph_display = graph_display
        self.plot_manager = PlotManager()

        self.size_values = self.get_size_values()

        self.size_order = []

        #-----Size Order Screen-----
        self.size_order_adjustment_screen = QWidget()
        self.size_order_adjustment_screen.setObjectName("size_order_adjustment_screen")
        self.size_order_adjustment_screen.setStyleSheet("""
            QWidget#size_order_adjustment_screen{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #f5f5ff,
                    stop:0.5 #f7f5fc,
                    stop:1 #f0f0ff
                );
                border: 2px solid black;
                border-radius: 16px;
            }
        """)
        self.create_size_order_adjustment_screen()

        main_layout = QVBoxLayout(self)
        main_layout.addWidget(self.size_order_adjustment_screen)
        main_layout.setContentsMargins(0,0,0,0)
        main_layout.setSpacing(0)

    def create_size_order_adjustment_screen(self):
        size_order_adjustment_screen_layout = QVBoxLayout(self.size_order_adjustment_screen)
    
        self.size_order_listwidget = QListWidget()
        self.size_order_listwidget.setObjectName("size_order_listwidget")

        # Enable drag & drop reordering
        self.size_order_listwidget.setDragDropMode(QListWidget.DragDropMode.InternalMove)
        for size in self.size_values:
            self.size_order_listwidget.addItem(QListWidgetItem(size))
            
        class CustomDelegate(QStyledItemDelegate):
            def paint(self, painter, option, index):
                option.displayAlignment = Qt.AlignmentFlag.AlignCenter
                font = QFont("SF Pro Display", 24)
                font.setWeight(600)
                option.font = font
                super().paint(painter, option, index)
        
        self.size_order_listwidget.setItemDelegate(CustomDelegate())
        self.size_order_listwidget.setStyleSheet("""
            QListWidget#size_order_listwidget{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #f5f5ff,
                    stop:0.5 #f7f5fc,
                    stop:1 #f0f0ff
                );
                border: transparent;
                border-radius: 16px;
            }
            QListWidget#size_order_listwidget::item {
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
            QListWidget#size_order_listwidget::item:selected {
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
            QListWidget#size_order_listwidget::item:hover {
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

        self.size_order_listwidget.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.size_order_listwidget.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.size_order_listwidget.setSpacing(3)

        self.size_order_listwidget.model().rowsMoved.connect(self.update_size_order)

        size_order_adjustment_screen_layout.addWidget(self.size_order_listwidget)

        # Add margins and spacing to make it look good and push content to the top
        size_order_adjustment_screen_layout.setContentsMargins(10, 10, 10, 10)

    def update_size_order(self):
        self.size_order = [self.size_order_model.item(i).text() for i in range(self.size_order_model .rowCount())]
        db = self.plot_manager.get_db()
        if (db != []): 
            self.plot_manager.update_seaborn_legend("size_order",self.size_order)
        else:
            plot_parameters = plot_json[self.selected_graph].copy()
            plot_parameters["legend"]["seaborn_legends"]["size_order"] = self.size_order
            self.plot_manager.insert_plot_parameter(plot_parameters)
        self.graph_display.show_graph()

    def get_size_values(self):
        db = self.plot_manager.get_db()
        if (db != []):
            dataset = pd.read_csv("./dataset/user_dataset.csv")
            size_parameter = db["size"]
            if (size_parameter == None):
                return []
            return dataset[size_parameter].unique()
        else:
            return []

    def showEvent(self,event):
        super().showEvent(event)
        self.size_values = self.get_size_values()

class seaborn_legend_hue_order_adjustment_section(QWidget):
    def __init__(self,selected_graph,graph_display):
        super().__init__()
        self.selected_graph = selected_graph
        self.graph_display = graph_display
        self.plot_manager = PlotManager()

        self.hue_order = []

        #-----Change Hue Warning Widget-----
        self.hue_order_warning_widget = QWidget()
        self.hue_order_warning_widget.setObjectName("hue_order_warning_widget")
        self.hue_order_warning_widget.setStyleSheet("""
            QWidget#hue_order_warning_widget{
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

        self.hue_order_warning_label = QLabel("Invalid Hue for Hue Order")
        self.hue_order_warning_label.setObjectName("hue_order_warning_label")
        self.hue_order_warning_label.setStyleSheet("""
            QLabel#hue_order_warning_label{
                font-family: "SF Pro Display";
                font-weight: 600;
                font-size: 24px;
                padding: 6px;
                color: black;
                border: none;
                background: transparent;
            }
        """)
        self.hue_order_warning_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.hue_order_warning_label.setWordWrap(True)

        hue_order_warning_layout = QVBoxLayout(self.hue_order_warning_widget)
        hue_order_warning_layout.addWidget(self.hue_order_warning_label)
        hue_order_warning_layout.setSpacing(0)
        hue_order_warning_layout.setContentsMargins(0,0,0,0)

        self.hue_order_warning_widget.setMinimumHeight(70)
        self.hue_order_warning_widget.hide()

        #-----Get the Hue Values-----
        self.hue_values = self.get_hue_values()

        #-----Hue Order Screen-----
        self.hue_order_adjustment_screen = QWidget()
        self.hue_order_adjustment_screen.setObjectName("hue_order_adjustment_screen")
        self.hue_order_adjustment_screen.setStyleSheet("""
            QWidget#hue_order_adjustment_screen{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #f5f5ff,
                    stop:0.5 #f7f5fc,
                    stop:1 #f0f0ff
                );
                border: 2px solid black;
                border-radius: 16px;
            }
        """)
        self.create_hue_order_adjustment_screen()

    def create_hue_order_adjustment_screen(self):
        hue_order_adjustment_screen_layout = QVBoxLayout(self.hue_order_adjustment_screen)
    
        self.hue_order_listwidget = QListWidget()
        self.hue_order_listwidget.setObjectName("hue_order_listwidget")
        # Enable drag & drop reordering
        self.hue_order_listwidget.setDragDropMode(QListWidget.DragDropMode.InternalMove)
        for hue in self.hue_values:
            self.hue_order_listwidget.addItem(QListWidgetItem(str(hue)))
            
        class CustomDelegate(QStyledItemDelegate):
            def paint(self, painter, option, index):
                option.displayAlignment = Qt.AlignmentFlag.AlignCenter
                font = QFont("SF Pro Display", 24)
                font.setWeight(600)
                option.font = font
                super().paint(painter, option, index)
        
        self.hue_order_listwidget.setItemDelegate(CustomDelegate())
        self.hue_order_listwidget.setStyleSheet("""
            QListWidget#hue_order_listwidget{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #f5f5ff,
                    stop:0.5 #f7f5fc,
                    stop:1 #f0f0ff
                );
                border: transparent;
                border-radius: 16px;
            }
            QListWidget#hue_order_listwidget::item {
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
            QListWidget#hue_order_listwidget::item:selected {
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
            QListWidget#hue_order_listwidget::item:hover {
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

        self.hue_order_listwidget.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.hue_order_listwidget.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.hue_order_listwidget.setSpacing(3)

        self.hue_order_listwidget.model().rowsMoved.connect(self.update_hue_order)

        hue_order_adjustment_screen_layout.addWidget(self.hue_order_warning_widget)
        hue_order_adjustment_screen_layout.addWidget(self.hue_order_listwidget)

        # Add margins and spacing to make it look good and push content to the top
        hue_order_adjustment_screen_layout.setContentsMargins(10, 10, 10, 10)

        main_layout = QVBoxLayout(self)
        main_layout.addWidget(self.hue_order_adjustment_screen)
        main_layout.setContentsMargins(0,0,0,0)
        main_layout.setSpacing(0)

    def update_hue_order(self):
        self.hue_order = [self.hue_order_listwidget.item(i).text() for i in range(self.hue_order_listwidget.count())]
        db = self.plot_manager.get_db()
        if (db != []): 
            self.plot_manager.update_seaborn_legend("hue_order",self.hue_order)
        else:
            plot_parameters = plot_json[self.selected_graph].copy()
            plot_parameters["legend"]["seaborn_legends"]["hue_order"] = self.hue_order
            self.plot_manager.insert_plot_parameter(plot_parameters)
        self.graph_display.show_graph()

    def get_hue_values(self):
        db = self.plot_manager.get_db()
        if (db != []):
            dataset = pd.read_csv("./dataset/user_dataset.csv")
            hue_parameter = db["hue"][0]
            if (hue_parameter == None):
                self.hue_order_warning_widget.show()
                return []
            if ("self.dataset" in hue_parameter):
                self.hue_order_warning_widget.show()
                return []
            if ("float" in str(dataset[hue_parameter].dtype)):
                self.hue_order_warning_widget.show()
                return []
            self.hue_order_warning_widget.hide()
            return dataset[hue_parameter].unique()
        else:
            return []

    def showEvent(self,event):
        super().showEvent(event)
        self.hue_value = self.get_hue_values()
        self.hue_order_listwidget.clear()
        for row,hue_value in enumerate(self.hue_value):
            self.hue_order_listwidget.insertItem(row,QListWidgetItem(str(hue_value)))

class seaborn_legend_style_order_adjustment_section(QWidget):
    def __init__(self,selected_graph,graph_display):
        super().__init__()
        self.selected_graph = selected_graph
        self.graph_display = graph_display
        self.plot_manager = PlotManager()

        self.style_values = self.get_style_values()

        self.style_order = []

        #-----Style Order Screen-----
        self.style_order_adjustment_screen = QWidget()
        self.style_order_adjustment_screen.setObjectName("style_order_adjustment_screen")
        self.style_order_adjustment_screen.setStyleSheet("""
            QWidget#style_order_adjustment_screen{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #f5f5ff,
                    stop:0.5 #f7f5fc,
                    stop:1 #f0f0ff
                );
                border: 2px solid black;
                border-radius: 16px;
            }
        """)
        self.create_style_order_adjustment_screen()

        main_layout = QVBoxLayout(self)
        main_layout.addWidget(self.style_order_adjustment_screen)
        main_layout.setContentsMargins(0,0,0,0)
        main_layout.setSpacing(0)

    def create_style_order_adjustment_screen(self):
        style_order_adjustment_screen_layout = QVBoxLayout(self.style_order_adjustment_screen)
    
        self.style_order_listwidget = QListWidget()
        self.style_order_listwidget.setObjectName("style_order_listwidget")

        # Enable drag & drop reordering
        self.style_order_listwidget.setDragDropMode(QListWidget.DragDropMode.InternalMove)
        for style in self.style_values:
            self.style_order_listwidget.addItem(QListWidgetItem(style))
            
        class CustomDelegate(QStyledItemDelegate):
            def paint(self, painter, option, index):
                option.displayAlignment = Qt.AlignmentFlag.AlignCenter
                font = QFont("SF Pro Display", 24)
                font.setWeight(600)
                option.font = font
                super().paint(painter, option, index)
        
        self.style_order_listwidget.setItemDelegate(CustomDelegate())
        self.style_order_listwidget.setStyleSheet("""
            QListWidget#style_order_listwidget{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #f5f5ff,
                    stop:0.5 #f7f5fc,
                    stop:1 #f0f0ff
                );
                border: transparent;
                border-radius: 16px;
            }
            QListWidget#style_order_listwidget::item {
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
            QListWidget#style_order_listwidget::item:selected {
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
            QListWidget#style_order_listwidget::item:hover {
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

        self.style_order_listwidget.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.style_order_listwidget.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.style_order_listwidget.setSpacing(3)

        self.style_order_listwidget.model().rowsMoved.connect(self.update_style_order)

        style_order_adjustment_screen_layout.addWidget(self.style_order_listwidget)

        # Add margins and spacing to make it look good and push content to the top
        style_order_adjustment_screen_layout.setContentsMargins(10, 10, 10, 10)

    def update_style_order(self):
        self.style_order = [self.style_order_model.item(i).text() for i in range(self.style_order_model .rowCount())]
        db = self.plot_manager.get_db()
        if (db != []): 
            self.plot_manager.update_seaborn_legend("style_order",self.style_order)
        else:
            plot_parameters = plot_json[self.selected_graph].copy()
            plot_parameters["legend"]["seaborn_legends"]["style_order"] = self.style_order
            self.plot_manager.insert_plot_parameter(plot_parameters)
        self.graph_display.show_graph()

    def get_style_values(self):
        db = self.plot_manager.get_db()
        if (db != []):
            dataset = pd.read_csv("./dataset/user_dataset.csv")
            size_parameter = db["style"]
            if (size_parameter == None):
                return []
            return dataset[size_parameter].unique()
        else:
            return []

    def showEvent(self,event):
        super().showEvent(event)
        self.style_values = self.get_style_values()

class legend_button(QDialog):
    def __init__(self,selected_graph, graph_display):
        super().__init__()
        self.setWindowTitle("Customize Legend")

        self.selected_graph = selected_graph
        self.graph_display = graph_display

        self.legend_parameters = list(plot_json[self.selected_graph]["legend"].keys())[:-1]
        self.seaborn_specific_legend_parameters = list(plot_json[self.selected_graph]["legend"]["seaborn_legends"].keys())

        self.legend_parameters.extend(self.seaborn_specific_legend_parameters)

        self.current_screen_index = 0

        self.available_screen_names = [legend_visible_adjustment_section,legend_label_adjustment_section,
                                  legend_loc_adjustment_section,legend_bbox_to_anchor_adjustment_section,
                                  legend_ncol_adjustment_section,legend_fontsize_adjustment_section,
                                  legend_title_adjustment_section,legend_title_fontsize_adjustment_section,
                                  legend_frameon_adjustment_section,legend_face_color_adjustment_section,
                                  legend_edge_color_adjustment_section,legend_framealpha_adjustment_section,
                                  legend_shadow_adjustment_section,legend_fancybox_adjustment_section,
                                  legend_borderpad_adjustment_section,legend_label_color_adjustment_section,
                                  legend_alignment_adjustment_section,legend_columnspacing_adjustment_section,
                                  legend_handletextpad_adjustment_section,legend_borderaxespad_adjustment_section,
                                  legend_handlelength_adjustment_section,legend_handleheight_adjustment_section,
                                  legend_markerfirst_adjustment_section,seaborn_legend_adjustment_section,
                                  seaborn_legend_off_adjustment_section,seaborn_legend_markers_adjustment_section,
                                  seaborn_legend_dashes_adjustment_section,seaborn_legend_size_order_adjustment_section,
                                  seaborn_legend_hue_order_adjustment_section,seaborn_legend_style_order_adjustment_section]

        self.available_screens = dict()

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

        self.legend_parameters_section = QWidget()
        self.legend_parameters_section.setObjectName("legend_parameter_section")
        self.legend_parameters_section.setStyleSheet("""
            QWidget#legend_parameter_section{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #f5f5ff,
                    stop:0.5 #f7f5fc,
                    stop:1 #f0f0ff
                );
                border: 2px solid black;
                border-radius: 16px;
            }
        """)
        self.create_legend_parameter_buttons()

        #Place the buttons and the dataset next to each other side by side
        self.layout = QHBoxLayout(self)
        self.layout.addWidget(self.legend_parameters_section,stretch=1)
        self.layout.addSpacing(10)
        
        #Add the parameters screen to the layout
        for screen_name,screen in zip(self.legend_parameters,self.available_screen_names):
            parameter_screen = screen(self.selected_graph,self.graph_display)
            parameter_screen.hide()
            self.available_screens[screen_name] = parameter_screen
            self.layout.addWidget(parameter_screen,stretch=1)
        
        #Show the first parameter screen
        self.available_screens.get(self.legend_parameters[self.current_screen_index]).show()

        #Create a shortcut for the user to go to the previous column by press up
        up_shortcut = QShortcut(QKeySequence("up"), self) 
        up_shortcut.activated.connect(self.columns_go_up)  

        #Create a shortcut for the user to go to the next column by press down
        down_shortcut = QShortcut(QKeySequence("down"), self) 
        down_shortcut.activated.connect(self.columns_go_down)

        #Create a shortcut for the user to close the dialog window
        close_shortcut = QShortcut(QKeySequence("ESC"), self) 
        close_shortcut.activated.connect(self.close_application)

        #Make sure this gets drawn.
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        
    def create_legend_parameter_buttons(self):
        legend_parameter_button_layout = QVBoxLayout(self.legend_parameters_section)
    
        self.legend_parameter_list_view = QListView()
        self.legend_parameter_model = QStringListModel(self.legend_parameters)

        self.legend_parameter_list_view.setModel(self.legend_parameter_model)
        self.legend_parameter_list_view.setObjectName("legend_parameter_list_view")
        self.legend_parameter_list_view.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)

        screen_index = self.legend_parameter_model.index(0)  
        self.legend_parameter_list_view.setCurrentIndex(screen_index)

        class CustomDelegate(QStyledItemDelegate):
            def paint(self, painter, option, index):
                option.displayAlignment = Qt.AlignmentFlag.AlignCenter
                font = QFont("SF Pro Display", 24)
                font.setWeight(600)
                option.font = font
                super().paint(painter, option, index)
        
        self.legend_parameter_list_view.setItemDelegate(CustomDelegate())

        self.legend_parameter_list_view.setStyleSheet("""
            QListView#legend_parameter_list_view{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #f5f5ff,
                    stop:0.5 #f7f5fc,
                    stop:1 #f0f0ff
                );
                border: transparent;
                border-radius: 16px;
            }
            QListView#legend_parameter_list_view::item {
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
            QListView#legend_parameter_list_view::item:selected {
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
            QListView#legend_parameter_list_view::item:hover {
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

        self.legend_parameter_list_view.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.legend_parameter_list_view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.legend_parameter_list_view.setSpacing(3)

        self.legend_parameter_list_view.clicked.connect(self.change_current_parameter_screen)

        legend_parameter_button_layout.addWidget(self.legend_parameter_list_view)

        # Add margins and spacing to make it look good and push content to the top
        legend_parameter_button_layout.setContentsMargins(10, 10, 10, 10)

    def change_current_parameter_screen(self,index):
        current_screen_name = self.legend_parameter_model.data(index,Qt.ItemDataRole.DisplayRole)
        self.available_screens.get(self.legend_parameters[self.current_screen_index]).hide()
        self.available_screens.get(current_screen_name).show()
        self.current_screen_index = index.row()
    
    def columns_go_up(self):
        self.available_screens.get(self.legend_parameters[self.current_screen_index]).hide()
        self.current_screen_index -= 1
        self.current_screen_index %= len(self.legend_parameters)
        self.available_screens.get(self.legend_parameters[self.current_screen_index]).show()
        new_screen_index = self.legend_parameter_model.index(self.current_screen_index)
        self.legend_parameter_list_view.setCurrentIndex(new_screen_index)
        self.legend_parameter_list_view.scrollTo(new_screen_index,QAbstractItemView.ScrollHint.PositionAtCenter)

    def columns_go_down(self):
        self.available_screens.get(self.legend_parameters[self.current_screen_index]).hide()
        self.current_screen_index += 1
        self.current_screen_index %= len(self.legend_parameters)
        self.available_screens.get(self.legend_parameters[self.current_screen_index]).show()
        new_screen_index = self.legend_parameter_model.index(self.current_screen_index)
        self.legend_parameter_list_view.setCurrentIndex(new_screen_index)
        self.legend_parameter_list_view.scrollTo(new_screen_index,QAbstractItemView.ScrollHint.PositionAtCenter)

    def close_application(self):
        self.close()

class grid_visible_adjustment_section(QWidget):
    def __init__(self,selected_graph,graph_display):
        super().__init__()

        self.selected_graph = selected_graph
        self.graph_display = graph_display
        self.plot_manager = PlotManager()
        
        self.grid_visible_state = False

        #Create a widget to display the grid visibility adjustment section and style it for consistency
        self.grid_visibility_adjustment_section = QWidget()
        self.grid_visibility_adjustment_section.setObjectName("grid_visibility_adjustment_section")
        self.grid_visibility_adjustment_section.setStyleSheet("""
            QWidget#grid_visibility_adjustment_section{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #f5f5ff,
                    stop:0.5 #f7f5fc,
                    stop:1 #f0f0ff
                );
                border: 2px solid black;
                border-radius: 16px;
            }
        """)

        #Create a label to put on top of the QPushButton
        self.grid_visibility_label = QLabel("Grid On")
        self.grid_visibility_label.setWordWrap(True)
        self.grid_visibility_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.grid_visibility_label.setObjectName("grid_visibility_label")
        self.grid_visibility_label.setStyleSheet("""
            QLabel#grid_visibility_label{
                font-family: "SF Pro Display";
                font-weight: 600;
                font-size: 24px;
                padding: 6px;
                color: black;
                border: none;
                background: transparent;
            }
        """)
        self.grid_visibility_label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
    
        #Create a button to allow the user to switch grid visibility
        self.grid_visibility_button = QPushButton()
        self.grid_visibility_button.setObjectName("grid_visibility_button")
        self.grid_visibility_button.setStyleSheet("""
            QPushButton#grid_visibility_button{
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
                font-size: 16px;
                padding: 6px;
                color: black;
            }
            QPushButton#grid_visibility_button:hover{
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
        self.grid_visibility_button.setMinimumHeight(50)
        
        #Put the label on top of the button we created for control grid visibility
        grid_visibility_button_layout = QVBoxLayout(self.grid_visibility_button)
        grid_visibility_button_layout.addWidget(self.grid_visibility_label)
        grid_visibility_button_layout.setContentsMargins(0,0,0,0)
        grid_visibility_button_layout.setSpacing(0)

        #Connect the grid visibility button to a function to switch between the two states
        self.grid_visibility_button.clicked.connect(self.switch_grid_visibility)

        #Create a button layout for the grid visibility adjustment section
        button_layout = QVBoxLayout(self.grid_visibility_adjustment_section)

        #Add the grid visibility button to the layout
        button_layout.addWidget(self.grid_visibility_button)

        #Set the spacing, margins, and stretch to make it look good
        button_layout.setSpacing(0)
        button_layout.setContentsMargins(10,10,10,10)
        button_layout.addStretch()

        #Create a layout for the main widget and store the frameon adjustment section in
        main_layout = QVBoxLayout(self)
        main_layout.addWidget(self.grid_visibility_adjustment_section)

        #Add the spacing and margins to make sure that the section fits nicely
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0,0,0,0)

    def switch_grid_visibility(self):
        self.grid_visible_state = not self.grid_visible_state
        if (self.grid_visible_state == False):
            self.grid_visibility_label.setText("Grid On")
        else:
            self.grid_visibility_label.setText("Grid Off")

        self.update_grid_visibility()

    def update_grid_visibility(self):
        db = self.plot_manager.get_db()
        if (db != []):
            self.plot_manager.update_grid("visible",self.grid_visible_state)
        else:
            plot_parameters = plot_json[self.selected_graph].copy()
            plot_parameters["grid"]["visible"] = self.grid_visible_state
            self.plot_manager.insert_plot_parameter(plot_parameters)
        self.graph_display.show_graph()

class grid_which_adjustment_section(QWidget):
    def __init__(self,selected_graph,graph_display):
        super().__init__()
        
        self.selected_graph = selected_graph
        self.graph_display = graph_display
        self.plot_manager = PlotManager()

        self.grid_which = ""
        self.grid_which_arguments = ["major","minor","both"]

        self.grid_which_adjustment_screen = QWidget()
        self.grid_which_adjustment_screen.setObjectName("grid_which_adjustment_screen")
        self.grid_which_adjustment_screen.setStyleSheet("""
            QWidget#grid_which_adjustment_screen{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #f5f5ff,
                    stop:0.5 #f7f5fc,
                    stop:1 #f0f0ff
                );
                border: 2px solid black;
                border-radius: 16px;
            }
        """)
        self.create_grid_which_adjustment_screen()
        
        main_layout = QVBoxLayout(self)
        main_layout.addWidget(self.grid_which_adjustment_screen)
        main_layout.setContentsMargins(0,0,0,0)
        main_layout.setSpacing(0) 

    def create_grid_which_adjustment_screen(self):
        grid_which_adjustment_screen_layout = QVBoxLayout(self.grid_which_adjustment_screen)

        self.grid_which_adjustment_list_view = QListView()
        self.grid_which_adjustment_model = QStringListModel(self.grid_which_arguments)

        self.grid_which_adjustment_list_view.setModel(self.grid_which_adjustment_model)
        self.grid_which_adjustment_list_view.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.grid_which_adjustment_list_view.setObjectName("grid_which_adjustment_list_view")
        self.grid_which_adjustment_list_view.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)

        class CustomDelegate(QStyledItemDelegate):
            def paint(self, painter, option, index):
                option.displayAlignment = Qt.AlignmentFlag.AlignCenter
                font = QFont("SF Pro Display", 24)
                font.setWeight(600)
                option.font = font
                super().paint(painter, option, index)
        
        self.grid_which_adjustment_list_view.setItemDelegate(CustomDelegate())

        self.grid_which_adjustment_list_view.setStyleSheet("""
            QListView#grid_which_adjustment_list_view{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #f5f5ff,
                    stop:0.5 #f7f5fc,
                    stop:1 #f0f0ff
                );
                border: transparent;
                border-radius: 16px;
            }
            QListView#grid_which_adjustment_list_view::item {
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
            QListView#grid_which_adjustment_list_view::item:selected {
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
            QListView#grid_which_adjustment_list_view::item:hover {
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

        self.grid_which_adjustment_list_view.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.grid_which_adjustment_list_view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.grid_which_adjustment_list_view.setSpacing(3)

        self.grid_which_adjustment_list_view.clicked.connect(self.change_grid_which_argument)
        grid_which_adjustment_screen_layout.addWidget(self.grid_which_adjustment_list_view)

        # Add margins and spacing to make it look good and push content to the top
        grid_which_adjustment_screen_layout.setContentsMargins(10, 10, 10, 10)

    def change_grid_which_argument(self,index):
        self.grid_which = self.grid_which_adjustment_model.data(index,Qt.ItemDataRole.DisplayRole)
        self.update_grid_which()

    def update_grid_which(self):
        db  = self.plot_manager.get_db()
        if (db != []):
            self.plot_manager.update_grid("which",self.grid_which)
        else: 
            plot_parameters = plot_json[self.selected_graph].copy()
            plot_parameters["grid"]["which"] = self.grid_which
            self.plot_manager.insert_plot_parameter(plot_parameters)
        self.graph_display.show_graph()

class grid_axis_adjustment_section(QWidget):
    def __init__(self,selected_graph,graph_display):
        super().__init__()
        
        self.selected_graph = selected_graph
        self.graph_display = graph_display
        self.plot_manager = PlotManager()

        self.grid_axis = ""
        self.grid_axis_arguments = ["both","x","y"]

        self.grid_axis_adjustment_screen = QWidget()
        self.grid_axis_adjustment_screen.setObjectName("grid_axis_adjustment_screen")
        self.grid_axis_adjustment_screen.setStyleSheet("""
            QWidget#grid_axis_adjustment_screen{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #f5f5ff,
                    stop:0.5 #f7f5fc,
                    stop:1 #f0f0ff
                );
                border: 2px solid black;
                border-radius: 16px;
            }
        """)
        self.create_grid_axis_adjustment_screen()
        
        main_layout = QVBoxLayout(self)
        main_layout.addWidget(self.grid_axis_adjustment_screen)
        main_layout.setContentsMargins(0,0,0,0)
        main_layout.setSpacing(0) 

    def create_grid_axis_adjustment_screen(self):
        grid_axis_adjustment_screen_layout = QVBoxLayout(self.grid_axis_adjustment_screen)

        self.grid_axis_adjustment_list_view = QListView()
        self.grid_axis_adjustment_model = QStringListModel(self.grid_axis_arguments)

        self.grid_axis_adjustment_list_view.setModel(self.grid_axis_adjustment_model)
        self.grid_axis_adjustment_list_view.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.grid_axis_adjustment_list_view.setObjectName("grid_axis_adjustment_list_view")
        self.grid_axis_adjustment_list_view.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)

        class CustomDelegate(QStyledItemDelegate):
            def paint(self, painter, option, index):
                option.displayAlignment = Qt.AlignmentFlag.AlignCenter
                font = QFont("SF Pro Display", 24)
                font.setWeight(600)
                option.font = font
                super().paint(painter, option, index)
        
        self.grid_axis_adjustment_list_view.setItemDelegate(CustomDelegate())

        self.grid_axis_adjustment_list_view.setStyleSheet("""
            QListView#grid_axis_adjustment_list_view{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #f5f5ff,
                    stop:0.5 #f7f5fc,
                    stop:1 #f0f0ff
                );
                border: transparent;
                border-radius: 16px;
            }
            QListView#grid_axis_adjustment_list_view::item {
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
            QListView#grid_axis_adjustment_list_view::item:selected {
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
            QListView#grid_axis_adjustment_list_view::item:hover {
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

        self.grid_axis_adjustment_list_view.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.grid_axis_adjustment_list_view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.grid_axis_adjustment_list_view.setSpacing(3)

        self.grid_axis_adjustment_list_view.clicked.connect(self.change_grid_axis_argument)
        grid_axis_adjustment_screen_layout.addWidget(self.grid_axis_adjustment_list_view)

        # Add margins and spacing to make it look good and push content to the top
        grid_axis_adjustment_screen_layout.setContentsMargins(10, 10, 10, 10)

    def change_grid_axis_argument(self,index):
        self.grid_axis = self.grid_axis_adjustment_model.data(index,Qt.ItemDataRole.DisplayRole)
        self.update_grid_axis()

    def update_grid_axis(self):
        db  = self.plot_manager.get_db()
        if (db != []):
            self.plot_manager.update_grid("axis",self.grid_axis)
        else: 
            plot_parameters = plot_json[self.selected_graph].copy()
            plot_parameters["grid"]["axis"] = self.grid_axis
            self.plot_manager.insert_plot_parameter(plot_parameters)
        self.graph_display.show_graph()
        
class grid_color_adjustment_section(QWidget):
    def __init__(self,selected_graph,graph_display):
        super().__init__()

        self.graph_display = graph_display
        self.plot_manager = PlotManager()
        self.selected_graph = selected_graph

        self.named_colors = list(mcolors.get_named_colors_mapping().keys())
        self.short_code_colors = self.named_colors[-8:]
        self.named_colors = [c.replace("xkcd:","") for c in self.named_colors]
        self.named_colors = [c.replace("tab:","") for c in self.named_colors]
        self.named_colors = self.named_colors[:-8]

        self.current_grid_color = ""

        #-----Home Screen-----

        self.grid_color_adjustment_homescreen = QWidget()
        self.grid_color_adjustment_homescreen.setObjectName("grid_color_adjustment_homescreen")
        self.grid_color_adjustment_homescreen.setStyleSheet("""
            QWidget#grid_color_adjustment_homescreen{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #f5f5ff,
                    stop:0.5 #f7f5fc,
                    stop:1 #f0f0ff
                );
                border: 2px solid black;
                border-radius: 16px;
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

        button_layout = QVBoxLayout(self.grid_color_adjustment_homescreen)
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
                border-radius: 16px;
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
                border-radius: 16px;
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
                border-radius: 16px;
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
                border-radius: 16px;
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
                border-radius: 16px;
            }  
        """)
        self.create_short_code_color_screen()
        self.short_code_color_screen.hide()

        #-----Initialize Screen Value-----

        self.available_screens = [self.grid_color_adjustment_homescreen,self.named_color_screen,
                                self.hex_code_color_screen,self.rgba_color_screen,
                                self.grayscale_color_screen,self.short_code_color_screen]
        self.previous_screen_idx = 0
        self.current_screen_idx = 0

        #-----Main Screen-----
        main_layout = QVBoxLayout(self)
        main_layout.addWidget(self.grid_color_adjustment_homescreen)
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
                border-radius: 16px;
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
                border-radius: 16px;
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
                border-radius: 16px;
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
                border-radius: 16px;
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
                border-radius: 16px;
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
                border-radius: 16px;
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
                border-radius: 16px;
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
                border-radius: 16px;
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
        self.short_code_color_list_view.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
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
                border-radius: 16px;
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
        self.grid_color_adjustment_homescreen.show()

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
        self.current_grid_color = None
        self.update_grid_color()

    def change_named_color(self,index):
        source_index = self.filter_proxy.mapToSource(index)
        self.current_grid_color = self.named_color_model.data(source_index, Qt.ItemDataRole.DisplayRole)
        self.update_grid_color()

    def change_hex_code_color(self):
        hex_code = self.hex_code_input.text().strip()

        if (hex_code == ""):
            self.hex_valid_input_widget.hide()
            self.hex_invalid_input_widget.hide()
            self.current_grid_color = None
            self.update_grid_color()
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
                self.current_grid_color = hex_code if hex_code[0] == "#" else "#" + hex_code
                self.update_grid_color()
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
            self.current_grid_color = None
            self.update_grid_color()
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

            self.current_grid_color = self.initial_rgba

            self.update_grid_color()
        else:
            self.rgba_valid_input_widget.hide()
            self.rgba_invalid_input_widget.show()

    def change_grayscale_color(self):
        grayscale_value = self.grayscale_input.text().strip()

        if (grayscale_value == ""): 
            self.grayscale_valid_input_widget.hide() 
            self.grayscale_invalid_input_widget.hide()
            self.current_grid_color = None
            self.update_grid_color()
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

        self.current_grid_color = grayscale_value
        self.update_grid_color()

    def change_short_code_color(self,index):
        self.current_grid_color = self.short_code_color_model.data(index, Qt.ItemDataRole.DisplayRole)
        self.update_grid_color()

    def update_grid_color(self):
        db = self.plot_manager.get_db()
        if (db != []):
            self.plot_manager.update_grid("color",self.current_grid_color)
        else:
            plot_parameters = plot_json[self.selected_graph].copy()
            plot_parameters["grid"]["color"] = self.current_grid_color
            self.plot_manager.insert_plot_parameter(plot_parameters)
        self.graph_display.show_graph()

    def mousePressEvent(self, event):
        if not self.color_search_bar.geometry().contains(event.position().toPoint()):
            self.color_search_bar.clearFocus()
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

class grid_linestyle_adjustment_section(QWidget):
    def __init__(self,selected_graph,graph_display):
        super().__init__()
        
        self.selected_graph = selected_graph
        self.graph_display = graph_display
        self.plot_manager = PlotManager()

        self.premade_linestyle_options = ["solid (-)","dashed (--)","dashdot (-.)","dotted (:)","None (—)"]
        self.linestyle_arguments = list(map(lambda x:x[x.index("(")+1:x.index(")")],self.premade_linestyle_options))
        self.linestyle_arguments = [linestyle if "None" not in name else "" for name,linestyle in zip(self.premade_linestyle_options,self.linestyle_arguments)]

        self.grid_linestyle = ""

        self.grid_offset = ""
        self.grid_sequence = ""

        #-----Valid Offset Widget-----
        self.valid_offset_widget = QWidget()
        self.valid_offset_widget.setObjectName("valid_offset_widget")
        self.valid_offset_widget.setStyleSheet("""
            QWidget#valid_offset_widget{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(94, 255, 234, 1),   
                    stop:0.3 rgba(63, 252, 180, 1), 
                    stop:0.6 rgba(150, 220, 255, 1),  
                    stop:1 rgba(180, 200, 255, 1)  
                );
                border: 2px solid black;
                border-radius: 16px;
            }
        """)

        self.valid_offset_label = QLabel("Valid Offset")
        self.valid_offset_label.setObjectName("valid_offset_label")
        self.valid_offset_label.setWordWrap(True)
        self.valid_offset_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.valid_offset_label.setStyleSheet("""
            QLabel#valid_offset_label{
                font-family: "SF Pro Display";
                font-weight: 600;
                font-size: 24px;
                padding: 6px;
                color: black;
                border: none;
                background: transparent;
            }
        """)
        
        valid_offset_widget_layout = QVBoxLayout(self.valid_offset_widget)
        valid_offset_widget_layout.addWidget(self.valid_offset_label)
        valid_offset_widget_layout.setContentsMargins(0,0,0,0)
        valid_offset_widget_layout.setSpacing(0)

        #-----Invalid Offset Widget-----
        self.invalid_offset_widget = QWidget()
        self.invalid_offset_widget.setObjectName("invalid_offset_widget")
        self.invalid_offset_widget.setStyleSheet("""
            QWidget#invalid_offset_widget{
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

        self.invalid_offset_label = QLabel("Invalid Offset")
        self.invalid_offset_label.setObjectName("invalid_offset_label")
        self.invalid_offset_label.setWordWrap(True)
        self.invalid_offset_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.invalid_offset_label.setStyleSheet("""
            QLabel#invalid_offset_label{
                font-family: "SF Pro Display";
                font-weight: 600;
                font-size: 24px;
                padding: 6px;
                color: black;
                border: none;
                background: transparent;
            }
        """)
        
        invalid_offset_widget_layout = QVBoxLayout(self.invalid_offset_widget)
        invalid_offset_widget_layout.addWidget(self.invalid_offset_label)
        invalid_offset_widget_layout.setContentsMargins(0,0,0,0)
        invalid_offset_widget_layout.setSpacing(0)

        #-----Valid On Off Sequence Widget-----
        self.valid_on_off_sequence_widget = QWidget()
        self.valid_on_off_sequence_widget.setObjectName("valid_on_off_sequence_widget")
        self.valid_on_off_sequence_widget.setStyleSheet("""
            QWidget#valid_on_off_sequence_widget{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(94, 255, 234, 1),   
                    stop:0.3 rgba(63, 252, 180, 1), 
                    stop:0.6 rgba(150, 220, 255, 1),  
                    stop:1 rgba(180, 200, 255, 1)  
                );
                border: 2px solid black;
                border-radius: 16px;
            }
        """)

        self.valid_on_off_sequence_label = QLabel("Valid Sequence")
        self.valid_on_off_sequence_label.setObjectName("valid_on_off_sequence_label")
        self.valid_on_off_sequence_label.setWordWrap(True)
        self.valid_on_off_sequence_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.valid_on_off_sequence_label.setStyleSheet("""
            QLabel#valid_on_off_sequence_label{
                font-family: "SF Pro Display";
                font-weight: 600;
                font-size: 24px;
                padding: 6px;
                color: black;
                border: none;
                background: transparent;
            }
        """)
        
        valid_on_off_sequence_widget_layout = QVBoxLayout(self.valid_on_off_sequence_widget)
        valid_on_off_sequence_widget_layout.addWidget(self.valid_on_off_sequence_label)
        valid_on_off_sequence_widget_layout.setContentsMargins(0,0,0,0)
        valid_on_off_sequence_widget_layout.setSpacing(0)

        #-----Invalid On Off Sequence Widget-----
        self.invalid_on_off_sequence_widget = QWidget()
        self.invalid_on_off_sequence_widget.setObjectName("invalid_on_off_sequence_widget")
        self.invalid_on_off_sequence_widget.setStyleSheet("""
            QWidget#invalid_on_off_sequence_widget{
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

        self.invalid_on_off_sequence_label = QLabel("Invalid Sequence")
        self.invalid_on_off_sequence_label.setObjectName("invalid_on_off_sequence_label")
        self.invalid_on_off_sequence_label.setWordWrap(True)
        self.invalid_on_off_sequence_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.invalid_on_off_sequence_label.setStyleSheet("""
            QLabel#invalid_on_off_sequence_label{
                font-family: "SF Pro Display";
                font-weight: 600;
                font-size: 24px;
                padding: 6px;
                color: black;
                border: none;
                background: transparent;
            }
        """)
        
        invalid_on_off_sequence_widget_layout = QVBoxLayout(self.invalid_on_off_sequence_widget)
        invalid_on_off_sequence_widget_layout.addWidget(self.invalid_on_off_sequence_label)
        invalid_on_off_sequence_widget_layout.setContentsMargins(0,0,0,0)
        invalid_on_off_sequence_widget_layout.setSpacing(0)

        #-----Control the Widget Size and hide them-----
        self.valid_offset_widget.setMinimumHeight(50)
        self.invalid_offset_widget.setMinimumHeight(50)
        
        self.valid_on_off_sequence_widget.setMinimumHeight(50)
        self.invalid_on_off_sequence_widget.setMinimumHeight(50)

        self.valid_offset_widget.hide()
        self.invalid_offset_widget.hide()

        self.valid_on_off_sequence_widget.hide()
        self.invalid_on_off_sequence_widget.hide()

        #-----Grid Linestyle Adjustment Screen-----
        self.grid_linestyle_adjustment_screen = QWidget()
        self.grid_linestyle_adjustment_screen.setObjectName("grid_linestyle_adjustment_screen")
        self.grid_linestyle_adjustment_screen.setStyleSheet("""
            QWidget#grid_linestyle_adjustment_screen{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #f5f5ff,
                    stop:0.5 #f7f5fc,
                    stop:1 #f0f0ff
                );
                border: 2px solid black;
                border-radius: 16px;
            }
        """)

        #-----Premade Linestyle Button and Label-----
        self.premade_linestyle_button = QPushButton()
        self.premade_linestyle_button.setObjectName("premade_linestyle_button")
        self.premade_linestyle_button.setStyleSheet("""
            QPushButton#premade_linestyle_button{
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
            QPushButton#premade_linestyle_button:hover{
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

        self.premade_linestyle_label = QLabel("Premade Linestyle")
        self.premade_linestyle_label.setObjectName("premade_linestyle_label")
        self.premade_linestyle_label.setWordWrap(True)
        self.premade_linestyle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.premade_linestyle_label.setStyleSheet("""
            QLabel#premade_linestyle_label{
                font-family: "SF Pro Display";
                font-weight: 600;
                font-size: 24px;
                padding: 6px;
                color: black;
                border: none;
                background: transparent;
            }
        """)
        self.premade_linestyle_label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

        premade_linestyle_button_layout = QVBoxLayout(self.premade_linestyle_button)
        premade_linestyle_button_layout.addWidget(self.premade_linestyle_label)
        premade_linestyle_button_layout.setContentsMargins(0,0,0,0)
        premade_linestyle_button_layout.setSpacing(0)

        #-----Custom Linestyle Button and Label-----
        self.custom_linestyle_button = QPushButton()
        self.custom_linestyle_button.setObjectName("custom_linestyle_button")
        self.custom_linestyle_button.setStyleSheet("""
            QPushButton#custom_linestyle_button{
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
            QPushButton#custom_linestyle_button:hover{
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

        self.custom_linestyle_label = QLabel("Custom Linestyle")
        self.custom_linestyle_label.setObjectName("custom_linestyle_label")
        self.custom_linestyle_label.setWordWrap(True)
        self.custom_linestyle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.custom_linestyle_label.setStyleSheet("""
            QLabel#custom_linestyle_label{
                font-family: "SF Pro Display";
                font-weight: 600;
                font-size: 24px;
                padding: 6px;
                color: black;
                border: none;
                background: transparent;
            }
        """)
        self.custom_linestyle_label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

        custom_linestyle_button_layout = QVBoxLayout(self.custom_linestyle_button)
        custom_linestyle_button_layout.addWidget(self.custom_linestyle_label)
        custom_linestyle_button_layout.setContentsMargins(0,0,0,0)
        custom_linestyle_button_layout.setSpacing(0)

        #-----Set the size for each button-----
        self.premade_linestyle_button.setMinimumHeight(45)
        self.custom_linestyle_button.setMinimumHeight(45)

        #-----Connect Each Button to its associated function-----
        self.premade_linestyle_button.clicked.connect(self.change_to_premade_linestyle_screen)
        self.custom_linestyle_button.clicked.connect(self.change_to_custom_linestyle_screen)

        #-----Add Buttons to Grid Linestyle Adjustment Screen-----
        grid_linestyle_adjustment_screen_layout = QVBoxLayout(self.grid_linestyle_adjustment_screen)
        grid_linestyle_adjustment_screen_layout.addWidget(self.premade_linestyle_button)
        grid_linestyle_adjustment_screen_layout.addWidget(self.custom_linestyle_button)
        grid_linestyle_adjustment_screen_layout.setContentsMargins(10,10,10,10)
        grid_linestyle_adjustment_screen_layout.setSpacing(5)
        grid_linestyle_adjustment_screen_layout.addStretch()

        #-----Premade Linestyle Screen-----
        self.premade_linestyle_screen = QWidget()
        self.premade_linestyle_screen.setObjectName("premade_linestyle_screen")
        self.premade_linestyle_screen.setStyleSheet("""
            QWidget#premade_linestyle_screen{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #f5f5ff,
                    stop:0.5 #f7f5fc,
                    stop:1 #f0f0ff
                );
                border: 2px solid black;
                border-radius: 16px;
            }
        """)
        self.create_premade_linestyle_screen()
        self.premade_linestyle_screen.hide()

        #-----Custom Linestyle Screen-----
        self.custom_linestyle_screen = QWidget()
        self.custom_linestyle_screen.setObjectName("custom_linestyle_screen")
        self.custom_linestyle_screen.setStyleSheet("""
            QWidget#custom_linestyle_screen{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #f5f5ff,
                    stop:0.5 #f7f5fc,
                    stop:1 #f0f0ff
                );
                border: 2px solid black;
                border-radius: 16px;
            }
        """)
        self.create_custom_linestyle_screen()
        self.custom_linestyle_screen.hide()

        #-----Available Screen and Screen Index-----
        self.available_screens = [self.grid_linestyle_adjustment_screen,self.premade_linestyle_screen,
                                self.custom_linestyle_screen]
        self.current_screen_idx = 0

        #-----Add the Screens to the Main Layout-----
        main_layout = QVBoxLayout(self)
        main_layout.addWidget(self.grid_linestyle_adjustment_screen)
        main_layout.addWidget(self.premade_linestyle_screen)
        main_layout.addWidget(self.custom_linestyle_screen)
        main_layout.setContentsMargins(0,0,0,0)
        main_layout.setSpacing(0)

        #-----Keyboard Shortcut-----
        home_screen_shortcut = QShortcut(QKeySequence("left"),self)
        home_screen_shortcut.activated.connect(self.change_to_home_screen)

    def create_premade_linestyle_screen(self):
        premade_linestyle_screen_layout = QVBoxLayout(self.premade_linestyle_screen)

        self.premade_linestyle_list_view = QListView()
        self.premade_linestyle_model = QStringListModel(self.premade_linestyle_options)

        self.premade_linestyle_list_view.setModel(self.premade_linestyle_model)
        self.premade_linestyle_list_view.setObjectName("premade_linestyle_list_view")

        class CustomDelegate(QStyledItemDelegate):
            def paint(self, painter, option, index):
                option.displayAlignment = Qt.AlignmentFlag.AlignCenter
                font = QFont("SF Pro Display", 24)
                font.setWeight(600)
                option.font = font
                super().paint(painter, option, index)
        
        self.premade_linestyle_list_view.setItemDelegate(CustomDelegate())

        self.premade_linestyle_list_view.setStyleSheet("""
            QListView#premade_linestyle_list_view{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #f5f5ff,
                    stop:0.5 #f7f5fc,
                    stop:1 #f0f0ff
                );
                border: transparent;
                border-radius: 16px;
            }
            QListView#premade_linestyle_list_view::item {
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
            QListView#premade_linestyle_list_view::item:selected {
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
            QListView#premade_linestyle_list_view::item:hover {
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

        self.premade_linestyle_list_view.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.premade_linestyle_list_view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.premade_linestyle_list_view.setSpacing(3)

        self.premade_linestyle_list_view.clicked.connect(self.change_premade_linestyle)

        premade_linestyle_screen_layout.addWidget(self.premade_linestyle_list_view)

        # Add margins and spacing to make it look good and push content to the top
        premade_linestyle_screen_layout.setContentsMargins(10, 10, 10, 10)

    def create_custom_linestyle_screen(self):
        custom_linestyle_screen_layout = QVBoxLayout(self.custom_linestyle_screen)

        instructions_widget = QWidget()
        instructions_widget.setObjectName("instructions_widget")
        instructions_widget.setStyleSheet("""
            QWidget#instructions_widget{
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
            }
        """)

        instructions_label = QLabel("Enter the Sequence Separated By Spaces")
        instructions_label.setObjectName("instructions_label")
        instructions_label.setWordWrap(True)
        instructions_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        instructions_label.setStyleSheet("""
            QLabel#instructions_label{
                font-family: "SF Pro Display";
                font-weight: 600;
                font-size: 24px;
                padding: 6px;
                color: black;
                border: none;
                background: transparent;
            }
        """)

        instructions_layout = QVBoxLayout(instructions_widget)
        instructions_layout.addWidget(instructions_label)
        instructions_layout.setContentsMargins(0,0,0,0)
        instructions_layout.setSpacing(0)

        self.offset_input = QLineEdit()
        self.offset_input.setObjectName("offset_input")
        self.offset_input.setPlaceholderText("Offset:")
        self.offset_input.setStyleSheet("""
            QLineEdit#offset_input{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #f5f5ff,
                    stop:0.5 #f7f5fc,
                    stop:1 #f0f0ff
                );
                color: black;
                font-size: 24pt;
                border: 2px solid black;
                border-radius: 16px;
            }
        """)

        self.sequence_input = QLineEdit()
        self.sequence_input.setObjectName("on_off_sequence")
        self.sequence_input.setPlaceholderText("Sequence:")
        self.sequence_input.setStyleSheet("""
            QLineEdit#on_off_sequence{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #f5f5ff,
                    stop:0.5 #f7f5fc,
                    stop:1 #f0f0ff
                );
                color: black;
                font-size: 24pt;
                border: 2px solid black;
                border-radius: 16px;
            }
        """)

        self.offset_input.setMinimumHeight(60)
        self.sequence_input.setMinimumHeight(60)

        self.offset_input.textChanged.connect(self.change_grid_linestyle_offset)
        self.sequence_input.textChanged.connect(self.change_grid_linestyle_sequence)

        custom_linestyle_screen_layout.addWidget(instructions_widget)
        custom_linestyle_screen_layout.addWidget(self.offset_input)
        custom_linestyle_screen_layout.addWidget(self.sequence_input)
        custom_linestyle_screen_layout.addWidget(self.valid_offset_widget)
        custom_linestyle_screen_layout.addWidget(self.invalid_offset_widget)
        custom_linestyle_screen_layout.addWidget(self.valid_on_off_sequence_widget)
        custom_linestyle_screen_layout.addWidget(self.invalid_on_off_sequence_widget)
        
        custom_linestyle_screen_layout.setContentsMargins(10,10,10,10)
        custom_linestyle_screen_layout.setSpacing(10)
        custom_linestyle_screen_layout.addStretch()

    def change_to_home_screen(self):
        self.available_screens[self.current_screen_idx].hide()
        self.current_screen_idx = 0
        self.available_screens[self.current_screen_idx].show()

    def change_to_premade_linestyle_screen(self):
        self.available_screens[self.current_screen_idx].hide()
        self.current_screen_idx = 1
        self.available_screens[self.current_screen_idx].show()

    def change_to_custom_linestyle_screen(self):
        self.available_screens[self.current_screen_idx].hide()
        self.current_screen_idx = 2
        self.available_screens[self.current_screen_idx].show()

    def change_premade_linestyle(self,index):
        index = self.premade_linestyle_options.index(self.premade_linestyle_model.data(index,Qt.ItemDataRole.DisplayRole))
        self.grid_linestyle = self.linestyle_arguments[index]
        self.update_grid_linestyle()

    def change_grid_linestyle_offset(self):
        grid_linestyle_offset = self.offset_input.text().strip()

        if (grid_linestyle_offset == ""):
            self.valid_offset_widget.hide()
            self.invalid_offset_widget.hide()
            self.valid_on_off_sequence_widget.hide()
            self.invalid_on_off_sequence_widget.hide()
            self.grid_offset = ""
            self.update_grid_linestyle()
            return

        try:
            grid_linestyle_offset = float(grid_linestyle_offset)
            if (grid_linestyle_offset < 0):
                raise Exception
            self.valid_offset_widget.show()
            self.invalid_offset_widget.hide()
            self.valid_on_off_sequence_widget.hide()
            self.invalid_on_off_sequence_widget.hide()
        except:
            self.valid_offset_widget.hide()
            self.invalid_offset_widget.show()
            self.valid_on_off_sequence_widget.hide()
            self.invalid_on_off_sequence_widget.hide()

        self.grid_offset = grid_linestyle_offset
        self.change_custom_grid_linestyle()
        self.update_grid_linestyle()

    def change_grid_linestyle_sequence(self):
        grid_linestyle_sequence = self.sequence_input.text().strip().split(" ")
        grid_linestyle_sequence = list(filter(lambda x:x != "",grid_linestyle_sequence))

        if (grid_linestyle_sequence == []):
            self.valid_on_off_sequence_widget.hide()
            self.invalid_on_off_sequence_widget.hide()
            self.valid_offset_widget.hide() 
            self.invalid_offset_widget.hide()
            self.grid_sequence = ""
            self.update_grid_linestyle()
            return

        try:
            grid_linestyle_sequence = list(map(float,grid_linestyle_sequence))
            
            if (len(list(filter(lambda x:x < 0,grid_linestyle_sequence))) != 0):
                raise Exception

            if (len(grid_linestyle_sequence) < 4 or len(grid_linestyle_sequence) % 2 != 0):
                raise Exception

            self.valid_on_off_sequence_widget.show()
            self.invalid_on_off_sequence_widget.hide()
            self.valid_offset_widget.hide() 
            self.invalid_offset_widget.hide()
        except:
            self.valid_on_off_sequence_widget.hide()
            self.invalid_on_off_sequence_widget.show()
            self.valid_offset_widget.hide() 
            self.invalid_offset_widget.hide()

        self.grid_sequence = grid_linestyle_sequence
        
        self.change_custom_grid_linestyle()
        self.update_grid_linestyle()

    def change_custom_grid_linestyle(self):
        if (self.grid_offset != "" and self.grid_sequence != ""): 
            self.grid_linestyle = [self.grid_offset,self.grid_sequence]
            self.update_grid_linestyle()

    def update_grid_linestyle(self):
        db = self.plot_manager.get_db()
        if (db != []):
            self.plot_manager.update_grid("linestyle",self.grid_linestyle)
        else:
            plot_parameters = plot_json[self.selected_graph].copy()
            plot_parameters["grid"]["linestyle"] = self.grid_linestyle
            self.plot_manager.insert_plot_parameter(plot_parameters)
        self.graph_display.show_graph()
    
    def mousePressEvent(self, event):
        if not self.offset_input.geometry().contains(event.position().toPoint()):
            self.offset_input.clearFocus()
        if not self.sequence_input.geometry().contains(event.position().toPoint()):
            self.sequence_input.clearFocus()
        super().mousePressEvent(event)

class grid_linewidth_adjustment_section(QWidget):
    def __init__(self,selected_graph,graph_display):
        super().__init__()
        
        self.selected_graph = selected_graph
        self.graph_display = graph_display
        self.plot_manager = PlotManager()

        self.grid_linewidth = ""

        #-----Valid Offset Widget-----
        self.valid_linewidth_widget = QWidget()
        self.valid_linewidth_widget.setObjectName("valid_linewidth_widget")
        self.valid_linewidth_widget.setStyleSheet("""
            QWidget#valid_linewidth_widget{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(94, 255, 234, 1),   
                    stop:0.3 rgba(63, 252, 180, 1), 
                    stop:0.6 rgba(150, 220, 255, 1),  
                    stop:1 rgba(180, 200, 255, 1)  
                );
                border: 2px solid black;
                border-radius: 16px;
            }
        """)

        self.valid_linewidth_label = QLabel("Valid Linewidth")
        self.valid_linewidth_label.setObjectName("valid_linewidth_label")
        self.valid_linewidth_label.setWordWrap(True)
        self.valid_linewidth_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.valid_linewidth_label.setStyleSheet("""
            QLabel#valid_linewidth_label{
                font-family: "SF Pro Display";
                font-weight: 600;
                font-size: 24px;
                padding: 6px;
                color: black;
                border: none;
                background: transparent;
            }
        """)
        
        valid_linewidth_widget_layout = QVBoxLayout(self.valid_linewidth_widget)
        valid_linewidth_widget_layout.addWidget(self.valid_linewidth_label)
        valid_linewidth_widget_layout.setContentsMargins(0,0,0,0)
        valid_linewidth_widget_layout.setSpacing(0)

        #-----Invalid Offset Widget-----
        self.invalid_linewidth_widget = QWidget()
        self.invalid_linewidth_widget.setObjectName("invalid_linewidth_widget")
        self.invalid_linewidth_widget.setStyleSheet("""
            QWidget#invalid_linewidth_widget{
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

        self.invalid_linewidth_label = QLabel("Invalid Linewidth")
        self.invalid_linewidth_label.setObjectName("invalid_linewidth_label")
        self.invalid_linewidth_label.setWordWrap(True)
        self.invalid_linewidth_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.invalid_linewidth_label.setStyleSheet("""
            QLabel#invalid_linewidth_label{
                font-family: "SF Pro Display";
                font-weight: 600;
                font-size: 24px;
                padding: 6px;
                color: black;
                border: none;
                background: transparent;
            }
        """)
        
        invalid_linewidth_widget_layout = QVBoxLayout(self.invalid_linewidth_widget)
        invalid_linewidth_widget_layout.addWidget(self.invalid_linewidth_label)
        invalid_linewidth_widget_layout.setContentsMargins(0,0,0,0)
        invalid_linewidth_widget_layout.setSpacing(0)

        #-----Hide Both Validity Check Widgets-----
        self.valid_linewidth_widget.hide()
        self.invalid_linewidth_widget.hide()

        #-----Set the size for both Validitiy Check Widgets-----
        self.valid_linewidth_widget.setMinimumHeight(50)
        self.invalid_linewidth_widget.setMinimumHeight(50)

        #-----Grid Linewidth Adjustment Screen-----
        self.grid_linewidth_adjustment_screen = QWidget()
        self.grid_linewidth_adjustment_screen.setObjectName("grid_linewidth_adjustment")
        self.grid_linewidth_adjustment_screen.setStyleSheet(""" 
            QWidget#grid_linewidth_adjustment{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #f5f5ff,
                    stop:0.5 #f7f5fc,
                    stop:1 #f0f0ff
                );
                border: 2px solid black;
                border-radius: 16px;
            }
        """)
        
        #-----Grid Linewidth Input-----
        self.grid_linewidth_input = QLineEdit()
        self.grid_linewidth_input.setObjectName("grid_linewidth_input")
        self.grid_linewidth_input.setPlaceholderText("Linewidth: ")
        self.grid_linewidth_input.setStyleSheet("""
            QLineEdit#grid_linewidth_input{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #f5f5ff,
                    stop:0.5 #f7f5fc,
                    stop:1 #f0f0ff
                );
                color: black;
                font-size: 24pt;
                border: 2px solid black;
                border-radius: 16px;
            }
        """)

        self.grid_linewidth_input.textChanged.connect(self.change_grid_linewidth)
        self.grid_linewidth_input.setMinimumHeight(60)

        #-----Grid Linewidth Adjustment Screen Layout-----
        grid_linewidth_adjustment_screen_layout = QVBoxLayout(self.grid_linewidth_adjustment_screen)
        grid_linewidth_adjustment_screen_layout.addWidget(self.grid_linewidth_input)
        grid_linewidth_adjustment_screen_layout.addWidget(self.valid_linewidth_widget)
        grid_linewidth_adjustment_screen_layout.addWidget(self.invalid_linewidth_widget)
        grid_linewidth_adjustment_screen_layout.setContentsMargins(10,10,10,10)
        grid_linewidth_adjustment_screen_layout.setSpacing(10)
        grid_linewidth_adjustment_screen_layout.addStretch()

        main_layout = QVBoxLayout(self)
        main_layout.addWidget(self.grid_linewidth_adjustment_screen)
        main_layout.setContentsMargins(0,0,0,0)
        main_layout.setSpacing(0)

    def change_grid_linewidth(self): 
        linewidth = self.grid_linewidth_input.text().strip()
        if (linewidth == ""):
            self.valid_linewidth_widget.hide()
            self.invalid_linewidth_widget.hide()
            self.grid_linewidth = 0.8
            self.update_grid_linewidth()
            return

        try:
            linewidth = float(linewidth)
            if (linewidth < 0): 
                raise Exception
            self.valid_linewidth_widget.show()
            self.invalid_linewidth_widget.hide()
        except:
            linewidth = 0.8
            self.valid_linewidth_widget.hide()
            self.invalid_linewidth_widget.show()

        self.grid_linewidth = linewidth
        self.update_grid_linewidth()

    def update_grid_linewidth(self):
        db = self.plot_manager.get_db()
        if (db != []):
            self.plot_manager.update_grid("linewidth",self.grid_linewidth)
        else:
            plot_parameters = plot_json[self.selected_graph].copy()
            plot_parameters["grid"]["linewidth"] = self.grid_linewidth
            self.plot_manager.insert_plot_parameter(plot_parameters)
        self.graph_display.show_graph()

    def mousePressEvent(self,event):
        if not self.grid_linewidth_input.geometry().contains(event.position().toPoint()):
            self.grid_linewidth_input.clearFocus()
        super().mousePressEvent(event)

class grid_alpha_adjustment_section(QWidget):
    def __init__(self,selected_graph,graph_display):
        super().__init__()
        
        self.selected_graph = selected_graph
        self.graph_display = graph_display
        self.plot_manager = PlotManager()

        self.grid_alpha = ""

        #-----Valid Alpha Widget-----
        self.valid_alpha_widget = QWidget()
        self.valid_alpha_widget.setObjectName("valid_alpha_widget")
        self.valid_alpha_widget.setStyleSheet("""
            QWidget#valid_alpha_widget{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(94, 255, 234, 1),   
                    stop:0.3 rgba(63, 252, 180, 1), 
                    stop:0.6 rgba(150, 220, 255, 1),  
                    stop:1 rgba(180, 200, 255, 1)  
                );
                border: 2px solid black;
                border-radius: 16px;
            }
        """)

        self.valid_alpha_label = QLabel("Valid Alpha")
        self.valid_alpha_label.setObjectName("valid_alpha_label")
        self.valid_alpha_label.setWordWrap(True)
        self.valid_alpha_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.valid_alpha_label.setStyleSheet("""
            QLabel#valid_alpha_label{
                font-family: "SF Pro Display";
                font-weight: 600;
                font-size: 24px;
                padding: 6px;
                color: black;
                border: none;
                background: transparent;
            }
        """)
        
        valid_alpha_widget_layout = QVBoxLayout(self.valid_alpha_widget)
        valid_alpha_widget_layout.addWidget(self.valid_alpha_label)
        valid_alpha_widget_layout.setContentsMargins(0,0,0,0)
        valid_alpha_widget_layout.setSpacing(0)

        #-----Invalid Alpha Widget-----
        self.invalid_alpha_widget = QWidget()
        self.invalid_alpha_widget.setObjectName("invalid_alpha_widget")
        self.invalid_alpha_widget.setStyleSheet("""
            QWidget#invalid_alpha_widget{
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

        self.invalid_alpha_label = QLabel("Invalid Alpha")
        self.invalid_alpha_label.setObjectName("invalid_alpha_label")
        self.invalid_alpha_label.setWordWrap(True)
        self.invalid_alpha_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.invalid_alpha_label.setStyleSheet("""
            QLabel#invalid_alpha_label{
                font-family: "SF Pro Display";
                font-weight: 600;
                font-size: 24px;
                padding: 6px;
                color: black;
                border: none;
                background: transparent;
            }
        """)
        
        invalid_alpha_widget_layout = QVBoxLayout(self.invalid_alpha_widget)
        invalid_alpha_widget_layout.addWidget(self.invalid_alpha_label)
        invalid_alpha_widget_layout.setContentsMargins(0,0,0,0)
        invalid_alpha_widget_layout.setSpacing(0)

        #-----Hide Both Validity Check Widgets-----
        self.valid_alpha_widget.hide()
        self.invalid_alpha_widget.hide()

        #-----Set the size for both Validitiy Check Widgets-----
        self.valid_alpha_widget.setMinimumHeight(50)
        self.invalid_alpha_widget.setMinimumHeight(50)

        #-----Grid Linewidth Adjustment Screen-----
        self.grid_alpha_adjustment_screen = QWidget()
        self.grid_alpha_adjustment_screen.setObjectName("grid_alpha_adjustment_screen")
        self.grid_alpha_adjustment_screen.setStyleSheet(""" 
            QWidget#grid_alpha_adjustment_screen{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #f5f5ff,
                    stop:0.5 #f7f5fc,
                    stop:1 #f0f0ff
                );
                border: 2px solid black;
                border-radius: 16px;
            }
        """)
        
        #-----Grid Linewidth Input-----
        self.grid_alpha_input = QLineEdit()
        self.grid_alpha_input.setObjectName("grid_alpha_input")
        self.grid_alpha_input.setPlaceholderText("Alpha: ")
        self.grid_alpha_input.setStyleSheet("""
            QLineEdit#grid_alpha_input{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #f5f5ff,
                    stop:0.5 #f7f5fc,
                    stop:1 #f0f0ff
                );
                color: black;
                font-size: 24pt;
                border: 2px solid black;
                border-radius: 16px;
            }
        """)

        self.grid_alpha_input.textChanged.connect(self.change_grid_alpha)
        self.grid_alpha_input.setMinimumHeight(60)

        #-----Grid Linewidth Adjustment Screen Layout-----
        grid_alpha_adjustment_screen_layout = QVBoxLayout(self.grid_alpha_adjustment_screen)
        grid_alpha_adjustment_screen_layout.addWidget(self.grid_alpha_input)
        grid_alpha_adjustment_screen_layout.addWidget(self.valid_alpha_widget)
        grid_alpha_adjustment_screen_layout.addWidget(self.invalid_alpha_widget)
        grid_alpha_adjustment_screen_layout.setContentsMargins(10,10,10,10)
        grid_alpha_adjustment_screen_layout.setSpacing(10)
        grid_alpha_adjustment_screen_layout.addStretch()

        main_layout = QVBoxLayout(self)
        main_layout.addWidget(self.grid_alpha_adjustment_screen)
        main_layout.setContentsMargins(0,0,0,0)
        main_layout.setSpacing(0)

    def change_grid_alpha(self): 
        alpha = self.grid_alpha_input.text().strip()
        if (alpha == ""):
            self.valid_alpha_widget.hide()
            self.invalid_alpha_widget.hide()
            self.grid_alpha = 0.8
            self.update_grid_alpha()
            return

        try:
            alpha = float(alpha)
            if (alpha < 0 or alpha > 1): 
                raise Exception
            self.valid_alpha_widget.show()
            self.invalid_alpha_widget.hide()
            self.grid_alpha = alpha
            self.update_grid_alpha()
        except:
            self.valid_alpha_widget.hide()
            self.invalid_alpha_widget.show()

    def update_grid_alpha(self):
        db = self.plot_manager.get_db()
        if (db != []):
            self.plot_manager.update_grid("alpha",self.grid_alpha)
        else:
            plot_parameters = plot_json[self.selected_graph].copy()
            plot_parameters["grid"]["alpha"] = self.grid_alpha
            self.plot_manager.insert_plot_parameter(plot_parameters)
        self.graph_display.show_graph()

    def mousePressEvent(self,event):
        if not self.grid_alpha_input.geometry().contains(event.position().toPoint()):
            self.grid_alpha_input.clearFocus()
        super().mousePressEvent(event)

class grid_zorder_adjustment_section(QWidget):
    def __init__(self,selected_graph,graph_display):
        super().__init__()
        
        self.selected_graph = selected_graph
        self.graph_display = graph_display
        self.plot_manager = PlotManager()

        self.grid_zorder = 2

        #-----Valid Alpha Widget-----
        self.valid_zorder_widget = QWidget()
        self.valid_zorder_widget.setObjectName("valid_zorder_widget")
        self.valid_zorder_widget.setStyleSheet("""
            QWidget#valid_zorder_widget{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(94, 255, 234, 1),   
                    stop:0.3 rgba(63, 252, 180, 1), 
                    stop:0.6 rgba(150, 220, 255, 1),  
                    stop:1 rgba(180, 200, 255, 1)  
                );
                border: 2px solid black;
                border-radius: 16px;
            }
        """)

        self.valid_zorder_label = QLabel("Valid Zorder")
        self.valid_zorder_label.setObjectName("valid_zorder_label")
        self.valid_zorder_label.setWordWrap(True)
        self.valid_zorder_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.valid_zorder_label.setStyleSheet("""
            QLabel#valid_zorder_label{
                font-family: "SF Pro Display";
                font-weight: 600;
                font-size: 24px;
                padding: 6px;
                color: black;
                border: none;
                background: transparent;
            }
        """)
        
        valid_zorder_widget_layout = QVBoxLayout(self.valid_zorder_widget)
        valid_zorder_widget_layout.addWidget(self.valid_zorder_label)
        valid_zorder_widget_layout.setContentsMargins(0,0,0,0)
        valid_zorder_widget_layout.setSpacing(0)

        #-----Invalid Alpha Widget-----
        self.invalid_zorder_widget = QWidget()
        self.invalid_zorder_widget.setObjectName("invalid_zorder_widget")
        self.invalid_zorder_widget.setStyleSheet("""
            QWidget#invalid_zorder_widget{
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

        self.invalid_zorder_label = QLabel("Invalid Zorder")
        self.invalid_zorder_label.setObjectName("invalid_zorder_label")
        self.invalid_zorder_label.setWordWrap(True)
        self.invalid_zorder_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.invalid_zorder_label.setStyleSheet("""
            QLabel#invalid_zorder_label{
                font-family: "SF Pro Display";
                font-weight: 600;
                font-size: 24px;
                padding: 6px;
                color: black;
                border: none;
                background: transparent;
            }
        """)
        
        invalid_zorder_widget_layout = QVBoxLayout(self.invalid_zorder_widget)
        invalid_zorder_widget_layout.addWidget(self.invalid_zorder_label)
        invalid_zorder_widget_layout.setContentsMargins(0,0,0,0)
        invalid_zorder_widget_layout.setSpacing(0)

        #-----Hide Both Validity Check Widgets-----
        self.valid_zorder_widget.hide()
        self.invalid_zorder_widget.hide()

        #-----Set the size for both Validitiy Check Widgets-----
        self.valid_zorder_widget.setMinimumHeight(50)
        self.invalid_zorder_widget.setMinimumHeight(50)

        #-----Grid Zorder Adjustment Screen-----
        self.grid_zorder_adjustment_screen = QWidget()
        self.grid_zorder_adjustment_screen.setObjectName("grid_zorder_adjustment_screen")
        self.grid_zorder_adjustment_screen.setStyleSheet(""" 
            QWidget#grid_zorder_adjustment_screen{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #f5f5ff,
                    stop:0.5 #f7f5fc,
                    stop:1 #f0f0ff
                );
                border: 2px solid black;
                border-radius: 16px;
            }
        """)
        
        #-----Grid Zorder Input-----
        self.grid_zorder_input = QLineEdit()
        self.grid_zorder_input.setObjectName("grid_zorder_input")
        self.grid_zorder_input.setPlaceholderText("zorder: ")
        self.grid_zorder_input.setStyleSheet("""
            QLineEdit#grid_zorder_input{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #f5f5ff,
                    stop:0.5 #f7f5fc,
                    stop:1 #f0f0ff
                );
                color: black;
                font-size: 24pt;
                border: 2px solid black;
                border-radius: 16px;
            }
        """)

        self.grid_zorder_input.textChanged.connect(self.change_grid_zorder)
        self.grid_zorder_input.setMinimumHeight(60)

        #-----Grid Zorder Adjustment Screen Layout-----
        grid_zorder_adjustment_screen_layout = QVBoxLayout(self.grid_zorder_adjustment_screen)
        grid_zorder_adjustment_screen_layout.addWidget(self.grid_zorder_input)
        grid_zorder_adjustment_screen_layout.addWidget(self.valid_zorder_widget)
        grid_zorder_adjustment_screen_layout.addWidget(self.invalid_zorder_widget)
        grid_zorder_adjustment_screen_layout.setContentsMargins(10,10,10,10)
        grid_zorder_adjustment_screen_layout.setSpacing(10)
        grid_zorder_adjustment_screen_layout.addStretch()

        main_layout = QVBoxLayout(self)
        main_layout.addWidget(self.grid_zorder_adjustment_screen)
        main_layout.setContentsMargins(0,0,0,0)
        main_layout.setSpacing(0)

    def change_grid_zorder(self): 
        zorder = self.grid_zorder_input.text().strip()
        if (zorder == ""):
            self.valid_zorder_widget.hide()
            self.invalid_zorder_widget.hide()
            self.grid_zorder = 2
            self.update_grid_zorder()
            return

        try:
            zorder = float(zorder)
            self.valid_zorder_widget.show()
            self.invalid_zorder_widget.hide()
            self.grid_zorder = zorder
            self.update_grid_zorder()
        except:
            self.valid_zorder_widget.hide()
            self.invalid_zorder_widget.show()

    def update_grid_zorder(self):
        db = self.plot_manager.get_db()
        if (db != []):
            self.plot_manager.update_grid("zorder",self.grid_zorder)
        else:
            plot_parameters = plot_json[self.selected_graph].copy()
            plot_parameters["grid"]["zorder"] = self.grid_zorder
            self.plot_manager.insert_plot_parameter(plot_parameters)
        self.graph_display.show_graph()

    def mousePressEvent(self,event):
        if not self.grid_zorder_input.geometry().contains(event.position().toPoint()):
            self.grid_zorder_input.clearFocus()
        super().mousePressEvent(event)

class grid_dashes_adjustment_section(QWidget):
    def __init__(self,selected_graph,graph_display):
        super().__init__()
        
        self.selected_graph = selected_graph
        self.graph_display = graph_display
        self.plot_manager = PlotManager()

        self.grid_offset = None
        self.grid_sequence = None

        self.grid_dashes = ""

        #-----Valid Offset Widget-----
        self.valid_offset_widget = QWidget()
        self.valid_offset_widget.setObjectName("valid_offset_widget")
        self.valid_offset_widget.setStyleSheet("""
            QWidget#valid_offset_widget{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(94, 255, 234, 1),   
                    stop:0.3 rgba(63, 252, 180, 1), 
                    stop:0.6 rgba(150, 220, 255, 1),  
                    stop:1 rgba(180, 200, 255, 1)  
                );
                border: 2px solid black;
                border-radius: 16px;
            }
        """)

        self.valid_offset_label = QLabel("Valid Offset")
        self.valid_offset_label.setObjectName("valid_offset_label")
        self.valid_offset_label.setWordWrap(True)
        self.valid_offset_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.valid_offset_label.setStyleSheet("""
            QLabel#valid_offset_label{
                font-family: "SF Pro Display";
                font-weight: 600;
                font-size: 24px;
                padding: 6px;
                color: black;
                border: none;
                background: transparent;
            }
        """)
        
        valid_offset_widget_layout = QVBoxLayout(self.valid_offset_widget)
        valid_offset_widget_layout.addWidget(self.valid_offset_label)
        valid_offset_widget_layout.setContentsMargins(0,0,0,0)
        valid_offset_widget_layout.setSpacing(0)

        #-----Invalid Offset Widget-----
        self.invalid_offset_widget = QWidget()
        self.invalid_offset_widget.setObjectName("invalid_offset_widget")
        self.invalid_offset_widget.setStyleSheet("""
            QWidget#invalid_offset_widget{
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

        self.invalid_offset_label = QLabel("Invalid Offset")
        self.invalid_offset_label.setObjectName("invalid_offset_label")
        self.invalid_offset_label.setWordWrap(True)
        self.invalid_offset_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.invalid_offset_label.setStyleSheet("""
            QLabel#invalid_offset_label{
                font-family: "SF Pro Display";
                font-weight: 600;
                font-size: 24px;
                padding: 6px;
                color: black;
                border: none;
                background: transparent;
            }
        """)
        
        invalid_offset_widget_layout = QVBoxLayout(self.invalid_offset_widget)
        invalid_offset_widget_layout.addWidget(self.invalid_offset_label)
        invalid_offset_widget_layout.setContentsMargins(0,0,0,0)
        invalid_offset_widget_layout.setSpacing(0)

        #-----Valid Sequence Widget-----
        self.valid_sequence_widget = QWidget()
        self.valid_sequence_widget.setObjectName("valid_sequence_widget")
        self.valid_sequence_widget.setStyleSheet("""
            QWidget#valid_sequence_widget{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(94, 255, 234, 1),   
                    stop:0.3 rgba(63, 252, 180, 1), 
                    stop:0.6 rgba(150, 220, 255, 1),  
                    stop:1 rgba(180, 200, 255, 1)  
                );
                border: 2px solid black;
                border-radius: 16px;
            }
        """)

        self.valid_sequence_label = QLabel("Valid Sequence")
        self.valid_sequence_label.setObjectName("valid_sequence_label")
        self.valid_sequence_label.setWordWrap(True)
        self.valid_sequence_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.valid_sequence_label.setStyleSheet("""
            QLabel#valid_sequence_label{
                font-family: "SF Pro Display";
                font-weight: 600;
                font-size: 24px;
                padding: 6px;
                color: black;
                border: none;
                background: transparent;
            }
        """)
        
        valid_sequence_widget_layout = QVBoxLayout(self.valid_sequence_widget)
        valid_sequence_widget_layout.addWidget(self.valid_sequence_label)
        valid_sequence_widget_layout.setContentsMargins(0,0,0,0)
        valid_sequence_widget_layout.setSpacing(0)

        #-----Invalid Sequence Widget-----
        self.invalid_sequence_widget = QWidget()
        self.invalid_sequence_widget.setObjectName("invalid_sequence_widget")
        self.invalid_sequence_widget.setStyleSheet("""
            QWidget#invalid_sequence_widget{
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

        self.invalid_sequence_label = QLabel("Invalid Sequence")
        self.invalid_sequence_label.setObjectName("invalid_sequence_label")
        self.invalid_sequence_label.setWordWrap(True)
        self.invalid_sequence_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.invalid_sequence_label.setStyleSheet("""
            QLabel#invalid_sequence_label{
                font-family: "SF Pro Display";
                font-weight: 600;
                font-size: 24px;
                padding: 6px;
                color: black;
                border: none;
                background: transparent;
            }
        """)
        
        invalid_sequence_widget_layout = QVBoxLayout(self.invalid_sequence_widget)
        invalid_sequence_widget_layout.addWidget(self.invalid_sequence_label)
        invalid_sequence_widget_layout.setContentsMargins(0,0,0,0)
        invalid_sequence_widget_layout.setSpacing(0)

        #-----Customize the Widgets-----
        self.valid_offset_widget.hide()
        self.valid_sequence_widget.hide()
        self.invalid_offset_widget.hide()
        self.invalid_sequence_widget.hide()

        self.valid_offset_widget.setMinimumHeight(60)
        self.valid_sequence_widget.setMinimumHeight(60)
        self.invalid_offset_widget.setMinimumHeight(60)
        self.invalid_sequence_widget.setMinimumHeight(60)

        #-----Store all the valid/invalid widgets in a list-----
        self.validity_check_widgets = [self.valid_offset_widget,self.invalid_offset_widget,
                                    self.valid_sequence_widget,self.invalid_sequence_widget]

        #-----Grid Dashes Adjustment Screen-----
        self.grid_dashes_adjustment_screen = QWidget()
        self.grid_dashes_adjustment_screen.setObjectName("grid_dashes_adjustment_screen")
        self.grid_dashes_adjustment_screen.setStyleSheet("""
            QWidget#grid_dashes_adjustment_screen{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #f5f5ff,
                    stop:0.5 #f7f5fc,
                    stop:1 #f0f0ff
                );
                border: 2px solid black;
                border-radius: 16px;
            }
        """)
        self.create_grid_dashes_adjustment_screen()

        #-----Add the Grid Dashes Adjustment Screen to the Main Screen-----
        main_layout = QVBoxLayout(self)
        main_layout.addWidget(self.grid_dashes_adjustment_screen)
        main_layout.setContentsMargins(0,0,0,0)
        main_layout.setSpacing(0)

    def create_grid_dashes_adjustment_screen(self):
        grid_dashes_adjustment_screen_layout = QVBoxLayout(self.grid_dashes_adjustment_screen)
        
        self.grid_dashes_offset_input = QLineEdit()
        self.grid_dashes_offset_input.setObjectName("grid_dashes_offset_input")
        self.grid_dashes_offset_input.setPlaceholderText("Offset: ")
        self.grid_dashes_offset_input.setStyleSheet("""
            QLineEdit#grid_dashes_offset_input{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #f5f5ff,
                    stop:0.5 #f7f5fc,
                    stop:1 #f0f0ff
                );
                color: black;
                font-size: 24pt;
                border: 2px solid black;
                border-radius: 16px;
            }
        """)

        self.grid_dashes_sequence_input = QLineEdit()
        self.grid_dashes_sequence_input.setObjectName("grid_dashes_sequence_input")
        self.grid_dashes_sequence_input.setPlaceholderText("Sequence: ")
        self.grid_dashes_sequence_input.setStyleSheet("""
            QLineEdit#grid_dashes_sequence_input{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #f5f5ff,
                    stop:0.5 #f7f5fc,
                    stop:1 #f0f0ff
                );
                color: black;
                font-size: 24pt;
                border: 2px solid black;
                border-radius: 16px;
            }
        """)

        self.grid_dashes_offset_input.setMinimumHeight(60)
        self.grid_dashes_sequence_input.setMinimumHeight(60)

        self.grid_dashes_offset_input.textChanged.connect(self.change_grid_dashes_offset)
        self.grid_dashes_sequence_input.textChanged.connect(self.change_grid_dashes_sequence)

        grid_dashes_adjustment_screen_layout.addWidget(self.grid_dashes_offset_input)
        grid_dashes_adjustment_screen_layout.addWidget(self.grid_dashes_sequence_input)
        grid_dashes_adjustment_screen_layout.addWidget(self.valid_offset_widget)
        grid_dashes_adjustment_screen_layout.addWidget(self.valid_sequence_widget)
        grid_dashes_adjustment_screen_layout.addWidget(self.invalid_offset_widget)
        grid_dashes_adjustment_screen_layout.addWidget(self.invalid_sequence_widget)
        
        grid_dashes_adjustment_screen_layout.setContentsMargins(10,10,10,10)
        grid_dashes_adjustment_screen_layout.setSpacing(10)
        grid_dashes_adjustment_screen_layout.addStretch()

    def change_grid_dashes_offset(self):
        grid_dashes_offset = self.grid_dashes_offset_input.text().strip()

        [widget.hide() for widget in self.validity_check_widgets]

        if (grid_dashes_offset == ""):
            self.grid_offset = None
            self.update_grid_dashes()
            return 

        try:
            grid_dashes_offset = float(grid_dashes_offset)
            if (grid_dashes_offset < 0):
                raise Exception
            self.valid_offset_widget.show()
        except:
            self.invalid_offset_widget.show()
        else:
            self.update_grid_dashes()

    def change_grid_dashes_sequence(self):
        grid_dashes_sequence = self.grid_dashes_sequence_input.text().strip()

        if (" " in grid_dashes_sequence):
            grid_dashes_sequence = grid_dashes_sequence.split(" ")
        elif ("," in grid_dashes_sequence):
            grid_dashes_sequence = grid_dashes_sequence.split(",")
        else:
            grid_dashes_sequence = [grid_dashes_sequence]

        [widget.hide() for widget in self.validity_check_widgets]

        if (grid_dashes_sequence == ['']):
            self.grid_sequence = None
            self.update_grid_dashes()
            return 

        try:
            grid_dashes_sequence = list(map(float,grid_dashes_sequence))
            grid_dashes_sequence = list(filter(lambda x:x > 0,grid_dashes_sequence))

            if (len(grid_dashes_sequence) < 4 or len(grid_dashes_sequence) % 2 == 1):
                raise Exception

            self.valid_sequence_widget.show()
        except:
            self.invalid_sequence_widget.show()
        else:
            self.grid_sequence = grid_dashes_sequence
            self.update_grid_dashes()

    def change_grid_dashes(self):
        self.grid_dashes = [None,None]
        if (self.grid_offset is None and self.grid_sequence is not None):
            self.grid_dashes = [0,self.grid_sequence]
        if (self.grid_offset is not None and self.grid_sequence is not None):
            self.grid_dashes = [self.grid_offset,self.grid_sequence]

    def update_grid_dashes(self):
        self.change_grid_dashes()
        db = self.plot_manager.get_db()
        if (db != []):
            self.plot_manager.update_grid("dashes",self.grid_dashes)
        else:
            plot_parameters = plot_json[self.selected_graph].copy()
            plot_parameters["grid"]["dashes"] = self.grid_dashes
            self.plot_manager.insert_plot_parameter(plot_parameters)
        self.graph_display.show_graph()

    def mousePressEvent(self, event):
        if not self.grid_dashes_offset_input.geometry().contains(event.position().toPoint()):
            self.grid_dashes_offset_input.clearFocus()
        if not self.grid_dashes_sequence_input.geometry().contains(event.position().toPoint()):
            self.grid_dashes_sequence_input.clearFocus()
        super().mousePressEvent(event)

class grid_snap_adjustment_section(QWidget):
    def __init__(self,selected_graph,graph_display):
        super().__init__()
        
        self.selected_graph = selected_graph
        self.graph_display = graph_display
        self.plot_manager = PlotManager()

        self.grid_snap_options = ["True","False","None"]

        self.grid_snap = ""

        #-----Grid Snap Adjustment Section-----
        self.grid_snap_adjustment_section = QWidget()
        self.grid_snap_adjustment_section.setObjectName("grid_snap_adjustment_section")
        self.grid_snap_adjustment_section.setStyleSheet("""
            QWidget#grid_snap_adjustment_section{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #f5f5ff,
                    stop:0.5 #f7f5fc,
                    stop:1 #f0f0ff
                );
                border: 2px solid black;
                border-radius: 16px;
            }
        """)
        self.create_grid_snap_adjustment_section()

        #-----Put it on the main widget-----
        main_layout = QVBoxLayout(self) 
        main_layout.addWidget(self.grid_snap_adjustment_section)
        main_layout.setContentsMargins(0,0,0,0)
        main_layout.setSpacing(0)

    def create_grid_snap_adjustment_section(self): 
        grid_snap_adjustment_section_layout = QVBoxLayout(self.grid_snap_adjustment_section)

        self.grid_snap_list_view = QListView()
        self.grid_snap_model = QStringListModel(self.grid_snap_options)

        self.grid_snap_list_view.setModel(self.grid_snap_model)
        self.grid_snap_list_view.setObjectName("grid_snap_list_view")

        class CustomDelegate(QStyledItemDelegate):
            def paint(self, painter, option, index):
                option.displayAlignment = Qt.AlignmentFlag.AlignCenter
                font = QFont("SF Pro Display", 24)
                font.setWeight(600)
                option.font = font
                super().paint(painter, option, index)
        
        self.grid_snap_list_view.setItemDelegate(CustomDelegate())

        self.grid_snap_list_view.setStyleSheet("""
            QListView#grid_snap_list_view{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #f5f5ff,
                    stop:0.5 #f7f5fc,
                    stop:1 #f0f0ff
                );
                border: transparent;
                border-radius: 16px;
            }
            QListView#grid_snap_list_view::item {
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
            QListView#grid_snap_list_view::item:selected {
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
            QListView#grid_snap_list_view::item:hover {
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

        self.grid_snap_list_view.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.grid_snap_list_view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.grid_snap_list_view.setSpacing(3)

        self.grid_snap_list_view.clicked.connect(self.change_grid_snap)

        grid_snap_adjustment_section_layout.addWidget(self.grid_snap_list_view)

        # Add margins and spacing to make it look good and push content to the top
        grid_snap_adjustment_section_layout.setContentsMargins(10, 10, 10, 10)

    def change_grid_snap(self,index):
        grid_snap = self.grid_snap_model.data(index,Qt.ItemDataRole.DisplayRole)
        if (grid_snap == "True"):
            self.grid_snap = True
        if (grid_snap == "False"):
            self.grid_snap = False
        if (grid_snap == "None"):
            self.grid_snap = None
        self.update_grid_snap()

    def update_grid_snap(self):
        db = self.plot_manager.get_db()
        if (db != []):
            self.plot_manager.update_grid("snap",self.grid_snap)
        else:
            plot_parameters = plot_json[self.selected_graph].copy()
            plot_parameters["grid"]["snap"] = self.grid_snap
            self.plot_manager.insert_plot_parameter(plot_parameters)
        self.graph_display.show_graph()

class grid_button(QDialog):
    def __init__(self,selected_graph, graph_display):
        super().__init__()
        self.setWindowTitle("Customize Grid")

        self.selected_graph = selected_graph
        self.graph_display = graph_display

        self.grid_parameters = list(plot_json[self.selected_graph]["grid"].keys())

        self.current_screen_index = 0
        self.available_screen_names = [grid_visible_adjustment_section,grid_which_adjustment_section,
                                       grid_axis_adjustment_section,grid_color_adjustment_section,
                                       grid_linestyle_adjustment_section,grid_linewidth_adjustment_section,
                                       grid_alpha_adjustment_section,grid_zorder_adjustment_section,
                                       grid_dashes_adjustment_section,grid_snap_adjustment_section]

        self.available_screens = dict()

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

        self.grid_parameters_section = QWidget()
        self.grid_parameters_section.setObjectName("grid_parameters_section")
        self.grid_parameters_section.setStyleSheet("""
            QWidget#grid_parameters_section{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #f5f5ff,
                    stop:0.5 #f7f5fc,
                    stop:1 #f0f0ff
                );
                border: 2px solid black;
                border-radius: 16px;
            }
        """)
        self.create_grid_parameter_buttons()

        #Place the buttons and the dataset next to each other side by side
        self.layout = QHBoxLayout(self)
        self.layout.addWidget(self.grid_parameters_section,stretch=1)
        self.layout.addSpacing(10)
        
        #Add the parameters screen to the layout
        for screen_name,screen in zip(self.grid_parameters,self.available_screen_names):
            parameter_screen = screen(self.selected_graph,self.graph_display)
            parameter_screen.hide()
            self.available_screens[screen_name] = parameter_screen
            self.layout.addWidget(parameter_screen,stretch=1)
        
        #Show the first parameter screen
        self.available_screens.get(self.grid_parameters[self.current_screen_index]).show()

        #Create a shortcut for the user to go to the previous column by press up
        up_shortcut = QShortcut(QKeySequence("up"), self) 
        up_shortcut.activated.connect(self.columns_go_up)  

        #Create a shortcut for the user to go to the next column by press down
        down_shortcut = QShortcut(QKeySequence("down"), self) 
        down_shortcut.activated.connect(self.columns_go_down)

        #Create a shortcut for the user to close the dialog window
        close_shortcut = QShortcut(QKeySequence("ESC"), self) 
        close_shortcut.activated.connect(self.close_application)

        #Make sure this gets drawn.
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        
    def create_grid_parameter_buttons(self):
        grid_parameter_button_layout = QVBoxLayout(self.grid_parameters_section)
    
        self.grid_parameter_list_view = QListView()
        self.grid_parameter_model = QStringListModel(self.grid_parameters)

        self.grid_parameter_list_view.setModel(self.grid_parameter_model)
        self.grid_parameter_list_view.setObjectName("grid_parameter_list_view")
        self.grid_parameter_list_view.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)

        screen_index = self.grid_parameter_model.index(0)  
        self.grid_parameter_list_view.setCurrentIndex(screen_index)

        class CustomDelegate(QStyledItemDelegate):
            def paint(self, painter, option, index):
                option.displayAlignment = Qt.AlignmentFlag.AlignCenter
                font = QFont("SF Pro Display", 24)
                font.setWeight(600)
                option.font = font
                super().paint(painter, option, index)
        
        self.grid_parameter_list_view.setItemDelegate(CustomDelegate())

        self.grid_parameter_list_view.setStyleSheet("""
            QListView#grid_parameter_list_view{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #f5f5ff,
                    stop:0.5 #f7f5fc,
                    stop:1 #f0f0ff
                );
                border: transparent;
                border-radius: 16px;
            }
            QListView#grid_parameter_list_view::item {
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
            QListView#grid_parameter_list_view::item:selected {
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
            QListView#grid_parameter_list_view::item:hover {
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

        self.grid_parameter_list_view.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.grid_parameter_list_view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.grid_parameter_list_view.setSpacing(3)

        self.grid_parameter_list_view.clicked.connect(self.change_current_parameter_screen)

        grid_parameter_button_layout.addWidget(self.grid_parameter_list_view)

        # Add margins and spacing to make it look good and push content to the top
        grid_parameter_button_layout.setContentsMargins(10, 10, 10, 10)

    def change_current_parameter_screen(self,index):
        current_screen_name = self.grid_parameter_model.data(index,Qt.ItemDataRole.DisplayRole)
        self.available_screens.get(self.grid_parameters[self.current_screen_index]).hide()
        self.available_screens.get(current_screen_name).show()
        self.current_screen_index = index.row()
    
    def columns_go_up(self):
        self.available_screens.get(self.grid_parameters[self.current_screen_index]).hide()
        self.current_screen_index -= 1
        self.current_screen_index %= len(self.grid_parameters)
        self.available_screens.get(self.grid_parameters[self.current_screen_index]).show()
        new_screen_index = self.grid_parameter_model.index(self.current_screen_index)
        self.grid_parameter_list_view.setCurrentIndex(new_screen_index)
        self.grid_parameter_list_view.scrollTo(new_screen_index,QAbstractItemView.ScrollHint.PositionAtCenter)

    def columns_go_down(self):
        self.available_screens.get(self.grid_parameters[self.current_screen_index]).hide()
        self.current_screen_index += 1
        self.current_screen_index %= len(self.grid_parameters)
        self.available_screens.get(self.grid_parameters[self.current_screen_index]).show()
        new_screen_index = self.grid_parameter_model.index(self.current_screen_index)
        self.grid_parameter_list_view.setCurrentIndex(new_screen_index)
        self.grid_parameter_list_view.scrollTo(new_screen_index,QAbstractItemView.ScrollHint.PositionAtCenter)

    def close_application(self):
        self.close()

class hue_button(QDialog):
    def __init__(self,selected_graph,graph_display):
        super().__init__()

        self.setWindowTitle("Customize Hue")

        self.selected_graph = selected_graph
        self.graph_display = graph_display 
        self.plot_manager = PlotManager()

        self.dataset = pd.read_csv("./dataset/user_dataset.csv")
        self.categorical_columns = self.get_categorical_columns()
        self.numerical_columns = self.get_numerical_columns()
        self.columns = self.categorical_columns + self.numerical_columns

        self.hue = [None,{True:"True",False:"False"}]
        self.hue_parameters = ["Categorical Column","Numerical Column","Boolean Expression","Set Hue as None"]

        self.premade_boolean_expression_format = {
            "column":"",
            "operation":"",
            "value":"",
        }
        self.manual_boolean_expression_format = {
            "column":"",
            "operation":"",
            "value":"",
        }

        self.premade_nested_boolean_expression = []
        self.manual_nested_boolean_expression = []

        self.categorical_operations = ["==", "!=", "isin", "notin", "contains", 
                                        "startswith", "endswith", "len","regex",
                                        "lower","upper"]
        self.numerical_operations = ["==", "!=", ">", "<", ">=", "<=", 
                                    "between", "between_exclusive", "isin", "notin"]

        self.boolean_expression_check = {
            "==":lambda col, val: col == val,
            "!=":lambda col, val: col != val,
            ">":lambda col, val: col > val,
            "<":lambda col, val: col < val,
            ">=":lambda col, val: col >= val,
            "<=":lambda col, val: col <= val,
            "between":lambda col, val: col.between(val[0], val[1]),
            "between_exclusive":lambda col, val: col.gt(val[0]) & col.lt(val[1]),
            "isin":lambda col, val: col.isin(val),
            "notin":lambda col, val: ~col.isin(val),
            "contains":lambda col, val: col.str.contains(val),
            "startswith": lambda col, val: col.str.startswith(val),
            "endswith": lambda col, val: col.str.endswith(val),
            "len":lambda col, val: col.str.len() == val,
            "regex":lambda col, val:col.str.match(val),
            "lower":lambda col, val: col.str.lower() == val,
            "upper":lambda col, val: col.str.upper() == val,
        }

        #-----Column Validiity Check For Manual Boolean Expression Widgets-----
        self.manual_valid_column_widget = QWidget()
        self.manual_valid_column_widget.setObjectName("manual_valid_column_widget")
        self.manual_valid_column_widget.setStyleSheet("""
            QWidget#manual_valid_column_widget{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(94, 255, 234, 1),   
                    stop:0.3 rgba(63, 252, 180, 1), 
                    stop:0.6 rgba(150, 220, 255, 1),
                    stop:1 rgba(180, 200, 255, 1)  
                );
                border: 2px solid black;
                border-radius: 16px;
            }
        """)

        self.manual_valid_column_label = QLabel("Valid Column")
        self.manual_valid_column_label.setWordWrap(True)
        self.manual_valid_column_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.manual_valid_column_label.setObjectName("manual_valid_column_label")
        self.manual_valid_column_label.setStyleSheet("""
            QLabel#manual_valid_column_label{
                font-family: "SF Pro Display";
                font-weight: 600;
                font-size: 24px;
                padding: 6px;
                color: black;
                border: none;
                background: transparent;
            }
        """)

        manual_valid_column_layout = QVBoxLayout(self.manual_valid_column_widget)
        manual_valid_column_layout.addWidget(self.manual_valid_column_label)
        manual_valid_column_layout.setSpacing(0)
        manual_valid_column_layout.setContentsMargins(0,0,0,0)

        self.manual_invalid_column_widget = QWidget()
        self.manual_invalid_column_widget.setObjectName("manual_invalid_column")
        self.manual_invalid_column_widget.setStyleSheet("""
            QWidget#manual_invalid_column{
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

        self.manual_invalid_column_label = QLabel("Invalid Column")
        self.manual_invalid_column_label.setWordWrap(True)
        self.manual_invalid_column_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.manual_invalid_column_label.setObjectName("manual_invalid_column_label")
        self.manual_invalid_column_label.setStyleSheet("""
            QLabel#manual_invalid_column_label{
                font-family: "SF Pro Display";
                font-weight: 600;
                font-size: 24px;
                padding: 6px;
                color: black;
                border: none;
                background: transparent;
            }
        """)

        manual_invalid_column_layout = QVBoxLayout(self.manual_invalid_column_widget)
        manual_invalid_column_layout.addWidget(self.manual_invalid_column_label)
        manual_invalid_column_layout.setSpacing(0)
        manual_invalid_column_layout.setContentsMargins(0,0,0,0)

        self.manual_valid_column_widget.setMaximumHeight(100)
        self.manual_invalid_column_widget.setMaximumHeight(100)

        self.manual_valid_column_widget.hide()
        self.manual_invalid_column_widget.hide()

        #-----Operator Validiity Check For Manual Boolean Expression Widgets-----
        self.manual_valid_operator_widget = QWidget()
        self.manual_valid_operator_widget.setObjectName("manual_valid_operator")
        self.manual_valid_operator_widget.setStyleSheet("""
            QWidget#manual_valid_operator{
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

        self.manual_valid_operator_label = QLabel("Valid Operator")
        self.manual_valid_operator_label.setWordWrap(True)
        self.manual_valid_operator_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.manual_valid_operator_label.setObjectName("manual_valid_operator_label")
        self.manual_valid_operator_label.setStyleSheet("""
            QLabel#manual_valid_operator_label{
                font-family: "SF Pro Display";
                font-weight: 600;
                font-size: 24px;
                padding: 6px;
                color: black;
                border: none;
                background: transparent;
            }
        """)

        manual_valid_operator_layout = QVBoxLayout(self.manual_valid_operator_widget)
        manual_valid_operator_layout.addWidget(self.manual_valid_operator_label)
        manual_valid_operator_layout.setSpacing(0)
        manual_valid_operator_layout.setContentsMargins(0,0,0,0)

        self.manual_invalid_operator_widget = QWidget()
        self.manual_invalid_operator_widget.setObjectName("manual_invalid_operator")
        self.manual_invalid_operator_widget.setStyleSheet("""
            QWidget#manual_invalid_operator{
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

        self.manual_invalid_operator_label = QLabel("Invalid Operator")
        self.manual_invalid_operator_label.setWordWrap(True)
        self.manual_invalid_operator_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.manual_invalid_operator_label.setObjectName("manual_invalid_operator_label")
        self.manual_invalid_operator_label.setStyleSheet("""
            QLabel#manual_invalid_operator_label{
                font-family: "SF Pro Display";
                font-weight: 600;
                font-size: 24px;
                padding: 6px;
                color: black;
                border: none;
                background: transparent;
            }
        """)

        manual_invalid_operator_layout = QVBoxLayout(self.manual_invalid_operator_widget)
        manual_invalid_operator_layout.addWidget(self.manual_invalid_operator_label)
        manual_invalid_operator_layout.setSpacing(0)
        manual_invalid_operator_layout.setContentsMargins(0,0,0,0)

        self.manual_valid_operator_widget.setMaximumHeight(100)
        self.manual_invalid_operator_widget.setMaximumHeight(100)

        self.manual_valid_operator_widget.hide()
        self.manual_invalid_operator_widget.hide()

        #-----Value Validiity Check For Manual Boolean Expression Widgets-----
        self.manual_valid_value_widget = QWidget()
        self.manual_valid_value_widget.setObjectName("manual_valid_value")
        self.manual_valid_value_widget.setStyleSheet("""
            QWidget#manual_valid_value{
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

        self.manual_valid_value_label = QLabel("Valid Value")
        self.manual_valid_value_label.setWordWrap(True)
        self.manual_valid_value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.manual_valid_value_label.setObjectName("manual_valid_value_label")
        self.manual_valid_value_label.setStyleSheet("""
            QLabel#manual_valid_value_label{
                font-family: "SF Pro Display";
                font-weight: 600;
                font-size: 24px;
                padding: 6px;
                color: black;
                border: none;
                background: transparent;
            }
        """)

        manual_valid_value_layout = QVBoxLayout(self.manual_valid_value_widget)
        manual_valid_value_layout.addWidget(self.manual_valid_value_label)
        manual_valid_value_layout.setSpacing(0)
        manual_valid_value_layout.setContentsMargins(0,0,0,0)

        self.manual_invalid_value_widget = QWidget()
        self.manual_invalid_value_widget.setObjectName("manual_invalid_value")
        self.manual_invalid_value_widget.setStyleSheet("""
            QWidget#manual_invalid_value{
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

        self.manual_invalid_value_label = QLabel("Invalid Valid")
        self.manual_invalid_value_label.setWordWrap(True)
        self.manual_invalid_value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.manual_invalid_value_label.setObjectName("manual_invalid_value_label")
        self.manual_invalid_value_label.setStyleSheet("""
            QLabel#manual_invalid_value_label{
                font-family: "SF Pro Display";
                font-weight: 600;
                font-size: 24px;
                padding: 6px;
                color: black;
                border: none;
                background: transparent;
            }
        """)

        manual_invalid_value_layout = QVBoxLayout(self.manual_invalid_value_widget)
        manual_invalid_value_layout.addWidget(self.manual_invalid_value_label)
        manual_invalid_value_layout.setSpacing(0)
        manual_invalid_value_layout.setContentsMargins(0,0,0,0)

        self.manual_valid_value_widget.setMaximumHeight(100)
        self.manual_invalid_value_widget.setMaximumHeight(100)

        self.manual_valid_value_widget.hide()
        self.manual_invalid_value_widget.hide()

        #-----Boolean Expression Validiity Check For Manual Boolean Expression Widgets-----
        self.manual_valid_expression_widget = QWidget()
        self.manual_valid_expression_widget.setObjectName("manual_valid_expression_widget")
        self.manual_valid_expression_widget.setStyleSheet("""
            QWidget#manual_valid_expression_widget{
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

        self.manual_valid_expression_label = QLabel("Valid Boolean Expression")
        self.manual_valid_expression_label.setWordWrap(True)
        self.manual_valid_expression_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.manual_valid_expression_label.setObjectName("manual_valid_expression_label")
        self.manual_valid_expression_label.setStyleSheet("""
            QLabel#manual_valid_expression_label{
                font-family: "SF Pro Display";
                font-weight: 600;
                font-size: 24px;
                padding: 6px;
                color: black;
                border: none;
                background: transparent;
            }
        """)

        manual_valid_expression_layout = QVBoxLayout(self.manual_valid_expression_widget)
        manual_valid_expression_layout.addWidget(self.manual_valid_expression_label)
        manual_valid_expression_layout.setSpacing(0)
        manual_valid_expression_layout.setContentsMargins(0,0,0,0)

        self.manual_invalid_expression_widget = QWidget()
        self.manual_invalid_expression_widget.setObjectName("manual_invalid_expression_widget")
        self.manual_invalid_expression_widget.setStyleSheet("""
            QWidget#manual_invalid_expression_widget{
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

        self.manual_invalid_expression_label = QLabel("Invalid Boolean Expression")
        self.manual_invalid_expression_label.setWordWrap(True)
        self.manual_invalid_expression_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.manual_invalid_expression_label.setObjectName("manual_invalid_expression_label")
        self.manual_invalid_expression_label.setStyleSheet("""
            QLabel#manual_invalid_expression_label{
                font-family: "SF Pro Display";
                font-weight: 600;
                font-size: 24px;
                padding: 6px;
                color: black;
                border: none;
                background: transparent;
            }
        """)

        manual_invalid_expression_layout = QVBoxLayout(self.manual_invalid_expression_widget)
        manual_invalid_expression_layout.addWidget(self.manual_invalid_expression_label)
        manual_invalid_expression_layout.setSpacing(0)
        manual_invalid_expression_layout.setContentsMargins(0,0,0,0)

        self.manual_valid_expression_widget.setMaximumHeight(100)
        self.manual_invalid_expression_widget.setMaximumHeight(100)

        self.manual_valid_expression_widget.hide()
        self.manual_invalid_expression_widget.hide()

        #-----List of manual validity check widgets-----
        self.manual_validity_check_widgets = [self.manual_valid_column_widget,
                                              self.manual_valid_operator_widget,
                                              self.manual_valid_value_widget,
                                              self.manual_valid_expression_widget,
                                              self.manual_invalid_column_widget,
                                              self.manual_invalid_operator_widget,
                                              self.manual_invalid_value_widget,
                                              self.manual_invalid_expression_widget]

        #-----Input Validiity Check For Premade Boolean Expression Widgets-----
        self.premade_valid_input_widget = QWidget()
        self.premade_valid_input_widget.setObjectName("premade_valid_input")
        self.premade_valid_input_widget.setStyleSheet("""
            QWidget#premade_valid_input{
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

        self.premade_valid_input_label = QLabel("Valid Value Input")
        self.premade_valid_input_label.setWordWrap(True)
        self.premade_valid_input_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.premade_valid_input_label.setObjectName("premade_valid_input_label")
        self.premade_valid_input_label.setStyleSheet("""
            QLabel#premade_valid_input_label{
                font-family: "SF Pro Display";
                font-weight: 600;
                font-size: 24px;
                padding: 6px;
                color: black;
                border: none;
                background: transparent;
            }
        """)

        premade_valid_input_layout = QVBoxLayout(self.premade_valid_input_widget)
        premade_valid_input_layout.addWidget(self.premade_valid_input_label)
        premade_valid_input_layout.setSpacing(0)
        premade_valid_input_layout.setContentsMargins(0,0,0,0)

        self.premade_invalid_input_widget = QWidget()
        self.premade_invalid_input_widget.setObjectName("premade_invalid_input")
        self.premade_invalid_input_widget.setStyleSheet("""
            QWidget#premade_invalid_input{
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

        self.premade_invalid_input_label = QLabel("Invalid Value Input")
        self.premade_invalid_input_label.setWordWrap(True)
        self.premade_invalid_input_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.premade_invalid_input_label.setObjectName("premade_invalid_input_label")
        self.premade_invalid_input_label.setStyleSheet("""
            QLabel#premade_invalid_input_label{
                font-family: "SF Pro Display";
                font-weight: 600;
                font-size: 24px;
                padding: 6px;
                color: black;
                border: none;
                background: transparent;
            }
        """)

        premade_invalid_input_layout = QVBoxLayout(self.premade_invalid_input_widget)
        premade_invalid_input_layout.addWidget(self.premade_invalid_input_label)
        premade_invalid_input_layout.setSpacing(0)
        premade_invalid_input_layout.setContentsMargins(0,0,0,0)

        self.premade_valid_input_widget.setMaximumHeight(100)
        self.premade_invalid_input_widget.setMaximumHeight(100)

        self.premade_valid_input_widget.hide()
        self.premade_invalid_input_widget.hide()

        #-----And/Or Logical Button for Manual Boolean Expression-----
        self.manual_and_logical_button = QPushButton("Add and logcial")
        self.manual_and_logical_button.setObjectName("manual_add_and_logical")
        self.manual_and_logical_button.setStyleSheet("""
            QPushButton#manual_add_and_logical{
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
            QPushButton#manual_add_and_logical:hover{
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
        self.manual_and_logical_button.hide()

        self.manual_or_logical_button = QPushButton("Add or logcial")
        self.manual_or_logical_button.setObjectName("manual_add_or_logical")
        self.manual_or_logical_button.setStyleSheet("""
            QPushButton#manual_add_or_logical{
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
            QPushButton#manual_add_or_logical:hover{
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
        self.manual_or_logical_button.hide()

        self.manual_and_logical_button.clicked.connect(self.manual_add_and_logical_to_boolean_expression)
        self.manual_or_logical_button.clicked.connect(self.manual_add_or_logical_to_boolean_expression)

        #-----And/Or Logical Button for Premade Boolean Expression-----

        self.premade_and_logical_button = QPushButton("Add and logcial")
        self.premade_and_logical_button.setObjectName("premade_add_and_logical")
        self.premade_and_logical_button.setStyleSheet("""
            QPushButton#premade_add_and_logical{
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
            QPushButton#premade_add_and_logical:hover{
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
        self.premade_and_logical_button.hide()

        self.premade_or_logical_button = QPushButton("Add or logcial")
        self.premade_or_logical_button.setObjectName("premade_add_or_logical")
        self.premade_or_logical_button.setStyleSheet("""
            QPushButton#premade_add_or_logical{
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
            QPushButton#premade_add_or_logical:hover{
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
        self.premade_or_logical_button.hide()

        self.premade_and_logical_button.clicked.connect(self.premade_add_and_logical_to_boolean_expression)
        self.premade_or_logical_button.clicked.connect(self.premade_add_or_logical_to_boolean_expression)

        #-----Hue Mapping Button-----
        self.hue_mapping_button = QPushButton("Add Hue Mapping")
        self.hue_mapping_button.setObjectName("hue_mapping_button")
        self.hue_mapping_button.setStyleSheet("""
            QPushButton#hue_mapping_button{
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
            QPushButton#hue_mapping_button:hover{
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
        self.hue_mapping_button.clicked.connect(self.change_to_hue_mapping_screen)

        #-----Logical Operator Buttons-----
        self.available_logical_operators = [self.premade_and_logical_button,self.premade_or_logical_button,
                                            self.manual_and_logical_button,self.manual_or_logical_button]

        #-----Home Screen-----
        self.hue_parameter_section = QWidget()
        self.hue_parameter_section.setObjectName("hue_parameter")
        self.hue_parameter_section.setStyleSheet("""
            QWidget#hue_parameter{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #f5f5ff,
                    stop:0.5 #f7f5fc,
                    stop:1 #f0f0ff
                );
                border: 2px solid black;
                border-radius: 16px;
            }            
        """)
        self.create_hue_parameter_buttons()

        #-----Categorical Column Screen-----
        self.categorical_column_screen = QWidget()
        self.categorical_column_screen.setObjectName("categorical_column_screen")
        self.categorical_column_screen.setStyleSheet("""
            QWidget#categorical_column_screen{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #f5f5ff,
                    stop:0.5 #f7f5fc,
                    stop:1 #f0f0ff
                );
                border: 2px solid black;
                border-radius: 16px;
            }   
        """)
        self.create_categorical_column_screen()
        self.categorical_column_screen.hide()

        #-----Numerical Column Screen-----
        self.numerical_column_screen = QWidget()
        self.numerical_column_screen.setObjectName("numerical_column_screen")
        self.numerical_column_screen.setStyleSheet("""
            QWidget#numerical_column_screen{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #f5f5ff,
                    stop:0.5 #f7f5fc,
                    stop:1 #f0f0ff
                );
                border: 2px solid black;
                border-radius: 16px;
            }  
        """)
        self.create_numerical_column_screen()
        self.numerical_column_screen.hide()

        #------Boolean Expression Screen ------
        self.boolean_expression_screen = QWidget()
        self.boolean_expression_screen.setObjectName("boolean_expression_screen")
        self.boolean_expression_screen.setStyleSheet("""
            QWidget#boolean_expression_screen{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #f5f5ff,
                    stop:0.5 #f7f5fc,
                    stop:1 #f0f0ff
                );
                border: 2px solid black;
                border-radius: 16px;
            }  
        """)
        self.create_boolean_expression_screen()
        self.boolean_expression_screen.hide()

        #-----Boolean Expression Manual Input Screen-----
        self.boolean_expression_manual_input_screen = QWidget()
        self.boolean_expression_manual_input_screen.setObjectName("boolean_expression_manual_input_screen")
        self.boolean_expression_manual_input_screen.setStyleSheet("""
            QWidget#boolean_expression_manual_input_screen{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #f5f5ff,
                    stop:0.5 #f7f5fc,
                    stop:1 #f0f0ff
                );
                border: 2px solid black;
                border-radius: 16px;
            }  
        """)
        self.create_boolean_expression_manual_input_screen()
        self.boolean_expression_manual_input_screen.hide()

        #-----Boolean Expression Premade Select Column Screen-----
        self.boolean_expression_premade_select_column_screen = QWidget()
        self.boolean_expression_premade_select_column_screen.setObjectName("boolean_expression_premade_select_column_screen")
        self.boolean_expression_premade_select_column_screen.setStyleSheet("""
            QWidget#boolean_expression_premade_select_column_screen{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #f5f5ff,
                    stop:0.5 #f7f5fc,
                    stop:1 #f0f0ff
                );
                border: 2px solid black;
                border-radius: 16px;
            }  
        """)
        self.create_boolean_expression_premade_select_column_screen()
        self.boolean_expression_premade_select_column_screen.hide()

        #-----Boolean Expression Premade Select Operator Screen-----
        self.boolean_expression_premade_select_operator_screen = QWidget()
        self.boolean_expression_premade_select_operator_screen.setObjectName("boolean_expression_premade_select_operator_screen")
        self.boolean_expression_premade_select_operator_screen.setStyleSheet("""
            QWidget#boolean_expression_premade_select_operator_screen{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #f5f5ff,
                    stop:0.5 #f7f5fc,
                    stop:1 #f0f0ff
                );
                border: 2px solid black;
                border-radius: 16px;
            }  
        """)
        self.create_boolean_expression_premade_select_operator_screen()
        self.boolean_expression_premade_select_operator_screen.hide()

        #-----Boolean Expression Premade Input Value Screen-----
        self.boolean_expression_premade_input_value_screen = QWidget()
        self.boolean_expression_premade_input_value_screen.setObjectName("boolean_expression_premade_input_value_screen")
        self.boolean_expression_premade_input_value_screen.setStyleSheet("""
            QWidget#boolean_expression_premade_input_value_screen{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #f5f5ff,
                    stop:0.5 #f7f5fc,
                    stop:1 #f0f0ff
                );
                border: 2px solid black;
                border-radius: 16px;
            }  
        """)
        self.create_boolean_expression_premade_input_value_screen()
        self.boolean_expression_premade_input_value_screen.hide()

        #-----Logical Operator Screen-----
        self.logical_operator_screen = QWidget()
        self.logical_operator_screen.setObjectName("logical_operator_screen")
        self.logical_operator_screen.setStyleSheet("""
            QWidget#logical_operator_screen{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #f5f5ff,
                    stop:0.5 #f7f5fc,
                    stop:1 #f0f0ff
                );
                border: 2px solid black;
                border-radius: 16px;
            }  
        """)
        self.create_logical_operator_screen()
        self.logical_operator_screen.hide()

        #-----Hue Mapping Screen-----
        self.hue_mapping_screen = QWidget()
        self.hue_mapping_screen.setObjectName("hue_mapping_screen")
        self.hue_mapping_screen.setStyleSheet("""
            QWidget#hue_mapping_screen{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #f5f5ff,
                    stop:0.5 #f7f5fc,
                    stop:1 #f0f0ff
                );
                border: 2px solid black;
                border-radius: 16px;
            }
        """)
        self.create_hue_mapping_screen()
        self.hue_mapping_screen.hide()

        #-----Hue Adjustment Section-----
        self.hue_adjustment_section = QWidget()
        self.hue_adjustment_section.setObjectName("hue_adjustment_section")
        self.hue_adjustment_section.setStyleSheet(""" 
            QWidget#hue_adjustment_section{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #f5f5ff,
                    stop:0.5 #f7f5fc,
                    stop:1 #f0f0ff
                );
                border: 2px solid black;
                border-radius: 16px;
            }   
        """)

        hue_adjustment_section_layout = QVBoxLayout(self.hue_adjustment_section)
        hue_adjustment_section_layout.addWidget(self.categorical_column_screen)
        hue_adjustment_section_layout.addWidget(self.numerical_column_screen)
        hue_adjustment_section_layout.addWidget(self.boolean_expression_screen)
        hue_adjustment_section_layout.addWidget(self.boolean_expression_manual_input_screen)
        hue_adjustment_section_layout.addWidget(self.boolean_expression_premade_select_column_screen)
        hue_adjustment_section_layout.addWidget(self.boolean_expression_premade_select_operator_screen)
        hue_adjustment_section_layout.addWidget(self.boolean_expression_premade_input_value_screen)
        hue_adjustment_section_layout.addWidget(self.logical_operator_screen)
        hue_adjustment_section_layout.addWidget(self.hue_mapping_screen)
        hue_adjustment_section_layout.setContentsMargins(0,0,0,0)

        #-----Initialize Screen Value-----
        self.available_screens = [self.categorical_column_screen,
                                self.numerical_column_screen,self.boolean_expression_screen,
                                self.boolean_expression_manual_input_screen,
                                self.boolean_expression_premade_select_column_screen,
                                self.boolean_expression_premade_select_operator_screen,
                                self.boolean_expression_premade_input_value_screen,
                                self.logical_operator_screen,self.hue_mapping_screen]
        self.current_screen_idx = 0
        self.available_screens[self.current_screen_idx].show()

        #-----Initialize the QDialog Screen-----
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

        #-----Main Screen-----
        main_layout = QHBoxLayout(self)
        main_layout.addWidget(self.hue_parameter_section,stretch=1)
        main_layout.addWidget(self.hue_adjustment_section,stretch=1)
        main_layout.setContentsMargins(15,15,15,15)
        main_layout.setSpacing(10)

        #-----Shortcuts-----
        previous_screen_shortcut = QShortcut(QKeySequence("left"),self)
        previous_screen_shortcut.activated.connect(self.change_to_previous_screen)

        close_screen_shortcut = QShortcut(QKeySequence("Esc"),self)
        close_screen_shortcut.activated.connect(self.close_dialog)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

    def get_categorical_columns(self):
        columns = self.dataset.select_dtypes(include=["category","object","string","bool"]).columns
        if (not columns.empty):
            self.column_name = columns[0]
            return columns.tolist()
        return []

    def get_numerical_columns(self):
        columns = self.dataset.select_dtypes(include=["float","int","bool"]).columns
        if (not columns.empty):
            self.column_name = columns[0]
            return columns.tolist()
        return []

    def premade_add_and_logical_to_boolean_expression(self):
        self.premade_nested_boolean_expression.append(self.hue)
        self.premade_nested_boolean_expression.append("and")

        self.premade_boolean_expression_format = {
            "column":"",
            "operation":"",
            "value":"",
        }
        self.boolean_expression_value_input.clear()

        self.premade_and_logical_button.hide()
        self.premade_or_logical_button.hide()

        self.change_to_premade_boolean_expression_screen()

    def premade_add_or_logical_to_boolean_expression(self):
        self.premade_nested_boolean_expression.append(self.hue)
        self.premade_nested_boolean_expression.append("or")

        self.premade_boolean_expression_format = {
            "column":"",
            "operation":"",
            "value":"",
        }
        self.boolean_expression_value_input.clear()

        self.premade_and_logical_button.hide()
        self.premade_or_logical_button.hide()

        self.change_to_premade_boolean_expression_screen()

    def manual_add_and_logical_to_boolean_expression(self):
        self.manual_nested_boolean_expression.append(self.hue)
        self.manual_nested_boolean_expression.append("and")
        
        self.manual_nest_boolean_expression = {
            "column":"",
            "operation":"",
            "value":"",
        }
        self.manual_boolean_expression_column_input.clear()
        self.manual_boolean_expression_operator_input.clear()
        self.manual_boolean_expression_value_input.clear()

        self.manual_and_logical_button.hide()
        self.manual_or_logical_button.hide()

        self.change_to_manual_boolean_expression_screen()

    def manual_add_or_logical_to_boolean_expression(self):
        self.manual_nested_boolean_expression.append(self.hue)
        self.manual_nested_boolean_expression.append("or")
        
        self.manual_nest_boolean_expression = {
            "column":"",
            "operation":"",
            "value":"",
        }
        self.manual_boolean_expression_column_input.clear()
        self.manual_boolean_expression_operator_input.clear()
        self.manual_boolean_expression_value_input.clear()

        self.manual_and_logical_button.hide()
        self.manual_or_logical_button.hide()

        self.change_to_manual_boolean_expression_screen()

    def create_hue_parameter_buttons(self):
        hue_parameter_button_layout = QVBoxLayout(self.hue_parameter_section)

        self.hue_parameter_list_view = QListView()
        self.hue_parameter_model = QStringListModel(self.hue_parameters)

        self.hue_parameter_list_view.setModel(self.hue_parameter_model)
        self.hue_parameter_list_view.setObjectName("hue_parameter_list_view")
        self.hue_parameter_list_view.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)

        screen_index = self.hue_parameter_model.index(0)  
        self.hue_parameter_list_view.setCurrentIndex(screen_index)

        class CustomDelegate(QStyledItemDelegate):
            def paint(self, painter, option, index):
                option.displayAlignment = Qt.AlignmentFlag.AlignCenter
                font = QFont("SF Pro Display", 24)
                font.setWeight(600)
                option.font = font
                super().paint(painter, option, index)
        
        self.hue_parameter_list_view.setItemDelegate(CustomDelegate())

        self.hue_parameter_list_view.setStyleSheet("""
            QListView#hue_parameter_list_view{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #f5f5ff,
                    stop:0.5 #f7f5fc,
                    stop:1 #f0f0ff
                );
                border: transparent;
                border-radius: 16px;
            }
            QListView#hue_parameter_list_view::item {
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
            QListView#hue_parameter_list_view::item:selected {
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
            QListView#hue_parameter_list_view::item:hover {
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

        self.hue_parameter_list_view.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.hue_parameter_list_view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.hue_parameter_list_view.setSpacing(3)

        self.hue_parameter_list_view.clicked.connect(self.change_current_parameter_screen)

        hue_parameter_button_layout.addWidget(self.hue_parameter_list_view)

        # Add margins and spacing to make it look good and push content to the top
        hue_parameter_button_layout.setContentsMargins(10, 10, 10, 10)

    def create_categorical_column_screen(self):
        categorical_column_screen_layout = QVBoxLayout(self.categorical_column_screen)

        self.categorical_column_search_bar = QLineEdit()
        self.categorical_column_search_bar.setObjectName("categorical_column_search_bar")
        self.categorical_column_search_bar.setPlaceholderText("Search: ")
        self.categorical_column_search_bar.setStyleSheet("""
            QLineEdit#categorical_column_search_bar{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #f5f5ff,
                    stop:0.5 #f7f5fc,
                    stop:1 #f0f0ff
                );
                color: black;
                font-size: 24pt;
                border: 2px solid black;
                border-radius: 16px;
            }
        """)
        self.categorical_column_search_bar.setMinimumHeight(60)
        categorical_column_screen_layout.addWidget(self.categorical_column_search_bar)
        categorical_column_screen_layout.addSpacing(15)
    
        self.categorical_column_list_view = QListView()
        self.categorical_column_model = QStringListModel(self.categorical_columns)

        self.categorical_filter_proxy = QSortFilterProxyModel()
        self.categorical_filter_proxy.setSourceModel(self.categorical_column_model)
        self.categorical_filter_proxy.setFilterCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive) 
        self.categorical_filter_proxy.setFilterKeyColumn(0)  

        self.categorical_column_search_bar.textChanged.connect(self.categorical_filter_proxy.setFilterFixedString)

        self.categorical_column_list_view.setModel(self.categorical_filter_proxy)
        self.categorical_column_list_view.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.categorical_column_list_view.setObjectName("categorical_column_list_view")
        self.categorical_column_list_view.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)

        class CustomDelegate(QStyledItemDelegate):
            def paint(self, painter, option, index):
                option.displayAlignment = Qt.AlignmentFlag.AlignCenter
                font = QFont("SF Pro Display", 24)
                font.setWeight(600)
                option.font = font
                super().paint(painter, option, index)
        
        self.categorical_column_list_view.setItemDelegate(CustomDelegate())

        self.categorical_column_list_view.setStyleSheet("""
            QListView#categorical_column_list_view{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #f5f5ff,
                    stop:0.5 #f7f5fc,
                    stop:1 #f0f0ff
                );
                border: transparent;
                border-radius: 16px;
            }
            QListView#categorical_column_list_view::item {
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
            QListView#categorical_column_list_view::item:selected {
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
            QListView#categorical_column_list_view::item:hover {
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

        self.categorical_column_list_view.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.categorical_column_list_view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.categorical_column_list_view.setSpacing(3)

        self.categorical_column_list_view.clicked.connect(self.change_categorical_hue_column)

        categorical_column_screen_layout.addWidget(self.categorical_column_list_view)

        # Add margins and spacing to make it look good and push content to the top
        categorical_column_screen_layout.setContentsMargins(10, 10, 10, 10)

    def create_numerical_column_screen(self):
        numerical_column_screen_layout = QVBoxLayout(self.numerical_column_screen)

        self.numerical_column_search_bar = QLineEdit()
        self.numerical_column_search_bar.setObjectName("numerical_column_search_bar")
        self.numerical_column_search_bar.setPlaceholderText("Search: ")
        self.numerical_column_search_bar.setStyleSheet("""
            QLineEdit#numerical_column_search_bar{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #f5f5ff,
                    stop:0.5 #f7f5fc,
                    stop:1 #f0f0ff
                );
                color: black;
                font-size: 24pt;
                border: 2px solid black;
                border-radius: 16px;
            }
        """)
        self.numerical_column_search_bar.setMinimumHeight(60)
        numerical_column_screen_layout.addWidget(self.numerical_column_search_bar)
        numerical_column_screen_layout.addSpacing(15)
    
        self.numerical_column_list_view = QListView()
        self.numerical_column_model = QStringListModel(self.numerical_columns)

        self.numerical_filter_proxy = QSortFilterProxyModel()
        self.numerical_filter_proxy.setSourceModel(self.numerical_column_model)
        self.numerical_filter_proxy.setFilterCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive) 
        self.numerical_filter_proxy.setFilterKeyColumn(0)  

        self.numerical_column_search_bar.textChanged.connect(self.numerical_filter_proxy.setFilterFixedString)

        self.numerical_column_list_view.setModel(self.numerical_filter_proxy)
        self.numerical_column_list_view.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.numerical_column_list_view.setObjectName("numerical_column_list_view")

        class CustomDelegate(QStyledItemDelegate):
            def paint(self, painter, option, index):
                option.displayAlignment = Qt.AlignmentFlag.AlignCenter
                font = QFont("SF Pro Display", 24)
                font.setWeight(600)
                option.font = font
                super().paint(painter, option, index)
        
        self.numerical_column_list_view.setItemDelegate(CustomDelegate())

        self.numerical_column_list_view.setStyleSheet("""
            QListView#numerical_column_list_view{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #f5f5ff,
                    stop:0.5 #f7f5fc,
                    stop:1 #f0f0ff
                );
                border: transparent;
                border-radius: 16px;
            }
            QListView#numerical_column_list_view::item {
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
            QListView#numerical_column_list_view::item:selected {
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
            QListView#numerical_column_list_view::item:hover {
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

        self.numerical_column_list_view.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.numerical_column_list_view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.numerical_column_list_view.setSpacing(3)

        self.numerical_column_list_view.clicked.connect(self.change_numerical_hue_column)

        numerical_column_screen_layout.addWidget(self.numerical_column_list_view)

        # Add margins and spacing to make it look good and push content to the top
        numerical_column_screen_layout.setContentsMargins(10, 10, 10, 10)

    def create_boolean_expression_screen(self):
        boolean_expression_layout = QVBoxLayout(self.boolean_expression_screen)

        self.manual_boolean_expression_button = QPushButton()
        self.manual_boolean_expression_button.setObjectName("manual_boolean_expression_button")
        self.manual_boolean_expression_button.setStyleSheet("""
            QPushButton#manual_boolean_expression_button{
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
            QPushButton#manual_boolean_expression_button:hover{
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

        self.manual_boolean_expression_label = QLabel("Manual Boolean Expression")
        self.manual_boolean_expression_label.setWordWrap(True)
        self.manual_boolean_expression_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.manual_boolean_expression_label.setObjectName("manual_boolean_expression_label")
        self.manual_boolean_expression_label.setStyleSheet("""
            QLabel#manual_boolean_expression_label{
                font-family: "SF Pro Display";
                font-weight: 600;
                font-size: 24px;
                padding: 6px;
                color: black;
                border: none;
                background: transparent;
            }
        """)
        self.manual_boolean_expression_label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

        self.premade_boolean_expression_button = QPushButton("")
        self.premade_boolean_expression_button.setObjectName("premade_boolean_expression_button")
        self.premade_boolean_expression_button.setStyleSheet("""
            QPushButton#premade_boolean_expression_button{
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
            QPushButton#premade_boolean_expression_button:hover{
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

        self.premade_boolean_expression_label = QLabel("Premade Boolean Expression")
        self.premade_boolean_expression_label.setWordWrap(True)
        self.premade_boolean_expression_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.premade_boolean_expression_label.setObjectName("premade_boolean_expression_label")
        self.premade_boolean_expression_label.setStyleSheet("""
            QLabel#premade_boolean_expression_label{
                font-family: "SF Pro Display";
                font-weight: 600;
                font-size: 24px;
                padding: 6px;
                color: black;
                border: none;
                background: transparent;
            }
        """)
        self.premade_boolean_expression_label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

        manual_boolean_expression_layout = QVBoxLayout(self.manual_boolean_expression_button)
        manual_boolean_expression_layout.addWidget(self.manual_boolean_expression_label)
        manual_boolean_expression_layout.setContentsMargins(0,0,0,0)
        manual_boolean_expression_layout.setSpacing(0)

        premade_boolean_expression_layout = QVBoxLayout(self.premade_boolean_expression_button)
        premade_boolean_expression_layout.addWidget(self.premade_boolean_expression_label)
        premade_boolean_expression_layout.setContentsMargins(0,0,0,0)
        premade_boolean_expression_layout.setSpacing(0)

        self.manual_boolean_expression_button.setMinimumHeight(70)
        self.premade_boolean_expression_button.setMinimumHeight(70)
        self.manual_boolean_expression_button.clicked.connect(self.change_to_manual_boolean_expression_screen)
        self.premade_boolean_expression_button.clicked.connect(self.change_to_premade_boolean_expression_screen)

        boolean_expression_layout.addWidget(self.manual_boolean_expression_button)
        boolean_expression_layout.addWidget(self.premade_boolean_expression_button)
        boolean_expression_layout.setContentsMargins(10,10,10,10)
        boolean_expression_layout.setSpacing(10)        
        boolean_expression_layout.addStretch()

    def create_boolean_expression_manual_input_screen(self):
        manual_boolean_expression_layout= QVBoxLayout(self.boolean_expression_manual_input_screen)

        self.manual_boolean_expression_column_input = QLineEdit()
        self.manual_boolean_expression_column_input.setObjectName("manual_boolean_expression_column_input")
        self.manual_boolean_expression_column_input.setPlaceholderText("Column:")
        self.manual_boolean_expression_column_input.setStyleSheet("""
            QLineEdit#manual_boolean_expression_column_input{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #f5f5ff,
                    stop:0.5 #f7f5fc,
                    stop:1 #f0f0ff
                );
                color: black;
                font-size: 24pt;
                border: 2px solid black;
                border-radius: 16px;
            }
        """)
        self.manual_boolean_expression_column_input.setMinimumHeight(60)
        self.manual_boolean_expression_column_input.textChanged.connect(self.change_boolean_expression_manual_column_input)

        self.manual_boolean_expression_operator_input = QLineEdit()
        self.manual_boolean_expression_operator_input.setObjectName("manual_boolean_expression_operator_input")
        self.manual_boolean_expression_operator_input.setPlaceholderText("Operator:")
        self.manual_boolean_expression_operator_input.setStyleSheet("""
            QLineEdit#manual_boolean_expression_operator_input{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #f5f5ff,
                    stop:0.5 #f7f5fc,
                    stop:1 #f0f0ff
                );
                color: black;
                font-size: 24pt;
                border: 2px solid black;
                border-radius: 16px;
            }
        """)
        self.manual_boolean_expression_operator_input.setMinimumHeight(60)
        self.manual_boolean_expression_operator_input.textChanged.connect(self.change_boolean_expression_manual_operator_input)

        self.manual_boolean_expression_value_input = QLineEdit()
        self.manual_boolean_expression_value_input.setObjectName("manual_boolean_expression_value_input")
        self.manual_boolean_expression_value_input.setPlaceholderText("Value:")
        self.manual_boolean_expression_value_input.setStyleSheet("""
            QLineEdit#manual_boolean_expression_value_input{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #f5f5ff,
                    stop:0.5 #f7f5fc,
                    stop:1 #f0f0ff
                );
                color: black;
                font-size: 24pt;
                border: 2px solid black;
                border-radius: 16px;
            }
        """)
        self.manual_boolean_expression_value_input.setMinimumHeight(60)
        self.manual_boolean_expression_value_input.textChanged.connect(self.change_boolean_expression_manual_value_input)

        manual_boolean_expression_layout.addWidget(self.manual_boolean_expression_column_input)
        manual_boolean_expression_layout.addWidget(self.manual_boolean_expression_operator_input)
        manual_boolean_expression_layout.addWidget(self.manual_boolean_expression_value_input)
        for widgets in self.manual_validity_check_widgets:
            manual_boolean_expression_layout.addWidget(widgets)
        manual_boolean_expression_layout.addStretch()
        manual_boolean_expression_layout.addWidget(self.manual_and_logical_button)
        manual_boolean_expression_layout.addWidget(self.manual_or_logical_button)
        
        manual_boolean_expression_layout.setContentsMargins(10,10,10,10)
        manual_boolean_expression_layout.setSpacing(10)

    def create_boolean_expression_premade_select_column_screen(self):
        premade_boolean_expression_column_layout = QVBoxLayout(self.boolean_expression_premade_select_column_screen)

        self.boolean_expression_column_search_bar = QLineEdit()
        self.boolean_expression_column_search_bar.setObjectName("boolean_expression_column_search_bar")
        self.boolean_expression_column_search_bar.setPlaceholderText("Search: ")
        self.boolean_expression_column_search_bar.setStyleSheet("""
            QLineEdit#boolean_expression_column_search_bar{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #f5f5ff,
                    stop:0.5 #f7f5fc,
                    stop:1 #f0f0ff
                );
                color: black;
                font-size: 24pt;
                border: 2px solid black;
                border-radius: 16px;
            }
        """)
        self.boolean_expression_column_search_bar.setMinimumHeight(60)
        premade_boolean_expression_column_layout.addWidget(self.boolean_expression_column_search_bar)
        premade_boolean_expression_column_layout.addSpacing(15)

        self.boolean_expression_columns = self.categorical_columns + self.numerical_columns
    
        self.boolean_expression_column_list_view = QListView()
        self.boolean_expression_column_model = QStringListModel(self.boolean_expression_columns)

        self.boolean_expression_column_proxy = QSortFilterProxyModel()
        self.boolean_expression_column_proxy.setSourceModel(self.boolean_expression_column_model)
        self.boolean_expression_column_proxy.setFilterCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive) 
        self.boolean_expression_column_proxy.setFilterKeyColumn(0)  

        self.boolean_expression_column_search_bar.textChanged.connect(self.boolean_expression_column_proxy.setFilterFixedString)

        self.boolean_expression_column_list_view.setModel(self.boolean_expression_column_proxy)
        self.boolean_expression_column_list_view.setObjectName("boolean_expression_column_list_view")
        self.boolean_expression_column_list_view.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)

        class CustomDelegate(QStyledItemDelegate):
            def paint(self, painter, option, index):
                option.displayAlignment = Qt.AlignmentFlag.AlignCenter
                font = QFont("SF Pro Display", 24)
                font.setWeight(600)
                option.font = font
                super().paint(painter, option, index)
        
        self.boolean_expression_column_list_view.setItemDelegate(CustomDelegate())

        self.boolean_expression_column_list_view.setStyleSheet("""
            QListView#boolean_expression_column_list_view{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #f5f5ff,
                    stop:0.5 #f7f5fc,
                    stop:1 #f0f0ff
                );
                border: transparent;
                border-radius: 16px;
            }
            QListView#boolean_expression_column_list_view::item {
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
            QListView#boolean_expression_column_list_view::item:selected {
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
            QListView#boolean_expression_column_list_view::item:hover {
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

        self.boolean_expression_column_list_view.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.boolean_expression_column_list_view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.boolean_expression_column_list_view.setSpacing(3)

        self.boolean_expression_column_list_view.clicked.connect(self.change_boolean_expression_premade_column)

        premade_boolean_expression_column_layout.addWidget(self.boolean_expression_column_list_view)

        # Add margins and spacing to make it look good and push content to the top
        premade_boolean_expression_column_layout.setContentsMargins(10, 10, 10, 10)

    def create_boolean_expression_premade_select_operator_screen(self):
        premade_boolean_expression_operation_layout = QVBoxLayout(self.boolean_expression_premade_select_operator_screen)
    
        self.boolean_expression_operations_list_view = QListView()
        self.boolean_expression_operations_model = QStringListModel(self.categorical_operations)

        self.boolean_expression_operations_list_view.setModel(self.boolean_expression_operations_model)
        self.boolean_expression_operations_list_view.setObjectName("boolean_expression_operations_list_view")
        self.boolean_expression_operations_list_view.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)

        class CustomDelegate(QStyledItemDelegate):
            def paint(self, painter, option, index):
                option.displayAlignment = Qt.AlignmentFlag.AlignCenter
                font = QFont("SF Pro Display", 24)
                font.setWeight(600)
                option.font = font
                super().paint(painter, option, index)
        
        self.boolean_expression_operations_list_view.setItemDelegate(CustomDelegate())

        self.boolean_expression_operations_list_view.setStyleSheet("""
            QListView#boolean_expression_operations_list_view{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #f5f5ff,
                    stop:0.5 #f7f5fc,
                    stop:1 #f0f0ff
                );
                border: transparent;
                border-radius: 16px;
            }
            QListView#boolean_expression_operations_list_view::item {
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
            QListView#boolean_expression_operations_list_view::item:selected {
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
            QListView#boolean_expression_operations_list_view::item:hover {
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

        self.boolean_expression_operations_list_view.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.boolean_expression_operations_list_view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.boolean_expression_operations_list_view.setSpacing(3)

        self.boolean_expression_operations_list_view.clicked.connect(self.change_boolean_expression_premade_operation)

        premade_boolean_expression_operation_layout.addWidget(self.boolean_expression_operations_list_view)

        # Add margins and spacing to make it look good and push content to the top
        premade_boolean_expression_operation_layout.setContentsMargins(10, 10, 10, 10)

    def create_boolean_expression_premade_input_value_screen(self):
        premade_boolean_expression_value_layout = QVBoxLayout(self.boolean_expression_premade_input_value_screen)

        self.instructions_widget = QWidget()
        self.instructions_widget.setObjectName("instructions_widget")
        self.instructions_widget.setStyleSheet("""
            QWidget#instructions_widget{
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
            }
        """)
        self.instructions_widget.setMinimumHeight(50)

        self.instructions_label = QLabel("Seperate values by space")
        self.instructions_label.setWordWrap(True)
        self.instructions_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.instructions_label.setObjectName("instructions_label")
        self.instructions_label.setStyleSheet("""
            QLabel#instructions_label{
                font-family: "SF Pro Display";
                font-weight: 600;
                font-size: 24px;
                padding: 6px;
                color: black;
                border: none;
                background: transparent;
            }
        """)

        instructions_widget_layout = QVBoxLayout(self.instructions_widget)
        instructions_widget_layout.addWidget(self.instructions_label)
        instructions_widget_layout.setContentsMargins(0,0,0,0)
        instructions_widget_layout.setSpacing(0)

        premade_logical_operator_button = QPushButton("Add Logical Operator")
        premade_logical_operator_button.setObjectName("premade_logical_operator_button")
        premade_logical_operator_button.setStyleSheet("""
            QPushButton#premade_logical_operator_button{
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
            QPushButton#premade_logical_operator_button:hover{
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
        premade_logical_operator_button.clicked.connect(self.change_to_logical_operator_screen)

        self.boolean_expression_value_input = QLineEdit()
        self.boolean_expression_value_input.setObjectName("boolean_expression_value_input")
        self.boolean_expression_value_input.setPlaceholderText("Value: ")
        self.boolean_expression_value_input.setStyleSheet("""
            QLineEdit#boolean_expression_value_input{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #f5f5ff,
                    stop:0.5 #f7f5fc,
                    stop:1 #f0f0ff
                );
                color: black;
                font-size: 24pt;
                border: 2px solid black;
                border-radius: 16px;
            }
        """)
        self.boolean_expression_value_input.setMinimumHeight(60)
        self.boolean_expression_value_input.textChanged.connect(self.change_boolean_expression_premade_value)

        premade_boolean_expression_value_layout.addWidget(self.instructions_widget)
        premade_boolean_expression_value_layout.addSpacing(5)
        premade_boolean_expression_value_layout.addWidget(self.boolean_expression_value_input)
        premade_boolean_expression_value_layout.addWidget(self.premade_valid_input_widget)
        premade_boolean_expression_value_layout.addWidget(self.premade_invalid_input_widget)
        premade_boolean_expression_value_layout.addStretch()
        premade_boolean_expression_value_layout.addWidget(premade_logical_operator_button)
        premade_boolean_expression_value_layout.addWidget(self.hue_mapping_button)
        premade_boolean_expression_value_layout.setContentsMargins(10,10,10,10)
        premade_boolean_expression_value_layout.setSpacing(5)

    def create_logical_operator_screen(self):
        logical_operator_screen_layout = QVBoxLayout(self.logical_operator_screen)
        for button in self.available_logical_operators:
            button.hide()
            logical_operator_screen_layout.addWidget(button)
        logical_operator_screen_layout.setContentsMargins(10,10,10,10)
        logical_operator_screen_layout.setSpacing(5)
        logical_operator_screen_layout.addStretch()

    def create_hue_mapping_screen(self):
        hue_mapping_screen_layout = QVBoxLayout(self.hue_mapping_screen)
        
        self.true_marker_input = QLineEdit()
        self.true_marker_input.setObjectName("true_marker_input")
        self.true_marker_input.setPlaceholderText("True Marker:")
        self.true_marker_input.setStyleSheet("""
            QLineEdit#true_marker_input{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #f5f5ff,
                    stop:0.5 #f7f5fc,
                    stop:1 #f0f0ff
                );
                color: black;
                font-size: 24pt;
                border: 2px solid black;
                border-radius: 16px;
            }
        """)
        self.true_marker_input.setMinimumHeight(60)
        
        self.false_marker_input = QLineEdit()
        self.false_marker_input.setObjectName("false_marker_input")
        self.false_marker_input.setPlaceholderText("False Marker:")
        self.false_marker_input.setStyleSheet("""
            QLineEdit#false_marker_input{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #f5f5ff,
                    stop:0.5 #f7f5fc,
                    stop:1 #f0f0ff
                );
                color: black;
                font-size: 24pt;
                border: 2px solid black;
                border-radius: 16px;
            }
        """)
        self.false_marker_input.setMinimumHeight(60)

        self.true_marker_input.textChanged.connect(self.change_true_marker_input)
        self.false_marker_input.textChanged.connect(self.change_false_marker_input)

        hue_mapping_screen_layout.addWidget(self.true_marker_input)
        hue_mapping_screen_layout.addWidget(self.false_marker_input)
        hue_mapping_screen_layout.setContentsMargins(10,10,10,10)
        hue_mapping_screen_layout.setSpacing(5)
        hue_mapping_screen_layout.addStretch()

    def change_current_parameter_screen(self, index):
        screen_name = self.hue_parameter_model.data(index,Qt.ItemDataRole.DisplayRole)
        
        if (screen_name == "Categorical Column"):
            self.change_to_categorical_column_hue_screen()
        
        if (screen_name == "Numerical Column"):
            self.change_to_numerical_column_hue_screen()

        if (screen_name == "Boolean Expression"):
            self.change_to_boolean_expression_hue_screen()

        if (screen_name == "Set Hue as None"):
            self.change_hue_to_none()

    def change_to_previous_screen(self):
        self.available_screens[self.current_screen_idx].hide()
        if (self.current_screen_idx == 3 or self.current_screen_idx == 4):
            self.current_screen_idx = 2
            self.premade_boolean_expression_format["column"] = ""
        elif (self.current_screen_idx >= 5 and self.current_screen_idx < 7):
            self.current_screen_idx -= 1
            if (self.current_screen_idx == 4):
                self.premade_boolean_expression_format["operation"] = ""
            if (self.current_screen_idx == 5):
                self.boolean_expression_value_input.clear()
                self.premade_boolean_expression_format["value"] = ""
        else:
            self.current_screen_idx = 6

        self.available_screens[self.current_screen_idx].show() 

    def change_to_categorical_column_hue_screen(self):
        self.available_screens[self.current_screen_idx].hide()
        self.current_screen_idx = 0
        self.available_screens[self.current_screen_idx].show()

    def change_to_numerical_column_hue_screen(self):
        self.available_screens[self.current_screen_idx].hide()
        self.current_screen_idx = 1
        self.available_screens[self.current_screen_idx].show()

    def change_to_boolean_expression_hue_screen(self):
        self.available_screens[self.current_screen_idx].hide()
        self.current_screen_idx = 2
        self.available_screens[self.current_screen_idx].show()

    def change_to_manual_boolean_expression_screen(self):
        self.available_screens[self.current_screen_idx].hide()
        self.current_screen_idx = 3
        self.available_screens[self.current_screen_idx].show()

    def change_to_premade_boolean_expression_screen(self):
        self.available_screens[self.current_screen_idx].hide()
        self.current_screen_idx = 4
        self.available_screens[self.current_screen_idx].show()

    def change_to_operators_boolean_expression_screen(self):
        self.available_screens[self.current_screen_idx].hide()
        self.current_screen_idx = 5
        self.available_screens[self.current_screen_idx].show()

    def change_to_value_boolean_expression_screen(self):
        self.available_screens[self.current_screen_idx].hide()
        self.current_screen_idx = 6
        self.available_screens[self.current_screen_idx].show()

    def change_to_logical_operator_screen(self):
        self.available_screens[self.current_screen_idx].hide()

        [button.hide() for button in self.available_logical_operators]
        if (self.current_screen_idx == 3): 
            self.available_logical_operators[2].show()
            self.available_logical_operators[3].show()
        if (self.current_screen_idx == 6):
            self.available_logical_operators[0].show()
            self.available_logical_operators[1].show()

        self.current_screen_idx = 7
        self.available_screens[self.current_screen_idx].show()

    def change_to_hue_mapping_screen(self):
        if (self.hue[1] == None):
            self.hue[1] = {True:"True",False:"False"}

        self.available_screens[self.current_screen_idx].hide()
        self.current_screen_idx = 8
        self.available_screens[self.current_screen_idx].show()

    def change_categorical_hue_column(self,index):
        source_index = self.categorical_filter_proxy.mapToSource(index)
        self.hue[0] = self.categorical_column_model.data(source_index, Qt.ItemDataRole.DisplayRole)
        self.hue[1] = None
        self.update_hue()
        
    def change_numerical_hue_column(self,index):
        source_index = self.numerical_filter_proxy.mapToSource(index)
        self.hue[0] = self.numerical_column_model.data(source_index, Qt.ItemDataRole.DisplayRole)
        self.hue[1] = None
        self.update_hue()

    def change_boolean_expression_manual_column_input(self):
        self.manual_boolean_expression_column = self.manual_boolean_expression_column_input.text().strip()

        list(map(lambda w: w.hide(), self.manual_validity_check_widgets))

        if (self.manual_boolean_expression_column in self.columns):
            self.manual_validity_check_widgets[0].show()
            self.manual_validity_check_widgets[4].hide()
            self.manual_boolean_expression_format["column"] = self.manual_boolean_expression_column
        elif (self.manual_boolean_expression_column == ""):
            self.manual_boolean_expression_format["column"] = ""
            return 
        else:
            self.manual_validity_check_widgets[0].hide()
            self.manual_validity_check_widgets[4].show()

        self.change_boolean_expression_manual_input()

    def change_boolean_expression_manual_operator_input(self):
        self.list_of_operators = self.numerical_operations + self.categorical_operations

        self.manual_boolean_expression_operator = self.manual_boolean_expression_operator_input.text().strip()

        list(map(lambda w: w.hide(), self.manual_validity_check_widgets))


        if (self.manual_boolean_expression_operator in self.list_of_operators):
            self.manual_validity_check_widgets[1].show()
            self.manual_validity_check_widgets[4].hide()
            self.manual_boolean_expression_format["operation"] = self.manual_boolean_expression_operator
        elif (self.manual_boolean_expression_operator == ""):
            self.manual_boolean_expression_format["operation"] = ""
            return 
        else:
            self.manual_validity_check_widgets[1].hide()
            self.manual_validity_check_widgets[5].show()

        self.change_boolean_expression_manual_input()

    def change_boolean_expression_manual_value_input(self):
        manual_boolean_expression_values = self.manual_boolean_expression_value_input.text().strip().split(" ")
        manual_boolean_expression_values = list(filter(lambda x:x != "",manual_boolean_expression_values))

        list(map(lambda w: w.hide(), self.manual_validity_check_widgets))

        if (manual_boolean_expression_values != []):
            try:
                if (len(manual_boolean_expression_values) == 1 and self.manual_boolean_expression_format["operation"] != "isin"):
                    manual_boolean_expression_values = float(manual_boolean_expression_values[0])
                else:
                    manual_boolean_expression_values = list(map(float,manual_boolean_expression_values))
                self.manual_boolean_expression_format["value"] = manual_boolean_expression_values
            except:
                self.manual_boolean_expression_format["value"] = manual_boolean_expression_values
            self.manual_validity_check_widgets[2].show()
            self.manual_validity_check_widgets[6].hide()

            self.change_boolean_expression_manual_input()
        else:
            self.manual_boolean_expression_format["value"] = ""

    def change_boolean_expression_manual_input(self):
        boolean_expression_parts = list(self.manual_boolean_expression_format.values())
        boolean_expression_parts = list(filter(lambda x:x != "",boolean_expression_parts))
        if (len(boolean_expression_parts) != 3):
            return

        list(map(lambda x:x.hide(),self.manual_validity_check_widgets))

        try:
            column_name = self.manual_boolean_expression_format["column"]
            column = self.dataset[column_name]
            column_type = "numerical" if pd.api.types.is_numeric_dtype(column) else "categorical"
            operation = self.manual_boolean_expression_format["operation"]
            value = self.manual_boolean_expression_format["value"]

            if (isinstance(value,list)):
                if (isinstance(value[0],float) and column_type != "numerical"):
                    raise Exception
                if (isinstance(value[0],str) and column_type != "categorical"):
                    raise Exception
            else:
                if (isinstance(value,float) and column_type != "numerical"):
                    raise Exception
                if (isinstance(value,str) and column_type != "categorical"):
                    raise Exception

            if ((operation == "between" or operation == "is_between") and not (value[0] <= value[1])):
                raise Exception

            if (operation in ["contains","startswith","endswith","regex","len","lower","upper"] and len(value) > 1):
                raise Exception

            self.boolean_expression_check[operation](column,value)

            self.manual_valid_expression_widget.show()
            self.manual_invalid_expression_widget.hide()

            self.manual_and_logical_button.show()
            self.manual_or_logical_button.show()
        except:
            self.manual_valid_expression_widget.hide()
            self.manual_invalid_expression_widget.show()

            self.manual_and_logical_button.hide()
            self.manual_or_logical_button.hide()
        else:
            numerical_operations = ["==","!=",">","<",">=","<="]

            if (operation in numerical_operations):
                boolean_expression = f"self.dataset['{column_name}'] {operation} {value}"
            elif (operation == "isin"):
                boolean_expression = f"self.dataset['{column_name}'].{operation}({value})"
            elif (operation == "notin"):
                boolean_expression = f"~self.dataset['{column_name}'].{operation}({value})"
            elif (operation == "between"):
                boolean_expression = f"self.dataset['{column_name}'].{operation}({value[0]},{value[1]})"
            elif operation == "between_exclusive":
                boolean_expression = f"self.dataset['{column_name}'].gt({value[0]}) & self.dataset['{column_name}'].lt({value[1]})" 
            elif (operation == "len"):
                boolean_expression = f"self.dataset['{column_name}'].str.{operation}() == {value}"
            elif (operation == "len"):
                boolean_expression = f"self.dataset['{column_name}'].str.{operation}() == 0"
            elif (operation == "contains"):
                boolean_expression = f"self.dataset['{column_name}'].str.{operation}({value},case=False)"
            elif (operation == "startswith"):
                boolean_expression = f"self.dataset['{column_name}'].str.{operation}({value})"
            elif (operation == "endswith"):
                boolean_expression = f"self.dataset['{column_name}'].str.{operation}({value})"
            elif (operation == "regex"):
                boolean_expression = f"self.dataset['{column_name}'].str.match({value})"
            elif (operation == "lower"):
                boolean_expression = f"self.dataset['{column_name}'].str.{operation}() == {value}" 
            elif (operation == "upper"):
                boolean_expression = f"self.dataset['{column_name}'].str.{operation}() == {value}" 
                
            self.hue[0] = " ".join(self.manual_nested_boolean_expression + [boolean_expression])
            self.hue[1] = None
            self.update_hue()

    def change_boolean_expression_premade_column(self,index):
        source_index = self.boolean_expression_column_proxy.mapToSource(index)
        column_name = self.boolean_expression_column_model.data(source_index, Qt.ItemDataRole.DisplayRole)
        self.premade_boolean_expression_format["column"] = column_name
        if (pd.api.types.is_numeric_dtype(self.dataset[column_name])):
            self.numeric_column_type = True
            self.boolean_expression_operations_model.setStringList(self.numerical_operations)
        else:
            self.numeric_column_type = False
            self.boolean_expression_operations_model.setStringList(self.categorical_operations)

        self.change_to_operators_boolean_expression_screen()

    def change_boolean_expression_premade_operation(self,index):
        operation = self.boolean_expression_operations_model.data(index, Qt.ItemDataRole.DisplayRole)
        self.premade_boolean_expression_format["operation"] = operation
        self.change_to_value_boolean_expression_screen()

    def change_boolean_expression_premade_value(self):
        boolean_expression_value = self.boolean_expression_value_input.text().strip().split(" ")
        boolean_expression_value = list[str](filter(lambda x:x != "",boolean_expression_value))

        if (boolean_expression_value == []):
            self.premade_valid_input_widget.hide()
            self.premade_invalid_input_widget.hide()
            self.premade_and_logical_button.hide()
            self.premade_or_logical_button.hide()
            self.premade_boolean_expression_format["value"] = ""
            self.hue_value = None
            self.update_hue()
            return 

        try:
            if (len(boolean_expression_value) == 1 and self.premade_boolean_expression_format["operation"] != "isin"):
                boolean_expression_value = float(boolean_expression_value[0])
            else:
                boolean_expression_value = list(map(float,boolean_expression_value))
            self.premade_boolean_expression_format["value"] = boolean_expression_value
        except:
            self.premade_boolean_expression_format["value"] = boolean_expression_value

        try:
            column_name = self.premade_boolean_expression_format["column"]
            column = self.dataset[column_name]
            operation = self.premade_boolean_expression_format["operation"]
            value = self.premade_boolean_expression_format["value"]

            if (isinstance(value,list)):
                if (isinstance(value[0],float) and not self.numeric_column_type):
                    raise Exception
                if (isinstance(value[0],str) and self.numeric_column_type):
                    raise Exception
            else:
                if (isinstance(value,float) and not self.numeric_column_type):
                    raise Exception
                if (isinstance(value,str) and self.numeric_column_type):
                    raise Exception


            if ((operation == "between" or operation == "between_exclusive") and not (value[0] <= value[1])):
                raise Exception

            if (operation in ["contains","startswith","endswith","regex","len","lower","upper"] and len(value) > 1):
                raise Exception

            self.boolean_expression_check[operation](column,value)
            
            self.premade_valid_input_widget.show()
            self.premade_invalid_input_widget.hide()

            self.premade_and_logical_button.show()
            self.premade_or_logical_button.show()
        except:
            self.premade_valid_input_widget.hide()
            self.premade_invalid_input_widget.show()

            self.premade_and_logical_button.hide()
            self.premade_or_logical_button.hide()
        else:
            numerical_operations = ["==","!=",">","<",">=","<="]

            if (operation in numerical_operations):
                boolean_expression = f"self.dataset['{column_name}'] {operation} {value}"
            elif (operation == "isin"):
                boolean_expression = f"self.dataset['{column_name}'].{operation}({value})"
            elif (operation == "notin"):
                boolean_expression = f"~self.dataset['{column_name}'].{operation}({value})"
            elif (operation == "between"):
                boolean_expression = f"self.dataset['{column_name}'].{operation}({value[0]},{value[1]})"
            elif operation == "between_exclusive":
                boolean_expression = f"self.dataset['{column_name}'].gt({value[0]}) & self.dataset['{column_name}'].lt({value[1]})" 
            elif (operation == "len"):
                boolean_expression = f"self.dataset['{column_name}'].str.{operation}() == {value}"
            elif (operation == "len"):
                boolean_expression = f"self.dataset['{column_name}'].str.{operation}() == 0"
            elif (operation == "contains"):
                boolean_expression = f"self.dataset['{column_name}'].str.{operation}({value},case=False)"
            elif (operation == "startswith"):
                boolean_expression = f"self.dataset['{column_name}'].str.{operation}({value})"
            elif (operation == "endswith"):
                boolean_expression = f"self.dataset['{column_name}'].str.{operation}({value})"
            elif (operation == "regex"):
                boolean_expression = f"self.dataset['{column_name}'].str.match({value})"
            elif (operation == "lower"):
                boolean_expression = f"self.dataset['{column_name}'].str.{operation}() == {value}" 
            elif (operation == "upper"):
                boolean_expression = f"self.dataset['{column_name}'].str.{operation}() == {value}" 

            self.hue[0] = " ".join(self.premade_nested_boolean_expression + [boolean_expression])
            self.update_hue()

    def change_true_marker_input(self):
        true_marker = self.true_marker_input.text().strip()

        if (true_marker == ""):
            self.hue[1][True] = "True"
            self.update_hue()
            return 

        self.hue[1][True] = true_marker
        self.update_hue()

    def change_false_marker_input(self):
        false_marker = self.false_marker_input.text().strip()

        if (false_marker == ""):
            self.hue[1][False] = "False"
            self.update_hue()
            return 

        self.hue[1][False] = false_marker
        self.update_hue()

    def change_hue_to_none(self):
        self.hue_value = None
        self.update_hue()

    def update_hue(self):
        #Grab the newest entry in the json
        db = self.plot_manager.get_db()
        dataset = pd.read_csv("./dataset/user_dataset.csv")
        #Check if the entry is empty or not and update if it's not empty and create one with the state if it's empty
        if (db != []):
            self.plot_manager.update_hue(self.hue)

            hue_order = db["legend"]["seaborn_legends"]["hue_order"]

            if (self.hue[0] is not None and hue_order is not None and "self.dataset" not in self.hue[0]):
                hue_value = set(dataset[self.hue[0]].unique())
                hue_order = set(hue_order)
                if (hue_order - hue_value != set()):
                    self.plot_manager.update_seaborn_legend("hue_order",None)
        else:
            plot_parameters = plot_json[self.selected_graph].copy()
            plot_parameters["hue"] = self.hue
            self.plot_manager.insert_plot_parameter(plot_parameters)
        self.graph_display.show_graph()

    def mousePressEvent(self, event):
        if not self.categorical_column_search_bar.geometry().contains(event.position().toPoint()):
            self.categorical_column_search_bar.clearFocus()
        if not self.numerical_column_search_bar.geometry().contains(event.position().toPoint()):
            self.numerical_column_search_bar.clearFocus()
        if not self.manual_boolean_expression_column_input.geometry().contains(event.position().toPoint()):
            self.manual_boolean_expression_column_input.clearFocus()
        if not self.manual_boolean_expression_operator_input.geometry().contains(event.position().toPoint()):
            self.manual_boolean_expression_operator_input.clearFocus()
        if not self.manual_boolean_expression_value_input.geometry().contains(event.position().toPoint()):
            self.manual_boolean_expression_value_input.clearFocus()
        if not self.boolean_expression_column_search_bar.geometry().contains(event.position().toPoint()):
            self.boolean_expression_column_search_bar.clearFocus()
        if not self.boolean_expression_value_input.geometry().contains(event.position().toPoint()):
            self.boolean_expression_value_input.clearFocus()
        super().mousePressEvent(event)

    def showEvent(self, event):
        super().showEvent(event)

        db = self.plot_manager.get_db()
        if (db != []):
            previous_hue = db["hue"]

        self.dataset = pd.read_csv("./dataset/user_dataset.csv")
        self.categorical_columns = self.get_categorical_columns()
        self.numerical_columns = self.get_numerical_columns()
        self.premade_boolean_expression_format = {
            "column":"",
            "operation":"",
            "value":"",
        }
        self.manual_boolean_expression_format = {
            "column":"",
            "operation":"",
            "value":"",
        }
        self.premade_nested_boolean_expression = []
        self.manual_nest_boolean_expression = []
        self.numeric_column_type = False

        self.categorical_column_search_bar.clear()
        self.numerical_column_search_bar.clear()
        self.boolean_expression_value_input.clear()
        self.manual_boolean_expression_column_input.clear()
        self.manual_boolean_expression_operator_input.clear()
        self.manual_boolean_expression_value_input.clear()

        self.hue = previous_hue
        self.update_hue()

    def close_dialog(self):
        self.close()

class style_button(QDialog):
    def __init__(self,selected_graph,graph_display):
        super().__init__()

        self.setWindowTitle("Customize Style")
        
        self.selected_graph = selected_graph
        self.graph_display = graph_display 
        self.plot_manager = PlotManager()

        self.style = None

        #-----Initialize the QDialog Window-----
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

        #-----Create the Style Home Screen-----
        self.style_adjustment_section = QWidget()
        self.style_adjustment_section.setObjectName("style_adjustment_section")
        self.style_adjustment_section.setStyleSheet("""
            QWidget#style_adjustment_section{
               background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #f5f5ff,
                    stop:0.5 #f7f5fc,
                    stop:1 #f0f0ff
                );
                border: 2px solid black;
                border-radius: 16px; 
            }
        """)

        self.categorical_column_style_button = QPushButton()
        self.categorical_column_style_button.setObjectName("categorical_column_style_button")
        self.categorical_column_style_button.setStyleSheet("""
            QPushButton#categorical_column_style_button{
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
            QPushButton#categorical_column_style_button:hover{
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