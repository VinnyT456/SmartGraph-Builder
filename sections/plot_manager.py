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
        return self.db.all()[-1]

    def insert_x_axis_data(self, plot_data):
        if (self.db.all() != [] and self.db.all()[-1]["y-axis"] != ""):
            self.db.truncate()
        self.db.insert(plot_data)

    def insert_y_axis_data(self, plot_data):
        if (self.db.all() != [] and self.db.all()[-1]["x-axis"] != ""):
            self.db.truncate()
        self.db.insert(plot_data)

    def check_x_axis_title(self,title):
        current_title = self.db.all()[-1]["axis title"]
        current_title[0] = title
        self.db.update({"axis title":current_title},Query().version == self.current_version)

    def check_y_axis_title(self,title):
        current_title = self.db.all()[-1]["axis title"]
        current_title[1] = title
        self.db.update({"axis title":current_title},Query().version == self.current_version)

    def insert_plot_parameter(self, plot_data):
        plot_copy = plot_data.copy()
        plot_copy["version"] = self.current_version + 1
        self.db.insert(plot_copy)