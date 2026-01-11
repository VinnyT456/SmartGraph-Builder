from PyQt6.QtCore import QUrl
from tinydb import TinyDB, Query

class PlotManager:
    def __init__(self, db_path="plot_config.json"):
        self.db = TinyDB(db_path)
        self.graphs = ["Scatter Plot","Line Plot","Regression Plot","Bar Plot",
                       "Count Plot","Box Plot","Violin Plot","Swarm Plot",
                       "Strip Plot","Histogram","KDE Plot","ECDF Plot","Rug Plot",
                       "Heatmap","Pair Plot","Joint Plot","Cluster Map"]

    @property
    def current_version(self):
        records = self.db.all()
        if not records:
            return 1
        return records[-1]["version"]

    def get_db(self):
        if (self.db.all() != []):
            return self.db.all()[-1]
        return []

    def get_specific_db(self,graph):
        return self.db.all()[self.graphs.index(graph)]

    def insert_x_axis_data(self, plot_data):
        if (self.db.all() != [] and self.db.all()[-1]["y"] != ""):
            self.db.truncate()
        self.db.insert(plot_data)

    def insert_y_axis_data(self, plot_data):
        if (self.db.all() != [] and self.db.all()[-1]["x"] != ""):
            self.db.truncate()
        self.db.insert(plot_data)

    def update_x_axis_title(self,title):
        current_title = self.db.all()[-1]["axis-title"]
        current_title["x-axis-title"] = title
        self.db.update({"axis-title":current_title},Query().version == self.current_version)

    def update_y_axis_title(self,title):
        current_title = self.db.all()[-1]["axis-title"]
        current_title["y-axis-title"] = title
        self.db.update({"axis-title":current_title},Query().version == self.current_version)

    def update_title(self,title):
        self.db.update({"title":title},Query().version == self.current_version)

    def update_legend(self,parameter,new_value):
        self.db.update(lambda db: db["legend"].update({parameter:new_value}) or db,Query().version == self.current_version)

    def update_seaborn_legend(self,parameter,new_value):
        self.db.update(lambda db: db["legend"]["seaborn_legends"].update({parameter:new_value}) or db, Query().version == self.current_version)

    def update_grid(self,parameter,new_value):
        self.db.update(lambda db: db["grid"].update({parameter:new_value}) or db, Query().version == self.current_version)

    def update_hue(self,hue):
        self.db.update({"hue":hue},Query().version == self.current_version)

    def update_style(self,style):
        self.db.update({"style":style},Query().version == self.current_version)

    def update_size(self,size):
        self.db.update({"size":size},Query().version == self.current_version)

    def update_sizes(self,sizes):
        self.db.update({"sizes":sizes},Query().version == self.current_version)

    def update_palette(self,palette):
        self.db.update({"palette":palette},Query().version == self.current_version)

    def update_alpha(self,alpha):
        self.db.update({"alpha":alpha},Query().version == self.current_version)

    def update_marker(self,marker):
        self.db.update({"marker":marker},Query().version == self.current_version)

    def update_s(self,s):
        self.db.update({"s":s},Query().version == self.current_version)

    def update_edgecolors(self,edgecolors):
        self.db.update({"edgecolors":edgecolors},Query().version == self.current_version)

    def insert_plot_parameter(self, plot_data):
        plot_copy = plot_data.copy()
        plot_copy["version"] = self.current_version + 1
        plot_copy.pop('_id', None)
        self.db.insert(plot_copy)
        