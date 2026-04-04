import copy
import inspect
import matplotlib.axes as maxes
from io import BytesIO
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QImage, QPainter, QPainterPath, QPixmap
from PyQt6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QStackedLayout,
    QWidget,
    QVBoxLayout,
)
from sections.plot_manager import PlotManager
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
import matplotlib.colors as mcolors
import pandas as pd
import numpy as np
import json


class graph_generator(QWidget):
    def __init__(self):
        super().__init__()

        self.plot_manager = PlotManager()

        self.gradient = None
        gradient = np.linspace(0, 1, 1024).reshape(1, -1)
        gradient = np.repeat(gradient, 1024, axis=0)
        self.gradient = gradient

        with open("./default_plot_config.json", "r") as file:
            self.default_graph_parameters = json.load(file)

        self.new_plot_config = dict()

        self.xkcd_colors = list(mcolors.XKCD_COLORS.keys())
        self.tab_colors = list(mcolors.TABLEAU_COLORS.keys())

        self.xkcd_colors = [c.replace("xkcd:", "") for c in self.xkcd_colors]
        self.tab_colors = [c.replace("tab:", "") for c in self.tab_colors]

        self.parameters_to_skip = [
            "x-axis-title",
            "y-axis-title",
            "title",
            "legend",
            "seaborn_legends",
            "grid",
        ]

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

    def prepare_plotting(self):
        self.current_graph_parameters = copy.deepcopy(self.plot_manager.get_db())
        self.graph_type = self.current_graph_parameters.pop("type")
        self.current_graph_parameters.pop("version")

        self.clean_plot_config(
            self.current_graph_parameters,
            self.default_graph_parameters[self.graph_type],
        )

        self.dataset = pd.read_csv(self.current_graph_parameters.get("data"))
        self.available_graphs = {"Scatter Plot": [sns.scatterplot, maxes.Axes.scatter]}

        self.x_axis_title_parameter = self.new_plot_config.get("x-axis-title","")
        self.y_axis_title_parameter = self.new_plot_config.get("y-axis-title","")
        self.title_parameter = self.new_plot_config.get("title","")

        self.grid_parameter = self.new_plot_config.get("grid","")
        self.grid_dashes = (self.grid_parameter if isinstance(self.grid_parameter, dict) else {}).get("dashes", "")

        if self.grid_dashes != "" and None not in self.grid_dashes:
            grid_offset = self.grid_dashes[0]
            grid_sequence = self.grid_dashes[1]
            self.grid_parameter["dashes"] = (grid_offset, *grid_sequence)

        self.legend_parameters = self.new_plot_config.get("legend","")
        self.seaborn_legend_parameters = self.new_plot_config.get("seaborn_legends","")
        
        self.hue = self.new_plot_config.get("hue",None)
        self.hue_mapping = self.hue[1] if self.hue is not None else None 

        if self.hue_mapping is not None:
            true_mapping = self.hue_mapping["true"]
            false_mapping = self.hue_mapping["false"]
            self.hue_mapping = {
                True: true_mapping,
                False: false_mapping,
            }

        if (self.hue is not None):
            self.new_plot_config["hue"] = self.new_plot_config["hue"][0]

        for key in ["legend", "grid", "x-axis-title", "y-axis-title", "title", "seaborn_legends"]:
            self.new_plot_config.pop(key, None)

        self.graph_parameters = self.new_plot_config.copy()
        self.graph_parameters["data"] = self.dataset

        self.x_axis = self.new_plot_config.get("x")
        self.y_axis = self.new_plot_config.get("y")

    def apply_gradient_background(self, fig, ax):
        colors = ["#f5f5ff", "#f7f5fc", "#f0f0ff"]
        cmap = LinearSegmentedColormap.from_list("qt_gradient", colors)
        bg_ax = fig.add_axes([0, 0, 1, 1], zorder=0)
        bg_ax.axis("off")

        bg_ax.imshow(
            self.gradient,
            aspect="auto",
            cmap=cmap,
            origin="lower",
            extent=[0, 1, 0, 1],
            transform=bg_ax.transAxes,
        )

        ax.imshow(
            self.gradient,
            aspect="auto",
            cmap=cmap,
            origin="lower",
            extent=[*ax.get_xlim(), *ax.get_ylim()],
            zorder=0,
        )
        ax.set_facecolor((0, 0, 0, 0))
        ax.set_zorder(1)

    def get_usable_graph_params(self):
        graph_func = self.available_graphs.get(self.graph_type)[0]
        graph_kwargs = self.available_graphs.get(self.graph_type)[1]
        if graph_func is None:
            return {}

        seaborn_parameters = inspect.signature(graph_func)
        matplotlib_parameters = inspect.signature(graph_kwargs)

        seaborn_parameters = list(seaborn_parameters.parameters.keys())
        matplotlib_parameters = list(matplotlib_parameters.parameters.keys())

        valid_params = set(seaborn_parameters + matplotlib_parameters)

        graph_parameters_copy = self.graph_parameters.copy()
        graph_parameters_copy.update(self.current_graph_parameters.get("seaborn_legends"))

        graph_parameters = {
            k: v for k, v in graph_parameters_copy.items() if k in valid_params
        }

        return graph_parameters

    def convert_hue(self):
        hue_argument = self.graph_parameters.get("hue",None)
        if hue_argument is not None and isinstance(hue_argument, str) and "self.dataset" in hue_argument:
            hue_argument = hue_argument.replace("self.dataset['", "").replace("']", "")
            hue_argument = hue_argument.replace('self.dataset["', "").replace('"]', "")
            hue_argument = self.dataset.eval(hue_argument)
            if self.hue_mapping is not None:
                hue_argument = hue_argument.map(self.hue_mapping)
            self.graph_parameters["hue"] = hue_argument

    def set_legend(self, graph):
        graph_legend_parameter_copy = self.legend_parameters.copy()
        graph_label = graph_legend_parameter_copy.pop("label")
        legend_visibility = graph_legend_parameter_copy.pop("visible")

        legend = graph.get_legend()

        if not legend_visibility:
            legend.set_visible(False)
            return

        # If legend exists, remove it so we can recreate with parameters
        if legend is not None:
            legend.remove()

        # Assign label to artists if needed (matplotlib-only case)
        if graph_label and not graph_label.startswith("_"):
            for artist in graph.lines + graph.collections:
                artist.set_label(graph_label)

        # Recreate legend with your parameters
        legend = graph.legend(**graph_legend_parameter_copy)
        legend.set_visible(True)
        legend.set_label(graph_label)

    def set_seaborn_legend(self, graph):
        graph_legend_parameter_copy = self.legend_parameters.copy()
        graph_label = graph_legend_parameter_copy.pop("label")
        legend_visibility = graph_legend_parameter_copy.pop("visible")

        legend = graph.get_legend()

        if not legend_visibility:
            legend.set_visible(False)
            return

        if legend is not None:
            legend.remove()

        if graph_legend_parameter_copy["title"] is None and legend is not None:
            graph_legend_parameter_copy["title"] = legend.get_title().get_text()

        handles, labels = graph.get_legend_handles_labels()

        legend = graph.legend(handles, labels, **graph_legend_parameter_copy)
        legend.set_visible(True)
        legend.set_label(graph_label)

    def create_graph(self):
        self.prepare_plotting()

        if self.x_axis is None or self.y_axis is None:
            return None

        self.convert_hue()

        #usable_graph_parameters = self.get_usable_graph_params()

        widget = QWidget()
        widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        # make the matplotlib figure
        graph = self.available_graphs.get(self.graph_type)[0](**self.graph_parameters)

        fig = graph.get_figure()
        self.apply_gradient_background(fig, graph)

        if not graph.has_data():
            graph.set_xlim(0, 10)
            graph.set_ylim(0, 10)

        if self.x_axis_title_parameter != "":
            graph.set_xlabel(self.x_axis_title)
        if self.y_axis_title_parameter != "":
            graph.set_ylabel(self.y_axis_title)
        if self.title_parameter != "":
            graph.set_title(self.graph_title)
        if self.grid_parameter != "":
            if self.graph_grid_parameter["visible"]:
                graph.grid(
                    **{
                        k: v
                        for k, v in self.graph_grid_parameter.items()
                        if v is not None and v != [None, None]
                    }
                )
            else:
                graph.grid(False)

        if (self.legend_parameters != ""):
            graph_label = self.legend_parameters["label"]
            legend_visibility = self.legend_parameters["visible"]
            if (
                self.new_plot_config.get("hue",None) is None
                and self.new_plot_config.get("style",None) is None
                and self.new_plot_config.get("size",None) is None
            ):
                if not legend_visibility and graph_label != "__nolegend__":
                    self.set_legend(graph)
            else:
                self.set_seaborn_legend(graph)

        fig = graph.get_figure()
        buf = BytesIO()
        fig.savefig(buf, format="png")
        buf.seek(0)
        plt.close(fig)

        # Draw the pixmap with the round corners
        image = QImage.fromData(buf.getvalue())
        pixmap = QPixmap.fromImage(image)
        mask = QPixmap(pixmap.size())
        mask.fill(Qt.GlobalColor.transparent)

        painter = QPainter(mask)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        path = QPainterPath()
        path.addRoundedRect(0, 0, pixmap.width(), pixmap.height(), 20, 20)
        painter.fillPath(path, Qt.GlobalColor.white)
        painter.end()

        pixmap.setMask(mask.createMaskFromColor(Qt.GlobalColor.transparent))

        # check the QImage conversion
        label = QLabel()
        label.setObjectName("image_label")
        label.setStyleSheet("""
            QLabel#image_label {
                border-radius: 16px;
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #f5f5ff,
                    stop:0.5 #f7f5fc,
                    stop:1 #f0f0ff
                );
                padding: 0px;
            }
        """)
        label.setScaledContents(True)
        label.setPixmap(pixmap)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        image_layout = QVBoxLayout(widget)
        image_layout.addWidget(label)
        image_layout.setContentsMargins(0, 0, 0, 0)
        image_layout.setSpacing(0)

        return widget


class new_graph_button(QPushButton):
    def __init__(self):
        super().__init__()

        self.setStyleSheet("""
            background: qlineargradient(
                x1:0, y1:1,
                x2:0, y2:0,
                stop:0.02 rgba(131, 125, 255, 1),
                stop:0.36 rgba(97, 97, 255, 1),
                stop:0.66 rgba(31, 162, 255, 1),
                stop:1 rgba(0, 212, 255, 1)
            );
            color: #c8f7ff;
        """)

        # Create a new label with the text New Graph and format it
        self.label = QLabel("New Graph")
        self.label.setWordWrap(True)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setStyleSheet("""
            font-family: "SF Pro Display";
            font-weight: 600;
            border-radius: 16px;
        """)
        self.label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

        # Control the size of the button and the label to ensure they fit together
        self.setMinimumHeight(35)
        self.label.setMinimumHeight(25)

        # Add the text onto the button and format it in order for it to fit
        layout = QVBoxLayout(self)
        layout.addWidget(self.label)
        layout.setContentsMargins(5, 0, 5, 0)


class undo_button(QPushButton):
    def __init__(self):
        super().__init__()

        self.setStyleSheet("""
            background: qlineargradient(
                x1:0, y1:1,
                x2:0, y2:0,
                stop:0.02 rgba(131, 125, 255, 1),
                stop:0.36 rgba(97, 97, 255, 1),
                stop:0.66 rgba(31, 162, 255, 1),
                stop:1 rgba(0, 212, 255, 1)
            );
            color: #c8f7ff;
            
        """)

        # Create a new label with the text Undo and format it
        self.label = QLabel("Undo")
        self.label.setWordWrap(True)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setStyleSheet("""
            font-family: "SF Pro Display";
            font-weight: 600;
            border-radius: 16px;
        """)
        self.label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

        # Control the size of the button and the label to ensure they fit together
        self.setMinimumHeight(35)
        self.label.setMinimumHeight(25)

        # Add the text onto the button and format it in order for it to fit
        layout = QVBoxLayout(self)
        layout.addWidget(self.label)
        layout.setContentsMargins(5, 0, 5, 0)


class clear_button(QPushButton):
    def __init__(self):
        super().__init__()

        self.setStyleSheet("""
            background: qlineargradient(
                x1:0, y1:1,
                x2:0, y2:0,
                stop:0.02 rgba(131, 125, 255, 1),
                stop:0.36 rgba(97, 97, 255, 1),
                stop:0.66 rgba(31, 162, 255, 1),
                stop:1 rgba(0, 212, 255, 1)
            );
            color: #c8f7ff;
            
        """)

        # Create a new label with the text Clear and format it
        self.label = QLabel("Clear")
        self.label.setWordWrap(True)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setStyleSheet("""
            font-family: "SF Pro Display";
            font-weight: 600;
            border-radius: 16px;
        """)
        self.label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

        # Control the size of the button and the label to ensure they fit together
        self.setMinimumHeight(35)
        self.label.setMinimumHeight(25)

        # Add the text onto the button and format it in order for it to fit
        layout = QVBoxLayout(self)
        layout.addWidget(self.label)
        layout.setContentsMargins(5, 0, 5, 0)


class previous_graph_button(QPushButton):
    def __init__(self):
        super().__init__()

        self.setStyleSheet("""
            background: qlineargradient(
                x1:0, y1:1,
                x2:0, y2:0,
                stop:0.02 rgba(131, 125, 255, 1),
                stop:0.36 rgba(97, 97, 255, 1),
                stop:0.66 rgba(31, 162, 255, 1),
                stop:1 rgba(0, 212, 255, 1)
            );
            color: #c8f7ff;
            
        """)

        # Create a new label with the text Previous Graph and format it
        self.label = QLabel("Previous Graph")
        self.label.setWordWrap(True)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setStyleSheet("""
            font-family: "SF Pro Display";
            font-weight: 600;
            border-radius: 16px;
        """)
        self.label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

        # Control the size of the button and the label to ensure they fit together
        self.setMinimumHeight(35)
        self.label.setMinimumHeight(25)

        # Add the text onto the button and format it in order for it to fit
        layout = QVBoxLayout(self)
        layout.addWidget(self.label)
        layout.setContentsMargins(5, 0, 5, 0)


class zoom_in_button(QPushButton):
    def __init__(self):
        super().__init__()

        self.setStyleSheet("""
            background: qlineargradient(
                x1:0, y1:1,
                x2:0, y2:0,
                stop:0.02 rgba(131, 125, 255, 1),
                stop:0.36 rgba(97, 97, 255, 1),
                stop:0.66 rgba(31, 162, 255, 1),
                stop:1 rgba(0, 212, 255, 1)
            );
            color: #c8f7ff;
            
        """)

        # Create a new label with the text Zoom In and format it
        self.label = QLabel("Zoom In")
        self.label.setWordWrap(True)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setStyleSheet("""
            font-family: "SF Pro Display";
            font-weight: 600;
            border-radius: 16px;
        """)
        self.label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

        # Control the size of the button and the label to ensure they fit together
        self.setMinimumHeight(35)
        self.label.setMinimumHeight(25)

        # Add the text onto the button and format it in order for it to fit
        layout = QVBoxLayout(self)
        layout.addWidget(self.label)
        layout.setContentsMargins(5, 0, 5, 0)


class zoom_out_button(QPushButton):
    def __init__(self):
        super().__init__()

        self.setStyleSheet("""
            background: qlineargradient(
                x1:0, y1:1,
                x2:0, y2:0,
                stop:0.02 rgba(131, 125, 255, 1),
                stop:0.36 rgba(97, 97, 255, 1),
                stop:0.66 rgba(31, 162, 255, 1),
                stop:1 rgba(0, 212, 255, 1)
            );
            color: #c8f7ff;
            
        """)

        # Create a new label with the text Zoom Out and format it
        self.label = QLabel("Zoom Out")
        self.label.setWordWrap(True)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setStyleSheet("""
            font-family: "SF Pro Display";
            font-weight: 600;
            border-radius: 16px;
        """)
        self.label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

        # Control the size of the button and the label to ensure they fit together
        self.setMinimumHeight(35)
        self.label.setMinimumHeight(25)

        # Add the text onto the button and format it in order for it to fit
        layout = QVBoxLayout(self)
        layout.addWidget(self.label)
        layout.setContentsMargins(5, 0, 5, 0)


class copy_code_button(QPushButton):
    def __init__(self):
        super().__init__()

        self.setStyleSheet("""
            background: qlineargradient(
                x1:0, y1:1,
                x2:0, y2:0,
                stop:0.02 rgba(131, 125, 255, 1),
                stop:0.36 rgba(97, 97, 255, 1),
                stop:0.66 rgba(31, 162, 255, 1),
                stop:1 rgba(0, 212, 255, 1)
            );
            color: #c8f7ff;
            
        """)

        # Create a new label with the text Copy Code and format it
        self.label = QLabel("Copy Code")
        self.label.setWordWrap(True)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setStyleSheet("""
            font-family: "SF Pro Display";
            font-weight: 600;
            border-radius: 16px;
        """)
        self.label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

        # Control the size of the button and the label to ensure they fit together
        self.setMinimumHeight(35)
        self.label.setMinimumHeight(25)

        # Add the text onto the button and format it in order for it to fit
        layout = QVBoxLayout(self)
        layout.addWidget(self.label)
        layout.setContentsMargins(5, 0, 5, 0)


class export_graph_button(QPushButton):
    def __init__(self):
        super().__init__()

        self.setStyleSheet("""
            background: qlineargradient(
                x1:0, y1:1,
                x2:0, y2:0,
                stop:0.02 rgba(131, 125, 255, 1),
                stop:0.36 rgba(97, 97, 255, 1),
                stop:0.66 rgba(31, 162, 255, 1),
                stop:1 rgba(0, 212, 255, 1)
            );
            color: #c8f7ff;
            
        """)

        # Create a new label with the text Export Graph and format it
        self.label = QLabel("Export Graph")
        self.label.setWordWrap(True)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setStyleSheet("""
            font-family: "SF Pro Display";
            font-weight: 600;
            border-radius: 16px;
        """)
        self.label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

        # Control the size of the button and the label to ensure they fit together
        self.setMinimumHeight(35)
        self.label.setMinimumHeight(25)

        # Add the text onto the button and format it in order for it to fit
        layout = QVBoxLayout(self)
        layout.addWidget(self.label)
        layout.setContentsMargins(5, 0, 5, 0)


class Graph_TopBar(QWidget):
    def __init__(self):
        super().__init__()

        # Put all the buttons together in a horizontal box and format
        layout = QHBoxLayout()
        layout.addWidget(new_graph_button(), stretch=1)
        layout.addWidget(undo_button(), stretch=1)
        layout.addWidget(clear_button(), stretch=1)
        layout.addWidget(previous_graph_button(), stretch=1)
        layout.addWidget(zoom_in_button(), stretch=1)
        layout.addWidget(zoom_out_button(), stretch=1)
        layout.addWidget(copy_code_button(), stretch=1)
        layout.addWidget(export_graph_button(), stretch=1)

        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)

        # Control the size of the box and apply the layout to the Top Bar
        self.setFixedHeight(50)
        self.setFixedWidth(620)
        self.setLayout(layout)

        self.setObjectName("graph_topbar")

        # Format the Top bar and the buttons on it
        self.setStyleSheet("""
            QWidget#graph_topbar{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #f5f5ff,
                    stop:0.5 #f7f5fc,
                    stop:1 #f0f0ff
                );
                border: 2px solid #c0c0ff;
                border-radius: 24px;
            }
            QPushButton{
                border-radius: 16px;
                padding: 2px; 
            }
        """)

        # Ensure the everything is properly drawn on the main window
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)


class Graph_Display(QWidget):
    def __init__(self):
        super().__init__()
        self.setObjectName("graph_display_main_screen")
        self.setStyleSheet("""
            QWidget#graph_display_main_screen{
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

        self.setFixedWidth(620)

        self.graph_generator = graph_generator()

        self.graph_widget = QWidget()
        self.graph_widget.setObjectName("graph_widget")
        self.graph_widget.setStyleSheet("""
            QWidget{
                background: transparent;
                border-radius: 24px;
            }
        """)

        # This layout is correct
        self.graph_display_layout = QStackedLayout(self)
        self.graph_display_layout.setContentsMargins(0, 0, 0, 0)
        self.graph_display_layout.setSpacing(0)

        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

    def show_graph(self):
        try:
            graph_widget = self.graph_generator.create_graph()
            if graph_widget is not None:
                self.graph_display_layout.addWidget(graph_widget)
                self.graph_display_layout.setCurrentWidget(graph_widget)
        except Exception as error:
            print(error)


class Graph_Section(QWidget):
    def __init__(self):
        super().__init__()
        self.setFixedWidth(620)

        self.graph_topbar = Graph_TopBar()
        self.display_graph = Graph_Display()

        layout = QVBoxLayout(self)
        layout.addWidget(self.graph_topbar)
        layout.addSpacing(5)
        layout.addWidget(self.display_graph)
        layout.setContentsMargins(0, 0, 0, 0)

        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
