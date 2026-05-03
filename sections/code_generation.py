from PyQt6.QtCore import (
    QEasingCurve,
    QPropertyAnimation,
    QStringListModel,
    QTimer,
    Qt,
)
from PyQt6.QtGui import QAction, QCursor, QFont, QKeySequence, QShortcut
from PyQt6.QtWidgets import (
    QAbstractItemView,
    QApplication,
    QDialog,
    QFileDialog,
    QHBoxLayout,
    QListView,
    QMenu,
    QPushButton,
    QSizePolicy,
    QStyledItemDelegate,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)
from pygments import highlight
from pygments.lexers import PythonLexer
from pygments.formatters import HtmlFormatter
from pygments.styles import get_all_styles
import textwrap


def export_python_code(file_path, python_code):
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(python_code)
    except Exception as e:
        return False
    return True


class Theme_Preview(QWidget):
    def __init__(self, items, on_select, parent=None, current_theme=None):
        super().__init__(parent)

        self.on_select = on_select
        self.current_theme = current_theme

        self.setWindowFlags(Qt.WindowType.Popup | Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        class CustomDelegate(QStyledItemDelegate):
            def paint(self, painter, option, index):
                option.displayAlignment = Qt.AlignmentFlag.AlignCenter
                font = QFont("SF Pro Display", 16)
                font.setWeight(600)
                option.font = font
                super().paint(painter, option, index)

        self.model = QStringListModel(items)
        self.view = QListView()
        self.view.setProperty("class", "menu_list_view")
        self.view.setModel(self.model)
        self.view.setItemDelegate(CustomDelegate())
        self.view.viewport().setMouseTracking(True)
        self.view.viewport().installEventFilter(self)
        self.view.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.view.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.view.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self.view.clicked.connect(self.item_clicked)

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.view)
        self.setLayout(layout)

        self.setFixedSize(150, 400)

    def item_clicked(self, index):
        value = self.model.data(index, Qt.ItemDataRole.DisplayRole)
        self.current_theme = value
        self.on_select(value)
        self.close()

    def eventFilter(self, obj, event):
        if obj == self.view.viewport():
            if event.type() == event.Type.MouseMove:
                index = self.view.indexAt(event.pos())
                if index.isValid():
                    value = self.model.data(index, Qt.ItemDataRole.DisplayRole)
                    self.view.setCurrentIndex(index)
                    self.on_select(value)
        return super().eventFilter(obj, event)

    def showEvent(self, event):
        super().showEvent(event)

        if self.current_theme in self.model.stringList():
            row = self.model.stringList().index(self.current_theme)
            index = self.model.index(row, 0)

            self.view.scrollTo(index, QAbstractItemView.ScrollHint.PositionAtCenter)


class full_screen_code_preview(QDialog):
    def __init__(self, code_section, graph_code=""):
        super().__init__()

        self.setFixedSize(800, 500)
        self.setProperty("class", "dialog_window")
        self.setObjectName("full_screen_code_preview")

        self.setWindowTitle("Full Screen Code Preview")

        self.code_section = code_section
        self.graph_code = graph_code

        self.code_preview_backgrounds = {
            "Light": """
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #f5f5ff,
                    stop:0.5 #f7f5fc,
                    stop:1 #f0f0ff
                );
            """,
            "Dark": """
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #1e1e2f,
                    stop:0.5 #232336,
                    stop:1 #1a1a2b
                );
            """,
        }

        self.style = code_section.style
        self.background = code_section.current_background

        self.code_preview_section_top_bar = QWidget()
        self.create_code_preview_section_top_bar()

        self.code_preview_section = QWidget()
        self.code_preview_section.setProperty("class", "dialog_section")
        self.code_preview_section.setObjectName("code_preview_section")
        self.create_code_preview_section()

        main_layout = QHBoxLayout(self)
        main_layout.addWidget(self.code_preview_section)

        # Create shortcuts for the user to exit
        esc_shortcut = QShortcut(QKeySequence(Qt.Key.Key_Escape), self)
        esc_shortcut.setContext(Qt.ShortcutContext.WindowShortcut)
        esc_shortcut.activated.connect(lambda: self.close())

    def create_code_preview_section_top_bar(self):
        self.code_preview_button = QPushButton("Code Preview")
        self.code_preview_button.setObjectName("code_preview_button")
        self.code_preview_button.setProperty("class", "code_section")
        self.code_preview_button.setFixedWidth(100)
        self.code_preview_button.setEnabled(False)

        self.copy_button = QPushButton("Copy Code")
        self.copy_button.setObjectName("copy_button")
        self.copy_button.setProperty("class", "code_section")
        self.copy_button.setFixedWidth(80)
        self.copy_button.clicked.connect(self.copy_python_code)

        self.export_code_button = QPushButton("Export Code")
        self.export_code_button.setObjectName("export_code_button")
        self.export_code_button.setProperty("class", "code_section")
        self.export_code_button.setFixedWidth(100)
        self.export_code_button.clicked.connect(self.export_python_code)

        self.theme_button = QPushButton("Theme")
        self.theme_button.setObjectName("theme_button")
        self.theme_button.setProperty("class", "code_section")
        self.theme_button.setFixedWidth(80)
        self.theme_button.clicked.connect(self.open_theme_preview)

        self.switch_background_button = QPushButton("Dark Background")
        self.switch_background_button.setObjectName("switch_background_button")
        self.switch_background_button.setProperty("class", "code_section")
        self.switch_background_button.setFixedWidth(120)
        self.switch_background_button.clicked.connect(self.switch_current_background)

        code_section_top_bar_layout = QHBoxLayout(self.code_preview_section_top_bar)
        code_section_top_bar_layout.addWidget(
            self.code_preview_button, alignment=Qt.AlignmentFlag.AlignLeft
        )
        code_section_top_bar_layout.addStretch()
        code_section_top_bar_layout.addWidget(self.copy_button)
        code_section_top_bar_layout.addWidget(self.export_code_button)
        code_section_top_bar_layout.addWidget(self.switch_background_button)
        code_section_top_bar_layout.addWidget(self.theme_button)
        code_section_top_bar_layout.setContentsMargins(0, 0, 0, 0)
        code_section_top_bar_layout.setSpacing(3)

    def create_code_preview_section(self):
        code_preview_section_layout = QVBoxLayout(self.code_preview_section)

        self.code_preview = QTextEdit()
        self.code_preview.setObjectName("code_browser")
        self.code_preview.setReadOnly(True)
        self.code_preview.setMinimumHeight(300)
        self.code_preview.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        self.code_preview.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        self.code_preview.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )

        self.formatter = HtmlFormatter(
            style=self.style, noclasses=True, nobackground=True
        )
        highlighted_code = highlight(self.graph_code, PythonLexer(), self.formatter)
        self.code_preview.setHtml(highlighted_code)

        code_preview_section_layout.addWidget(self.code_preview_section_top_bar)
        code_preview_section_layout.addWidget(self.code_preview)
        code_preview_section_layout.setContentsMargins(5, 5, 5, 5)
        code_preview_section_layout.setSpacing(5)

    def copy_python_code(self):
        clipboard = QApplication.clipboard()
        clipboard.setText(self.full_code)

        self.copy_button.setText("Copied")
        QTimer.singleShot(500, lambda: self.copy_button.setText("Copy Code"))

    def export_python_code(self):
        dialog = QFileDialog(self)
        dialog.setWindowTitle("Export Python File")
        dialog.setFileMode(QFileDialog.FileMode.AnyFile)
        dialog.setAcceptMode(QFileDialog.AcceptMode.AcceptSave)
        dialog.setWindowModality(Qt.WindowModality.ApplicationModal)
        dialog.setNameFilter("Python Files (*.py)")

        if not dialog.exec():
            return  # user cancelled safely

        self.raise_()
        self.activateWindow()
        self.show()

        file_path = dialog.selectedFiles()[0]
        if not file_path.endswith(".py"):
            file_path += ".py"

        success = export_python_code(file_path, self.graph_code)
        if success:
            self.export_code_button.setText("Exported")
        else:
            self.export_code_button.setText("Failed")

        QTimer.singleShot(1000, lambda: self.export_code_button.setText("Export Code"))

    def switch_current_background(self):
        self.code_section.current_background = self.switch_background_button.text().split(" ")[0]
        self.update_background(self.code_section.current_background)

        if self.switch_background_button.text() == "Dark Background":
            self.switch_background_button.setText("Light Background")
        else:
            self.switch_background_button.setText("Dark Background")

    def open_theme_preview(self):
        def on_select(theme):
            self.update_style(theme)

        self.styles = list(get_all_styles())

        self.popup = Theme_Preview(self.styles, on_select, self, self.style)

        # Position under cursor (like a menu)
        pos = QCursor.pos()
        self.popup.move(pos)

        self.popup.show()

    def update_style(self, style):
        self.style = style

        self.formatter = HtmlFormatter(
            style=self.style, noclasses=True, nobackground=True
        )
        highlighted_code = highlight(self.graph_code, PythonLexer(), self.formatter)
        self.code_preview.setHtml(highlighted_code)

        self.code_section.update_style(self.style)
        self.code_section.update_code()

    def update_background(self, background):
        self.background = background
        self.code_preview.setStyleSheet(self.code_preview_backgrounds[self.background])
        self.code_section.code_preview_section.setStyleSheet(self.code_preview_backgrounds[self.background])

    def update_graph_code(self, graph_code):
        self.graph_code = graph_code
        self.formatter = HtmlFormatter(
            style=self.style, noclasses=True, nobackground=True
        )
        highlighted_code = highlight(self.graph_code, PythonLexer(), self.formatter)
        self.code_preview.setHtml(highlighted_code)

    def showEvent(self, event):
        super().showEvent(event)

        # Fade animation
        self.fade_anim = QPropertyAnimation(self, b"windowOpacity")
        self.fade_anim.setDuration(200)
        self.fade_anim.setStartValue(0)
        self.fade_anim.setEndValue(1)
        self.fade_anim.setEasingCurve(QEasingCurve.Type.InOutQuad)

        # Slight scale effect (resize)
        start_rect = self.geometry()
        self.setGeometry(
            start_rect.adjusted(20, 20, -20, -20)  # slightly smaller
        )

        self.scale_anim = QPropertyAnimation(self, b"geometry")  # noqa: F405
        self.scale_anim.setDuration(200)
        self.scale_anim.setStartValue(self.geometry())
        self.scale_anim.setEndValue(start_rect)
        self.scale_anim.setEasingCurve(QEasingCurve.Type.OutBack)

        # Start animations
        self.fade_anim.start()
        self.scale_anim.start()


class code_theme_preview(QDialog):
    def __init__(self, code_section, graph_code=""):
        super().__init__()

        self.setFixedSize(800, 500)
        self.setProperty("class", "dialog_window")
        self.setObjectName("code_theme_preview")

        self.setWindowTitle("Code Theme Preview")

        self.styles = list(get_all_styles())
        self.theme = self.styles[0]

        self.code_section = code_section
        self.graph_code = graph_code

        self.current_background = code_section.current_background
        self.code_preview_backgrounds = {
            "Light": """
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #f5f5ff,
                    stop:0.5 #f7f5fc,
                    stop:1 #f0f0ff
                );
            """,
            "Dark": """
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #1e1e2f,
                    stop:0.5 #232336,
                    stop:1 #1a1a2b
                );
            """,
        }

        self.idx = 0

        self.theme_selection_section = QWidget()
        self.theme_selection_section.setProperty("class", "dialog_section")
        self.theme_selection_section.setObjectName("theme_selection_section")
        self.create_theme_selection_section()

        self.code_preview_section_top_bar = QWidget()
        self.create_code_preview_section_top_bar()

        self.code_preview_section = QWidget()
        self.code_preview_section.setProperty("class", "dialog_section")
        self.code_preview_section.setObjectName("code_preview_section")
        self.create_code_preview_section()
        self.code_preview.setStyleSheet(
            self.code_preview_backgrounds[self.current_background]
        )

        main_layout = QHBoxLayout(self)
        main_layout.addWidget(self.theme_selection_section, stretch=3)
        main_layout.addWidget(self.code_preview_section, stretch=7)
        main_layout.setSpacing(10)

        # Create a shortcut for the user to go to the previous theme by press up
        up_shortcut = QShortcut(QKeySequence(Qt.Key.Key_Up), self)
        up_shortcut.setContext(Qt.ShortcutContext.WindowShortcut)
        up_shortcut.activated.connect(lambda: self.change_current_theme_keyboard(-1))

        # Create a shortcut for the user to go to the next theme by press down
        down_shortcut = QShortcut(QKeySequence(Qt.Key.Key_Down), self)
        down_shortcut.setContext(Qt.ShortcutContext.WindowShortcut)
        down_shortcut.activated.connect(lambda: self.change_current_theme_keyboard(1))

        # Create shortcuts for the user to exit
        esc_shortcut = QShortcut(QKeySequence(Qt.Key.Key_Escape), self)
        esc_shortcut.setContext(Qt.ShortcutContext.WindowShortcut)
        esc_shortcut.activated.connect(lambda: self.close())

    def create_theme_selection_section(self):
        # Create the button layout for the themes
        theme_selection_section_layout = QVBoxLayout(self.theme_selection_section)

        # Create the list view and model that displays the themes available
        self.theme_selection_list_view = QListView()
        self.theme_selection_model = QStringListModel(self.styles)

        # Set the columns that will be displayed and block editting the column names
        self.theme_selection_list_view.setModel(self.theme_selection_model)
        self.theme_selection_list_view.setProperty("class", "list_view")
        self.theme_selection_list_view.setEditTriggers(
            QAbstractItemView.EditTrigger.NoEditTriggers
        )

        # Get the first column in list view and display it
        theme_index = self.theme_selection_model.index(0)
        self.theme_selection_list_view.setCurrentIndex(theme_index)

        # Modification to make the list view look better
        class CustomDelegate(QStyledItemDelegate):
            def paint(self, painter, option, index):
                option.displayAlignment = Qt.AlignmentFlag.AlignCenter
                font = QFont("SF Pro Display", 24)
                font.setWeight(600)
                option.font = font
                super().paint(painter, option, index)

        # Apply the modifications to the list view
        self.theme_selection_list_view.setItemDelegate(CustomDelegate())

        # Control what the scroll bar looks like and spacing between items
        self.theme_selection_list_view.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        self.theme_selection_list_view.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        self.theme_selection_list_view.setSpacing(3)

        # Connect the list view to automatically update the displayed column when clicked on
        self.theme_selection_list_view.clicked.connect(self.change_current_theme)

        # Add the customized list view to the column button screen
        theme_selection_section_layout.addWidget(self.theme_selection_list_view)

        # Add margins and spacing to make it look good and push content to the top
        theme_selection_section_layout.setContentsMargins(10, 10, 10, 10)
        theme_selection_section_layout.setSpacing(10)

    def create_code_preview_section_top_bar(self):
        self.code_preview_button = QPushButton("Code Preview")
        self.code_preview_button.setObjectName("code_preview_button")
        self.code_preview_button.setProperty("class", "code_section")
        self.code_preview_button.setFixedWidth(100)
        self.code_preview_button.setEnabled(False)

        self.copy_button = QPushButton("Copy Code")
        self.copy_button.setObjectName("copy_button")
        self.copy_button.setProperty("class", "code_section")
        self.copy_button.setFixedWidth(80)
        self.copy_button.clicked.connect(self.copy_python_code)

        self.apply_theme_button = QPushButton("Apply Theme")
        self.apply_theme_button.setObjectName("apply_them_button")
        self.apply_theme_button.setProperty("class", "code_section")
        self.apply_theme_button.setFixedWidth(100)
        self.apply_theme_button.clicked.connect(self.apply_theme_to_code)

        self.switch_background_button = QPushButton("Dark Background")
        self.switch_background_button.setObjectName("switch_background_button")
        self.switch_background_button.setProperty("class", "code_section")
        self.switch_background_button.setFixedWidth(120)
        self.switch_background_button.clicked.connect(self.switch_current_background)

        self.more_button = QPushButton("⋮")
        self.more_button.setObjectName("more_button")
        self.more_button.setProperty("class", "code_section")
        self.more_button.setFixedWidth(24)
        self.more_button.clicked.connect(self.open_more_settings)

        code_section_top_bar_layout = QHBoxLayout(self.code_preview_section_top_bar)
        code_section_top_bar_layout.addWidget(
            self.code_preview_button, alignment=Qt.AlignmentFlag.AlignLeft
        )
        code_section_top_bar_layout.addStretch()
        code_section_top_bar_layout.addWidget(self.copy_button)
        code_section_top_bar_layout.addWidget(self.apply_theme_button)
        code_section_top_bar_layout.addWidget(self.switch_background_button)
        code_section_top_bar_layout.addWidget(self.more_button)
        code_section_top_bar_layout.setContentsMargins(0, 0, 0, 0)
        code_section_top_bar_layout.setSpacing(3)

    def create_code_preview_section(self):
        code_preview_section_layout = QVBoxLayout(self.code_preview_section)

        self.code_preview = QTextEdit()
        self.code_preview.setObjectName("code_browser")
        self.code_preview.setReadOnly(True)
        self.code_preview.setMinimumHeight(300)
        self.code_preview.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        self.code_preview.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        self.code_preview.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )

        self.formatter = HtmlFormatter(
            style=self.theme, noclasses=True, nobackground=True
        )
        highlighted_code = highlight(self.graph_code, PythonLexer(), self.formatter)
        self.code_preview.setHtml(highlighted_code)

        code_preview_section_layout.addWidget(self.code_preview_section_top_bar)
        code_preview_section_layout.addWidget(self.code_preview)
        code_preview_section_layout.setContentsMargins(5, 5, 5, 5)
        code_preview_section_layout.setSpacing(5)

    def change_current_theme(self, index):
        self.theme = self.theme_selection_model.data(index, Qt.ItemDataRole.DisplayRole)

        scroll_pos = self.code_preview.verticalScrollBar().value()

        self.formatter = HtmlFormatter(
            style=self.theme, noclasses=True, nobackground=True
        )
        highlighted_code = highlight(self.graph_code, PythonLexer(), self.formatter)
        self.code_preview.setHtml(highlighted_code)

        self.code_preview.verticalScrollBar().setValue(scroll_pos)

    def change_current_theme_keyboard(self, direction):
        # Add one from the column index
        # Divide the index by the total amount to ensure it goes in a loop
        self.idx += direction
        self.idx %= len(self.styles)

        # Set the new column index with the one just calculated
        # Scroll to that column and update the selected column
        new_idx = self.theme_selection_model.index(self.idx)
        self.theme_selection_list_view.setCurrentIndex(new_idx)
        self.theme_selection_list_view.scrollTo(
            new_idx, QAbstractItemView.ScrollHint.PositionAtCenter
        )
        self.theme = self.styles[self.idx]

        self.change_current_theme(new_idx)

    def copy_python_code(self):
        clipboard = QApplication.clipboard()
        clipboard.setText(self.graph_code)

        self.copy_button.setText("Copied")
        QTimer.singleShot(500, lambda: self.copy_button.setText("Copy Code"))

    def apply_theme_to_code(self):
        self.code_section.current_background = self.current_background
        self.code_section.update_style(self.theme)
        self.code_section.update_code()

        self.apply_theme_button.setText("Applied")

        QTimer.singleShot(500, lambda: self.apply_theme_button.setText("Apply Theme"))

    def switch_current_background(self):
        self.current_background = self.switch_background_button.text().split(" ")[0]
        if self.switch_background_button.text() == "Dark Background":
            self.switch_background_button.setText("Light Background")
        else:
            self.switch_background_button.setText("Dark Background")

        self.code_preview.setStyleSheet(
            self.code_preview_backgrounds[self.current_background]
        )

    def open_more_settings(self):
        pass

    def update_graph_code(self, new_graph_code):
        self.graph_code = new_graph_code
        self.formatter = HtmlFormatter(
            style=self.theme, noclasses=True, nobackground=True
        )
        highlighted_code = highlight(self.graph_code, PythonLexer(), self.formatter)
        self.code_preview.setHtml(highlighted_code)

    def get_current_theme(self):
        return self.theme

    def showEvent(self, event):
        super().showEvent(event)

        # Fade animation
        self.fade_anim = QPropertyAnimation(self, b"windowOpacity")
        self.fade_anim.setDuration(200)
        self.fade_anim.setStartValue(0)
        self.fade_anim.setEndValue(1)
        self.fade_anim.setEasingCurve(QEasingCurve.Type.InOutQuad)

        # Slight scale effect (resize)
        start_rect = self.geometry()
        self.setGeometry(
            start_rect.adjusted(20, 20, -20, -20)  # slightly smaller
        )

        self.scale_anim = QPropertyAnimation(self, b"geometry")  # noqa: F405
        self.scale_anim.setDuration(200)
        self.scale_anim.setStartValue(self.geometry())
        self.scale_anim.setEndValue(start_rect)
        self.scale_anim.setEasingCurve(QEasingCurve.Type.OutBack)

        # Start animations
        self.fade_anim.start()
        self.scale_anim.start()


class Code_Section(QWidget):
    def __init__(self):
        super().__init__()

        # Create a small section to display the code and ensure it's drawn on the window
        self.setFixedWidth(620)
        self.setMinimumHeight(150)

        self.setProperty("class", "adjustment_section")

        self.current_background = "Light"
        self.code_preview_backgrounds = {
            "Light": """
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #f5f5ff,
                    stop:0.5 #f7f5fc,
                    stop:1 #f0f0ff
                );
            """,
            "Dark": """
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #1e1e2f,
                    stop:0.5 #232336,
                    stop:1 #1a1a2b
                );
            """,
        }

        self.style = "abap"

        self.code_theme_preview = code_theme_preview(self)
        self.full_screen_code_preview = full_screen_code_preview(self)

        self.code_section_top_bar = QWidget()
        self.create_code_section()
        self.code_section_top_bar.hide()

        self.code_preview_container = QWidget()
        self.code_preview_container.setProperty("class", "adjustment_section")

        self.code_preview_section = QTextEdit()
        self.code_preview_section.setObjectName("code_browser")
        self.code_preview_section.setReadOnly(True)
        self.code_preview_section.setMinimumHeight(100)
        self.code_preview_section.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        self.code_preview_section.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        self.code_preview_section.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        self.code_preview_section.hide()

        code_preview_container_layout = QVBoxLayout(self.code_preview_container)
        code_preview_container_layout.addWidget(self.code_preview_section)
        code_preview_container_layout.setContentsMargins(0, 0, 0, 0)

        main_layout = QVBoxLayout(self)
        main_layout.addWidget(self.code_section_top_bar)
        main_layout.addWidget(self.code_preview_container)
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
        self.code_preview_button = QPushButton("Code Preview")
        self.code_preview_button.setObjectName("code_preview_button")
        self.code_preview_button.setProperty("class", "code_section")
        self.code_preview_button.setFixedWidth(100)
        self.code_preview_button.setEnabled(False)

        self.copy_button = QPushButton("Copy Code")
        self.copy_button.setObjectName("copy_button")
        self.copy_button.setProperty("class", "code_section")
        self.copy_button.setFixedWidth(80)
        self.copy_button.clicked.connect(self.copy_python_code)

        self.full_screen_button = QPushButton("Full Screen")
        self.full_screen_button.setObjectName("full_screen_button")
        self.full_screen_button.setProperty("class", "code_section")
        self.full_screen_button.setFixedWidth(80)
        self.full_screen_button.clicked.connect(self.switch_to_full_screen)

        self.theme_button = QPushButton("Theme")
        self.theme_button.setObjectName("theme_button")
        self.theme_button.setProperty("class", "code_section")
        self.theme_button.setFixedWidth(60)
        self.theme_button.clicked.connect(self.switch_theme)

        self.export_code_button = QPushButton("Export Code")
        self.export_code_button.setObjectName("export_code_button")
        self.export_code_button.setProperty("class", "code_section")
        self.export_code_button.setFixedWidth(100)
        self.export_code_button.clicked.connect(self.export_python_code)

        code_section_top_bar_layout = QHBoxLayout(self.code_section_top_bar)
        code_section_top_bar_layout.addWidget(
            self.code_preview_button, alignment=Qt.AlignmentFlag.AlignLeft
        )
        code_section_top_bar_layout.addStretch()
        code_section_top_bar_layout.addWidget(self.copy_button)
        code_section_top_bar_layout.addWidget(self.export_code_button)
        code_section_top_bar_layout.addWidget(self.full_screen_button)
        code_section_top_bar_layout.addWidget(self.theme_button)
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

        def format_value(parameter, value):
            if isinstance(value, str):
                return f'"{value}"'
            elif parameter == "palette" and isinstance(value, list):
                if len(value) == 1:
                    return f'["{value[0]}"]'
                else:
                    return f'["{value[0]}","{value[1]}","{value[2]}"]'
            elif isinstance(value, list):
                return format_value(value[0])
            elif value is None:
                return "None"
            else:
                return str(value)

        for parameter, argument in self.plot_config["graph_data"].items():
            argument = format_value(parameter, argument)
            new_line = f"\n{indent}{parameter}={argument},"
            plot_code_statement += new_line
        plot_code_statement += "\n)\n"

        self.plot_config.pop("graph_data")

        plot_adjustment = ""

        for adjustment in list(self.plot_config.keys()):
            if adjustment == "legend" and not self.plot_config[adjustment].get(
                "visible", True
            ):
                continue

            plot_adjustment_line = self.matplotlib_plot_code_statements[adjustment]

            for parameter, argument in self.plot_config[adjustment].items():
                if parameter == "label":
                    plot_adjustment_line += format_value(parameter, argument)
                else:
                    plot_adjustment_line += (
                        f"{parameter}={format_value(parameter, argument)}"
                    )
                plot_adjustment_line += ", "
            plot_adjustment_line = plot_adjustment_line[:-2] + ")"
            plot_adjustment += plot_adjustment_line + "\n"

        self.full_code = (
            self.starter_code
            + plot_code_statement
            + plot_adjustment
            + self.show_graph_statement
        )

        self.update_code()

    def update_style(self, style):
        self.style = style

    def update_code(self):
        self.code_preview_container.setStyleSheet(
            self.code_preview_backgrounds[self.current_background]
        )

        scroll_pos = self.code_preview_section.verticalScrollBar().value()

        self.formatter = HtmlFormatter(
            style=self.style, noclasses=True, nobackground=True
        )
        highlighted_code = highlight(self.full_code, PythonLexer(), self.formatter)
        self.code_preview_section.setHtml(highlighted_code)

        self.code_preview_section.verticalScrollBar().setValue(scroll_pos)

    def copy_python_code(self):
        clipboard = QApplication.clipboard()
        clipboard.setText(self.full_code)

        self.copy_button.setText("Copied")
        QTimer.singleShot(500, lambda: self.copy_button.setText("Copy Code"))

    def switch_to_full_screen(self):
        self.full_screen_code_preview.update_style(self.style)
        self.full_screen_code_preview.update_background(self.current_background)
        self.full_screen_code_preview.update_graph_code(self.full_code)

        for d in QApplication.topLevelWidgets():
            if isinstance(d, QDialog) and d.isVisible():
                d.close()

        self.full_screen_code_preview.show()
        self.full_screen_code_preview.activateWindow()
        self.full_screen_code_preview.raise_()

    def switch_theme(self):
        self.code_theme_preview.update_graph_code(self.full_code)

        for d in QApplication.topLevelWidgets():
            if isinstance(d, QDialog) and d.isVisible():
                d.close()

        self.code_theme_preview.show()
        self.code_theme_preview.activateWindow()
        self.code_theme_preview.raise_()

    def export_python_code(self):
        dialog = QFileDialog(self)
        dialog.setWindowTitle("Export Python File")
        dialog.setFileMode(QFileDialog.FileMode.AnyFile)
        dialog.setAcceptMode(QFileDialog.AcceptMode.AcceptSave)
        dialog.setWindowModality(Qt.WindowModality.ApplicationModal)
        dialog.setNameFilter("Python Files (*.py)")

        if not dialog.exec():
            return  # user cancelled safely

        self.raise_()
        self.activateWindow()
        self.show()

        file_path = dialog.selectedFiles()[0]
        if not file_path.endswith(".py"):
            file_path += ".py"

        success = export_python_code(file_path, self.full_code)
        if success:
            self.export_code_button.setText("Exported")
        else:
            self.export_code_button.setText("Failed")

        QTimer.singleShot(1000, lambda: self.export_code_button.setText("Export Code"))
