from ..SPSReaction import RxnParameters, Reaction, create_reaction_parameters
from ..data.NuclearData import global_nuclear_data
from PySide6.QtWidgets import QLabel
from PySide6.QtWidgets import QVBoxLayout, QFormLayout, QGroupBox
from PySide6.QtWidgets import QSpinBox, QDoubleSpinBox, QComboBox
from PySide6.QtWidgets import QDialog, QDialogButtonBox
from PySide6.QtCore import Signal

MAXIMUM_NUCLEAR_Z: int = 110
MAXIMUM_NUCLEAR_A: int = 270
MINIMUM_BEAM_ENERGY: float = 0.0 #MeV
MAXIMUM_BEAM_ENERGY: float = 100.0 #MeV
MINIMUM_SPS_ANGLE: float = 0.0 #deg
MAXIMUM_SPS_ANGLE: float = 90.0 #deg
MINIMUM_MAG_FIELD: float = 0.0 #kG
MAXIMUM_MAG_FIELD: float = 16.0 #kG

class ReactionDialog(QDialog):
    new_reaction = Signal(RxnParameters,  str)
    update_reaction = Signal(float, float, float, str)

    def __init__(self, parent=None, rxn: Reaction =None, rxnKey: str =None, targets: list[str]=None, extraParams: bool = False):
        super().__init__(parent)
        self.setWindowTitle("Add Reaction")
        self.extraParams = extraParams
        tnameLabel = QLabel("Target Name", self)
        self.targetNameBox = QComboBox(self)
        for target in targets:
            self.targetNameBox.addItem(target)
        QBtn = QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        self.buttonBox = QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.accept)
        if rxn is not None:
            self.buttonBox.accepted.connect(self.send_reaction_update)
        else:
            self.buttonBox.accepted.connect(self.send_reaction)
        self.buttonBox.rejected.connect(self.reject)
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.layout.addWidget(tnameLabel)
        self.layout.addWidget(self.targetNameBox)
        self.create_reaction_inputs()
        if rxn is not None:
            self.set_initial_values(rxn)
            self.rxnKey = rxnKey
        self.layout.addWidget(self.buttonBox)

    def send_reaction(self) -> None :
        params = create_reaction_parameters(self.ztInput.value(), self.atInput.value(), self.zpInput.value(), self.apInput.value(), self.zeInput.value(), self.aeInput.value())
        if self.extraParams == True:
            params.beamEnergy = self.bkeInput.value()
            params.spsAngle = self.thetaInput.value()
            params.magneticField = self.bfieldInput.value()

        self.new_reaction.emit(params, self.targetNameBox.currentText())

    def send_reaction_update(self) -> None:
        self.update_reaction.emit(self.bkeInput.value(), self.thetaInput.value(), self.bfieldInput.value(), self.rxnKey)

    def create_reaction_inputs(self) -> None:
        self.nucleiGroupBox = QGroupBox("Reaction Nuclei",self)
        inputLayout = QFormLayout()
        self.ztInput = QSpinBox(self.nucleiGroupBox)
        self.ztInput.setRange(1, MAXIMUM_NUCLEAR_Z)
        self.atInput = QSpinBox(self.nucleiGroupBox)
        self.atInput.setRange(1, MAXIMUM_NUCLEAR_A)
        self.zpInput = QSpinBox(self.nucleiGroupBox)
        self.zpInput.setRange(1, MAXIMUM_NUCLEAR_Z)
        self.apInput = QSpinBox(self.nucleiGroupBox)
        self.apInput.setRange(1, MAXIMUM_NUCLEAR_A)
        self.zeInput = QSpinBox(self.nucleiGroupBox)
        self.zeInput.setRange(1, MAXIMUM_NUCLEAR_Z)
        self.aeInput = QSpinBox(self.nucleiGroupBox)
        self.aeInput.setRange(1, MAXIMUM_NUCLEAR_A)
        inputLayout.addRow("ZT",self.ztInput)
        inputLayout.addRow("AT",self.atInput)
        inputLayout.addRow("ZP",self.zpInput)
        inputLayout.addRow("AP",self.apInput)
        inputLayout.addRow("ZE",self.zeInput)
        inputLayout.addRow("AE",self.aeInput)

        self.nucleiGroupBox.setLayout(inputLayout)
        self.layout.addWidget(self.nucleiGroupBox)

        if self.extraParams == True:
            self.parameterGroupBox = QGroupBox("Reaction Parameters", self)
            parameterLayout = QFormLayout()
            self.bkeInput = QDoubleSpinBox(self.parameterGroupBox)
            self.bkeInput.setRange(MINIMUM_BEAM_ENERGY, MAXIMUM_BEAM_ENERGY)
            self.bkeInput.setDecimals(4)
            self.thetaInput = QDoubleSpinBox(self.parameterGroupBox)
            self.thetaInput.setRange(MINIMUM_SPS_ANGLE, MAXIMUM_SPS_ANGLE)
            self.thetaInput.setDecimals(4)
            self.bfieldInput = QDoubleSpinBox(self.parameterGroupBox)
            self.bfieldInput.setRange(MINIMUM_MAG_FIELD, MAXIMUM_MAG_FIELD)
            self.bfieldInput.setDecimals(6)
            parameterLayout.addRow("Beam KE(Mev)",self.bkeInput)
            parameterLayout.addRow("Theta(deg)",self.thetaInput)
            parameterLayout.addRow("Bfield(kG)",self.bfieldInput)
            self.parameterGroupBox.setLayout(parameterLayout)
            self.layout.addWidget(self.parameterGroupBox)

    def set_initial_values(self, rxn: Reaction) -> None:
        self.targetNameBox.setCurrentIndex(self.targetNameBox.findText(rxn.targetMaterial.name))
        self.targetNameBox.setEnabled(False)
        self.ztInput.setValue(rxn.params.target.Z)
        self.ztInput.setEnabled(False)
        self.atInput.setValue(rxn.params.target.A)
        self.atInput.setEnabled(False)
        self.zpInput.setValue(rxn.params.projectile.Z)
        self.zpInput.setEnabled(False)
        self.apInput.setValue(rxn.params.projectile.A)
        self.apInput.setEnabled(False)
        self.zeInput.setValue(rxn.params.ejectile.Z)
        self.zeInput.setEnabled(False)
        self.aeInput.setValue(rxn.params.ejectile.A)
        self.aeInput.setEnabled(False)
        self.bkeInput.setValue(rxn.params.beamEnergy)
        self.thetaInput.setValue(rxn.params.spsAngle)
        self.bfieldInput.setValue(rxn.params.magneticField)
	