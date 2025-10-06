import sys

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QSizePolicy, QWidget, QGridLayout,
    QPushButton, QLabel, QVBoxLayout, QHBoxLayout, QMenu
)

from sections.dataset import Dataset_Section
from sections.graph import Graph_Section
from sections.graph_parameter import GraphParameter_Section
from sections.data_preprocessing import DataPreprocessing_Section

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Simple Visual")
        self.setFixedSize(1400, 800)

        preprocessing_parameters_layout = QVBoxLayout()
        preprocessing_parameters_layout.addWidget(GraphParameter_Section())
        preprocessing_parameters_layout.addWidget(DataPreprocessing_Section())
        preprocessing_parameters_layout.setContentsMargins(0,0,0,0) 
        preprocessing_parameters_layout.setSpacing(0)
        preprocessing_section = QWidget()
        preprocessing_section.setLayout(preprocessing_parameters_layout) 


        window_layout = QHBoxLayout()
        window_layout.addWidget(Dataset_Section(),stretch=1)
        window_layout.addWidget(Graph_Section(),stretch=2)
        window_layout.addWidget(preprocessing_section,stretch=1)
        window_layout.setContentsMargins(0,0,0,0) 
        window_layout.setSpacing(0)

        window = QWidget()
        window.setLayout(window_layout)
        self.setCentralWidget(window)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec()
