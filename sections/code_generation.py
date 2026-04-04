from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QHBoxLayout,
    QPushButton,
    QSizePolicy,
    QTextBrowser,
    QVBoxLayout,
    QWidget,
)
from pygments import highlight
from pygments.lexers import PythonLexer
from pygments.formatters import HtmlFormatter
import textwrap

class Code_Section(QWidget):
    def __init__(self):
        super().__init__()

        # Create a small section to display the code and ensure it's drawn on the window
        self.setFixedWidth(620)
        self.setMinimumHeight(150)

        self.setProperty("class", "adjustment_section")

        self.code_section_top_bar = QWidget()
        self.create_code_section()
        self.code_section_top_bar.hide()

        self.code_preview_section = QTextBrowser()
        self.code_preview_section.setObjectName("code_browser")
        self.code_preview_section.setReadOnly(True)
        self.code_preview_section.setOpenExternalLinks(False)
        self.code_preview_section.setMinimumHeight(100)
        self.code_preview_section.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        self.code_preview_section.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.code_preview_section.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.code_preview_section.hide()

        self.formatter = HtmlFormatter(style="abap", noclasses=True, nobackground=True)

        main_layout = QVBoxLayout(self)
        main_layout.addWidget(self.code_section_top_bar)
        main_layout.addWidget(self.code_preview_section)
        main_layout.addStretch()
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(5)

        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

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

    def create_code_section(self):
        code_preview_button = QPushButton("Code Preview")
        code_preview_button.setProperty("class", "code_section")
        code_preview_button.setFixedWidth(100)
        code_preview_button.setEnabled(False)

        copy_button = QPushButton("Copy Code")
        copy_button.setProperty("class", "code_section")
        copy_button.setFixedWidth(80)

        full_screen_button = QPushButton("Full Screen")
        full_screen_button.setProperty("class", "code_section")
        full_screen_button.setFixedWidth(80)

        theme_button = QPushButton("Theme")
        theme_button.setProperty("class","code_section")
        theme_button.setFixedWidth(55)

        settings_button = QPushButton("Settings")
        settings_button.setProperty("class", "code_section")
        settings_button.setFixedWidth(65)

        code_section_top_bar_layout = QHBoxLayout(self.code_section_top_bar)
        code_section_top_bar_layout.addWidget(
            code_preview_button, alignment=Qt.AlignmentFlag.AlignLeft
        )
        code_section_top_bar_layout.addStretch()
        code_section_top_bar_layout.addWidget(copy_button)
        code_section_top_bar_layout.addWidget(full_screen_button)
        code_section_top_bar_layout.addWidget(theme_button)
        code_section_top_bar_layout.addWidget(settings_button)
        code_section_top_bar_layout.setContentsMargins(0, 0, 0, 0)
        code_section_top_bar_layout.setSpacing(3)

    def create_plot_config(self, current_plot_config):
        plot_config = dict()

        plot_config = {
            k: v
            for k, v in {
                "x-axis-title": current_plot_config.pop("x-axis-title", {}),
                "y-axis-title": current_plot_config.pop("y-axis-title", {}),
                "legend": current_plot_config.pop("legend", {}),
                "title": current_plot_config.pop("title", {}),
                "grid": current_plot_config.pop("grid", {}),
                "graph_data": current_plot_config.pop("seaborn_legend", {})
                | current_plot_config,
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

    def generate_python_code(self, graph_type, current_plot_config):
        self.code_section_top_bar.show()
        self.code_preview_section.show()

        self.new_plot_config = dict()
        self.plot_config = self.create_plot_config(current_plot_config)

        indent = " " * 4

        plot_code_statement = (
            self.seaborn_plot_code_statements[graph_type] + f"\n{indent}data=df,"
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

        scroll_pos = self.code_preview_section.verticalScrollBar().value()

        highlighted_code = highlight(full_code, PythonLexer(), self.formatter)
        self.code_preview_section.setHtml(highlighted_code)

        self.code_preview_section.verticalScrollBar().setValue(scroll_pos)

    def copy_python_code(self):
        pass
    
    def switch_to_full_screen(self):
        pass

    def switch_theme(self):
        pass

    def open_setting(self):
        pass