from ..SPSTarget import SPSTarget, TargetLayer
from PySide6.QtWidgets import QLabel, QLineEdit
from PySide6.QtWidgets import QHBoxLayout, QVBoxLayout, QGridLayout, QGroupBox
from PySide6.QtWidgets import QSpinBox, QDoubleSpinBox
from PySide6.QtWidgets import QDialog, QDialogButtonBox
from PySide6.QtCore import Signal

class TargetDialog(QDialog):
    new_target = Signal(str, list)
    def __init__(self, parent=None, target: SPSTarget =None):
        super().__init__(parent)
        self.setWindowTitle("Add A Target")
        nameLabel = QLabel("Target name", self)
        self.nameInput = QLineEdit(self)
        QBtn = QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        self.buttonBox = QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.accepted.connect(self.send_target)
        self.buttonBox.rejected.connect(self.reject)
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.layout.addWidget(nameLabel)
        self.layout.addWidget(self.nameInput)
        self.create_target_inputs()
        if target is not None:
            self.set_initial_values(target)
        self.layout.addWidget(self.buttonBox)

    def create_target_inputs(self) -> None:
        self.layerGroup = QGroupBox("Target Layers", self)
        layerGroupLayout = QHBoxLayout()

        self.layerAInputs = []
        self.layerZInputs = []
        self.layerSInputs = []
        self.layerThickInputs = []
        self.layer1GroupBox = QGroupBox("Layer 1", self.layerGroup)
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

        self.layer2GroupBox = QGroupBox("Layer 2", self.layerGroup)
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

        self.layer3GroupBox = QGroupBox("Layer 3", self.layerGroup)
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

        layerGroupLayout.addWidget(self.layer1GroupBox)
        layerGroupLayout.addWidget(self.layer2GroupBox)
        layerGroupLayout.addWidget(self.layer3GroupBox)
        self.layerGroup.setLayout(layerGroupLayout)

        self.layout.addWidget(self.layerGroup)

    def set_initial_values(self, target: SPSTarget) -> None:
        self.nameInput.setText(target.name)
        self.nameInput.setReadOnly(True)
        for i, layer in enumerate(target.layer_details):
            self.layerThickInputs[i].setValue(layer.thickness)
            for j, (z, a, s) in enumerate(layer.compound_list):
                self.layerZInputs[j+i*3].setValue(z)
                self.layerAInputs[j+i*3].setValue(a)
                self.layerSInputs[j+i*3].setValue(s)

    def send_target(self) -> None:
        name = self.nameInput.text()
        if name == "":
            return
        tlist = []
        z = 0
        a = 0
        s = 0
        for i in  range(3):
            tempLayer = TargetLayer()
            tempLayer.thickness = self.layerThickInputs[i].value()
            for j in range(3):
                z = self.layerZInputs[i*3 + j].value()
                a = self.layerAInputs[i*3 + j].value()
                s = self.layerSInputs[i*3 + j].value()
                if z != 0 and a != 0 and s != 0:
                    tempLayer.compound_list.append((z, a, s))
            if len(tempLayer.compound_list) != 0:
                tlist.append(tempLayer)

        if len(tlist) != 0:
            self.new_target.emit(name, tlist)