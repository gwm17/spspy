from .data.NuclearData import global_nuclear_data, NucleusData
from .SPSTarget import SPSTarget
from dataclasses import dataclass
from numpy import sqrt, cos, pi, sin

INVALID_KINETIC_ENERGY: float = -1000.0

@dataclass
class RxnParameters:
    target: NucleusData
    projectile: NucleusData
    ejectile: NucleusData
    beamEnergy: float = 0.0 #MeV
    magneticField: float = 0.0 #kG
    spsAngle: float = 0.0 #rad

def create_reaction_parameters(zt: int, at: int, zp: int, ap: int, ze: int, ae: int) -> RxnParameters:
    return RxnParameters(global_nuclear_data.get_data(zt, at), global_nuclear_data.get_data(zp, ap), global_nuclear_data.get_data(ze, ae))

class Reaction:
    C = 299792458 #speed of light m/s
    QBRHO2P = 1.0E-9*C #Converts qbrho to momentum (p) (kG*cm -> MeV/c)
    FP_MAGNIFICATION = 0.39
    FP_DISPERSION = 1.96

    def __init__(self, params: RxnParameters, target: SPSTarget):
        self.params = params
        self.targetMaterial = target

        self.rxnLayer = self.targetMaterial.get_rxn_layer(self.params.target.Z, self.params.target.A)
        self.setup_nuclei()

    def setup_nuclei(self) -> None:
        residZ = self.params.target.Z + self.params.projectile.Z - self.params.ejectile.Z
        residA = self.params.target.A + self.params.projectile.A - self.params.ejectile.A

        assert residZ > 0 and residA > 0,  "Unable to construct residual in Reaction!"

        self.residual = global_nuclear_data.get_data(residZ, residA)
        self.Qvalue = self.params.target.mass + self.params.projectile.mass - self.params.ejectile.mass - self.residual.mass

    def __str__(self) -> str:
        return f"{self.params.target.prettyIsotopicSymbol}({self.params.projectile.prettyIsotopicSymbol},{self.params.ejectile.prettyIsotopicSymbol}){self.residual.prettyIsotopicSymbol}"

    def __repr__(self) -> str:
        return f"{self.params.target.isotopicSymbol}({self.params.projectile.isotopicSymbol},{self.params.ejectile.isotopicSymbol}){self.residual.isotopicSymbol}_{self.params.beamEnergy}MeV_{self.params.spsAngle}rad_{self.params.magneticField}kG"

    def get_latex_rep(self) -> str:
        return f"{self.params.target.get_latex_rep()}({self.params.projectile.get_latex_rep()},{self.params.ejectile.get_latex_rep()}){self.residual.get_latex_rep()}"

    #MeV
    def calculate_ejectile_KE(self, excitation: float) -> float:
        rxnQ = self.Qvalue - excitation
        beamRxnEnergy = self.params.beamEnergy - self.targetMaterial.get_incoming_energyloss(self.params.projectile.Z, self.params.projectile.mass, self.params.beamEnergy, self.rxnLayer, 0.0)
        threshold = -rxnQ*(self.params.ejectile.mass+self.residual.mass)/(self.params.ejectile.mass + self.residual.mass - self.params.projectile.mass)
        if beamRxnEnergy < threshold:
            return INVALID_KINETIC_ENERGY
        
        term1 = sqrt(self.params.projectile.mass * self.params.ejectile.mass * beamRxnEnergy) / (self.params.ejectile.mass + self.residual.mass) * cos(self.params.spsAngle)
        term2 = (beamRxnEnergy * (self.residual.mass - self.params.projectile.mass) + self.residual.mass * rxnQ) / (self.params.ejectile.mass + self.residual.mass)
        if(term1**2.0 + term2) < 0:
            return INVALID_KINETIC_ENERGY

        ke1 = term1 + sqrt(term1**2.0 + term2)
        ke2 = term1 + sqrt(term1**2.0 + term2)

        ejectileEnergy = 0.0
        if ke1 > 0.0:
            ejectileEnergy = ke1**2.0
        else:
            ejectileEnergy = ke2**2.0

        ejectileEnergy -= self.targetMaterial.get_outgoing_energyloss(self.params.ejectile.Z, self.params.ejectile.mass, ejectileEnergy, self.rxnLayer, self.params.spsAngle)
        return ejectileEnergy

    def convert_ejectile_KE_2_rho(self, ejectileEnergy: float) -> float:
        if ejectileEnergy == INVALID_KINETIC_ENERGY:
            return 0.0
        p = sqrt( ejectileEnergy * (ejectileEnergy + 2.0 * self.params.ejectile.mass))
        #convert to QBrho
        qbrho = p/self.QBRHO2P
        return qbrho / (float(self.params.ejectile.Z) * self.params.magneticField)

    def calculate_excitation(self, rho: float) -> float:
        ejectileP = rho * float(self.params.ejectile.Z) * self.params.magneticField * self.QBRHO2P
        ejectileEnergy  = sqrt(ejectileP**2.0 + self.params.ejectile.mass**2.0) - self.params.ejectile.mass
        ejectileRxnEnergy = ejectileEnergy +  self.targetMaterial.get_outgoing_reverse_energyloss(self.params.ejectile.Z, self.params.ejectile.mass, ejectileEnergy, self.rxnLayer, self.params.spsAngle)
        ejectileRxnP = sqrt(ejectileRxnEnergy * (ejectileRxnEnergy + 2.0 * self.params.ejectile.mass))
        beamRxnEnergy = self.params.beamEnergy - self.targetMaterial.get_incoming_energyloss(self.params.projectile.Z, self.params.projectile.mass, self.params.beamEnergy, self.rxnLayer, 0.0)
        beamRxnP = sqrt(beamRxnEnergy * (beamRxnEnergy + 2.0 * self.params.projectile.mass))


        residRxnEnergy = beamRxnEnergy + self.params.projectile.mass + self.params.target.mass - ejectileRxnEnergy - self.params.ejectile.mass
        residRxnP2 = beamRxnP**2.0 + ejectileRxnP**2.0 - 2.0 * ejectileRxnP * beamRxnP * cos(self.params.spsAngle)
        return sqrt(residRxnEnergy**2.0 - residRxnP2) - self.residual.mass

    def calculate_focal_plane_offset(self, ejectileEnergy: float) -> float:
        if ejectileEnergy == INVALID_KINETIC_ENERGY:
            return 0.0
        ejectileRho = self.convert_ejectile_KE_2_rho(ejectileEnergy)
        k = sqrt(self.params.projectile.mass * self.params.ejectile.mass * self.params.beamEnergy / ejectileEnergy) * sin(self.params.spsAngle)
        k /= self.params.ejectile.mass + self.residual.mass - sqrt(self.params.projectile.mass * self.params.ejectile.mass * self.params.beamEnergy/ejectileEnergy) * cos(self.params.spsAngle)
        return -1.0*k*ejectileRho*self.FP_DISPERSION*self.FP_MAGNIFICATION

    #(MeV, rad, kG)
    def update_parameters(self, beamEnergy: float, spsAngle: float, magenticField: float):
        self.params.beamEnergy = beamEnergy
        self.params.spsAngle = spsAngle
        self.params.magneticField = magenticField