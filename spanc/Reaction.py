#!/usr/bin/env python3

from LayeredTarget import LayeredTarget, Target
from NucData import Masses
import numpy as np

class Nucleus:
	def __init__(self, z, a):
		self.Z = z
		self.A = a
		self.Symbol = Masses.GetSymbol(self.Z, self.A)
		self.GSMass = Masses.GetMass(self.Z, self.A)

	def Minus(self, rhs):
		final_Z = self.Z - rhs.Z
		final_A = self.A - rhs.A
		if final_A < 0 or final_Z < 0:
			print("Illegal minus operation on Nuclei!")
			return Nucleus(0,0)
		else:
			return Nucleus(final_Z, final_A)

	def Plus(self, rhs):
		return Nucleus(self.Z + rhs.Z, self.A + rhs.A)

class Reaction:
	DEG2RAD = np.pi/180.0 #degrees to radians
	C = 299792458 #speed of light m/s
	QBRHO2P = 1.0E-9*C #Converts qbrho to p (kG*cm -> MeV/c)
	def __init__(self, zt, at, zp, ap, ze, ae, beamKE, theta, bfield, tdata):
		self.Target = Nucleus(zt, at)
		self.Projectile = Nucleus(zp, ap)
		self.Ejectile = Nucleus(ze, ae)
		self.Residual = (self.Target.Plus(self.Projectile)).Minus(self.Ejectile)
		self.BKE = beamKE
		self.Theta = theta * self.DEG2RAD
		self.Bfield = bfield
		self.Name = self.Target.Symbol +"("+ self.Projectile.Symbol +","+ self.Ejectile.Symbol +")"+ self.Residual.Symbol
		self.target_data = tdata
		self.rxn_layer = self.target_data.FindLayerContainingElement(self.Target.Z, self.Target.A)

	def GetBKEAtRxn(self):
		return self.BKE - self.target_data.GetEnergyLoss(self.Projectile.Z, self.Projectile.A, self.BKE, self.Theta, self.rxn_layer)

	def GetEjectileKineticEnergyAtRxn(self, Elevel) :
		Q = self.Target.GSMass + self.Projectile.GSMass - (self.Ejectile.GSMass + self.Residual.GSMass + Elevel)
		Ethresh = -Q*(self.Ejectile.GSMass+self.Residual.GSMass)/(self.Ejectile.GSMass + self.Residual.GSMass - self.Projectile.GSMass)
		BKE_rxn = self.GetBKEAtRxn()
		if BKE_rxn < Ethresh:
			return 0.0
		term1 = np.sqrt(self.Projectile.GSMass*self.Ejectile.GSMass*BKE_rxn)/(self.Ejectile.GSMass + self.Residual.GSMass)*np.cos(self.Theta)
		term2 = (BKE_rxn*(self.Residual.GSMass - self.Projectile.GSMass) + self.Residual.GSMass*Q)/(self.Ejectile.GSMass + self.Residual.GSMass)
		ke1 = term1 + np.sqrt(term1**2.0 + term2)
		ke2 = term1 - np.sqrt(term1**2.0 + term2)

		if ke1 > 0:
			return ke1**2.0
		else :
			return ke2**2.0

	def GetEjectileKineticEnergyAtDet(self, Elevel):
		KE_at_rxn = self.GetEjectileKineticEnergyAtRxn(Elevel)
		KE_at_det = KE_at_rxn - self.target_data.GetEnergyLoss(self.Ejectile.Z, self.Ejectile.A, KE_at_rxn, self.Theta, self.rxn_layer, kind="ejectile")
		return KE_at_det

	def GetEjectileRho(self, Elevel):
		KE_at_det = self.GetEjectileKineticEnergyAtDet(Elevel)
		p = np.sqrt(KE_at_det*(KE_at_det + 2.0*self.Ejectile.GSMass))
		qbrho = p/self.QBRHO2P
		return qbrho/(self.Ejectile.Z*self.Bfield)

	def GetResidualExcitation(self, rho):
		p_eject_at_det = rho*self.Ejectile.Z*self.Bfield*self.QBRHO2P
		KE_eject_at_det = np.sqrt(p_eject_at_det**2.0 + self.Ejectile.GSMass**2.0) - self.Ejectile.GSMass
		KE_eject_at_rxn = KE_eject_at_det + self.target_data.GetReverseEnergyLoss(self.Ejectile.Z, self.Ejectile.A, KE_eject_at_det, self.Theta, self.rxn_layer)
		p_eject_at_rxn = np.sqrt(KE_eject_at_rxn*(KE_eject_at_rxn + 2.0*self.Ejectile.GSMass))
		E_eject_at_rxn = KE_eject_at_rxn+self.Ejectile.GSMass
		BKE_atRxn = self.GetBKEAtRxn()
		E_project = BKE_atRxn + self.Projectile.GSMass
		p_project = np.sqrt(BKE_atRxn*(BKE_atRxn + 2.0*self.Projectile.GSMass))
		E_resid = E_project + self.Target.GSMass - E_eject_at_rxn
		p2_resid = p_project**2.0 + p_eject_at_rxn**2.0 - 2.0*p_project*p_eject_at_rxn*np.cos(self.Theta)
		m_resid = np.sqrt(E_resid**2.0 - p2_resid)
		return m_resid - self.Residual.GSMass


	def ChangeReactionParameters(self, bke, theta, bf) :
		self.BKE = bke
		self.Theta = theta*self.DEG2RAD
		self.Bfield = bf