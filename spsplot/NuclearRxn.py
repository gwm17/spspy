#!/usr/bin/env python3

import numpy as np
import NucData


class Nucleus:
	def __init__(self, z, a):
		self.Z = z
		self.A = a
		self.Symbol = NucData.Masses.GetSymbol(self.Z, self.A)
		self.GSMass = NucData.Masses.GetMass(self.Z, self.A)

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
	def __init__(self, zt, at, zp, ap, ze, ae, beamKE, theta, bfield):
		self.Target = Nucleus(zt, at)
		self.Projectile = Nucleus(zp, ap)
		self.Ejectile = Nucleus(ze, ae)
		self.Residual = (self.Target.Plus(self.Projectile)).Minus(self.Ejectile)
		self.BKE = beamKE
		self.Theta = theta * self.DEG2RAD
		self.Bfield = bfield
		self.Name = self.Target.Symbol +"("+ self.Projectile.Symbol +","+ self.Ejectile.Symbol +")"+ self.Residual.Symbol

		self.residLevels = NucData.GetExcitations(self.Residual.Symbol)
		self.ejectKEvals = np.array(np.empty(len(self.residLevels)))
		self.ejectRhovals = np.array(np.empty(len(self.residLevels)))
		self.SetEjectileData()

	def GetEjectileKineticEnergy(self, Elevel) :
		Q = self.Target.GSMass + self.Projectile.GSMass - (self.Ejectile.GSMass + self.Residual.GSMass + Elevel)
		Ethresh = -Q*(self.Ejectile.GSMass+self.Residual.GSMass)/(self.Ejectile.GSMass + self.Residual.GSMass - self.Projectile.GSMass)
		if self.BKE < Ethresh:
			return 0.0
		term1 = np.sqrt(self.Projectile.GSMass*self.Ejectile.GSMass*self.BKE)/(self.Ejectile.GSMass + self.Residual.GSMass)*np.cos(self.Theta)
		term2 = (self.BKE*(self.Residual.GSMass - self.Projectile.GSMass) + self.Residual.GSMass*Q)/(self.Ejectile.GSMass + self.Residual.GSMass)
		ke1 = term1 + np.sqrt(term1**2.0 + term2)
		ke2 = term1 - np.sqrt(term1**2.0 + term2)

		if ke1 > 0:
			return ke1**2.0
		else :
			return ke2**2.0

	def GetEjectileRho(self, ke):
		p = np.sqrt(ke*(ke + 2.0*self.Ejectile.GSMass))
		return p/(self.QBRHO2P*self.Bfield*self.Ejectile.Z)

	def SetEjectileData(self):
		for index in range(len(self.residLevels)):
			self.ejectKEvals[index] = self.GetEjectileKineticEnergy(self.residLevels[index])
			self.ejectRhovals[index] = self.GetEjectileRho(self.ejectKEvals[index])

	def ChangeReactionParameters(self, bke, theta, bf) :
		self.BKE = bke
		self.Theta = theta*self.DEG2RAD
		self.Bfield = bf
		self.SetEjectileData()

	def AddLevel(self, Elevel):
		ke = self.GetEjectileKineticEnergy(Elevel)
		rho = self.GetEjectileRho(ke)

		self.residLevels = np.append(self.residLevels, Elevel)
		self.ejectKEvals = np.append(self.ejectKEvals, ke)
		self.ejectRhovals = np.append(self.ejectRhovals, rho)


