#!/usr/bin/env python3

from Reaction import Reaction
from qtpy.QtWidgets import QApplication, QWidget, QMainWindow
from qtpy.QtWidgets import QLabel, QMenuBar, QAction
from qtpy.QtWidgets import QHBoxLayout, QVBoxLayout, QGridLayout, QGroupBox
from qtpy.QtWidgets import QPushButton, QButtonGroup, QRadioButton
from qtpy.QtWidgets import QSpinBox, QDoubleSpinBox, QComboBox
from qtpy.QtWidgets import QDialog, QFileDialog, QDialogButtonBox
from qtpy.QtWidgets import QTableWidget, QTableWidgetItem
from qtpy.QtWidgets import QLineEdit, QTabWidget, QFormLayout
from qtpy.QtCore import Signal
import sys

class ReactionDialog(QDialog):
	new_reaction = Signal(Reaction)
	update_reaction = Signal(float, float, float, str)
	def __init__(self, parent=None, rxn=None):
		super().__init__(parent)
		self.setWindowTitle("Add A Reaction")

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

		self.CreateReactionInputs()
		if rxn is not None:
			self.SetInitialValues(rxn)
		self.layout.addWidget(self.buttonBox)


	def SendReaction(self) :
		rxn = Reaction(self.ztInput.value(), self.atInput.value(), self.zpInput.value(),self.apInput.value(),self.zeInput.value(),self.aeInput.value(), self.bkeInput.value(), self.thetaInput.value(), self.bfieldInput.value())
		self.new_reaction.emit(rxn)

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

class FPCheckGUI(QMainWindow):
	def __init__(self, parent=None):
		super().__init__(parent)
		self.setWindowTitle("FPCheck")
		self.reactions = [] #data

		self.centralLayout = QVBoxLayout()
		self.centralWidget = QWidget(self)
		self.setCentralWidget(self.centralWidget)
		self.centralWidget.setLayout(self.centralLayout)

		self.CreateMenus()
		self.CreateTable()

		self.show()

	def CreateMenus(self):
		self.fileMenu = self.menuBar().addMenu("File")
		saveAction = QAction("Save", self)
		loadAction = QAction("Load", self)
		exitAction = QAction("Exit", self)
		self.fileMenu.addAction(saveAction)
		self.fileMenu.addAction(loadAction)
		self.fileMenu.addAction(exitAction)


	def CreateTable(self):
		self.reactionTable = QTableWidget(self)
		self.reactionTable.setColumnCount(8)
		self.reactionTable.setHorizontalHeaderLabels(["Target","Projectile","Ejectile","Residual","Beam KE(MeV)","BField(kG)","Angle(deg)","FP ZOffset (cm)"])
		self.centralLayout.addWidget(self.reactionTable)
		self.reactionTable.resizeColumnsToContents()

		self.addButton = QPushButton("Add", self)
		self.addButton.clicked.connect(self.HandleAddReaction)
		self.centralLayout.addWidget(self.addButton)

	def HandleAddReaction(self):
		rxnDia = ReactionDialog(self)
		rxnDia.new_reaction.connect(self.AddReaction)
		rxnDia.exec()

	def UpdateTable(self):
		self.reactionTable.setRowCount(len(self.reactions))
		curRow = 0
		for rxn in self.reactions:
			self.reactionTable.setItem(curRow, 0, QTableWidgetItem(rxn.Target.Symbol))
			self.reactionTable.setItem(curRow, 1, QTableWidgetItem(rxn.Projectile.Symbol))
			self.reactionTable.setItem(curRow, 2, QTableWidgetItem(rxn.Ejectile.Symbol))
			self.reactionTable.setItem(curRow, 3, QTableWidgetItem(rxn.Residual.Symbol))
			self.reactionTable.setItem(curRow, 4, QTableWidgetItem(str(rxn.BKE)))
			self.reactionTable.setItem(curRow, 5, QTableWidgetItem(str(rxn.Bfield)))
			self.reactionTable.setItem(curRow, 6, QTableWidgetItem(str(rxn.Theta)))
			self.reactionTable.setItem(curRow, 7, QTableWidgetItem(str(rxn.GetFocalPlaneZOffset())))
			curRow += 1
		self.reactionTable.resizeColumnsToContents()
		self.reactionTable.resizeRowsToContents()

	def AddReaction(self, rxn):
		self.reactions.append(rxn)
		self.UpdateTable()



def main():
	myapp = QApplication(sys.argv)
	window = FPCheckGUI()
	sys.exit(myapp.exec_())

if __name__ == '__main__':
	main()
