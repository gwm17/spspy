from .SPSPlot import SPSPlot
from .SPSReaction import RxnParameters
from .ui.MPLCanvas import MPLCanvas
from .ui.ReactionDialog import ReactionDialog
from .ui.TargetDialog import TargetDialog
from .ui.ExcitationDialog import ExcitationDialog

from PySide6.QtWidgets import QApplication, QWidget, QMainWindow
from PySide6.QtWidgets import QLabel, QTabWidget, QTableWidget, QTableWidgetItem
from PySide6.QtWidgets import QHBoxLayout, QVBoxLayout, QGroupBox
from PySide6.QtWidgets import QPushButton, QRadioButton
from PySide6.QtWidgets import QDoubleSpinBox
from PySide6.QtWidgets import QFileDialog
from PySide6.QtGui import QAction

from qdarktheme import load_stylesheet
from enum import Enum, auto
import matplotlib as mpl
import sys
import pickle

class PlotType(Enum):
    PLOT_EX = auto()
    PLOT_KE = auto()
    PLOT_Z = auto()

class SPSPlotGUI(QMainWindow):
    def __init__(self, parent=None) :
        super().__init__(parent)
        self.setWindowTitle("SPSPlot")
        self.sps = SPSPlot()

        self.plotLayout = QVBoxLayout()
        self.targetLayout = QVBoxLayout()
        self.generalLayout = QVBoxLayout()
        self.centralWidget = QTabWidget(self)
        self.setCentralWidget(self.centralWidget)
        self.centralWidget.setLayout(self.generalLayout)

        self.targetTab = QWidget(self.centralWidget)
        self.targetTab.setLayout(self.targetLayout)
        self.plotTab = QWidget(self.centralWidget)
        self.plotTab.setLayout(self.plotLayout)
        self.centralWidget.addTab(self.plotTab, "Plot")
        self.centralWidget.addTab(self.targetTab, "Targets")

        self.plotType = PlotType.PLOT_EX
        self.create_menus()
        self.create_canvas()
        self.create_inputs()
        self.create_target_table()
        self.show()

    def create_canvas(self) -> None:
        self.canvas = MPLCanvas(self.plotTab, width=14, height=5, dpi=100)
        self.plotLayout.addWidget(self.canvas, 5)

    def create_menus(self) -> None:
        self.fileMenu = self.menuBar().addMenu("&File")
        saveAction = QAction("&Save...",self)
        openAction = QAction("&Open...",self)
        self.fileMenu.addAction(saveAction)
        self.fileMenu.addAction(openAction)
        self.fileMenu.addAction("&Exit", self.close)
        saveAction.triggered.connect(self.handle_save)
        openAction.triggered.connect(self.handle_open)
        
        self.addMenu = self.menuBar().addMenu("&New")
        newTargetAction = QAction("New target...", self)
        newReactionAction = QAction("New reaction...", self)
        newStateAction = QAction("New state...", self)
        self.addMenu.addAction(newTargetAction)
        self.addMenu.addAction(newReactionAction)
        self.addMenu.addAction(newStateAction)
        newStateAction.triggered.connect(self.handle_new_state)
        newReactionAction.triggered.connect(self.handle_new_reaction)
        newTargetAction.triggered.connect(self.handle_new_target)

    def create_inputs(self) -> None:
        inputLayout = QHBoxLayout()
        self.inputGroupBox = QGroupBox("Adjustable Inputs", self.plotTab)
        rhoMinLabel = QLabel("Rho Min", self.inputGroupBox)
        self.rhoMinInput = QDoubleSpinBox(self.inputGroupBox)
        self.rhoMinInput.setRange(0.0, 150.0)
        self.rhoMinInput.setSuffix(" cm")
        rhoMaxLabel = QLabel("RhoMax", self.inputGroupBox)
        self.rhoMaxInput = QDoubleSpinBox(self.inputGroupBox)
        self.rhoMaxInput.setRange(0.0,150.0)
        self.rhoMaxInput.setSuffix(" cm")
        bkeLabel = QLabel("Beam KE", self.inputGroupBox)
        self.bkeInput = QDoubleSpinBox(self.inputGroupBox)
        self.bkeInput.setRange(0.0, 500.0)
        self.bkeInput.setSuffix(" MeV")
        bfieldLabel = QLabel("B-field", self.inputGroupBox)
        self.bfieldInput = QDoubleSpinBox(self.inputGroupBox)
        self.bfieldInput.setRange(0.0, 17.0)
        self.bfieldInput.setSuffix(" kG")
        angleLabel = QLabel("Angle", self.inputGroupBox)
        self.angleInput = QDoubleSpinBox(self.inputGroupBox)
        self.angleInput.setRange(0.0, 180.0)
        self.angleInput.setSuffix(" deg")
        self.runButton = QPushButton("Set", self.inputGroupBox)
        self.runButton.clicked.connect(self.handle_run)

        self.energyButtonGroup = QGroupBox("Ex/KE switch",self.plotTab)
        buttonLayout = QHBoxLayout()
        self.exButton = QRadioButton("Excitation energy (MeV)", self.energyButtonGroup)
        self.exButton.toggled.connect(self.handle_ex_switch)
        self.exButton.toggle()
        self.keButton = QRadioButton("Ejectile Kinetic energy (MeV)", self.energyButtonGroup)
        self.keButton.toggled.connect(self.handle_ke_switch)
        self.zButton = QRadioButton("Focal Plane Z Shift (mm)", self.energyButtonGroup)
        self.zButton.toggled.connect(self.handle_z_switch)
        buttonLayout.addWidget(self.exButton)
        buttonLayout.addWidget(self.keButton)
        buttonLayout.addWidget(self.zButton)
        self.energyButtonGroup.setLayout(buttonLayout)

        inputLayout.addWidget(rhoMinLabel)
        inputLayout.addWidget(self.rhoMinInput)
        inputLayout.addWidget(rhoMaxLabel)
        inputLayout.addWidget(self.rhoMaxInput)
        inputLayout.addWidget(bkeLabel)
        inputLayout.addWidget(self.bkeInput)
        inputLayout.addWidget(bfieldLabel)
        inputLayout.addWidget(self.bfieldInput)
        inputLayout.addWidget(angleLabel)
        inputLayout.addWidget(self.angleInput)
        inputLayout.addWidget(self.runButton)
        self.inputGroupBox.setLayout(inputLayout)
        inputLayout.addWidget(self.energyButtonGroup)

        self.plotLayout.addWidget(self.inputGroupBox, 1)

    def create_target_table(self) -> None:
        self.targetGroup = QGroupBox("Targets", self.targetTab)
        tableLayout = QVBoxLayout()
        self.targetTable = QTableWidget(self.targetGroup)
        self.targetTable.setColumnCount(6)
        self.targetTable.setHorizontalHeaderLabels(["Layer1 Thickness(ug/cm^2", "Layer1 (Z, A, S)","Layer2 Thickness(ug/cm^2", "Layer2 (Z, A, S)","Layer3 Thickness(ug/cm^2", "Layer3 (Z, A, S)"])
        tableLayout.addWidget(self.targetTable)
        self.targetGroup.setLayout(tableLayout)
        self.targetLayout.addWidget(self.targetGroup)
        self.targetTable.resizeColumnsToContents()
        self.targetTable.cellDoubleClicked.connect(self.handle_update_target)

    def handle_save(self) -> None:
        fileName = QFileDialog.getSaveFileName(self, "Save Input","./","SPSPlot Files (*.sps)")
        if fileName[0]:
            with open(fileName[0], "wb") as file:
                pickle.dump(self.sps, file, pickle.HIGHEST_PROTOCOL)

    def handle_open(self) -> None:
        fileName = QFileDialog.getOpenFileName(self, "Open Input","./","SPSPlot Files (*.sps)")
        if fileName[0]:
            with open(fileName[0], "rb") as file:
                self.sps = pickle.load(file)
                self.update_inputs()
                self.update_plot()
                self.update_target_table()

    def handle_new_state(self) -> None:
        stDlg = ExcitationDialog(self, self.sps.data.keys())
        stDlg.new_level.connect(self.sps.add_excitation)
        if stDlg.exec():
            self.update_plot()

    def handle_new_reaction(self) -> None:
        rxnDlg = ReactionDialog(parent=self, targets=self.sps.targets.keys())
        rxnDlg.new_reaction.connect(self.add_reaction)
        rxnDlg.exec()

    def handle_new_target(self) -> None:
        targDlg = TargetDialog(self)
        targDlg.new_target.connect(self.sps.add_target)
        if targDlg.exec():
            self.update_target_table()
    
    def handle_update_target(self, row: int, col: int) -> None:
        targName = self.targetTable.verticalHeaderItem(row).text()
        targDia = TargetDialog(self, target=self.sps.targets[targName])
        targDia.new_target.connect(self.sps.add_target)
        if targDia.exec():
            self.update_target_table()
            self.sps.update_reactions()
            self.update_plot() #in case a reaction is using the target

    def handle_run(self) -> None:
        self.sps.beamEnergy = self.bkeInput.value()
        self.sps.spsAngle = self.angleInput.value()
        self.sps.magneticField = self.bfieldInput.value()
        self.sps.update_reactions()
        self.sps.rhoMin = self.rhoMinInput.value()
        self.sps.rhoMax = self.rhoMaxInput.value()
        self.update_plot()

    def handle_ex_switch(self) -> None:
        if self.exButton.isChecked() and self.plotType != PlotType.PLOT_EX:
            self.plotType = PlotType.PLOT_EX
            self.update_plot()

    def handle_ke_switch(self) -> None:
        if self.keButton.isChecked() and self.plotType != PlotType.PLOT_KE:
            self.plotType = PlotType.PLOT_KE
            self.update_plot()

    def handle_z_switch(self) -> None:
        if self.zButton.isChecked() and self.plotType != PlotType.PLOT_Z:
            self.plotType = PlotType.PLOT_Z
            self.update_plot()

    def add_reaction(self, rxnParams: RxnParameters, targName: str) -> None:
        rxnParams.beamEnergy = self.bkeInput.value()
        rxnParams.spsAngle = self.angleInput.value()
        rxnParams.magneticField = self.bfieldInput.value()
        self.sps.add_reaction(rxnParams, targName)
        self.update_plot()

    def update_plot(self) -> None:
        rhos = []
        exs = []
        kes = []
        zs = []
        rxns = []		
        for rxnNumber, rxn in enumerate(self.sps.data.values()):
            for point in rxn.excitations:
                rxns.append(rxnNumber+1)
                rhos.append(point.rho)
                exs.append(point.excitation)
                kes.append(point.kineticEnergy)
                zs.append(point.fpZ)
        self.canvas.axes.cla()
        self.canvas.axes.plot(rhos, rxns, marker="o", linestyle="None")
        for i in range(len(rxns)):
            y = rxns[i]
            x = rhos[i]
            label = ''
            if self.plotType == PlotType.PLOT_EX:
                label = "{:.2f}".format(exs[i])
            elif self.plotType == PlotType.PLOT_KE:
                label = "{:.2f}".format(kes[i])
            elif self.plotType == PlotType.PLOT_Z:
                label = "{:.2f}".format(zs[i])
            self.canvas.axes.annotate(label, (x,y), textcoords="offset points",xytext=(0,10),ha="center",rotation="vertical")
        ylabels = [r.rxn.get_latex_rep() for r in self.sps.data.values()]
        ylabels.append("Reactions")
        self.canvas.axes.set_xlim(self.sps.rhoMin, self.sps.rhoMax)
        self.canvas.axes.set_yticks(range(1,len(self.sps.data)+2))
        self.canvas.axes.set_yticklabels(ylabels)
        self.canvas.draw()

    def update_inputs(self):
        self.rhoMinInput.setValue(self.sps.rhoMin)
        self.rhoMaxInput.setValue(self.sps.rhoMax)
        self.bfieldInput.setValue(self.sps.magneticField)
        self.bkeInput.setValue(self.sps.beamEnergy)
        self.angleInput.setValue(self.sps.spsAngle)

    def update_target_table(self):
        self.targetTable.setRowCount(len(self.sps.targets))
        self.targetTable.setVerticalHeaderLabels(self.sps.targets.keys())
        for row, key in enumerate(self.sps.targets):
            for col, layer in enumerate(self.sps.targets[key].layer_details) :
                self.targetTable.setItem(row, col*2, QTableWidgetItem(str(layer.thickness)))
                self.targetTable.setCellWidget(row, 1+col*2, QLabel(str(layer)))
        self.targetTable.resizeColumnsToContents()
        self.targetTable.resizeRowsToContents()

def run_spsplot_ui():
    mpl.use("Qt5Agg")
    app = QApplication.instance()
    if not app:
        app = QApplication(sys.argv)
        app.setStyleSheet(load_stylesheet())
    window = SPSPlotGUI()
    sys.exit(app.exec_())