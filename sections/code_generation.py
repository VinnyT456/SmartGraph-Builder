from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget
import json


class plot_config_cleaner:
    def __init__(self, current_plot_config, default_plot_config):
        self.current_plot_config = current_plot_config
        self.default_plot_config = default_plot_config

        self.clean_plot_config = dict()
        self.clean_data()

    def clean_data(self):
        self.clean_plot_config["axis-title"] = dict()
        self.clean_plot_config["legend"] = dict()
        self.clean_plot_config["grid"] = dict()

        self.clean_axis_title_data()
        self.clean_legend_data()
        self.clean_grid_data()

        for parameter, argument in self.current_plot_config.items():
            if argument != self.default_plot_config[parameter]:
                self.clean_plot_config[parameter] = argument

    def clean_axis_title_data(self):
        for parameter, argument in self.current_plot_config["axis-title"].items():
            if argument != self.default_plot_config["axis-title"][parameter]:
                self.clean_plot_config["axis-title"][parameter] = argument

        self.current_plot_config.pop("axis-title")
        if self.clean_plot_config["axis-title"] == dict():
            self.clean_plot_config.pop("axis-title")

    def clean_legend_data(self):
        self.clean_plot_config["seaborn_legends"] = dict()
        self.clean_seaborn_legend_data()

        for parameter, argument in self.current_plot_config["legend"].items():
            if argument != self.default_plot_config["legend"][parameter]:
                self.clean_plot_config["legend"][parameter] = argument

        self.current_plot_config.pop("legend")
        if self.clean_plot_config["legend"] == dict():
            self.clean_plot_config.pop("legend")

    def clean_seaborn_legend_data(self):
        for parameter, argument in self.current_plot_config["legend"]["seaborn_legends"].items():
            if (argument != self.default_plot_config["legend"]["seaborn_legends"][parameter]):
                self.clean_plot_config["seaborn_legends"][parameter] = argument

        self.current_plot_config["legend"].pop("seaborn_legends")
        if (self.clean_plot_config["seaborn_legends"] == dict()):
            self.clean_plot_config.pop("seaborn_legend")

    def clean_grid_data(self):
        for parameter, argument in self.current_plot_config["grid"].items():
            if argument != self.default_plot_config["grid"][parameter]:
                self.clean_plot_config["grid"][parameter] = argument

        self.current_plot_config.pop("grid")
        if self.clean_plot_config["grid"] == dict():
            self.clean_plot_config.pop("grid")

    def get_clean_plot_config(self):
        return self.clean_plot_config

class Code_Generator:
    def __init__(self):
        self.current_plot_config = self.read_plot_config()
        self.dataset_path = "./dataset/user_dataset.csv"
        self.graph_type = self.current_plot_config.pop("type")
        self.default_plot_config = self.read_default_plot_config()

        self.plot_config_cleaner = plot_config_cleaner(
            self.current_plot_config, self.default_plot_config
        )
        self.clean_plot_config = self.plot_config_cleaner.get_clean_plot_config()

        self.plot_config = self.create_plot_config()

        self.import_statements = """
            import pandas as pd
            import seaborn as sns
            import matplotlib.pyplot as plt
        """
        
        self.dataset_statement = "df = pd.read_csv('dataset.csv')"

        self.seaborn_plot_code_statements = {
            "Scatter Plot":"sns.scatterplot("
        }

        self.matplotlib_plot_code_statements = {
            "x-axis-title":"plt.xlabel(",
            "y-axis-title":"plt.ylabel(",
            "title":"plt.title(",
            "legend":"plt.legend(",
            "grid":"plt.grid(",
        }

        self.show_graph_statement = "plt.show()"

    def read_plot_config(self):
        with open("./plot_config.json") as file:
            try:
                data = json.load(file)
                data = data["_default"]

                first_key = sorted(data.keys())[-1]
                plot_config = data[first_key].copy()
                plot_config.pop("version")
            except json.JSONDecodeError:
                return dict()

        return plot_config

    def read_default_plot_config(self):
        with open("./default_plot_config.json") as file:
            data = json.load(file)
            new_data = data[self.graph_type]
        return new_data

    def create_plot_config(self):
        plot_config = dict()

        plot_config = {k: v for k, v in {
            "axis_title": self.clean_plot_config.pop("axis-title", {}),
            "legend": self.clean_plot_config.pop("legend", {}),
            "title": self.clean_plot_config.pop("title", {}),
            "grid": self.clean_plot_config.pop("grid", {}),
            "graph_data": self.clean_plot_config.pop("seaborn_legend", {}) | self.clean_plot_config,
        }.items() if v}

        graph_data = plot_config.get("graph_data", {})
        seaborn_legends = graph_data.pop("seaborn_legends", {})
        graph_data = {**seaborn_legends, **graph_data}
        plot_config["graph_data"] = graph_data

        order = ["graph_data","title","axis_title","legend","grid"]

        plot_config = {k: plot_config.pop(k, {}) 
               for k in order if plot_config.get(k, {})}

        return plot_config

class Code_Section(QWidget):
    def __init__(self):
        super().__init__()

        # Create a small section to display the code and ensure it's drawn on the window
        self.setFixedWidth(620)
        self.setMinimumHeight(100)
        self.setStyleSheet("""
            QWidget{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #f5f5ff,
                    stop:0.5 #f7f5fc,
                    stop:1 #f0f0ff
                );
                border: 2px solid #d0d0ff;
                border-radius: 24px;
            }
        """)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)