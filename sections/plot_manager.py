from tinydb import TinyDB, Query

class PlotManager:
    def __init__(self, db_path="plot_config.json"):
        self.db = TinyDB(db_path)

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

    def insert_x_axis_data(self, plot_data):
        if (self.db.all() != [] and self.db.all()[-1]["y-axis"] != ""):
            self.db.truncate()
        self.db.insert(plot_data)

    def insert_y_axis_data(self, plot_data):
        if (self.db.all() != [] and self.db.all()[-1]["x-axis"] != ""):
            self.db.truncate()
        self.db.insert(plot_data)

    def update_x_axis_title(self,title):
        current_title = self.db.all()[-1]["axis title"]
        current_title["x-axis"] = title
        self.db.update({"axis title":current_title},Query().version == self.current_version)

    def update_y_axis_title(self,title):
        current_title = self.db.all()[-1]["axis title"]
        current_title["y-axis"] = title
        self.db.update({"axis title":current_title},Query().version == self.current_version)

    def update_title(self,title):
        self.db.update({"title":title},Query().version == self.current_version)

    def update_legend_loc(self,new_position):
        self.db.update(lambda db: db["legend"].update({"loc": new_position}) or db,Query().version == self.current_version)

    def update_legend_bbox_anchor(self,new_bbox_anchor):
        self.db.update(lambda db: db["legend"].update({"bbox_to_anchor":new_bbox_anchor}) or db,Query().version == self.current_version)
    
    def update_legend_ncol(self,new_ncol):
        self.db.update(lambda db: db["legend"].update({"ncol":new_ncol}) or db,Query().version == self.current_version)

    def insert_plot_parameter(self, plot_data):
        plot_copy = plot_data.copy()
        plot_copy["version"] = self.current_version + 1
        self.db.insert(plot_copy)