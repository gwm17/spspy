#!/usr/bin/env python3

import numpy as np 
import EnergyLossData as edata
from NucData import Masses

class EnergyLoss:
	MAX_FRACTIONAL_STEP=0.001
	MAX_H_E_PER_U=100000.0
	AVOGADRO=0.60221367
	MEV2U=1.0/931.4940954
	def __init__(self):
		self.ZP = 0
		self.AP = 0
		self.MP = 0
		self.ZT = np.zeros(0)
		self.AT = np.zeros(0)
		self.Stoich = np.zeros(0)
		self.illegalFlag = True

	def SetTargetData(self, zt, at, stoich):
		self.ZT = zt
		self.AT = at
		total = np.sum(stoich)
		self.Stoich = stoich/total
		for z in self.ZT:
			if z >= edata.MaxZ:
				self.illegalFlag = True
				return
		self.illegalFlag = False

	def GetEnergyLoss(self, zp, ap, e_initial, thickness):
		if self.illegalFlag:
			print("Unable to get energy loss with unset target data... returning 0")
			return 0.0

		if self.ZP != zp:
			self.ZP = zp
			self.AP = ap
			self.MP = Masses.GetMass(self.ZP, self.AP)*self.MEV2U

		e_final = e_initial
		x_traversed = 0
		x_step = 0.25*thickness
		e_step = self.GetTotalStoppingPower(e_final)*x_step/1000.0

		if thickness == 0.0:
			return 0.0
		go = True
		while go:
			if e_step/e_final > self.MAX_FRACTIONAL_STEP:
				x_step *= 0.5
				e_step = self.GetTotalStoppingPower(e_final)*x_step/1000.0
			elif x_step+x_traversed >= thickness:
				go = False
				x_step = thickness - x_traversed #get valid portion of last chunk
				e_final -= self.GetTotalStoppingPower(e_final)*x_step/1000.0
				if e_final <= 0.0:
					return e_initial
			else:
				x_traversed += x_step
				e_step = self.GetTotalStoppingPower(e_final)*x_step/1000.0
				e_final -= e_step
				if e_final <= 0.0:
					return e_initial
		return e_initial - e_final

	def GetReverseEnergyLoss(self, zp, ap, e_final, thickness):
		if self.illegalFlag:
			print("Unable to get energy loss with unset target data... returning 0")
			return 0.0

		if self.ZP != zp:
			self.ZP = zp
			self.AP = ap
			self.MP = Masses.GetMass(self.ZP, self.AP)*self.MEV2U

		e_initial = e_final
		x_traversed = 0
		x_step = 0.25*thickness
		e_step = self.GetTotalStoppingPower(e_initial)*x_step/1000.0

		if thickness == 0.0:
			return 0.0
		go = True
		while go:
			if e_step/e_final > self.MAX_FRACTIONAL_STEP:
				x_step *= 0.5
				e_step = self.GetTotalStoppingPower(e_initial)*x_step/1000.0
			elif x_step+x_traversed >= thickness:
				go = False
				x_step = thickness - x_traversed #get valid portion of last chunk
				e_initial += self.GetTotalStoppingPower(e_initial)*x_step/1000.0
			else:
				x_traversed += x_step
				e_step = self.GetTotalStoppingPower(e_initial)*x_step/1000.0
				e_final += e_step
				if e_final <= 0.0:
					return e_initial
		return abs(e_initial - e_final)

	def GetTotalStoppingPower(self, energy):
		return self.GetElectronicStoppingPower(energy)+self.GetNuclearStoppingPower(energy)

	def GetElectronicStoppingPower(self, energy):
		e_per_u = energy*1000.0/self.MP
		values = np.zeros(len(self.ZT))
		if e_per_u > self.MAX_H_E_PER_U:
			print("Bombarding energy exceeds maximum allowed value for energy loss! Returning 0")
			return 0.0
		elif e_per_u > 1000.0:
			for i in range(len(self.ZT)):
				values[i] = self.Hydrogen_dEdx_High(e_per_u, energy, self.ZT[i])
		elif e_per_u > 10.0:
			for i in range(len(self.ZT)):
				values[i] = self.Hydrogen_dEdx_Med(e_per_u, self.ZT[i])
		elif e_per_u > 0.0:
			for i in range(len(self.ZT)):
				values[i] = self.Hydrogen_dEdx_Low(e_per_u, self.ZT[i])
		else:
			print("Negative energy encountered at EnergyLoss::GetElectronicStoppingPower! Returning 0")
			return 0.0

		if self.ZP > 1:
			for i in range(len(values)):
				values[i] *= self.CalculateEffectiveChargeRatio(e_per_u, self.ZT[i])

		stopping_total = np.sum(values*self.Stoich)
		conv_factor = 0.0
		for i in range(len(self.ZT)):
			conv_factor += self.Stoich[i]*edata.NaturalMass[self.ZT[i]]
		stopping_total *= self.AVOGADRO/conv_factor
		return stopping_total

	def GetNuclearStoppingPower(self, energy):
		e = energy*1000.0
		stopping_total = 0.0
		for i in range(len(self.ZT)):
			zt = self.ZT[i]
			mt = edata.NaturalMass[self.ZT[i]]
			x = (self.MP + mt) * np.sqrt(self.ZP**(2.0/3.0) + zt**(2.0/3.0))
			epsilon = 32.53*mt*e/(self.ZP*zt*x)
			sn = 8.462*(0.5*np.log(1.0+epsilon)/(epsilon+0.10718*(epsilon**0.37544)))*self.ZP*zt*self.MP/x
			conversion_factor = self.AVOGADRO/mt
			stopping_total += sn*conversion_factor*self.Stoich[i]
		return stopping_total

	def Hydrogen_dEdx_Low(self, e_per_u, zt):
		return np.sqrt(e_per_u)*edata.HydrogenCoeff[zt][0]

	def Hydrogen_dEdx_Med(self, e_per_u, zt):
		x = edata.HydrogenCoeff[zt][1]*e_per_u**0.45
		y = edata.HydrogenCoeff[zt][2]/e_per_u * np.log(1.0 + edata.HydrogenCoeff[zt][3]/e_per_u + edata.HydrogenCoeff[zt][4]*e_per_u)
		return x*y/(x+y)

	def Hydrogen_dEdx_High(self, e_per_u, energy, zt):
		beta_sq = energy * (energy + 2.0*self.MP/self.MEV2U)/((energy + self.MP/self.MEV2U)**2.0)
		alpha = edata.HydrogenCoeff[zt][5]/beta_sq
		epsilon = edata.HydrogenCoeff[zt][6]*beta_sq/(1.0 - beta_sq) - beta_sq - edata.HydrogenCoeff[zt][7]
		for i in range(1,5):
			epsilon += edata.HydrogenCoeff[zt][7+i]*(np.log(e_per_u))**float(i)
		return alpha * np.log(epsilon)

	def CalculateEffectiveChargeRatio(self, e_per_u, zt):
		z_ratio=0
		if self.ZP == 2:
			ln_epu = np.log(e_per_u)
			gamma = 1.0+(0.007+0.00005*zt)*np.exp(-1.0*(7.6-ln_epu)**2.0)
			alpha = 0.7446 + 0.1429*ln_epu + 0.01562*ln_epu**2.0 - 0.00267*ln_epu**3.0 + 1.338e-6*ln_epu**8.0
			z_ratio = gamma*(1.0-np.exp(-alpha))*2.0
		elif self.ZP == 3:
			ln_epu = np.log(e_per_u)
			gamma = 1.0+(0.007+0.00005*zt)*np.exp(-1.0*(7.6-ln_epu)**2.0)
			alpha = 0.7138+0.002797*e_per_u+1.348e-6*e_per_u**2.0
			z_ratio = gamma*(1-np.exp(-alpha))*3.0
		else:
			B = 0.886*(e_per_u/25.0)**0.5/(self.ZP**(2.0/3.0))
			A = B + 0.0378*np.sin(np.pi/2.0*B)
			z_ratio = (1.0 - np.exp(-A)*(1.034-0.1777*np.exp(-0.08114*self.ZP)))*self.ZP
		return z_ratio*z_ratio


def main():
	targetA = np.array([12])
	targetZ = np.array([6])
	targetS = np.array([1])
	beamKE = 16.0
	thickness = 20.0

	eloss = EnergyLoss()
	eloss.SetTargetData(targetZ, targetA, targetS)
	print("Testing various cases for energy loss. Using 12C target with 20 ug/cm^2 thickness. Compare to values given by LISE++ or SRIM")
	result = eloss.GetEnergyLoss(1, 1, beamKE, 20.0)
	print("Case 1: ZP = 1, AP=1, Beam energy = 16 MeV -> Resulting energy loss = ", result, " MeV")
	beamKE = 1.0
	result = eloss.GetEnergyLoss(1, 1, beamKE, 20.0)
	print("Case 2: ZP = 1, AP=1, Beam energy = 1.0 MeV -> Resulting energy loss = ", result, " MeV")
	beamKE = 0.1
	result = eloss.GetEnergyLoss(1, 1, beamKE, 20.0)
	print("Case 3: ZP = 1, AP=1, Beam energy = 0.1 MeV -> Resulting energy loss = ", result, " MeV")
	beamKE = 0.01
	result = eloss.GetEnergyLoss(1, 1, beamKE, 20.0)
	print("Case 4: ZP = 1, AP=1, Beam energy = 0.01 MeV -> Resulting energy loss = ", result, " MeV")
	beamKE = 24.0
	result = eloss.GetEnergyLoss(2, 4, beamKE, 20.0)
	print("Case 5: ZP = 2, AP=4, Beam energy = 24.0 MeV -> Resulting energy loss = ", result, " MeV")
	beamKE = 24.0
	result = eloss.GetEnergyLoss(3, 6, beamKE, 20.0)
	print("Case 6: ZP = 3, AP=6, Beam energy = 24 MeV -> Resulting energy loss = ", result, " MeV")
	print("Finished.")

if __name__ == '__main__':
	main()
