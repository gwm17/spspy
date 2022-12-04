from .SPSReaction import *
from .SPSTarget import *
from .data.NuclearData import *
from dataclasses import dataclass, field

@dataclass
class Excitation:
    excitation: float = 0.0 #MeV
    kineticEnergy: float = 0.0 #MeV
    rho: float = 0.0 #cm
    fpZ: float = 0.0 #cm

@dataclass
class PlotData:
    rxn: Reaction
    excitations: list[Excitation] = field(default_factory=list)

class SPSPlot:
    def __init__(self):
        self.data : dict[str, PlotData] = {}
        self.targets : dict[str, SPSTarget] = {}
        self.spsAngle : float  = 0.0 #deg
        self.beamEnergy : float = 0.0 #MeV
        self.magneticField : float = 0.0 #kG
        self.rhoMin: float = 0.0 #cm
        self.rhoMax: float = 0.0 #cm

    def add_target(self, targName: str, layers: list[TargetLayer]) -> None:
        self.targets[targName] = SPSTarget(layers, name=targName)

    def add_reaction(self, params: RxnParameters, targetName: str) -> None:
        target = self.targets.get(targetName, None)
        if target is None:
            target = SPSTarget([TargetLayer([(1,1,1)], 0.0)]) #insert a dummy target if an invalid one is passed (i.e. no energy loss)

        plotData = PlotData(Reaction(params, target))
        exList = get_excitations(plotData.rxn.residual.Z, plotData.rxn.residual.A)
        for ex in exList:
            ke = plotData.rxn.calculate_ejectile_KE(ex)
            r = plotData.rxn.convert_ejectile_KE_2_rho(ke)
            z = plotData.rxn.calculate_focal_plane_offset(ke)
            plotData.excitations.append(Excitation(ex, ke, r, z))
        self.data[str(plotData.rxn)] = plotData
        
    def update_reactions(self) -> None:
        for datum in self.data.values():
            datum.rxn.update_parameters(self.beamEnergy, self.spsAngle, self.magneticField)
            for ex in datum.excitations:
                ex.kineticEnergy = datum.rxn.calculate_ejectile_KE(ex.excitation)
                ex.rho = datum.rxn.convert_ejectile_KE_2_rho(ex.kineticEnergy)

    def add_excitation(self, rxnName: str, excitation: float) -> None:
        if rxnName not in self.data:
            print("Cannot add excitation to non-existant reaction named ", rxnName)
            return

        datum = self.data[rxnName]
        ke = datum.rxn.calculate_ejectile_KE(excitation)
        rho = datum.rxn.convert_ejectile_KE_2_rho(ke)
        datum.excitations.append(Excitation(excitation, ke, rho))


