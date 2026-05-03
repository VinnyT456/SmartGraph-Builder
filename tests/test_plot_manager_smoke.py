from sections.plot_manager import PlotManager


def test_plot_manager_empty_db_has_version_1(tmp_path):
    db_path = tmp_path / "plot_config.json"
    pm = PlotManager(db_path=str(db_path))

    assert pm.get_db() == []


def test_plot_manager_can_insert_and_update(tmp_path):
    db_path = tmp_path / "plot_config.json"
    pm = PlotManager(db_path=str(db_path))

    pm.insert_plot_parameter(
        {
            "type": "Scatter Plot",
            "data": "dataset/user_dataset.csv",
            "x": "x",
            "y": "y",
            "axis-title": {"x-axis-title": "", "y-axis-title": ""},
            "title": "",
            "legend": {"label": "", "visible": True, "seaborn_legends": {}},
            "grid": {},
        }
    )

    db = pm.get_db()
    assert isinstance(db, dict)
    assert db["type"] == "Scatter Plot"
