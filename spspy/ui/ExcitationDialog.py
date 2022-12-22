from PySide6.QtWidgets import QLabel
from PySide6.QtWidgets import QVBoxLayout
from PySide6.QtWidgets import QDoubleSpinBox, QListWidget, QListWidgetItem
from PySide6.QtWidgets import QDialog, QDialogButtonBox
from PySide6.QtWidgets import QAbstractItemView
from PySide6.QtCore import Signal

class ExcitationDialog(QDialog):
    new_level = Signal(str,float)

    def __init__(self, parent, rxnList: list[str]) :
        super().__init__(parent)
        self.setWindowTitle("Add an Excitation")
        QBtn = QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        self.buttonBox = QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.accepted.connect(self.send_level)
        self.buttonBox.rejected.connect(self.reject)
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        rxnLabel = QLabel("Choose a reaction",self)
        self.reactionList = QListWidget(self)
        self.reactionList.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        for rxnName in rxnList:
            item = QListWidgetItem(rxnName)
            item.setText("")
            self.reactionList.addItem(item)
            self.reactionList.setItemWidget(item, QLabel(rxnName))
        stateLabel = QLabel("New state energy",self)
        self.stateInput = QDoubleSpinBox(self)
        self.stateInput.setRange(0.0,40.0)
        self.stateInput.setSuffix(" MeV")
        self.layout.addWidget(rxnLabel)
        self.layout.addWidget(self.reactionList)
        self.layout.addWidget(stateLabel)
        self.layout.addWidget(self.stateInput)
        self.layout.addWidget(self.buttonBox)

    def send_level(self) -> None:
        items = self.reactionList.selectedItems()
        if len(items) == 1:
            self.new_level.emit(self.reactionList.itemWidget(items[0]).text(),self.stateInput.value())