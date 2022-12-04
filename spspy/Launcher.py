from PySide6.QtWidgets import QApplication, QWidget, QMainWindow
from PySide6.QtWidgets import QLabel
from PySide6.QtWidgets import QHBoxLayout, QVBoxLayout, QGroupBox
from PySide6.QtWidgets import QPushButton
from PySide6.QtGui import QAction

from .SPSPlotUI import run_spsplot_ui, SPSPlotGUI
from .SpancUI import run_spanc_ui, SpancGUI

import sys
import matplotlib as mpl
from qdarktheme import load_stylesheet

class Launcher(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("SPSPY Launcher")
        self.mainLayout = QVBoxLayout()
        self.mainWidget = QWidget(self)
        self.setCentralWidget(self.mainWidget)
        self.mainWidget.setLayout(self.mainLayout)

        self.spsplotButton = QPushButton("Launch SPSPlot", self.mainWidget)
        self.spsplotButton.clicked.connect(self.handle_spsplot)
        self.spancButton = QPushButton("Launch SPANC", self.mainWidget)
        self.spancButton.clicked.connect(self.handle_spanc)

        self.mainLayout.addWidget(self.spsplotButton)
        self.mainLayout.addWidget(self.spancButton)
        self.show()

    def handle_spsplot(self) -> None:
        SPSPlotGUI(self)

    def handle_spanc(self) -> None:
        #run_spanc_ui()
        SpancGUI(self)


def run_launcher() -> None:
    mpl.use("Qt5Agg")
    app = QApplication.instance()
    if not app:
        app = QApplication(sys.argv)
        app.setStyleSheet(load_stylesheet())
    window = Launcher()
    sys.exit(app.exec_())