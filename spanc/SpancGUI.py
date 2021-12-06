#!/usr/bin/env python3

import Spanc as spc
from LayeredTarget import LayeredTarget, Target
from Reaction import Reaction
import sys
from qtpy.QtWidgets import QApplication, QWidget, QMainWindow
from qtpy.QtWidgets import QLabel, QMenuBar, QAction
from qtpy.QtWidgets import QHBoxLayout, QVBoxLayout, QGridLayout, QGroupBox
from qtpy.QtWidgets import QPushButton, QButtonGroup, QRadioButton
from qtpy.QtWidgets import QSpinBox, QDoubleSpinBox, QComboBox
from qtpy.QtWidgets import QDialog, QFileDialog, QDialogButtonBox
from qtpy.QtWidgets import QTableWidget, QTableWidgetItem
from qtpy.QtWidgets import QLineEdit, QTabWidget, QFormLayout
from qtpy.QtCore import Signal
import matplotlib as mpl
import pickle as pickle
import numpy as np
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure

class MPLCanvas(FigureCanvasQTAgg):
	def __init__(self, parent=None, width=5, height=4, dpi=100):
		self.fig = Figure(figsize=(width, height), dpi=dpi, edgecolor="black",linewidth=0.5,constrained_layout=True)
		self.axes = self.fig.add_subplot(111)
		self.axes.spines['top'].set_visible(False)
		super(MPLCanvas, self).__init__(self.fig)

class TargetDialog(QDialog):
	new_target = Signal(list, str)
	def __init__(self, parent=None, target=None):
		super().__init__(parent)
		self.setWindowTitle("Add A Target")

		nameLabel = QLabel("Target name", self)
		self.nameInput = QLineEdit(self)

		QBtn = QDialogButtonBox.Ok | QDialogButtonBox.Cancel
		self.buttonBox = QDialogButtonBox(QBtn)
		self.buttonBox.accepted.connect(self.accept)
		self.buttonBox.accepted.connect(self.SendTarget)
		self.buttonBox.rejected.connect(self.reject)
		self.layout = QVBoxLayout()
		self.setLayout(self.layout)

		self.layout.addWidget(nameLabel)
		self.layout.addWidget(self.nameInput)
		self.CreateTargetInputs()
		if target is not None:
			self.SetInitialValues(target)
		self.layout.addWidget(self.buttonBox)

	def CreateTargetInputs(self):
		self.layerAInputs = []
		self.layerZInputs = []
		self.layerSInputs = []
		self.layerThickInputs = []

		self.layer1GroupBox = QGroupBox("Layer 1", self)
		layer1Layout = QVBoxLayout()
		thick1Label = QLabel("Thickness(ug/cm^2)", self.layer1GroupBox)
		self.layerThickInputs.append(QDoubleSpinBox(self.layer1GroupBox))
		self.layerThickInputs[0].setRange(0, 999.0)
		self.layerThickInputs[0].setDecimals(4)
		self.layer1ComponentsBox = QGroupBox("Layer 1 Components", self.layer1GroupBox)
		layer1compLayout = QGridLayout()
		layer1compLayout.addWidget(QLabel("Z", self.layer1ComponentsBox), 0, 1)
		layer1compLayout.addWidget(QLabel("A", self.layer1ComponentsBox), 0, 2)
		layer1compLayout.addWidget(QLabel("Stoich", self.layer1ComponentsBox), 0, 3)
		for i in range(3):
			layer1compLayout.addWidget(QLabel("Component"+str(i), self.layer1ComponentsBox), i+1, 0)
			self.layerZInputs.append(QSpinBox(self.layer1ComponentsBox))
			self.layerAInputs.append(QSpinBox(self.layer1ComponentsBox))
			self.layerSInputs.append(QSpinBox(self.layer1ComponentsBox))
			layer1compLayout.addWidget(self.layerZInputs[i], i+1, 1)
			layer1compLayout.addWidget(self.layerAInputs[i], i+1, 2)
			layer1compLayout.addWidget(self.layerSInputs[i], i+1, 3)
		self.layer1ComponentsBox.setLayout(layer1compLayout)
		layer1Layout.addWidget(thick1Label)
		layer1Layout.addWidget(self.layerThickInputs[0])
		layer1Layout.addWidget(self.layer1ComponentsBox)
		self.layer1GroupBox.setLayout(layer1Layout)

		self.layer2GroupBox = QGroupBox("Layer 2", self)
		layer2Layout = QVBoxLayout()
		thick2Label = QLabel("Thickness(ug/cm^2)", self.layer2GroupBox)
		self.layerThickInputs.append(QDoubleSpinBox(self.layer2GroupBox))
		self.layerThickInputs[1].setRange(0, 999.0)
		self.layerThickInputs[1].setDecimals(4)
		self.layer2ComponentsBox = QGroupBox("Layer 2 Components", self.layer2GroupBox)
		layer2compLayout = QGridLayout()
		layer2compLayout.addWidget(QLabel("Z", self.layer2ComponentsBox), 0, 1)
		layer2compLayout.addWidget(QLabel("A", self.layer2ComponentsBox), 0, 2)
		layer2compLayout.addWidget(QLabel("Stoich", self.layer2ComponentsBox), 0, 3)
		for i in range(3):
			layer2compLayout.addWidget(QLabel("Component"+str(i), self.layer2ComponentsBox), i+1, 0)
			self.layerZInputs.append(QSpinBox(self.layer2ComponentsBox))
			self.layerAInputs.append(QSpinBox(self.layer2ComponentsBox))
			self.layerSInputs.append(QSpinBox(self.layer2ComponentsBox))
			layer2compLayout.addWidget(self.layerZInputs[i+3], i+1, 1)
			layer2compLayout.addWidget(self.layerAInputs[i+3], i+1, 2)
			layer2compLayout.addWidget(self.layerSInputs[i+3], i+1, 3)
		self.layer2ComponentsBox.setLayout(layer2compLayout)
		layer2Layout.addWidget(thick2Label)
		layer2Layout.addWidget(self.layerThickInputs[1])
		layer2Layout.addWidget(self.layer2ComponentsBox)
		self.layer2GroupBox.setLayout(layer2Layout)

		self.layer3GroupBox = QGroupBox("Layer 3", self)
		layer3Layout = QVBoxLayout()
		thick3Label = QLabel("Thickness(ug/cm^2)", self.layer3GroupBox)
		self.layerThickInputs.append(QDoubleSpinBox(self.layer3GroupBox))
		self.layerThickInputs[2].setRange(0, 999.0)
		self.layerThickInputs[2].setDecimals(4)
		self.layer3ComponentsBox = QGroupBox("Layer 3 Components", self.layer3GroupBox)
		layer3compLayout = QGridLayout()
		layer3compLayout.addWidget(QLabel("Z", self.layer3ComponentsBox), 0, 1)
		layer3compLayout.addWidget(QLabel("A", self.layer3ComponentsBox), 0, 2)
		layer3compLayout.addWidget(QLabel("Stoich", self.layer3ComponentsBox), 0, 3)
		for i in range(3):
			layer3compLayout.addWidget(QLabel("Component"+str(i), self.layer3ComponentsBox), i+1, 0)
			self.layerZInputs.append(QSpinBox(self.layer3ComponentsBox))
			self.layerAInputs.append(QSpinBox(self.layer3ComponentsBox))
			self.layerSInputs.append(QSpinBox(self.layer3ComponentsBox))
			layer3compLayout.addWidget(self.layerZInputs[i+6], i+1, 1)
			layer3compLayout.addWidget(self.layerAInputs[i+6], i+1, 2)
			layer3compLayout.addWidget(self.layerSInputs[i+6], i+1, 3)
		self.layer3ComponentsBox.setLayout(layer3compLayout)
		layer3Layout.addWidget(thick3Label)
		layer3Layout.addWidget(self.layerThickInputs[2])
		layer3Layout.addWidget(self.layer3ComponentsBox)
		self.layer3GroupBox.setLayout(layer3Layout)

		self.layout.addWidget(self.layer1GroupBox)
		self.layout.addWidget(self.layer2GroupBox)
		self.layout.addWidget(self.layer3GroupBox)

	def SetInitialValues(self, target):
		self.nameInput.setText(target.name)
		self.nameInput.setReadOnly(True)
		for i in range(len(target.targets)):
			self.layerThickInputs[i].setValue(target.targets[i].thickness)
			for j in range(len(target.targets[i].Z)):
				self.layerZInputs[j+i*3].setValue(target.targets[i].Z[j])
				self.layerAInputs[j+i*3].setValue(target.targets[i].A[j])
				self.layerSInputs[j+i*3].setValue(target.targets[i].S[j])

	def SendTarget(self):
		name = self.nameInput.text()
		if name == "":
			return

		t1 = Target()
		t2 = Target()
		t3 = Target()
		tlist = []
		Z1 = []
		A1 = []
		S1 = []
		Z2 = []
		A2 = []
		S2 = []
		Z3 = []
		A3 = []
		S3 = []
		z = 0
		a = 0
		s = 0
		thick1 = self.layerThickInputs[0].value()
		thick2 = self.layerThickInputs[1].value()
		thick3 = self.layerThickInputs[2].value()
		for i in range(3):
			z = self.layerZInputs[i].value()
			a = self.layerAInputs[i].value()
			s = self.layerSInputs[i].value()
			if z != 0 and a != 0 and s != 0:
				Z1.append(z)
				A1.append(a)
				S1.append(s)
			z = self.layerZInputs[i+3].value()
			a = self.layerAInputs[i+3].value()
			s = self.layerSInputs[i+3].value()
			if z != 0 and a != 0 and s != 0:
				Z2.append(z)
				A2.append(a)
				S2.append(s)
			z = self.layerZInputs[i+6].value()
			a = self.layerAInputs[i+6].value()
			s = self.layerSInputs[i+6].value()
			if z != 0 and a != 0 and s != 0:
				Z3.append(z)
				A3.append(a)
				S3.append(s)
		if len(Z1) != 0:
			t1.SetElements(Z1, A1, S1, thick1)
			tlist.append(t1)
		if len(Z2) != 0:
			t2.SetElements(Z2, A2, S2, thick2)
			tlist.append(t2)
		if len(Z3) != 0:
			t3.SetElements(Z3, A3, S3, thick3)
			tlist.append(t3)

		if len(tlist) != 0:
			self.new_target.emit(tlist, name)




class ReactionDialog(QDialog):
	new_reaction = Signal(int, int, int, int, int, int, float, float, float, str)
	update_reaction = Signal(float, float, float, str)
	def __init__(self, parent=None, rxn=None, rxnKey=None):
		super().__init__(parent)
		self.setWindowTitle("Add A Reaction")

		tnameLabel = QLabel("Target Name", self)
		self.targetNameBox = QComboBox(self)
		for target in parent.spanc.targets:
			self.targetNameBox.addItem(target)

		QBtn = QDialogButtonBox.Ok | QDialogButtonBox.Cancel
		self.buttonBox = QDialogButtonBox(QBtn)
		self.buttonBox.accepted.connect(self.accept)
		if rxn is not None:
			self.buttonBox.accepted.connect(self.SendReactionUpdate)
		else:
			self.buttonBox.accepted.connect(self.SendReaction)
		self.buttonBox.rejected.connect(self.reject)
		self.layout = QVBoxLayout()
		self.setLayout(self.layout)

		self.layout.addWidget(tnameLabel)
		self.layout.addWidget(self.targetNameBox)
		self.CreateReactionInputs()
		if rxn is not None:
			self.SetInitialValues(rxn)
			self.rxnKey = rxnKey
		self.layout.addWidget(self.buttonBox)


	def SendReaction(self) :
		self.new_reaction.emit(self.ztInput.value(),self.atInput.value(),self.zpInput.value(),self.apInput.value(),self.zeInput.value(),self.aeInput.value(), self.bkeInput.value(), self.thetaInput.value(), self.bfieldInput.value(), self.targetNameBox.currentText())

	def SendReactionUpdate(self):
		self.update_reaction.emit(self.bkeInput.value(), self.thetaInput.value(), self.bfieldInput.value(), self.rxnKey)

	def CreateReactionInputs(self) :
		self.nucleiGroupBox = QGroupBox("Reaction Nuclei",self)
		inputLayout = QFormLayout()
		self.ztInput = QSpinBox(self.nucleiGroupBox)
		self.ztInput.setRange(1, 110)
		self.atInput = QSpinBox(self.nucleiGroupBox)
		self.atInput.setRange(1,270)
		self.zpInput = QSpinBox(self.nucleiGroupBox)
		self.zpInput.setRange(1, 110)
		self.apInput = QSpinBox(self.nucleiGroupBox)
		self.apInput.setRange(1,270)
		self.zeInput = QSpinBox(self.nucleiGroupBox)
		self.zeInput.setRange(1, 110)
		self.aeInput = QSpinBox(self.nucleiGroupBox)
		self.aeInput.setRange(1,270)

		inputLayout.addRow("ZT",self.ztInput)
		inputLayout.addRow("AT",self.atInput)
		inputLayout.addRow("ZP",self.zpInput)
		inputLayout.addRow("AP",self.apInput)
		inputLayout.addRow("ZE",self.zeInput)
		inputLayout.addRow("AE",self.aeInput)

		self.parameterGroupBox = QGroupBox("Reaction Parameters", self)
		parameterLayout = QFormLayout()
		self.bkeInput = QDoubleSpinBox(self.parameterGroupBox)
		self.bkeInput.setRange(0.0, 40.0)
		self.bkeInput.setDecimals(4)
		self.thetaInput = QDoubleSpinBox(self.parameterGroupBox)
		self.thetaInput.setRange(0.0, 180.0)
		self.thetaInput.setDecimals(4)
		self.bfieldInput = QDoubleSpinBox(self.parameterGroupBox)
		self.bfieldInput.setRange(0.0, 16.0)
		self.bfieldInput.setDecimals(6)

		parameterLayout.addRow("Beam KE(Mev)",self.bkeInput)
		parameterLayout.addRow("Theta(deg)",self.thetaInput)
		parameterLayout.addRow("Bfield(kG)",self.bfieldInput)


		self.nucleiGroupBox.setLayout(inputLayout)
		self.parameterGroupBox.setLayout(parameterLayout)

		self.layout.addWidget(self.nucleiGroupBox)
		self.layout.addWidget(self.parameterGroupBox)

	def SetInitialValues(self, rxn):
		self.targetNameBox.setCurrentIndex(self.targetNameBox.findText(rxn.target_data.name))
		self.targetNameBox.setEnabled(False)
		self.ztInput.setValue(rxn.Target.Z)
		self.ztInput.setEnabled(False)
		self.atInput.setValue(rxn.Target.A)
		self.atInput.setEnabled(False)
		self.zpInput.setValue(rxn.Projectile.Z)
		self.zpInput.setEnabled(False)
		self.apInput.setValue(rxn.Projectile.A)
		self.apInput.setEnabled(False)
		self.zeInput.setValue(rxn.Ejectile.Z)
		self.zeInput.setEnabled(False)
		self.aeInput.setValue(rxn.Ejectile.A)
		self.aeInput.setEnabled(False)
		self.bkeInput.setValue(rxn.BKE)
		self.thetaInput.setValue(rxn.Theta/rxn.DEG2RAD)
		self.bfieldInput.setValue(rxn.Bfield)
		

class PeakDialog(QDialog):
	new_calibration = Signal(float, float, float, float, float, str)
	update_calibration = Signal(float, float, float, float, float, str, str)
	new_output = Signal(float, float, float, float, float, str)
	update_output = Signal(float, float, float, float, float, str, str)
	def __init__(self, peakType, parent=None, peak=None, peakKey=None):
		super().__init__(parent)
		self.setWindowTitle("Add A "+peakType+" Peak")

		rnameLabel = QLabel("Reaction Name", self)
		self.rxnNameBox = QComboBox(self)
		for reaction in parent.spanc.reactions:
			self.rxnNameBox.addItem(reaction)

		QBtn = QDialogButtonBox.Ok | QDialogButtonBox.Cancel
		self.buttonBox = QDialogButtonBox(QBtn)
		self.buttonBox.accepted.connect(self.accept)
		if peak is not None and peakType == "Calibration":
			self.buttonBox.accepted.connect(self.SendUpdateCalibrationPeak)
		elif peakType == "Calibration":
			self.buttonBox.accepted.connect(self.SendCalibrationPeak)
		elif peak is not None and peakType == "Output":
			self.buttonBox.accepted.connect(self.SendUpdateOutputPeak)
		elif peakType == "Output":
			self.buttonBox.accepted.connect(self.SendOutputPeak)
		self.buttonBox.rejected.connect(self.reject)
		self.layout = QVBoxLayout()
		self.setLayout(self.layout)

		self.layout.addWidget(rnameLabel)
		self.layout.addWidget(self.rxnNameBox)
		if peakType == "Calibration":
			self.CreateCalibrationInputs()
			if peak is not None:
				self.peakKey = peakKey
				self.SetCalibrationInputs(peak)
		elif peakType == "Output":
			self.CreateOutputInputs()
			if peak is not None:
				self.peakKey = peakKey
				self.SetOutputInputs(peak)
		self.layout.addWidget(self.buttonBox)

	def CreateCalibrationInputs(self):
		self.inputGroupBox = QGroupBox("Peak Parameters",self)
		inputLayout = QFormLayout()
		self.xInput = QDoubleSpinBox(self.inputGroupBox)
		self.xInput.setRange(-999, 999)
		self.xInput.setDecimals(6)
		self.uxsysInput = QDoubleSpinBox(self.inputGroupBox)
		self.uxsysInput.setRange(-999, 999)
		self.uxsysInput.setDecimals(6)
		self.uxstatInput = QDoubleSpinBox(self.inputGroupBox)
		self.uxstatInput.setRange(-999, 999)
		self.uxstatInput.setDecimals(6)
		self.exInput = QDoubleSpinBox(self.inputGroupBox)
		self.exInput.setDecimals(6)
		self.uexInput = QDoubleSpinBox(self.inputGroupBox)
		self.uexInput.setDecimals(6)

		inputLayout.addRow("Position(mm)", self.xInput)
		inputLayout.addRow("Position Stat. Error(mm)", self.uxstatInput)
		inputLayout.addRow("Position Sys. Error(mm)", self.uxsysInput)
		inputLayout.addRow("Excitation Energy(MeV)", self.exInput)
		inputLayout.addRow("Excitation Energy Error(MeV)", self.uexInput)

		self.inputGroupBox.setLayout(inputLayout)

		self.layout.addWidget(self.inputGroupBox)

	def CreateOutputInputs(self):
		self.inputGroupBox = QGroupBox("Peak Parameters",self)
		inputLayout = QFormLayout()
		self.xInput = QDoubleSpinBox(self.inputGroupBox)
		self.xInput.setRange(-999, 999)
		self.xInput.setDecimals(6)
		self.uxsysInput = QDoubleSpinBox(self.inputGroupBox)
		self.uxsysInput.setRange(-999, 999)
		self.uxsysInput.setDecimals(6)
		self.uxstatInput = QDoubleSpinBox(self.inputGroupBox)
		self.uxstatInput.setRange(-999, 999)
		self.uxstatInput.setDecimals(6)
		self.fwhmInput = QDoubleSpinBox(self.inputGroupBox)
		self.fwhmInput.setDecimals(6)
		self.ufwhmInput = QDoubleSpinBox(self.inputGroupBox)
		self.ufwhmInput.setDecimals(6)

		inputLayout.addRow("Position(mm)", self.xInput)
		inputLayout.addRow("Position Stat. Error(mm)", self.uxstatInput)
		inputLayout.addRow("Position Sys. Error(mm)", self.uxsysInput)
		inputLayout.addRow("Position FWHM(mm)", self.fwhmInput)
		inputLayout.addRow("Position FWHM Error(mm)", self.ufwhmInput)

		self.inputGroupBox.setLayout(inputLayout)

		self.layout.addWidget(self.inputGroupBox)

	def SetCalibrationInputs(self, peak):
		self.rxnNameBox.setCurrentIndex(self.rxnNameBox.findText(peak.reaction))
		self.xInput.setValue(peak.x)
		self.uxsysInput.setValue(peak.ux_sys)
		self.uxstatInput.setValue(peak.ux_stat)
		self.exInput.setValue(peak.Ex)
		self.uexInput.setValue(peak.uEx)

	def SetOutputInputs(self, peak):
		self.rxnNameBox.setCurrentIndex(self.rxnNameBox.findText(peak.reaction))
		self.xInput.setValue(peak.x)
		self.uxsysInput.setValue(peak.ux_sys)
		self.uxstatInput.setValue(peak.ux_stat)
		self.fwhmInput.setValue(peak.fwhm_x)
		self.ufwhmInput.setValue(peak.ufwhm_x)

	def SendCalibrationPeak(self):
		self.new_calibration.emit(self.xInput.value(), self.uxstatInput.value(),  self.uxsysInput.value(), self.exInput.value(), self.uexInput.value(), self.rxnNameBox.currentText())
	
	def SendUpdateCalibrationPeak(self):
		self.update_calibration.emit(self.xInput.value(), self.uxstatInput.value(),  self.uxsysInput.value(), self.exInput.value(), self.uexInput.value(), self.rxnNameBox.currentText(),self.peakKey)
	
	def SendOutputPeak(self):
		self.new_output.emit(self.xInput.value(), self.uxstatInput.value(),  self.uxsysInput.value(), self.fwhmInput.value(), self.ufwhmInput.value(), self.rxnNameBox.currentText())

	def SendUpdateOutputPeak(self):
		self.update_output.emit(self.xInput.value(), self.uxstatInput.value(),  self.uxsysInput.value(), self.fwhmInput.value(), self.ufwhmInput.value(), self.rxnNameBox.currentText(),self.peakKey)

class SpancGUI(QMainWindow):
	def __init__(self, parent=None):
		super().__init__(parent)
		self.setWindowTitle("SPANC")
		self.spanc = spc.Spanc()

		self.tablelayout = QVBoxLayout()
		self.plotlayout = QGridLayout() #2x2 grid
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


		self.CreateMenus()
		self.CreateFitCanvas() #(0,0)
		self.CreateResidualCanvas() #(1,0)
		self.CreateTargetTable() 
		self.CreateReactionTable()
		self.CreateCalibrationTable()
		self.CreateOutputTable()
		self.CreateFitTable() #(0,1)
		self.CreateResidualTable() #(1,1)

		self.show()

	def CreateMenus(self):
		self.fileMenu = self.menuBar().addMenu("&File")
		saveAction = QAction("&Save...",self)
		openAction = QAction("&Open...",self)
		self.fileMenu.addAction(saveAction)
		self.fileMenu.addAction(openAction)
		self.fileMenu.addAction("&Exit", self.close)
		saveAction.triggered.connect(self.HandleSave)
		openAction.triggered.connect(self.HandleOpen)
		
		self.addMenu = self.menuBar().addMenu("&New")
		newTargetAction = QAction("New target...", self)
		newReactionAction = QAction("New reaction...", self)
		newCalibrationAction = QAction("New calibration...", self)
		newOutputAction = QAction("New output...", self)
		self.addMenu.addAction(newTargetAction)
		self.addMenu.addAction(newReactionAction)
		self.addMenu.addAction(newCalibrationAction)
		self.addMenu.addAction(newOutputAction)
		newTargetAction.triggered.connect(self.HandleNewTarget)
		newReactionAction.triggered.connect(self.HandleNewReaction)
		newCalibrationAction.triggered.connect(self.HandleNewCalibration)
		newOutputAction.triggered.connect(self.HandleNewOutput)

	def CreateFitCanvas(self):
		self.fitGroup = QGroupBox("Calibration Fit", self.plotTab)
		fitLayout = QVBoxLayout()
		self.fitCanvas = MPLCanvas(self.fitGroup, width=6, height=6, dpi=100)
		self.fitOptionGroup = QGroupBox("Fit options", self.fitGroup)
		fitOptionLayout = QHBoxLayout()
		self.fitButton = QPushButton("Run Fit", self.fitOptionGroup)
		self.fitButton.clicked.connect(self.HandleRunFit)
		self.fitTypeBox = QComboBox(self.fitOptionGroup)
		self.fitTypeBox.addItem("linear")
		self.fitTypeBox.addItem("quadratic")
		self.fitTypeBox.addItem("cubic")

		fitOptionLayout.addWidget(QLabel("Fit type", self.fitOptionGroup))
		fitOptionLayout.addWidget(self.fitTypeBox)
		fitOptionLayout.addWidget(self.fitButton)
		self.fitOptionGroup.setLayout(fitOptionLayout)

		fitLayout.addWidget(self.fitCanvas)
		fitLayout.addWidget(self.fitOptionGroup)
		self.fitGroup.setLayout(fitLayout)

		self.plotlayout.addWidget(self.fitGroup,0,0)

	def CreateResidualCanvas(self):
		self.residGroup = QGroupBox("Fit Residuals", self.plotTab)
		residLayout = QVBoxLayout()
		self.residCanvas = MPLCanvas(self.residGroup, width=6, height=6, dpi=100)
		self.residOptionGroup = QGroupBox("Fit options", self.residGroup)
		residOptionLayout = QHBoxLayout()
		self.residButton = QPushButton("Run Resids.", self.residOptionGroup)
		self.residButton.clicked.connect(self.HandleRunResids)

		residOptionLayout.addWidget(self.residButton)
		self.residOptionGroup.setLayout(residOptionLayout)

		residLayout.addWidget(self.residCanvas)
		residLayout.addWidget(self.residOptionGroup)
		self.residGroup.setLayout(residLayout)

		self.plotlayout.addWidget(self.residGroup,1,0)

	def CreateTargetTable(self):
		self.targetGroup = QGroupBox("Targets", self.tableTab)
		targetLayout = QVBoxLayout()
		self.targetTable = QTableWidget(self.targetGroup)
		self.targetTable.setColumnCount(6)
		self.targetTable.setHorizontalHeaderLabels(["Layer1 Thickness(ug/cm^2", "Layer1 (Z, A, S)","Layer2 Thickness(ug/cm^2", "Layer2 (Z, A, S)","Layer3 Thickness(ug/cm^2", "Layer3 (Z, A, S)"])
		targetLayout.addWidget(self.targetTable)
		self.targetGroup.setLayout(targetLayout)
		self.tablelayout.addWidget(self.targetGroup)
		self.targetTable.resizeColumnsToContents()
		self.targetTable.cellDoubleClicked.connect(self.HandleUpdateTarget)

	def CreateReactionTable(self):
		self.rxnGroup = QGroupBox("Reactions", self.tableTab)
		rxnLayout = QVBoxLayout()
		self.reactionTable = QTableWidget(self.rxnGroup)
		self.reactionTable.setColumnCount(12)
		self.reactionTable.setHorizontalHeaderLabels(["Target","ZT","AT","ZP","AP","ZE","AE","ZR","AR","Beam KE(MeV)","BField(kG)","Angle(deg)"])
		rxnLayout.addWidget(self.reactionTable)
		self.rxnGroup.setLayout(rxnLayout)
		self.tablelayout.addWidget(self.rxnGroup)
		self.reactionTable.resizeColumnsToContents()
		self.reactionTable.cellDoubleClicked.connect(self.HandleUpdateReaction)

	def CreateCalibrationTable(self):
		self.calGroup = QGroupBox("Calibration Peaks", self.tableTab)
		calLayout = QVBoxLayout()
		self.calibrationTable = QTableWidget(self.calGroup)
		self.calibrationTable.setColumnCount(8)
		self.calibrationTable.setHorizontalHeaderLabels(["Reaction","x(mm)","ux stat.(mm)","ux sys.(mm)","rho(cm)","urho(cm)","Ex(MeV)","uEx(MeV)"])
		calLayout.addWidget(self.calibrationTable)
		self.calGroup.setLayout(calLayout)
		self.tablelayout.addWidget(self.calGroup)
		self.calibrationTable.resizeColumnsToContents()
		self.calibrationTable.cellDoubleClicked.connect(self.HandleUpdateCalibration)

	def CreateOutputTable(self):
		self.outGroup = QGroupBox("Output Peaks", self.tableTab)
		outLayout = QVBoxLayout()
		self.outputTable = QTableWidget(self.outGroup)
		self.outputTable.setColumnCount(12)
		self.outputTable.setHorizontalHeaderLabels(["Reaction","x(mm)","ux stat.(mm)","ux sys.(mm)","rho(cm)","urho(cm)","Ex(MeV)","uEx(MeV)","FWHM(mm)","uFWHM(mm)","FWHM(MeV)","uFWHM(MeV)"])
		outLayout.addWidget(self.outputTable)
		self.outGroup.setLayout(outLayout)
		self.tablelayout.addWidget(self.outGroup)
		self.outputTable.resizeColumnsToContents()
		self.outputTable.cellDoubleClicked.connect(self.HandleUpdateOutput)

	def CreateFitTable(self):
		self.ftableGroup = QGroupBox("Fit Results", self.plotTab)
		ftableLayout = QVBoxLayout()
		self.fitTable = QTableWidget(3, 9, self.ftableGroup)
		self.fitTable.setHorizontalHeaderLabels(["a0","ua0","a1","ua1","a2","ua2","a3","ua3","Chi Sq./NDF"])
		self.fitTable.setVerticalHeaderLabels(["linear","quadratic","cubic"])
		ftableLayout.addWidget(self.fitTable)
		self.ftableGroup.setLayout(ftableLayout)
		self.plotlayout.addWidget(self.ftableGroup,0,1)
		self.fitTable.resizeColumnsToContents()

	def CreateResidualTable(self):
		self.rtableGroup = QGroupBox("Residual Results", self.plotTab)
		rtableLayout = QVBoxLayout()
		self.residualTable = QTableWidget(self.rtableGroup)
		self.residualTable.setColumnCount(5)
		self.residualTable.setHorizontalHeaderLabels(["x(mm)","rho calc(cm)","rho fit(cm)","residual(cm)","studentized residual"])
		rtableLayout.addWidget(self.residualTable)
		self.rtableGroup.setLayout(rtableLayout)
		self.plotlayout.addWidget(self.rtableGroup,1,1)
		self.residualTable.resizeColumnsToContents()

	def HandleSave(self):
		fileName = QFileDialog.getSaveFileName(self, "Save Input","./","Text Files (*.pickle)")
		if fileName[0]:
			#self.spanc.WriteConfig(fileName[0])
			with open(fileName[0], "wb") as savefile:
				pickle.dump(self.spanc, savefile, pickle.HIGHEST_PROTOCOL)
				savefile.close()

	def HandleOpen(self):
		fileName = QFileDialog.getOpenFileName(self, "Open Input","./","Text Files (*.pickle)")
		if fileName[0]:
			with open(fileName[0], "rb") as openfile:
				self.spanc = pickle.load(openfile)
				self.UpdateTargetTable()
				self.UpdateReactionTable()
				self.UpdateCalibrationTable()
				self.UpdateOutputTable()
				openfile.close()

	def HandleNewTarget(self):
		targDia = TargetDialog(self)
		targDia.new_target.connect(self.AddTarget)
		targDia.exec()
		return

	def HandleUpdateTarget(self, row, col):
		targName = self.targetTable.verticalHeaderItem(row).text()
		targDia = TargetDialog(self, target=self.spanc.targets[targName])
		targDia.new_target.connect(self.UpdateTarget)
		targDia.exec()
		return

	def HandleNewReaction(self):
		rxnDia = ReactionDialog(self)
		rxnDia.new_reaction.connect(self.AddReaction)
		rxnDia.exec()
		return

	def HandleUpdateReaction(self, row, col):
		rxnName = self.reactionTable.verticalHeaderItem(row).text()
		rxnDia = ReactionDialog(self, rxn=self.spanc.reactions[rxnName], rxnKey=rxnName)
		rxnDia.update_reaction.connect(self.UpdateReaction)
		rxnDia.exec()
		return

	def HandleNewCalibration(self):
		calDia = PeakDialog("Calibration", self)
		calDia.new_calibration.connect(self.AddCalibration)
		calDia.exec()
		return

	def HandleUpdateCalibration(self, row, col):
		peakName = self.calibrationTable.verticalHeaderItem(row).text()
		calDia = PeakDialog("Calibration", self, peak=self.spanc.calib_peaks[peakName], peakKey=peakName)
		calDia.update_calibration.connect(self.UpdateCalibration)
		calDia.exec()
		return

	def HandleNewOutput(self):
		outDia = PeakDialog("Output", self)
		outDia.new_output.connect(self.AddOutput)
		outDia.exec()
		return

	def HandleUpdateOutput(self, row, col):
		peakName = self.outputTable.verticalHeaderItem(row).text()
		outDia = PeakDialog("Output",self,peak=self.spanc.output_peaks[peakName],peakKey=peakName)
		outDia.update_output.connect(self.UpdateOutput)
		outDia.exec()
		return

	def HandleRunFit(self):
		fit_type = self.fitTypeBox.currentText()
		npoints = len(self.spanc.calib_peaks)
		if npoints < 3 and fit_type == "linear":
			print("Warning! Too few points to properly fit a linear function. Results are invalid.")
		elif npoints < 4 and fit_type == "quadratic":
			print("Warning! Too few points to properly fit a quadratic function. Results are invalid")
		elif npoints < 5 and fit_type == "cubic":
			print("Warning! Too few points to properly fit a cubic function. Results are invalid")

		xarray, yarray, uxarray, uyarray = self.spanc.PerformFits()
		fitarray = np.linspace(np.amin(xarray), np.amax(xarray), 1000)
		self.fitCanvas.axes.cla()
		self.fitCanvas.axes.errorbar(xarray, yarray, yerr=uyarray, xerr=uxarray, marker="o", linestyle="None")
		self.fitCanvas.axes.plot(fitarray, self.spanc.fitters[fit_type].EvaluateFunction(fitarray))
		self.fitCanvas.axes.set_xlabel(r"$x$ (mm)")
		self.fitCanvas.axes.set_ylabel(r"$\rho$ (cm)")
		self.fitCanvas.draw()

		self.UpdateFitTable()
		self.spanc.CalculateOutputs(fit_type)
		self.UpdateOutputTable()
		self.fitFlag = True

	def HandleRunResids(self):
		fit_type = self.fitTypeBox.currentText()
		npoints = len(self.spanc.calib_peaks)
		if npoints < 3 and fit_type == "linear":
			print("Warning! Too few points to properly fit a linear function. Results are invalid.")
		elif npoints < 4 and fit_type == "quadratic":
			print("Warning! Too few points to properly fit a quadratic function. Results are invalid")
		elif npoints < 5 and fit_type == "cubic":
			print("Warning! Too few points to properly fit a cubic function. Results are invalid")

		xarray, resid_array, student_resids = self.spanc.CalculateResiduals(fit_type)
		self.residCanvas.axes.cla()
		self.residCanvas.axes.plot(xarray, resid_array, marker="o", linestyle="None")
		self.residCanvas.axes.set_xlabel(r"$x$ (mm)")
		self.residCanvas.axes.set_ylabel(r"Residual (cm)")
		self.residCanvas.draw()
		self.UpdateResidualTable(resid_array, student_resids)


	def AddTarget(self, layers, name):
		target = LayeredTarget()
		target.name = name
		for layer in layers:
			target.AddLayer(layer)
		self.spanc.targets[target.name] = target
		self.UpdateTargetTable()

	def UpdateTarget(self, layers, name):
		target = LayeredTarget()
		target.name = name
		for layer in layers:
			target.AddLayer(layer)
		self.spanc.targets[target.name] = target
		for rxn in self.spanc.reactions.values():
			if rxn.target_data.name == name:
				rxn.target_data = target
		self.UpdateTargetTable()
		self.spanc.CalculateCalibrations()
		self.UpdateReactionTable()
		self.UpdateCalibrationTable()
		if self.fitFlag is True:
			self.spanc.CalculateOutputs(self.fitTypeBox.currentText())
			self.UpdateOutputTable()

	def UpdateTargetTable(self):
		self.targetTable.setRowCount(len(self.spanc.targets))
		self.targetTable.setVerticalHeaderLabels(self.spanc.targets.keys())
		cur_row = 0
		for key in self.spanc.targets:
			for i in range(len(self.spanc.targets[key].targets)) :
				self.targetTable.setItem(cur_row, 0+i*2, QTableWidgetItem(str(self.spanc.targets[key].targets[i].thickness)))
				self.targetTable.setItem(cur_row, 1+i*2, QTableWidgetItem(self.spanc.targets[key].targets[i].GetComposition()))
			cur_row += 1
		self.targetTable.resizeColumnsToContents()
		self.targetTable.resizeRowsToContents()

	def AddReaction(self, zt, at, zp, ap, ze, ae, bke, theta, bfield, name):
		targ = self.spanc.targets[name]
		rxn = Reaction(zt, at, zp, ap, ze, ae, bke, theta, bfield, targ)
		count=0
		for key in self.spanc.reactions:
			if key == rxn.Name:
				count += 1
		rxn.Name = rxn.Name + "_" + str(count)
		self.spanc.reactions[rxn.Name] = rxn
		self.UpdateReactionTable()

	def UpdateReaction(self, bke, theta, bfield, key):
		self.spanc.reactions[key].ChangeReactionParameters(bke, theta, bfield)
		self.UpdateReactionTable()
		self.spanc.CalculateCalibrations()
		self.UpdateCalibrationTable()
		if self.fitFlag is True:
			self.spanc.CalculateOutputs(self.fitTypeBox.currentText())
			self.UpdateOutputTable()

	def UpdateReactionTable(self):
		self.reactionTable.setRowCount(len(self.spanc.reactions))
		self.reactionTable.setVerticalHeaderLabels(self.spanc.reactions.keys())
		cur_row = 0
		for key in self.spanc.reactions:
			self.reactionTable.setItem(cur_row, 0, QTableWidgetItem(str(self.spanc.reactions[key].target_data.name)))
			self.reactionTable.setItem(cur_row, 1, QTableWidgetItem(str(self.spanc.reactions[key].Target.Z)))
			self.reactionTable.setItem(cur_row, 2, QTableWidgetItem(str(self.spanc.reactions[key].Target.A)))
			self.reactionTable.setItem(cur_row, 3, QTableWidgetItem(str(self.spanc.reactions[key].Projectile.Z)))
			self.reactionTable.setItem(cur_row, 4, QTableWidgetItem(str(self.spanc.reactions[key].Projectile.A)))
			self.reactionTable.setItem(cur_row, 5, QTableWidgetItem(str(self.spanc.reactions[key].Ejectile.Z)))
			self.reactionTable.setItem(cur_row, 6, QTableWidgetItem(str(self.spanc.reactions[key].Ejectile.A)))
			self.reactionTable.setItem(cur_row, 7, QTableWidgetItem(str(self.spanc.reactions[key].Residual.Z)))
			self.reactionTable.setItem(cur_row, 8, QTableWidgetItem(str(self.spanc.reactions[key].Residual.A)))
			self.reactionTable.setItem(cur_row, 9, QTableWidgetItem(str(self.spanc.reactions[key].BKE)))
			self.reactionTable.setItem(cur_row, 10, QTableWidgetItem(str(self.spanc.reactions[key].Bfield)))
			self.reactionTable.setItem(cur_row, 11, QTableWidgetItem(str(self.spanc.reactions[key].Theta/self.spanc.reactions[key].DEG2RAD)))
			cur_row += 1
		self.reactionTable.resizeColumnsToContents()
		self.reactionTable.resizeRowsToContents()

	def AddCalibration(self, x, uxstat, uxsys, ex, uex, rxnname):
		peak_name = "Cal" + str(len(self.spanc.calib_peaks))
		self.spanc.AddCalibrationPeak(rxnname, peak_name, x, uxstat, uxsys, ex, uex)
		self.UpdateCalibrationTable()

	def UpdateCalibration(self, x, uxstat, uxsys, ex, uex, rxnname, peakname):
		self.spanc.AddCalibrationPeak(rxnname, peakname, x, uxstat, uxsys, ex, uex)
		self.UpdateCalibrationTable()
		

	def UpdateCalibrationTable(self):
		self.calibrationTable.setRowCount(len(self.spanc.calib_peaks))
		self.calibrationTable.setVerticalHeaderLabels(self.spanc.calib_peaks.keys())
		cur_row = 0
		for key in self.spanc.calib_peaks:
			self.calibrationTable.setItem(cur_row, 0, QTableWidgetItem(self.spanc.calib_peaks[key].reaction))
			self.calibrationTable.setItem(cur_row, 1, QTableWidgetItem(str(self.spanc.calib_peaks[key].x)))
			self.calibrationTable.setItem(cur_row, 2, QTableWidgetItem(str(self.spanc.calib_peaks[key].ux_stat)))
			self.calibrationTable.setItem(cur_row, 3, QTableWidgetItem(str(self.spanc.calib_peaks[key].ux_sys)))
			self.calibrationTable.setItem(cur_row, 4, QTableWidgetItem(str(self.spanc.calib_peaks[key].rho)))
			self.calibrationTable.setItem(cur_row, 5, QTableWidgetItem(str(self.spanc.calib_peaks[key].urho)))
			self.calibrationTable.setItem(cur_row, 6, QTableWidgetItem(str(self.spanc.calib_peaks[key].Ex)))
			self.calibrationTable.setItem(cur_row, 7, QTableWidgetItem(str(self.spanc.calib_peaks[key].uEx)))
			cur_row += 1
		self.calibrationTable.resizeColumnsToContents()
		self.calibrationTable.resizeRowsToContents()

	def AddOutput(self, x, uxstat, uxsys, fwhm, ufwhm, rxnname):
		peak_name = "Out" + str(len(self.spanc.output_peaks))
		self.spanc.AddOutputPeak(rxnname, peak_name, x, uxstat, uxsys, fwhm, ufwhm)
		self.UpdateOutputTable()

	def UpdateOutput(self, x, uxstat, uxsys, fwhm, ufwhm, rxnname, peakname):
		self.spanc.AddOutputPeak(rxnname, peakname, x, uxstat, uxsys, fwhm, ufwhm)
		self.UpdateOutputTable()

	def UpdateOutputTable(self):
		self.outputTable.setRowCount(len(self.spanc.output_peaks))
		self.outputTable.setVerticalHeaderLabels(self.spanc.output_peaks.keys())
		cur_row = 0
		for key in self.spanc.output_peaks:
			self.outputTable.setItem(cur_row, 0, QTableWidgetItem(self.spanc.output_peaks[key].reaction))
			self.outputTable.setItem(cur_row, 1, QTableWidgetItem(str(self.spanc.output_peaks[key].x)))
			self.outputTable.setItem(cur_row, 2, QTableWidgetItem(str(self.spanc.output_peaks[key].ux_stat)))
			self.outputTable.setItem(cur_row, 3, QTableWidgetItem(str(self.spanc.output_peaks[key].ux_sys)))
			self.outputTable.setItem(cur_row, 4, QTableWidgetItem(str(self.spanc.output_peaks[key].rho)))
			self.outputTable.setItem(cur_row, 5, QTableWidgetItem(str(self.spanc.output_peaks[key].urho)))
			self.outputTable.setItem(cur_row, 6, QTableWidgetItem(str(self.spanc.output_peaks[key].Ex)))
			self.outputTable.setItem(cur_row, 7, QTableWidgetItem(str(self.spanc.output_peaks[key].uEx)))
			self.outputTable.setItem(cur_row, 8, QTableWidgetItem(str(self.spanc.output_peaks[key].fwhm_x)))
			self.outputTable.setItem(cur_row, 9, QTableWidgetItem(str(self.spanc.output_peaks[key].ufwhm_x)))
			self.outputTable.setItem(cur_row, 10, QTableWidgetItem(str(self.spanc.output_peaks[key].fwhm_Ex)))
			self.outputTable.setItem(cur_row, 11, QTableWidgetItem(str(self.spanc.output_peaks[key].ufwhm_Ex)))
			cur_row += 1
		self.outputTable.resizeColumnsToContents()
		self.outputTable.resizeRowsToContents()

	def UpdateFitTable(self):
		cur_row=0
		for key in self.spanc.fitters:
			for i in range(len(self.spanc.fitters[key].parameters)):
				self.fitTable.setItem(cur_row, 0+i*2, QTableWidgetItem(str(self.spanc.fitters[key].parameters[i])))
				self.fitTable.setItem(cur_row, 1+i*2, QTableWidgetItem(str(self.spanc.fitters[key].GetParameterError(i))))
			#self.fitTable.setItem(cur_row, 8, QTableWidgetItem(str(self.spanc.fitters[key].redChiSq)))
			self.fitTable.setItem(cur_row, 8, QTableWidgetItem(str(self.spanc.fitters[key].ReducedChiSquare())))
			cur_row += 1
		self.fitTable.resizeColumnsToContents()
		self.fitTable.resizeRowsToContents()

	def UpdateResidualTable(self, resids, student_resids):
		self.residualTable.setRowCount(len(self.spanc.calib_peaks))
		self.residualTable.setVerticalHeaderLabels(self.spanc.calib_peaks.keys())
		cur_row=0
		for key in self.spanc.calib_peaks:
			self.residualTable.setItem(cur_row, 0, QTableWidgetItem(str(self.spanc.calib_peaks[key].x)))
			self.residualTable.setItem(cur_row, 1, QTableWidgetItem(str(self.spanc.calib_peaks[key].rho)))
			self.residualTable.setItem(cur_row, 2, QTableWidgetItem(str(self.spanc.calib_peaks[key].rho + resids[cur_row])))
			self.residualTable.setItem(cur_row, 3, QTableWidgetItem(str(resids[cur_row])))
			self.residualTable.setItem(cur_row, 4, QTableWidgetItem(str(student_resids[cur_row])))
			cur_row += 1
		self.residualTable.resizeColumnsToContents()
		self.residualTable.resizeRowsToContents()

def main() :
	mpl.use("Qt5Agg")
	myapp = QApplication(sys.argv)
	window = SpancGUI()
	sys.exit(myapp.exec_())


if __name__ == '__main__':
	main()