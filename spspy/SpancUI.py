from .Spanc import Spanc, PeakType
from .Fitter import convert_fit_points_to_arrays, convert_resid_points_to_arrays
from .ui.MPLCanvas import MPLCanvas
from .ui.ReactionDialog import ReactionDialog
from .ui.TargetDialog import TargetDialog
from .ui.PeakDialog import PeakDialog

from PySide6.QtWidgets import QApplication, QWidget, QMainWindow
from PySide6.QtWidgets import QLabel, QTabWidget, QTableWidget, QTableWidgetItem
from PySide6.QtWidgets import QHBoxLayout, QVBoxLayout, QGroupBox
from PySide6.QtWidgets import QPushButton, QTextEdit, QSpinBox
from PySide6.QtWidgets import QFileDialog
from PySide6.QtGui import QAction

from qdarktheme import load_stylesheet, load_palette
import matplotlib as mpl
import numpy as np
from numpy.typing import NDArray
import sys
import pickle

#Get y-value for baseline at 0
def baseline(x: float) -> float:
    return 0.0

class SpancGUI(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("SPANC")
        self.spanc = Spanc()
        self.tablelayout = QVBoxLayout()
        self.plotlayout = QHBoxLayout()
        self.layout = QVBoxLayout()
        self.centralWidget = QTabWidget(self)
        self.setCentralWidget(self.centralWidget)
        self.centralWidget.setLayout(self.layout)
        self.tableTab = QWidget(self.centralWidget)
        self.tableTab.setLayout(self.tablelayout)
        self.plotTab = QWidget(self.centralWidget)
        self.plotTab.setLayout(self.plotlayout)
        self.centralWidget.addTab(self.tableTab, "Data Tables")
        self.centralWidget.addTab(self.plotTab, "Plots and Fits")
        self.fitFlag = False
        self.create_menus()
        self.create_fit_canvas()
        self.create_target_table() 
        self.create_reaction_table()
        self.create_calibration_table()
        self.create_output_table()
        self.create_fit_result_text()
        self.show()

    def create_menus(self) -> None:
        self.fileMenu = self.menuBar().addMenu("&File")
        saveAction = QAction("&Save...",self)
        openAction = QAction("&Open...",self)
        saveFitAction = QAction("Save Fit Plot...", self)
        self.fileMenu.addAction(saveAction)
        self.fileMenu.addAction(openAction)
        self.fileMenu.addAction(saveFitAction)
        self.fileMenu.addAction("&Exit", self.close)
        saveAction.triggered.connect(self.handle_save)
        openAction.triggered.connect(self.handle_open)
        saveFitAction.triggered.connect(self.handle_save_fit)
        
        self.addMenu = self.menuBar().addMenu("&New")
        newTargetAction = QAction("New target...", self)
        newReactionAction = QAction("New reaction...", self)
        newCalibrationAction = QAction("New calibration...", self)
        newOutputAction = QAction("New output...", self)
        self.addMenu.addAction(newTargetAction)
        self.addMenu.addAction(newReactionAction)
        self.addMenu.addAction(newCalibrationAction)
        self.addMenu.addAction(newOutputAction)
        newTargetAction.triggered.connect(self.handle_new_target)
        newReactionAction.triggered.connect(self.handle_new_reaction)
        newCalibrationAction.triggered.connect(self.handle_new_calibration)
        newOutputAction.triggered.connect(self.handle_new_output)

    def create_fit_canvas(self) -> None:
        self.fitGroup = QGroupBox("Calibration Fit", self.plotTab)
        fitLayout = QVBoxLayout()
        self.fitCanvas = MPLCanvas(self.fitGroup, width=6, height=6, dpi=100)
        self.residCanvas = MPLCanvas(self.fitGroup, width=6, height=6, dpi=100)

        self.fitOptionGroup = QGroupBox("Fit options", self.fitGroup)
        fitOptionLayout = QHBoxLayout()
        self.fitButton = QPushButton("Run Fit", self.fitOptionGroup)
        self.fitButton.clicked.connect(self.handle_run_fit)
        self.fitOrderBox = QSpinBox(self.fitOptionGroup)
        self.fitOrderBox.valueChanged.connect(self.handle_change_fit_order)
        self.fitOrderBox.setValue(1)
        self.fitOrderBox.setMaximum(10)
        self.fitOrderBox.setMinimum(0)
        fitOptionLayout.addWidget(QLabel("Polynomial Order", self.fitOptionGroup))
        fitOptionLayout.addWidget(self.fitOrderBox)
        fitOptionLayout.addWidget(self.fitButton)
        self.fitOptionGroup.setLayout(fitOptionLayout)

        fitLayout.addWidget(QLabel("Fit", self.fitCanvas))
        fitLayout.addWidget(self.fitCanvas)
        fitLayout.addWidget(QLabel("Residuals", self.fitCanvas))
        fitLayout.addWidget(self.residCanvas)
        fitLayout.addWidget(self.fitOptionGroup)
        self.fitGroup.setLayout(fitLayout)
        self.plotlayout.addWidget(self.fitGroup)

    def create_target_table(self) -> None:
        self.targetGroup = QGroupBox("Targets", self.tableTab)
        targetLayout = QVBoxLayout()
        self.targetTable = QTableWidget(self.targetGroup)
        self.targetTable.setColumnCount(6)
        self.targetTable.setHorizontalHeaderLabels(["L1 Thickness(ug/cm^2)", "L1 Compound","L2 Thickness(ug/cm^2)", "L2 Compound","L3 Thickness(ug/cm^2)", "L3 Compound"])
        targetLayout.addWidget(self.targetTable)
        self.targetGroup.setLayout(targetLayout)
        self.tablelayout.addWidget(self.targetGroup)
        self.targetTable.resizeColumnsToContents()
        self.targetTable.cellDoubleClicked.connect(self.handle_update_target)

    def create_reaction_table(self) -> None:
        self.rxnGroup = QGroupBox("Reactions", self.tableTab)
        rxnLayout = QVBoxLayout()
        self.reactionTable = QTableWidget(self.rxnGroup)
        self.reactionTable.setColumnCount(5)
        self.reactionTable.setHorizontalHeaderLabels(["Target Material","Reaction Equation","Beam KE(MeV)","BField(kG)","Angle(deg)"])
        rxnLayout.addWidget(self.reactionTable)
        self.rxnGroup.setLayout(rxnLayout)
        self.tablelayout.addWidget(self.rxnGroup)
        self.reactionTable.resizeColumnsToContents()
        self.reactionTable.cellDoubleClicked.connect(self.handle_update_reaction)

    def create_calibration_table(self) -> None:
        self.calGroup = QGroupBox("Calibration Peaks", self.tableTab)
        calLayout = QVBoxLayout()
        self.calibrationTable = QTableWidget(self.calGroup)
        self.calibrationTable.setColumnCount(8)
        self.calibrationTable.setHorizontalHeaderLabels(["Reaction","x(mm)","ux stat.(mm)","ux sys.(mm)","rho(cm)","urho(cm)","Ex(MeV)","uEx(MeV)"])
        calLayout.addWidget(self.calibrationTable)
        self.calGroup.setLayout(calLayout)
        self.tablelayout.addWidget(self.calGroup)
        self.calibrationTable.resizeColumnsToContents()
        self.calibrationTable.cellDoubleClicked.connect(self.handle_update_calibration)

    def create_output_table(self) -> None:
        self.outGroup = QGroupBox("Output Peaks", self.tableTab)
        outLayout = QVBoxLayout()
        self.outputTable = QTableWidget(self.outGroup)
        self.outputTable.setColumnCount(12)
        self.outputTable.setHorizontalHeaderLabels(["Reaction","x(mm)","ux stat.(mm)","ux sys.(mm)","rho(cm)","urho(cm)","Ex(MeV)","uEx(MeV)","FWHM(mm)","uFWHM(mm)","FWHM(MeV)","uFWHM(MeV)"])
        outLayout.addWidget(self.outputTable)
        self.outGroup.setLayout(outLayout)
        self.tablelayout.addWidget(self.outGroup)
        self.outputTable.resizeColumnsToContents()
        self.outputTable.cellDoubleClicked.connect(self.handle_update_output)

    def create_fit_result_text(self) -> None:
        self.fitTextGroup = QGroupBox("Fit Results", self.plotTab)
        fitTextLayout = QVBoxLayout()
        self.fitResultText = QTextEdit(self.fitTextGroup)
        self.fitResultText.setReadOnly(True)
        fitTextLayout.addWidget(self.fitResultText)
        self.fitTextGroup.setLayout(fitTextLayout)
        self.plotlayout.addWidget(self.fitTextGroup)

    def handle_save(self) -> None:
        fileName = QFileDialog.getSaveFileName(self, "Save Input","./","SPANC Files (*.spanc)")
        if fileName[0]:
            #self.spanc.WriteConfig(fileName[0])
            with open(fileName[0], "wb") as savefile:
                pickle.dump(self.spanc, savefile, pickle.HIGHEST_PROTOCOL)
                savefile.close()

    def handle_save_fit(self) -> None:
        fileName = QFileDialog.getSaveFileName(self, "Save Fit Image","./","Image Files (*.png, *.eps)")
        if fileName[0]:
            self.fitCanvas.fig.savefig(fileName[0])

    def handle_open(self) -> None:
        fileName = QFileDialog.getOpenFileName(self, "Open Input","./","SPANC Files (*.spanc)")
        if fileName[0]:
            with open(fileName[0], "rb") as openfile:
                self.spanc = pickle.load(openfile)
                self.update_target_table()
                self.update_reaction_table()
                self.update_calibration_table()
                self.update_fit_order()
                self.update_output_table()
                openfile.close()

    def handle_new_target(self) -> None:
        targDia = TargetDialog(self)
        targDia.new_target.connect(self.spanc.add_target)
        if targDia.exec() :
            self.update_target_table()
        return

    def handle_update_target(self, row: int, col: int) -> None:
        targName = self.targetTable.verticalHeaderItem(row).text()
        targDia = TargetDialog(self, target=self.spanc.targets[targName])
        targDia.new_target.connect(self.spanc.add_target)
        if targDia.exec():
            self.update_target_table()
            self.spanc.calculate_calibrations()
            self.update_reaction_table()
            self.update_calibration_table()
            self.spanc.calculate_outputs()
            self.update_output_table()
        return

    def handle_new_reaction(self) -> None:
        rxnDia = ReactionDialog(self, targets=self.spanc.targets.keys(), extraParams=True)
        rxnDia.new_reaction.connect(self.spanc.add_reaction)
        if rxnDia.exec():
            self.update_reaction_table()
        return

    def handle_update_reaction(self, row: int, col: int) -> None:
        rxnName = self.reactionTable.verticalHeaderItem(row).text()
        rxnDia = ReactionDialog(self, targets=self.spanc.targets.keys(), rxn=self.spanc.reactions[rxnName], rxnKey=rxnName, extraParams=True)
        rxnDia.update_reaction.connect(self.spanc.update_reaction_parameters)
        if rxnDia.exec():
            self.update_reaction_table()
            self.spanc.calculate_calibrations()
            self.update_calibration_table()
            self.spanc.calculate_outputs()
            self.update_output_table()
        return

    def handle_new_calibration(self) -> None:
        calDia = PeakDialog(PeakType.CALIBRATION, self.spanc.reactions.keys(), self)
        calDia.new_peak.connect(self.spanc.add_calibration)
        if calDia.exec():
            self.update_calibration_table()
        return
        
    def handle_update_calibration(self, row: int, col: int) -> None:
        peakData = self.spanc.calibrations[row]
        calDia = PeakDialog(PeakType.CALIBRATION, self.spanc.reactions.keys(), self, peak=peakData)
        calDia.new_peak.connect(self.spanc.add_calibration)
        if calDia.exec():
            self.update_calibration_table()
        return

    def handle_new_output(self) -> None:
        outDia = PeakDialog(PeakType.OUTPUT, self.spanc.reactions.keys(), self)
        outDia.new_peak.connect(self.spanc.add_output)
        if outDia.exec():
            self.update_output_table()
        return

    def handle_update_output(self, row: int, col: int) -> None:
        peakData = self.spanc.calibrations[row]
        outDia = PeakDialog(PeakType.OUTPUT, self.spanc.reactions.keys(), self, peak=peakData)
        outDia.new_peak.connect(self.spanc.add_output)
        if outDia.exec():
            self.update_output_table()
        return

    def handle_change_fit_order(self, order: int) -> None:
        self.spanc.set_fit_order(order)        

    def handle_run_fit(self) -> None:
        order = self.spanc.fitter.polynomialOrder
        npoints = len(self.spanc.calibrations)
        if npoints < (order + 2):
            print(f"Warning! Attempting to fit {npoints} data points with order {order} polyomial, too few degrees of freedom!")
            print(f"Increase number of data points to at minimum {order+2} to use a polynomial of this order.")
            return
        fitData = self.spanc.fit()
        xArray, yArray, xErrArray, yErrArray = convert_fit_points_to_arrays(fitData)
        xMin = np.amin(xArray)
        xMax = np.amax(xArray)
        fitArray = np.linspace(xMin, xMax, 1000)
        self.fitCanvas.axes.cla()
        self.fitCanvas.axes.errorbar(xArray, yArray, yerr=yErrArray, xerr=xErrArray, marker="o", linestyle="None", elinewidth=2.0)
        self.fitCanvas.axes.plot(fitArray, self.spanc.fitter.evaluate(fitArray))
        self.fitCanvas.axes.set_xlabel(r"$x$ (mm)")
        self.fitCanvas.axes.set_ylabel(r"$\rho$ (cm)")
        self.fitCanvas.fig.tight_layout()
        self.fitCanvas.draw()
        self.spanc.calculate_outputs()
        self.update_output_table()
        self.fitFlag = True

        residData = self.spanc.get_residuals()
        xArray, residArray, studentResidArray = convert_resid_points_to_arrays(residData)
        self.residCanvas.axes.cla()
        self.residCanvas.axes.plot(xArray, residArray, marker="o", linestyle="None")
        self.residCanvas.axes.hlines(0.0, xMin, xMax, colors="r", linestyles="dashed")
        self.residCanvas.axes.set_xlabel(r"$x$ (mm)")
        self.residCanvas.axes.set_ylabel(r"Residual (cm)")
        self.residCanvas.fig.tight_layout()
        self.residCanvas.draw()
        self.update_fit_text(residArray, studentResidArray)

    def update_target_table(self) -> None:
        self.targetTable.setRowCount(len(self.spanc.targets))
        self.targetTable.setVerticalHeaderLabels(self.spanc.targets.keys())
        for row, key in enumerate(self.spanc.targets):
            for i, layer in enumerate(self.spanc.targets[key].layer_details) :
                self.targetTable.setItem(row, 0+i*2, QTableWidgetItem(str(layer.thickness)))
                self.targetTable.setCellWidget(row, 1+i*2, QLabel(str(layer)))
        self.targetTable.resizeColumnsToContents()
        self.targetTable.resizeRowsToContents()

    def update_reaction_table(self) -> None:
        self.reactionTable.setRowCount(len(self.spanc.reactions))
        self.reactionTable.setVerticalHeaderLabels(self.spanc.reactions.keys())
        for row, rxn in enumerate(self.spanc.reactions.values()):
            self.reactionTable.setItem(row, 0, QTableWidgetItem(str(rxn.targetMaterial)))
            self.reactionTable.setCellWidget(row, 1, QLabel(str(rxn)))
            self.reactionTable.setItem(row, 2, QTableWidgetItem(str(rxn.params.beamEnergy)))
            self.reactionTable.setItem(row, 3, QTableWidgetItem(str(rxn.params.magneticField)))
            self.reactionTable.setItem(row, 4, QTableWidgetItem(str(rxn.params.spsAngle)))
        self.reactionTable.resizeColumnsToContents()
        self.reactionTable.resizeRowsToContents()
        
    def update_calibration_table(self) -> None:
        self.calibrationTable.setRowCount(len(self.spanc.calibrations))
        self.calibrationTable.setVerticalHeaderLabels(self.spanc.calibrations.keys())
        for row, peak in enumerate(self.spanc.calibrations.values()):
            self.calibrationTable.setItem(row, 0, QTableWidgetItem(peak.rxnName))
            self.calibrationTable.setItem(row, 1, QTableWidgetItem(str(peak.position)))
            self.calibrationTable.setItem(row, 2, QTableWidgetItem(str(peak.positionErrStat)))
            self.calibrationTable.setItem(row, 3, QTableWidgetItem(str(peak.positionErrSys)))
            self.calibrationTable.setItem(row, 4, QTableWidgetItem(str(peak.rho)))
            self.calibrationTable.setItem(row, 5, QTableWidgetItem(str(peak.rhoErr)))
            self.calibrationTable.setItem(row, 6, QTableWidgetItem(str(peak.excitation)))
            self.calibrationTable.setItem(row, 7, QTableWidgetItem(str(peak.excitationErr)))
        self.calibrationTable.resizeColumnsToContents()
        self.calibrationTable.resizeRowsToContents()

    def update_output_table(self) -> None:
        self.outputTable.setRowCount(len(self.spanc.outputs))
        self.outputTable.setVerticalHeaderLabels(self.spanc.outputs.keys())
        for row, peak in enumerate(self.spanc.outputs.values()):
            self.outputTable.setItem(row, 0, QTableWidgetItem(peak.rxnName))
            self.outputTable.setItem(row, 1, QTableWidgetItem(str(peak.position)))
            self.outputTable.setItem(row, 2, QTableWidgetItem(str(peak.positionErrStat)))
            self.outputTable.setItem(row, 3, QTableWidgetItem(str(peak.positionErrSys)))
            self.outputTable.setItem(row, 4, QTableWidgetItem(str(peak.rho)))
            self.outputTable.setItem(row, 5, QTableWidgetItem(str(peak.rhoErr)))
            self.outputTable.setItem(row, 6, QTableWidgetItem(str(peak.excitation)))
            self.outputTable.setItem(row, 7, QTableWidgetItem(str(peak.excitationErr)))
            self.outputTable.setItem(row, 8, QTableWidgetItem(str(peak.positionFWHM)))
            self.outputTable.setItem(row, 9, QTableWidgetItem(str(peak.positionFWHMErr)))
            self.outputTable.setItem(row, 10, QTableWidgetItem(str(peak.excitationFWHM)))
            self.outputTable.setItem(row, 11, QTableWidgetItem(str(peak.excitationFWHMErr)))
        self.outputTable.resizeColumnsToContents()
        self.outputTable.resizeRowsToContents()

    def update_fit_order(self) -> None:
        self.fitOrderBox.setValue(self.spanc.fitter.polynomialOrder)

    #generate markdown text string and render in the text edit
    def update_fit_text(self, residuals: NDArray[np.float64], studentizedResiduals: NDArray[np.float64]) -> None:
        markdownString = (f"# Fit Results\n"
                          f"## Polynomial Order: {self.spanc.fitter.polynomialOrder} \n \n"
                          f"## Chi-Square: {self.spanc.fitter.get_chisquare():.3f} \n \n"
                          f"## NDF: {self.spanc.fitter.get_ndf()} \n \n"
                          f"## Reduced Chi-Square {self.spanc.fitter.get_reduced_chisquare():.3f} \n \n"
                          f"## Parameter Values (a0 -> aN): {np.array_str(self.spanc.fitter.get_parameters(), precision=3)} \n \n"
                          f"## Parameter Uncertanties (ua0 -> uaN): {np.array_str(self.spanc.fitter.get_parameter_errors(), precision=3)} \n \n"
                          f"## Residuals (x0 -> xN): {np.array_str(residuals, precision=3)} \n \n"
                          f"## Studentized Residuals (x0 -> xN): {np.array_str(studentizedResiduals, precision=3)} \n \n")
        self.fitResultText.setMarkdown(markdownString)

def run_spanc_ui() :
    mpl.use("Qt5Agg")
    app = QApplication.instance()
    if not app:
        app = QApplication(sys.argv)
        app.setStyleSheet(load_stylesheet())
    window = SpancGUI()
    sys.exit(app.exec_())