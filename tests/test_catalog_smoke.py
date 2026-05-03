from sections.graph_parameter import SEABORN_PLOTS


def test_seaborn_plots_catalog_has_scatter_plot():
    # The catalog is the UI's source of truth for "what plot types exist".
    assert "Scatter Plot" in SEABORN_PLOTS

    scatter = SEABORN_PLOTS["Scatter Plot"]
    assert isinstance(scatter.get("parameters"), list)
    assert "x-axis" in scatter["parameters"]
    assert "y-axis" in scatter["parameters"]


def test_catalog_entries_are_well_formed():
    # Avoid checking that every thumbnail exists on disk (many are not committed yet).
    # Instead, validate that the catalog structure is consistent.
    for name, spec in SEABORN_PLOTS.items():
        assert isinstance(name, str) and name
        assert isinstance(spec, dict)

        # Every plot should declare a parameters list (even if incomplete).
        params = spec.get("parameters")
        assert isinstance(params, list), f"{name}: expected list 'parameters'"
        assert len(params) > 0, f"{name}: expected non-empty 'parameters'"

        # If an image field is present, it should be a png path string.
        image = spec.get("Image")
        assert isinstance(image, str) and image.endswith(".png"), f"{name}: bad Image"
