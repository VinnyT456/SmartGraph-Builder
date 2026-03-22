import re
from PyQt6.QtCore import QAbstractTableModel, Qt, QPropertyAnimation, QEasingCurve
from PyQt6.QtWidgets import (
    QDialog, QFileDialog, QHBoxLayout, QHeaderView, QLabel, QLineEdit, QPushButton, QSizePolicy, QTableView, QWidget, QVBoxLayout
)
import pandas as pd
import os

class ColumnManagementWindow(QDialog):
    def __init__(self,dataset_table):
        super().__init__()

        self.dataset_table = dataset_table

        self.setWindowTitle("Column Management")
        self.setObjectName("column_management_window")
        self.setFixedHeight(300)
        self.setFixedWidth(500)

        self.setStyleSheet("""
            QDialog#column_management_window{
                background: qlineargradient(
                    x1:0, y1:1, x2:0, y2:0,
                    stop:0 rgba(255, 0, 255, 255),
                    stop:0.22 rgba(252, 86, 191, 255),
                    stop:0.46 rgba(247, 96, 96, 255),
                    stop:0.71 rgba(255, 180, 82, 255),
                    stop:0.90 rgba(245, 219, 51, 255)
                );
            }
        """)

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

        self.scale_anim = QPropertyAnimation(self, b"geometry")
        self.scale_anim.setDuration(200)
        self.scale_anim.setStartValue(self.geometry())
        self.scale_anim.setEndValue(start_rect)
        self.scale_anim.setEasingCurve(QEasingCurve.Type.OutBack)

        # Start animations
        self.fade_anim.start()
        self.scale_anim.start()

class DatapointWindow(QDialog):
    def __init__(self,dataset_table):
        super().__init__()

        self.dataset_table = dataset_table

        self.setWindowTitle("Enter the x/y datapoints")
        self.setFixedHeight(300)
        self.setFixedWidth(500)

        self.setObjectName("data_point_window")

        layout = QVBoxLayout()

        self.x_datapoints = QLineEdit()
        self.x_datapoints.setPlaceholderText("X:")
        self.x_datapoints.setObjectName("X_data")

        self.y_datapoints = QLineEdit()
        self.y_datapoints.setPlaceholderText("Y:")
        self.y_datapoints.setObjectName("Y_data")

        self.z_datapoints = QLineEdit()
        self.z_datapoints.setPlaceholderText("Z:")
        self.z_datapoints.setObjectName("Z_data")

        self.submit_button = QPushButton("Submit")
        self.submit_button.setObjectName("submit_button")

        self.x_datapoints.setFixedHeight(60)
        self.y_datapoints.setFixedHeight(60)
        self.z_datapoints.setFixedHeight(60)
        self.submit_button.setFixedHeight(60)
        self.submit_button.setFixedWidth(200)

        layout.addWidget(self.x_datapoints)
        layout.addWidget(self.y_datapoints)
        layout.addWidget(self.z_datapoints)
        layout.addWidget(self.submit_button,alignment=Qt.AlignmentFlag.AlignCenter)
        layout.setContentsMargins(10,10,10,10)
        layout.setSpacing(10)
        self.setLayout(layout)

        self.submit_button.clicked.connect(self.create_dataset)

    def create_dataset(self):
        x_points = self.x_datapoints.text().strip()
        y_points = self.y_datapoints.text().strip()
        z_points = self.z_datapoints.text().strip()

        x_valid_input = self.valid_inputs(x_points)
        y_valid_input = self.valid_inputs(y_points)
        z_valid_input = self.valid_inputs(z_points)


        if (x_valid_input and y_valid_input and z_valid_input):
            
            #Find all positive/negative decimal numbers
            #Find all positive/negative integer numbers
            length = max(len(re.findall(r"[-+]?\d*\.\d+|[-+]?\d+",x_points)),
                        len(re.findall(r"[-+]?\d*\.\d+|[-+]?\d+",y_points)),
                        len(re.findall(r"[-+]?\d*\.\d+|[-+]?\d+",z_points)))

            if (length == 0):
                return

            if (x_points == ""):
                x_points = ("0 " * length).strip()
            if (y_points == ""):
                y_points = ("0 " * length).strip()
            if (z_points == ""):
                z_points = ("0 " * length).strip()

            try:
                x_points = list(map(float,x_points.replace(","," ").split(" ")))
                y_points = list(map(float,y_points.replace(","," ").split(" ")))
                z_points = list(map(float,z_points.replace(","," ").split(" ")))
            except ValueError:
                pass

            if (len(x_points) != len(y_points) != len(z_points)):
                return 

            df = pd.DataFrame({
                "X": x_points,
                "Y": y_points,
                "Z": z_points,
            },dtype=float)

            folder_path = "dataset"

            if (not os.path.exists(folder_path)):
                os.mkdir(folder_path)

            if os.listdir(folder_path):
                for file in os.listdir(folder_path):
                    if (not file.startswith("user_dataset")):
                        os.remove(f"{folder_path}/{file}")

            df.to_csv("dataset/user_dataset.csv",index=False)

            file_path = "dataset/user_dataset.csv"
            if (file_path):
                self.dataset_table.import_file(file_path)
            self.close()

    def valid_inputs(self,user_input):
        numbers = user_input.split()
        try:
            for num in numbers:
                float(num)
            return True
        except ValueError:
            return False

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

        self.scale_anim = QPropertyAnimation(self, b"geometry")
        self.scale_anim.setDuration(200)
        self.scale_anim.setStartValue(self.geometry())
        self.scale_anim.setEndValue(start_rect)
        self.scale_anim.setEasingCurve(QEasingCurve.Type.OutBack)

        # Start animations
        self.fade_anim.start()
        self.scale_anim.start()

class PrepareDataset(QAbstractTableModel):
    def __init__(self, df):
        super().__init__()
        self.df = df

    def rowCount(self, parent=None):
        return len(self.df)

    def columnCount(self, parent=None):
        return len(self.df.columns)

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid():
            return None

        value = self.df.iat[index.row(), index.column()]

        if role == Qt.ItemDataRole.DisplayRole:
            return str(value)

        elif role == Qt.ItemDataRole.TextAlignmentRole:
            return Qt.AlignmentFlag.AlignCenter
        return None

    def headerData(self, section, orientation, role=Qt.ItemDataRole.DisplayRole):
        if role == Qt.ItemDataRole.DisplayRole:
            if orientation == Qt.Orientation.Horizontal:
                return str(self.df.columns[section])
            else:
                return str(section + 1)
        return None

    def flags(self, index):
        return Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled

    def setHeaderData(self, section, orientation, value, role=Qt.ItemDataRole.EditRole):
        if orientation == Qt.Orientation.Horizontal and role == Qt.ItemDataRole.EditRole:
            old_name = self.df.columns[section]
            self.df.rename(columns={old_name: value}, inplace=True)
            self.headerDataChanged.emit(orientation, section, section)
            return True
        return False
        
class displayDataset(QTableView):
    def __init__(self):
        super().__init__()
        
        self.setObjectName("displayDataset")

        self.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.horizontalHeader().setSectionsClickable(False)
        self.horizontalHeader().setStretchLastSection(True)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Fixed)
        self.horizontalHeader().setHighlightSections(False)

        self.setAlternatingRowColors(True)
        self.setShowGrid(False)

        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

    def import_file(self,file_path):
        self.model = PrepareDataset(pd.read_csv(file_path))
        self.setModel(self.model)
        self.verticalHeader().setVisible(False)
        self.setShowGrid(True)
        self.setSortingEnabled(False)

    def mousePressEvent(self, event):
        index = self.indexAt(event.pos())

        if index.isValid() and self.selectionModel().isSelected(index):
            self.clearSelection()
        else:
            super().mousePressEvent(event)

class import_replace_dataset_button(QPushButton):
    def __init__(self,dataset_table):
        super().__init__()
        self.dataset_table = dataset_table
        self.setObjectName("import_dataset")

        self.label = QLabel("Import Dataset")
        self.label.setObjectName("import_dataset_label")
        self.label.setWordWrap(True)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

        self.setMinimumHeight(35)
        self.label.setMinimumHeight(25)

        layout = QVBoxLayout(self)
        layout.addWidget(self.label)
        layout.setContentsMargins(5, 0, 5, 0)  

        self.clicked.connect(self.select_file)

    def select_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open CSV", "", "CSV Files (*.csv)"
        )
        if (file_path):
            dataset = pd.read_csv(file_path)

            folder_path = "dataset"

            if (not os.path.exists(folder_path)):
                os.mkdir(folder_path)

            if os.listdir(folder_path):
                for file in os.listdir(folder_path):
                    if (not file.startswith("user_dataset")):
                        os.remove(f"{folder_path}/{file}")

            dataset.to_csv("dataset/user_dataset.csv",index=False)
            file_path = "dataset/user_dataset.csv"
            if (file_path):
                self.dataset_table.import_file(file_path)

class enter_datapoints_button(QPushButton):
    def __init__(self,dataset_table):
        super().__init__()
        self.setObjectName("enter_data_points_button")
        self.dataset_table = dataset_table

        self.label = QLabel("Enter Datapoints")
        self.label.setObjectName("enter_data_points_label")
        self.label.setWordWrap(True)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

        self.setMinimumHeight(35)
        self.label.setMinimumHeight(25)

        layout = QVBoxLayout(self)
        layout.addWidget(self.label)
        layout.setContentsMargins(5, 0, 5, 0)  

        self.clicked.connect(self.enter_datapoints)

    def enter_datapoints(self):
        data_point_window = DatapointWindow(self.dataset_table)
        data_point_window.exec()

class column_management_button(QPushButton):
    def __init__(self,dataset_table):
        super().__init__()
        self.setObjectName("column_management_button")
        self.dataset_table = dataset_table

        self.label = QLabel("Column Management")
        self.label.setObjectName("column_management_label")
        self.label.setWordWrap(True)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

        self.setMinimumHeight(35)
        self.label.setMinimumHeight(25)

        layout = QVBoxLayout(self)
        layout.addWidget(self.label)
        layout.setContentsMargins(5, 0, 5, 0)
        self.clicked.connect(self.open_column_management_window)

    def open_column_management_window(self):
        column_management = ColumnManagementWindow(self.dataset_table)
        column_management.exec()

class Dataset_TopBar(QWidget):
    def __init__(self,table):
        super().__init__()

        self.setObjectName("dataset_topbar")
        self.dataset_table = table

        self.setFixedHeight(50)
        self.setFixedWidth(350)
        
        layout = QHBoxLayout(self)
        layout.addWidget(import_replace_dataset_button(self.dataset_table))
        layout.addWidget(enter_datapoints_button(self.dataset_table))
        layout.addWidget(column_management_button(self.dataset_table))
        layout.setContentsMargins(5,5,5,5) 
        layout.setSpacing(5)

        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

class Dataset_Table(QWidget):
    def __init__(self,table):
        super().__init__()
        self.setObjectName("dataset_table")

        self.dataset_table = table

        layout = QVBoxLayout()
        layout.addWidget(self.dataset_table)
        layout.setContentsMargins(0,0,0,0) 
        layout.setSpacing(5)

        self.setFixedWidth(350)
        self.setLayout(layout)

        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

class Dataset_Section(QWidget):
    def __init__(self):
        super().__init__()
        self.setFixedWidth(350)

        self.dataset = displayDataset()
        self.dataset_topbar = Dataset_TopBar(self.dataset)
        self.dataset_table = Dataset_Table(self.dataset)

        layout = QVBoxLayout(self)
        layout.addWidget(self.dataset_topbar)
        layout.addSpacing(5)
        layout.addWidget(self.dataset_table)
        layout.setContentsMargins(0,0,0,0) 

        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
