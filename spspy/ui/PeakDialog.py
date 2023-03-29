from ..Spanc import Peak, PeakType, INVALID_PEAK_ID
from PySide6.QtWidgets import QLabel
from PySide6.QtWidgets import QVBoxLayout, QFormLayout, QGroupBox
from PySide6.QtWidgets import QComboBox, QDoubleSpinBox
from PySide6.QtWidgets import QDialog, QDialogButtonBox, QPushButton
from PySide6.QtCore import Signal

class PeakDialog(QDialog):
    new_peak = Signal(Peak)
    delete_peak = Signal(Peak)
    
    def __init__(self, peakType: PeakType, rxnList: list[str], parent=None,  peak: Peak=None):
        super().__init__(parent)
        self.setWindowTitle(f"Add A {peakType.value} Peak")
        rnameLabel = QLabel("Reaction Name", self)
        self.rxnNameBox = QComboBox(self)
        for reaction in rxnList:
            self.rxnNameBox.addItem(reaction)
        QBtn = QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        self.buttonBox = QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
        self.centralLayout = QVBoxLayout()
        self.setLayout(self.centralLayout)
        self.centralLayout.addWidget(rnameLabel)
        self.centralLayout.addWidget(self.rxnNameBox)
        if peakType == PeakType.CALIBRATION:
            self.create_calibration_inputs()
            if peak is not None:
                self.setWindowTitle(f"Update A {peakType.value} Peak")
                self.set_calibration_inputs(peak)
                self.peakID = peak.peakID
                self.buttonBox.accepted.connect(self.send_update_calibration_peak)
                self.deleteButton = QPushButton("Delete", self)
                self.deleteButton.clicked.connect(self.send_delete_calibration_peak)
                self.centralLayout.addWidget(self.deleteButton)
            else:
                self.buttonBox.accepted.connect(self.send_calibration_peak)
        elif peakType == PeakType.OUTPUT:
            self.create_output_inputs()
            if peak is not None:
                self.setWindowTitle(f"Update A {peakType.value} Peak")
                self.set_output_inputs(peak)
                self.peakID = peak.peakID
                self.buttonBox.accepted.connect(self.send_update_output_peak)
            else:
                self.buttonBox.accepted.connect(self.send_output_peak)
        self.centralLayout.addWidget(self.buttonBox)

    def create_calibration_inputs(self) -> None:
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
        inputLayout.addRow("Position Sys. Error(mm)", self.uxsysInput)
        inputLayout.addRow("Position Stat. Error(mm)", self.uxstatInput)
        inputLayout.addRow("Excitation Energy(MeV)", self.exInput)
        inputLayout.addRow("Excitation Energy Error(MeV)", self.uexInput)
        self.inputGroupBox.setLayout(inputLayout)
        self.centralLayout.addWidget(self.inputGroupBox)

    def create_output_inputs(self) -> None:
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
        inputLayout.addRow("Position Sys. Error(mm)", self.uxsysInput)
        inputLayout.addRow("Position Stat. Error(mm)", self.uxstatInput)
        inputLayout.addRow("Position FWHM(mm)", self.fwhmInput)
        inputLayout.addRow("Position FWHM Error(mm)", self.ufwhmInput)
        self.inputGroupBox.setLayout(inputLayout)
        self.centralLayout.addWidget(self.inputGroupBox)

    def set_calibration_inputs(self, peak: Peak) -> None:
        self.rxnNameBox.setCurrentIndex(self.rxnNameBox.findText(peak.rxnName))
        self.xInput.setValue(peak.position)
        self.uxsysInput.setValue(peak.positionErrSys)
        self.uxstatInput.setValue(peak.positionErrStat)
        self.exInput.setValue(peak.excitation)
        self.uexInput.setValue(peak.excitationErr)

    def set_output_inputs(self, peak: Peak) -> None:
        self.rxnNameBox.setCurrentIndex(self.rxnNameBox.findText(peak.rxnName))
        self.xInput.setValue(peak.position)
        self.uxsysInput.setValue(peak.positionErrSys)
        self.uxstatInput.setValue(peak.positionErrStat)
        self.fwhmInput.setValue(peak.positionFWHM)
        self.ufwhmInput.setValue(peak.positionFWHMErr)

    def send_calibration_peak(self) -> None:
        peak = Peak(excitation=self.exInput.value(), excitationErr=self.uexInput.value(), position=self.xInput.value(),
                    positionErrStat=self.uxstatInput.value(), positionErrSys=self.uxsysInput.value(), rxnName=self.rxnNameBox.currentText(), peakID=INVALID_PEAK_ID)
        self.new_peak.emit(peak)
    
    def send_update_calibration_peak(self) -> None:
        peak = Peak(excitation=self.exInput.value(), excitationErr=self.uexInput.value(), position=self.xInput.value(),
                    positionErrStat=self.uxstatInput.value(), positionErrSys=self.uxsysInput.value(), rxnName=self.rxnNameBox.currentText(), peakID=self.peakID)
        self.new_peak.emit(peak)

    def send_delete_calibration_peak(self) -> None:
        peak = Peak(excitation=self.exInput.value(), excitationErr=self.uexInput.value(), position=self.xInput.value(),
                    positionErrStat=self.uxstatInput.value(), positionErrSys=self.uxsysInput.value(), rxnName=self.rxnNameBox.currentText(), peakID=self.peakID)
        self.delete_peak.emit(peak)
        self.done(3)
    
    def send_output_peak(self) -> None:
        peak = Peak(position=self.xInput.value(), positionErrStat=self.uxstatInput.value(), positionErrSys=self.uxsysInput.value(),
                    positionFWHM=self.fwhmInput.value(), positionFWHMErr=self.ufwhmInput.value(), rxnName=self.rxnNameBox.currentText(), peakID=INVALID_PEAK_ID)
        self.new_peak.emit(peak)

    def send_update_output_peak(self) -> None:
        peak = Peak(position=self.xInput.value(), positionErrStat=self.uxstatInput.value(), positionErrSys=self.uxsysInput.value(),
                    positionFWHM=self.fwhmInput.value(), positionFWHMErr=self.ufwhmInput.value(), rxnName=self.rxnNameBox.currentText(), peakID=self.peakID)
        self.new_peak.emit(peak)
