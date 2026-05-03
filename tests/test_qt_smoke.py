from PyQt6.QtWidgets import QWidget


def test_qt_can_create_widget(qapp):
    """
    Minimal Qt smoke test.

    This ensures the GitHub Actions xvfb + pytest-qt setup is working and that
    PyQt6 can create widgets in a headless environment.
    """

    w = QWidget()
    w.setObjectName("qt_smoke_widget")
    assert w.objectName() == "qt_smoke_widget"
