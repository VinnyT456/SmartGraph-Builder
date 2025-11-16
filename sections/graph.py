import copy
import inspect
from io import BytesIO
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QImage, QPainter, QPainterPath, QPixmap
from PyQt6.QtWidgets import (
    QHBoxLayout, QLabel, QPushButton, QSizePolicy, QStackedLayout, QWidget, QVBoxLayout
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

        with open('default_plot_config.json', 'r') as file:
            self.default_graph_parameters = json.load(file)

        self.xkcd_colors = list(mcolors.XKCD_COLORS.keys())
        self.tab_colors = list(mcolors.TABLEAU_COLORS.keys())

        self.xkcd_colors = [c.replace("xkcd:","") for c in self.xkcd_colors]
        self.tab_colors = [c.replace("tab:","") for c in self.tab_colors]

    def prepare_plotting(self):
        self.current_graph_parameters = copy.deepcopy(self.plot_manager.get_db())
        self.default_config_plot_manager = PlotManager("./default_plot_config.json")

        self.dataset = pd.read_csv(self.current_graph_parameters.get("data"))

        self.graph_type = self.current_graph_parameters["type"]
        self.available_graphs = {
            "Scatter Plot":sns.scatterplot
        }

        self.graph_axis_titles = self.current_graph_parameters.get("axis-title")
        self.x_axis_title = self.graph_axis_titles["x-axis-title"]
        self.y_axis_title = self.graph_axis_titles["y-axis-title"]

        self.graph_title = self.current_graph_parameters.get("title")
        self.graph_grid_parameter = self.current_graph_parameters.get("grid")

        self.graph_legend_parameters = self.current_graph_parameters.get("legend")
        self.graph_seaborn_legend_parameters = self.graph_legend_parameters["seaborn_legends"]
        self.graph_legend_parameters.pop("seaborn_legends",None)

        self.default_graph_legend_parameters = self.default_graph_parameters[self.graph_type].get("legend")
        self.default_graph_legend_parameters.pop("seaborn_legends",None)
        self.default_graph_legend_parameters.pop("visible",None)
        self.default_graph_legend_parameters.pop("label",None)

        for key in ["legend","version","type","grid","axis-title","title"]:
            self.current_graph_parameters.pop(key,None)

        self.graph_parameters = self.current_graph_parameters.copy()
        self.graph_parameters["data"] = self.dataset

        self.x_axis = self.current_graph_parameters.get("x")
        self.y_axis = self.current_graph_parameters.get("y")

    def apply_gradient_background(self, fig, ax):
        colors = ["#f5f5ff", "#f7f5fc", "#f0f0ff"] 
        cmap = LinearSegmentedColormap.from_list("qt_gradient", colors)
        bg_ax = fig.add_axes([0, 0, 1, 1], zorder=0)
        bg_ax.axis("off")  

        bg_ax.imshow(
            self.gradient,
            aspect='auto',
            cmap=cmap,
            origin='lower',
            extent=[0, 1, 0, 1],
            transform=bg_ax.transAxes
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
        graph_func = self.available_graphs.get(self.graph_type)
        if graph_func is None:
            return {}

        sig = inspect.signature(graph_func)
        valid_params = set(sig.parameters.keys())

        graph_params = {
            k: v for k, v in {**self.graph_parameters, **self.graph_seaborn_legend_parameters}.items()
            if k in valid_params
        }

        return graph_params

    def convert_hue(self):
        hue_argument = self.graph_parameters["hue"]
        if (isinstance(hue_argument,str) and "self.dataset" in hue_argument):
            hue_argument = hue_argument.replace("self.dataset['","").replace("']","")
            hue_argument = hue_argument.replace('self.dataset["',"").replace('"]',"")
            hue_argument = self.dataset.eval(hue_argument)
            self.graph_parameters["hue"] = hue_argument

    def convert_color(self):
        facecolor_argument = self.graph_legend_parameters["facecolor"]
        edgecolor_argument = self.graph_legend_parameters["edgecolor"]
        labelcolor_argument = self.graph_legend_parameters["labelcolor"]
        grid_color_argument = self.graph_grid_parameter["color"]

        if (facecolor_argument in self.xkcd_colors):
            facecolor_argument = "xkcd:" + facecolor_argument
        elif (facecolor_argument in self.tab_colors):
            facecolor_argument = "tab:" + facecolor_argument

        if (edgecolor_argument in self.xkcd_colors):
            edgecolor_argument = "xkcd:" + edgecolor_argument
        elif (edgecolor_argument in self.tab_colors):
            edgecolor_argument = "tab:" + edgecolor_argument

        if (labelcolor_argument in self.xkcd_colors):
            labelcolor_argument = "xkcd:" + labelcolor_argument
        elif (labelcolor_argument in self.tab_colors):
            labelcolor_argument = "tab:" + labelcolor_argument

        if (grid_color_argument in self.xkcd_colors):
            grid_color_argument = "xkcd:" + grid_color_argument
        elif (grid_color_argument in self.tab_colors):
            grid_color_argument = "tab:" + grid_color_argument

        self.graph_legend_parameters["facecolor"] = facecolor_argument
        self.graph_legend_parameters["edgecolor"] = edgecolor_argument
        self.graph_legend_parameters["labelcolor"] = labelcolor_argument
        self.graph_grid_parameter["color"] = grid_color_argument

    def set_legend(self,graph,legend_visibility,graph_label):
        if (legend_visibility and not graph_label.startswith("_")):
            if graph.legend_:
                graph.legend_.remove()
            for artist in graph.get_children():
                try:
                    artist.set_label(graph_label)
                except:
                    pass
            legend = graph.legend(**self.graph_legend_parameters)
            legend.set_visible(legend_visibility)
        else:
            legend = None

    def set_hue_legend(self,legend):
        legend_parameters = {
            "loc": lambda val: legend.set_loc(val),
            "bbox_to_anchor": lambda val: legend.set_bbox_to_anchor(val),
            "ncol": lambda val: setattr(legend, "_ncol", val),  # internal, but works
            "fontsize": lambda val: [text.set_fontsize(val) for text in legend.get_texts()],
            "title": lambda val: legend.set_title(val),
            "title_fontsize": lambda val: legend.get_title().set_fontsize(val),
            "frameon": lambda val: legend.set_frame_on(val),
            "facecolor": lambda val: legend.get_frame().set_facecolor(val),
            "edgecolor": lambda val: legend.get_frame().set_edgecolor(val),
            "framealpha": lambda val: legend.get_frame().set_alpha(val),
            "shadow": lambda val: legend.set_shadow(val),
            "fancybox": lambda val: legend.get_frame().set_boxstyle("round" if val else "square"),
            "borderpad": lambda val: legend.get_frame().set_boxstyle(f"round,pad={val}"),
            "labelcolor": lambda val: [text.set_color(val) for text in legend.get_texts()],
            "alignment": lambda val: setattr(legend._legend_box, "align", val),
            "columnspacing": lambda val: setattr(legend._legend_box, "sep", val),
            "handletextpad": lambda val: setattr(legend._legend_handle_box, "sep", val),
            "borderaxespad": lambda val: legend.get_frame().set_pad(val),
            "handlelength": lambda val: [handle.set_markersize(val) for handle in legend.legendHandles],
            "handleheight": lambda val: None,
            "markerfirst": lambda val: setattr(legend._legend_handle_box, "markerfirst", val)
        }

        for (parameter,value),default_value in zip(self.graph_legend_parameters.items(),self.default_graph_legend_parameters.values()):
            try:
                if (value != default_value):
                    legend_parameters[parameter](value)
            except:
                continue

    def create_graph(self):
        self.prepare_plotting()

        if (self.x_axis == None or self.y_axis == None):
            return None

        self.convert_hue()
        self.convert_color()

        usable_graph_parameters = self.get_usable_graph_params()

        widget = QWidget()
        widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        # make the matplotlib figure
        graph = self.available_graphs.get(self.graph_type)(**usable_graph_parameters)

        fig = graph.get_figure()
        self.apply_gradient_background(fig, graph)

        if not graph.has_data():
            graph.set_xlim(0, 10)
            graph.set_ylim(0, 10)

        if (self.x_axis_title != ""):
            graph.set_xlabel(self.x_axis_title)
        if (self.y_axis_title != ""):
            graph.set_ylabel(self.y_axis_title)
        if (self.graph_title != ""):
            graph.set_title(self.graph_title)
        if (self.graph_grid_parameter["visible"] is not None):
            if (self.graph_grid_parameter["visible"]):
                graph.grid(**{k: v for k, v in self.graph_grid_parameter.items() if v is not None and v != [None,None]})
            else:
                graph.grid(False)
        
        graph_label = self.graph_legend_parameters.pop("label")
        legend_visibility = self.graph_legend_parameters.pop("visible")
        if (legend_visibility == True and not graph_label.startswith("_") and self.graph_parameters["hue"] == None):
            self.set_legend(graph,legend_visibility,graph_label)
        elif (self.graph_parameters["hue"] is not None):
            self.set_hue_legend(graph.legend_)

        fig = graph.get_figure()
        buf = BytesIO()
        fig.savefig(buf, format="png")
        buf.seek(0)
        plt.close(fig)

        #Draw the pixmap with the round corners
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
        image_layout.setContentsMargins(0,0,0,0)
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

        #Create a new label with the text New Graph and format it
        self.label = QLabel("New Graph")
        self.label.setWordWrap(True)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setStyleSheet("""
            font-family: "SF Pro Display";
            font-weight: 600;
            border-radius: 16px;
        """) 
        self.label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

        #Control the size of the button and the label to ensure they fit together
        self.setMinimumHeight(35)
        self.label.setMinimumHeight(25)

        #Add the text onto the button and format it in order for it to fit
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

        #Create a new label with the text Undo and format it
        self.label = QLabel("Undo")
        self.label.setWordWrap(True)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setStyleSheet("""
            font-family: "SF Pro Display";
            font-weight: 600;
            border-radius: 16px;
        """) 
        self.label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

        #Control the size of the button and the label to ensure they fit together
        self.setMinimumHeight(35)
        self.label.setMinimumHeight(25)

        #Add the text onto the button and format it in order for it to fit
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

        #Create a new label with the text Clear and format it
        self.label = QLabel("Clear")
        self.label.setWordWrap(True)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setStyleSheet("""
            font-family: "SF Pro Display";
            font-weight: 600;
            border-radius: 16px;
        """) 
        self.label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

        #Control the size of the button and the label to ensure they fit together
        self.setMinimumHeight(35)
        self.label.setMinimumHeight(25)

        #Add the text onto the button and format it in order for it to fit
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

        #Create a new label with the text Previous Graph and format it
        self.label = QLabel("Previous Graph")
        self.label.setWordWrap(True)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setStyleSheet("""
            font-family: "SF Pro Display";
            font-weight: 600;
            border-radius: 16px;
        """) 
        self.label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

        #Control the size of the button and the label to ensure they fit together
        self.setMinimumHeight(35)
        self.label.setMinimumHeight(25)

        #Add the text onto the button and format it in order for it to fit
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

        #Create a new label with the text Zoom In and format it
        self.label = QLabel("Zoom In")
        self.label.setWordWrap(True)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setStyleSheet("""
            font-family: "SF Pro Display";
            font-weight: 600;
            border-radius: 16px;
        """) 
        self.label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

        #Control the size of the button and the label to ensure they fit together
        self.setMinimumHeight(35)
        self.label.setMinimumHeight(25)

        #Add the text onto the button and format it in order for it to fit
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

        #Create a new label with the text Zoom Out and format it
        self.label = QLabel("Zoom Out")
        self.label.setWordWrap(True)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setStyleSheet("""
            font-family: "SF Pro Display";
            font-weight: 600;
            border-radius: 16px;
        """) 
        self.label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

        #Control the size of the button and the label to ensure they fit together
        self.setMinimumHeight(35)
        self.label.setMinimumHeight(25)

        #Add the text onto the button and format it in order for it to fit
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

        #Create a new label with the text Copy Code and format it
        self.label = QLabel("Copy Code")
        self.label.setWordWrap(True)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setStyleSheet("""
            font-family: "SF Pro Display";
            font-weight: 600;
            border-radius: 16px;
        """) 
        self.label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

        #Control the size of the button and the label to ensure they fit together
        self.setMinimumHeight(35)
        self.label.setMinimumHeight(25)

        #Add the text onto the button and format it in order for it to fit
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

        #Create a new label with the text Export Graph and format it
        self.label = QLabel("Export Graph")
        self.label.setWordWrap(True)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setStyleSheet("""
            font-family: "SF Pro Display";
            font-weight: 600;
            border-radius: 16px;
        """) 
        self.label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

        #Control the size of the button and the label to ensure they fit together
        self.setMinimumHeight(35)
        self.label.setMinimumHeight(25)

        #Add the text onto the button and format it in order for it to fit
        layout = QVBoxLayout(self)
        layout.addWidget(self.label)
        layout.setContentsMargins(5, 0, 5, 0)  

class Graph_TopBar(QWidget):
    def __init__(self):
        super().__init__()
        
        #Put all the buttons together in a horizontal box and format
        layout = QHBoxLayout()
        layout.addWidget(new_graph_button(),stretch=1)
        layout.addWidget(undo_button(),stretch=1)
        layout.addWidget(clear_button(),stretch=1)
        layout.addWidget(previous_graph_button(),stretch=1)
        layout.addWidget(zoom_in_button(),stretch=1)
        layout.addWidget(zoom_out_button(),stretch=1)
        layout.addWidget(copy_code_button(),stretch=1)
        layout.addWidget(export_graph_button(),stretch=1)
        
        layout.setContentsMargins(5,5,5,5) 
        layout.setSpacing(5)

        #Control the size of the box and apply the layout to the Top Bar
        self.setFixedHeight(50)
        self.setFixedWidth(620)
        self.setLayout(layout)

        self.setObjectName("graph_topbar")

        #Format the Top bar and the buttons on it
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

        #Ensure the everything is properly drawn on the main window
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
        self.graph_display_layout.setContentsMargins(0,0,0,0)
        self.graph_display_layout.setSpacing(0)

        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

    def show_graph(self):
        try:
            graph_widget = self.graph_generator.create_graph()
            if (graph_widget != None):
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
        layout.setContentsMargins(0,0,0,0) 

        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
