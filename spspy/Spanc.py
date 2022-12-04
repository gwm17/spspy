from .SPSReaction import *
from .SPSTarget import *
from .Fitter import *
from .data.NuclearData import *
from dataclasses import dataclass, field
import numpy as np
from enum import Enum

INVALID_PEAK_ID: int = -1

class PeakType(Enum):
    CALIBRATION = "Calibration"
    OUTPUT = "Output"

@dataclass
class Peak:
    excitation: float = 0.0 #MeV
    excitationErr: float = 0.0 #MeV
    position: float = 0.0 #arb
    positionErrStat: float = 0.0 #arb
    positionErrSys: float = 0.0 #arb
    rho: float = 0.0 #cm
    rhoErr: float = 0.0 #cm
    positionFWHM: float = 0.0
    positionFWHMErr: float = 0.0
    excitationFWHM: float = 0.0
    excitationFWHMErr: float = 0.0
    rxnName: str = ""
    peakID: int = INVALID_PEAK_ID

class Spanc:
    def __init__(self):
        self.targets: dict[str, SPSTarget] = {}
        self.reactions: dict[str, Reaction] = {}
        self.calibrations: dict[int, Peak] = {}
        self.outputs: dict[int, Peak] = {}
        self.fitter : Fitter = Fitter()
        self.isFit: bool = False

    def set_fit_order(self, order: int) -> None:
        self.fitter.set_polynomial_order(order)

    #return fit data so that the data points can be drawn
    def fit(self) -> list[FitPoint]:
        fitData = [FitPoint(peak.position, peak.rho, np.sqrt(peak.positionErrStat**2.0 + peak.positionErrSys**2.0), peak.rhoErr) for peak in self.calibrations.values()]
        self.fitter.run(data=fitData)
        self.isFit = True
        return fitData

    def get_residuals(self) -> list[FitResidual]:
        return self.fitter.get_residuals()

    def add_target(self, targName: str, layers: list[TargetLayer]) -> None:
        self.targets[targName] = SPSTarget(layers, name=targName)

    def add_reaction(self, params: RxnParameters, targetName: str) -> None:
        if targetName not in self.targets:
            print("Cannot create reaction with non-existant target ", targetName)
            return
        key = f"Rxn{len(self.reactions)}"
        rxn = Reaction(params, target=self.targets[targetName])
        self.reactions[key] = rxn

    def update_reaction_parameters(self, beamEnergy: float, spsAngle: float, magneticField: float, rxnName: str):
        if rxnName in self.reactions:
            rxn = self.reactions[rxnName]
            rxn.params.beamEnergy = beamEnergy
            rxn.params.spsAngle = spsAngle
            rxn.params.magneticField = magneticField

    def add_calibration(self, data: Peak) -> None:
        if data.rxnName in self.reactions:
            rxn = self.reactions[data.rxnName]
            data.rho = rxn.convert_ejectile_KE_2_rho(rxn.calculate_ejectile_KE(data.excitation))
            data.rhoErr = np.abs(rxn.convert_ejectile_KE_2_rho(rxn.calculate_ejectile_KE(data.excitation + data.excitationErr)) - data.rho)
            if data.peakID == INVALID_PEAK_ID:
                data.peakID = len(self.calibrations)
            self.calibrations[data.peakID] = data
        return

    def add_output(self, data: Peak) -> None:
        if data.peakID == INVALID_PEAK_ID:
            data.peakID = len(self.outputs)
        self.outputs[data.peakID] = data
        return

    def calculate_output_urho(self, peak: Peak) -> float:
        urho = 0.0
        paramErrors = self.fitter.get_parameter_errors()
        for i, paramErr in enumerate(paramErrors):
            urho += (self.fitter.evaluate_param_derivative(peak.position, i) * paramErr)**2.0
        urho += (self.fitter.evaluate_derivative(peak.position)*np.sqrt(peak.positionErrStat**2.0 + peak.positionErrSys**2.0))**2.0
        return np.sqrt(urho)

    def calculate_outputs(self) -> None:
        if self.isFit == False:
            return

        for output in self.outputs.values():
            rxn = self.reactions[output.rxnName]
            output.rho = self.fitter.evaluate(output.position)
            output.rhoErr = self.calculate_output_urho(output)
            output.excitation = rxn.calculate_excitation(output.rho)
            output.excitationErr = np.abs(rxn.calculate_excitation(output.rho + output.rhoErr) - output.excitation)
			
            if output.positionFWHM == 0:
                output.excitationFWHM = 0
                output.excitationFWHMErr = 0
            else:
                rhoLo = self.fitter.evaluate(output.position - output.positionFWHM * 0.5)
                rhoHi = self.fitter.evaluate(output.position + output.positionFWHM * 0.5)
                exLo = rxn.calculate_excitation(rhoLo)
                exHi = rxn.calculate_excitation(rhoHi)
                output.excitationFWHM = abs(exHi - exLo)
                output.excitationFWHMErr = output.positionFWHMErr/output.positionFWHM*output.excitationFWHM

    def calculate_calibrations(self) -> None:
        for calibration in self.calibrations.values():
            rxn = self.reactions[calibration.rxnName]
            calibration.rho = rxn.convert_ejectile_KE_2_rho(rxn.calculate_ejectile_KE(calibration.excitation))
            calibration.rhoErr = np.abs(rxn.convert_ejectile_KE_2_rho(rxn.calculate_ejectile_KE(calibration.excitation + calibration.excitationErr)) - calibration.rho)