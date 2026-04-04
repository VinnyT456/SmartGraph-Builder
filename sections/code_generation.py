from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QPushButton, QVBoxLayout, QWidget
from pygments import highlight
from pygments.lexers import PythonLexer
from pygments.formatters import TerminalFormatter
import textwrap
import json


class Code_Generator:
    def __init__(self):
        self.current_plot_config = self.read_plot_config()
        self.dataset_path = "./dataset/user_dataset.csv"
        self.graph_type = self.current_plot_config.pop("type")
        self.default_plot_config = self.read_default_plot_config()

        self.parameters_to_skip = [
            "x-axis-title",
            "y-axis-title",
            "title",
            "legend",
            "seaborn_legends",
            "grid",
        ]

        self.new_plot_config = dict()
        self.clean_plot_config(self.current_plot_config, self.default_plot_config)

        self.plot_config = self.create_plot_config()

        self.starter_code = textwrap.dedent("""
            import pandas as pd
            import seaborn as sns
            import matplotlib.pyplot as plt

            df = pd.read_csv('path/to/your_dataset.csv')

            plt.figure(figsize=(7,6))
        """)

        self.seaborn_plot_code_statements = {"Scatter Plot": "sns.scatterplot("}

        self.matplotlib_plot_code_statements = {
            "x-axis-title": "plt.xlabel(",
            "y-axis-title": "plt.ylabel(",
            "title": "plt.title(",
            "legend": "plt.legend(",
            "grid": "plt.grid(",
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

    def clean_plot_config(
        self, current_plot_config, default_plot_config, special_parameter=""
    ):
        for parameter, argument in current_plot_config.items():
            if parameter in self.parameters_to_skip:
                self.parameters_to_skip.remove(parameter)
                self.new_plot_config[parameter] = dict()
                self.clean_plot_config(
                    current_plot_config[parameter],
                    default_plot_config[parameter],
                    parameter,
                )
            elif special_parameter == "" and argument != default_plot_config[parameter]:
                self.new_plot_config[parameter] = argument
            elif special_parameter != "" and argument != default_plot_config[parameter]:
                self.new_plot_config[special_parameter][parameter] = argument

    def create_plot_config(self):
        plot_config = dict()

        plot_config = {
            k: v
            for k, v in {
                "x-axis-title": self.new_plot_config.pop("x-axis-title", {}),
                "y-axis-title": self.new_plot_config.pop("y-axis-title", {}),
                "legend": self.new_plot_config.pop("legend", {}),
                "title": self.new_plot_config.pop("title", {}),
                "grid": self.new_plot_config.pop("grid", {}),
                "graph_data": self.new_plot_config.pop("seaborn_legend", {})
                | self.new_plot_config,
            }.items()
            if v
        }

        graph_data = plot_config.get("graph_data", {})
        seaborn_legends = graph_data.pop("seaborn_legends", {})
        graph_data = {**graph_data, **seaborn_legends}
        plot_config["graph_data"] = graph_data

        order = [
            "graph_data",
            "title",
            "x-axis-title",
            "y-axis-title",
            "legend",
            "grid",
        ]

        plot_config = {
            k: plot_config.pop(k, {}) for k in order if plot_config.get(k, {})
        }

        return plot_config

    def generate_python_code(self):
        indent = " " * 4

        plot_code_statement = (
            self.seaborn_plot_code_statements[self.graph_type] + f"\n{indent}data=df,"
        )

        def format_value(value):
            if isinstance(value, str):
                return f'"{value}"'
            elif isinstance(value, list):
                return format_value(value[0])
            elif value is None:
                return "None"
            else:
                return str(value)

        for parameter, argument in self.plot_config["graph_data"].items():
            argument = format_value(argument)
            new_line = f"\n{indent}{parameter}={argument},"
            plot_code_statement += new_line
        plot_code_statement += "\n)\n"

        self.plot_config.pop("graph_data")

        plot_adjustment = ""

        for adjustment in list(self.plot_config.keys()):
            plot_adjustment_line = self.matplotlib_plot_code_statements[adjustment]

            for parameter, argument in self.plot_config[adjustment].items():
                if parameter == "label":
                    plot_adjustment_line += format_value(argument)
                else:
                    plot_adjustment_line += f"{parameter}={format_value(argument)}"
                plot_adjustment_line += ", "
            plot_adjustment_line = plot_adjustment_line[:-2] + ")"
            plot_adjustment += plot_adjustment_line + "\n"

        full_code = (
            self.starter_code
            + plot_code_statement
            + plot_adjustment
            + self.show_graph_statement
        )

        print(highlight(full_code, PythonLexer(), TerminalFormatter()))


class Code_Section(QWidget):
    def __init__(self):
        super().__init__()

        # Create a small section to display the code and ensure it's drawn on the window
        self.setFixedWidth(620)
        self.setMinimumHeight(150)

        self.setProperty("class", "adjustment_section")

        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

        self.create_code_section()

    def create_code_section(self):
        copy_button = QPushButton("Copy Code")
        copy_button.setStyleSheet("""
            QPushButton{
                border: 2px solid #d0d0ff;
                border-radius: 8px 
            }
        """)
        copy_button.setFixedWidth(70)

        layout = QVBoxLayout(self)
        layout.addWidget(
            copy_button,
            alignment=Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignRight,
        )
        layout.setContentsMargins(0, 10, 10, 0)


if __name__ == "__main__":
    Code_Generator().generate_python_code()
