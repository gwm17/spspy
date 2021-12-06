#!/usr/bin/env python3

import SPSPlot as spsplt
import sys
from qtpy.QtWidgets import QApplication, QWidget, QMainWindow
from qtpy.QtWidgets import QLabel, QMenuBar, QAction
from qtpy.QtWidgets import QHBoxLayout, QVBoxLayout, QGroupBox
from qtpy.QtWidgets import QPushButton, QButtonGroup, QRadioButton
from qtpy.QtWidgets import QSpinBox, QDoubleSpinBox, QComboBox
from qtpy.QtWidgets import QDialog, QFileDialog, QDialogButtonBox
from qtpy.QtCore import Signal
import matplotlib as mpl
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure


class MPLCanvas(FigureCanvasQTAgg):
	def __init__(self, parent=None, width=5, height=4, dpi=100):
		self.fig = Figure(figsize=(width, height), dpi=dpi, edgecolor="black",linewidth=0.5)
		self.axes = self.fig.add_subplot(111)
		self.axes.spines['top'].set_visible(False)
		super(MPLCanvas, self).__init__(self.fig)

class ReactionDialog(QDialog):
	new_reaction = Signal(int, int, int, int, int, int)
	def __init__(self, parent=None):
		super().__init__(parent)
		self.setWindowTitle("Add A Reaction")
		QBtn = QDialogButtonBox.Ok | QDialogButtonBox.Cancel
		self.buttonBox = QDialogButtonBox(QBtn)
		self.buttonBox.accepted.connect(self.accept)
		self.buttonBox.accepted.connect(self.SendReaction)
		self.buttonBox.rejected.connect(self.reject)
		self.layout = QVBoxLayout()
		self.setLayout(self.layout)

		self.CreateReactionInputs()
		self.layout.addWidget(self.buttonBox)


	def SendReaction(self) :
		self.new_reaction.emit(self.ztInput.value(),self.atInput.value(),self.zpInput.value(),self.apInput.value(),self.zeInput.value(),self.aeInput.value())

	def CreateReactionInputs(self) :
		self.nucleiGroupBox = QGroupBox("Reaction Nuclei",self)
		inputLayout = QVBoxLayout()
		ztLabel = QLabel("ZT",self.nucleiGroupBox)
		self.ztInput = QSpinBox(self.nucleiGroupBox)
		self.ztInput.setRange(1, 110)
		atLabel = QLabel("AT",self.nucleiGroupBox)
		self.atInput = QSpinBox(self.nucleiGroupBox)
		self.atInput.setRange(1,270)
		zpLabel = QLabel("ZP",self.nucleiGroupBox)
		self.zpInput = QSpinBox(self.nucleiGroupBox)
		self.zpInput.setRange(1, 110)
		apLabel = QLabel("AP",self.nucleiGroupBox)
		self.apInput = QSpinBox(self.nucleiGroupBox)
		self.apInput.setRange(1,270)
		zeLabel = QLabel("ZE",self.nucleiGroupBox)
		self.zeInput = QSpinBox(self.nucleiGroupBox)
		self.zeInput.setRange(1, 110)
		aeLabel = QLabel("AE",self.nucleiGroupBox)
		self.aeInput = QSpinBox(self.nucleiGroupBox)
		self.aeInput.setRange(1,270)

		inputLayout.addWidget(ztLabel)
		inputLayout.addWidget(self.ztInput)
		inputLayout.addWidget(atLabel)
		inputLayout.addWidget(self.atInput)
		inputLayout.addWidget(zpLabel)
		inputLayout.addWidget(self.zpInput)
		inputLayout.addWidget(apLabel)
		inputLayout.addWidget(self.apInput)
		inputLayout.addWidget(zeLabel)
		inputLayout.addWidget(self.zeInput)
		inputLayout.addWidget(aeLabel)
		inputLayout.addWidget(self.aeInput)
		self.nucleiGroupBox.setLayout(inputLayout)
		self.layout.addWidget(self.nucleiGroupBox)


class LevelDialog(QDialog):
	new_level = Signal(str,float)
	def __init__(self, parent) :
		super().__init__(parent)
		self.setWindowTitle("Add a Level")
		QBtn = QDialogButtonBox.Ok | QDialogButtonBox.Cancel
		self.buttonBox = QDialogButtonBox(QBtn)
		self.buttonBox.accepted.connect(self.accept)
		self.buttonBox.accepted.connect(self.SendLevel)
		self.buttonBox.rejected.connect(self.reject)
		self.layout = QVBoxLayout()
		self.setLayout(self.layout)
		rxnLabel = QLabel("Choose a reaction",self)
		self.reactionList = QComboBox(self)
		for rxnName in parent.sps.reactions:
			self.reactionList.addItem(rxnName)
		stateLabel = QLabel("New state energy",self)
		self.stateInput = QDoubleSpinBox(self)
		self.stateInput.setRange(0.0,40.0)
		self.stateInput.setSuffix(" MeV")

		self.layout.addWidget(rxnLabel)
		self.layout.addWidget(self.reactionList)
		self.layout.addWidget(stateLabel)
		self.layout.addWidget(self.stateInput)
		self.layout.addWidget(self.buttonBox)

	def SendLevel(self):
		self.new_level.emit(self.reactionList.currentText(),self.stateInput.value())

		

class SPSPlotGUI(QMainWindow):
	def __init__(self, parent=None) :
		super().__init__(parent)
		self.setWindowTitle("SPSPlot")
		self.sps = spsplt.SPSPlot()

		self.generalLayout = QVBoxLayout()
		self.centralWidget = QWidget(self)
		self.setCentralWidget(self.centralWidget)
		self.centralWidget.setLayout(self.generalLayout)
		self.energyFlag = True #True = ex False = ke

		self.CreateCanvas()
		self.CreateMenus()
		self.CreateInputs()

		self.show()

	def CreateCanvas(self):
		self.canvas = MPLCanvas(self, width=14, height=5, dpi=100)
		self.generalLayout.addWidget(self.canvas, 5)

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
		newStateAction = QAction("New state...", self)
		newReactionAction = QAction("New reaction...", self)
		self.addMenu.addAction(newStateAction)
		self.addMenu.addAction(newReactionAction)
		newStateAction.triggered.connect(self.HandleNewState)
		newReactionAction.triggered.connect(self.HandleNewReaction)

	def CreateInputs(self):
		inputLayout = QHBoxLayout()
		self.inputGroupBox = QGroupBox("Adjustable Inputs", self)
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
		self.runButton = QPushButton("Run", self.inputGroupBox)
		self.runButton.clicked.connect(self.HandleRun)

		self.energyButtonGroup = QGroupBox("Ex/KE switch",self)
		buttonLayout = QHBoxLayout()
		self.exButton = QRadioButton("Excitation energy", self.energyButtonGroup)
		self.exButton.toggled.connect(self.HandleExSwitch)
		self.keButton = QRadioButton("Ejectile Kinetic energy", self.energyButtonGroup)
		self.keButton.toggled.connect(self.HandleKESwitch)
		buttonLayout.addWidget(self.exButton)
		buttonLayout.addWidget(self.keButton)
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

		self.generalLayout.addWidget(self.inputGroupBox, 1)

	def HandleSave(self):
		fileName = QFileDialog.getSaveFileName(self, "Save Input","./","Text Files (*.txt *.inp)")
		if fileName[0]:
			self.sps.WriteConfig(fileName[0])

	def HandleOpen(self):
		fileName = QFileDialog.getOpenFileName(self, "Open Input","./","Text Files (*.txt *.inp)")
		if fileName[0]:
			self.sps.ReadConfig(fileName[0])
			self.UpdateInputs()
			self.UpdatePlot()

	def HandleNewState(self):
		stDlg = LevelDialog(self)
		stDlg.new_level.connect(self.sps.AddLevel)
		if stDlg.exec():
			self.UpdatePlot()

	def HandleNewReaction(self):
		rxnDlg = ReactionDialog(self)
		rxnDlg.new_reaction.connect(self.sps.AddReaction)
		if rxnDlg.exec():
			self.UpdatePlot()

	def HandleRun(self):
		self.sps.ChangeReactionParameters(self.bkeInput.value(), self.angleInput.value(), self.bfieldInput.value())
		self.sps.rhoMin = self.rhoMinInput.value()
		self.sps.rhoMax = self.rhoMaxInput.value()
		self.UpdatePlot()

	def HandleExSwitch(self):
		if self.exButton.isChecked() and (not self.energyFlag):
			self.energyFlag = True
			self.UpdatePlot()

	def HandleKESwitch(self):
		if self.keButton.isChecked() and self.energyFlag:
			self.energyFlag = False
			self.UpdatePlot()


	def UpdatePlot(self):
		rxnNumber = 0
		rhos = []
		exs = []
		kes = []
		rxns = []		
		for rxnName in self.sps.reactions:
			rxnNumber += 1
			rxn = self.sps.reactions[rxnName]
			for i in range(len(rxn.residLevels)):
				rxns.append(rxnNumber)
				rhos.append(rxn.ejectRhovals[i])
				exs.append(rxn.residLevels[i])
				kes.append(rxn.ejectKEvals[i])

		self.canvas.axes.cla()
		self.canvas.axes.plot(rhos, rxns, marker="o", linestyle="None")
		for i in range(len(rxns)):
			y = rxns[i]
			x = rhos[i]
			label = ''
			if self.energyFlag:
				label = "{:.2f}".format(exs[i])
			else:
				label = "{:.2f}".format(kes[i])
			self.canvas.axes.annotate(label, (x,y), textcoords="offset points",xytext=(0,10),ha="center",rotation="90")
		self.canvas.axes.set_xlim(self.sps.rhoMin, self.sps.rhoMax)
		self.canvas.axes.set_yticks(range(1,rxnNumber+1))
		self.canvas.axes.set_yticklabels(self.sps.reactions)
		self.canvas.draw()

	def UpdateInputs(self):
		self.rhoMinInput.setValue(self.sps.rhoMin)
		self.rhoMaxInput.setValue(self.sps.rhoMax)
		self.bfieldInput.setValue(self.sps.Bfield)
		self.bkeInput.setValue(self.sps.beamKE)
		self.angleInput.setValue(self.sps.angle)



def main() :
	mpl.use("Qt5Agg")
	myapp = QApplication(sys.argv)
	window = SPSPlotGUI()
	sys.exit(myapp.exec_())


if __name__ == '__main__':
	main()