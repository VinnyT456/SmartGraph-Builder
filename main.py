import os 
import sys

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
)

from sections.ai_summary import AI_Summary_Section
from sections.dataset import Dataset_Section
from sections.graph import Graph_Section
from sections.graph_parameter import GraphParameter_Section
from sections.data_preprocessing import DataPreprocessing_Section
from sections.code_generation import Code_Section

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SmartGraph Builder")
        self.setFixedSize(1400, 800)

        #Create a vertical box layout and add the graph parameter and data preprocessing section in it
        preprocessing_parameters_layout = QVBoxLayout()
        preprocessing_parameters_layout.addWidget(GraphParameter_Section(),stretch=6)
        preprocessing_parameters_layout.addWidget(DataPreprocessing_Section(),stretch=4)
        preprocessing_parameters_layout.setContentsMargins(0,0,0,0) 
        preprocessing_parameters_layout.setSpacing(20)

        #Add the layout we just created into the preprocessing/parameter section on the right
        preprocessing_section = QWidget()
        preprocessing_section.setLayout(preprocessing_parameters_layout) 

        #Create a vertical box layout and add the dataset and AI summary section in it
        dataset_ai_layout = QVBoxLayout()
        dataset_ai_layout.addWidget(Dataset_Section(),stretch=6)
        dataset_ai_layout.addWidget(AI_Summary_Section(),stretch=4)
        dataset_ai_layout.setContentsMargins(0,0,0,0)
        dataset_ai_layout.setSpacing(20)

        #Add the layout we just created to the dataset/AI summary section on the left
        dataset_section = QWidget()
        dataset_section.setLayout(dataset_ai_layout)

        #Create a vertical box layout and add the graph and code generation section in it
        graph_code_layout = QVBoxLayout()
        graph_code_layout.addWidget(Graph_Section(),stretch=9)
        graph_code_layout.addWidget(Code_Section(),stretch=1)
        graph_code_layout.setContentsMargins(0,0,0,0)
        graph_code_layout.setSpacing(20)

        graph_section = QWidget()
        graph_section.setLayout(graph_code_layout)

        #Create a horizontal box layout to store all the sections that we have available
        window_layout = QHBoxLayout()
        window_layout.addWidget(dataset_section)
        window_layout.addSpacing(20)
        window_layout.addWidget(graph_section) 
        window_layout.addSpacing(20)
        window_layout.addWidget(preprocessing_section)
        window_layout.setContentsMargins(20,20,20,20) 
        window_layout.setSpacing(0)                     

        #Apply the layout we created onto the window and display it
        window = QWidget()
        window.setObjectName("MainWindow")
        window.setLayout(window_layout)

        window.setStyleSheet("""
            QWidget#MainWindow {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #7f9cf5, stop:0.5 #b299f8, stop:1 #a15ee0);
                }
        """)
        self.setCentralWidget(window)

        #Check that the dataset folder is empty
        folder_path = 'dataset'
        if (os.listdir(folder_path)):
            for file in os.listdir(folder_path):
                file_path = f"{folder_path}/{file}"
                os.remove(file_path)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec()
