#!/bin/usr/env python3

import numpy as np 
import EnergyLoss as eloss

class Target:
	def __init__(self):
		self.thickness=0
		self.Z = np.empty(0)
		self.A = np.empty(0)
		self.S = np.empty(0)
		self.energy_loss = eloss.EnergyLoss()

	def SetElements(self, z, a, s, thick):
		self.Z = z
		self.A = a
		self.S = s
		self.thickness = thick
		self.energy_loss.SetTargetData(self.Z, self.A, self.S)

	def GetComposition(self):
		comp_string = "("
		for i in range(len(self.Z)):
			comp_string +=  "("+ str(self.Z[i]) +","+ str(self.A[i]) +","+ str(self.S[i]) +")"
			if not(i == len(self.Z)-1):
				comp_string += ","
		comp_string += ")"
		return comp_string

	def HasElement(self, z, a):
		for i in range(len(self.Z)):
			if self.Z[i] == z and self.A[i] == a:
				return True
		return False

	def GetEnergyLossTotal(self, zp, ap, start_energy, theta):
		if theta == np.pi/2.0:
			return start_energy
		elif theta > np.pi/2.0:
			return self.energy_loss.GetEnergyLoss(zp, ap, start_energy, self.thickness/abs(np.cos(np.pi - theta)))
		else:
			return self.energy_loss.GetEnergyLoss(zp, ap, start_energy, self.thickness/abs(np.cos(theta)))

	def GetEnergyLossHalf(self, zp, ap, start_energy, theta):
		if theta == np.pi/2.0:
			return start_energy
		elif theta > np.pi/2.0:
			return self.energy_loss.GetEnergyLoss(zp, ap, start_energy, self.thickness/abs(2.0*np.cos(np.pi - theta)))
		else:
			return self.energy_loss.GetEnergyLoss(zp, ap, start_energy, self.thickness/abs(2.0*np.cos(theta)))

	def GetReverseEnergyLossTotal(self, zp, ap, final_energy, theta):
		if theta == np.pi/2.0:
			return final_energy
		elif theta > np.pi/2.0:
			return self.energy_loss.GetReverseEnergyLoss(zp, ap, final_energy, self.thickness/abs(np.cos(np.pi - theta)))
		else:
			return self.energy_loss.GetReverseEnergyLoss(zp, ap, final_energy, self.thickness/abs(np.cos(theta)))

	def GetReverseEnergyLossHalf(self, zp, ap, final_energy, theta):
		if theta == np.pi/2.0:
			return final_energy
		elif theta > np.pi/2.0:
			return self.energy_loss.GetReverseEnergyLoss(zp, ap, final_energy, self.thickness/abs(2.0*np.cos(np.pi - theta)))
		else:
			return self.energy_loss.GetReverseEnergyLoss(zp, ap, final_energy, self.thickness/abs(2.0*np.cos(theta)))

class LayeredTarget:
	def __init__(self):
		self.targets = [] #Order of layers matters!
		self.name = ''

	def AddLayer(self, z, a, s, thick):
		targ = Target()
		targ.SetElements(z, a, s, thick)
		self.targets.append(targ)

	def AddLayer(self, targ):
		if not isinstance(targ, Target) :
			print("Cannot add layer if it is not of type Target!")
			return
		else :
			self.targets.append(targ)

	def FindLayerContainingElement(self, z, a):
		for i in range(len(self.targets)):
			if self.targets[i].HasElement(z, a):
				return i
		return -1

	def GetEnergyLoss(self, zp, ap, initial_energy, theta, rxn_layer, kind="projectile"):
		if rxn_layer < 0 or rxn_layer > len(self.targets):
			print("Bad reaction layer at LayeredTarget::GetEnergyLoss")
			return 0.0

		e_lost = 0.0
		new_energy = initial_energy
		if kind == "projectile":
			for i in range(rxn_layer+1):
				if i == rxn_layer:
					e_lost += self.targets[i].GetEnergyLossHalf(zp, ap, new_energy, theta)
					new_energy = initial_energy - e_lost
				else:
					e_lost += self.targets[i].GetEnergyLossTotal(zp, ap, new_energy, theta)
					new_energy = initial_energy - e_lost
		elif kind == "ejectile":
			for i in range(rxn_layer, len(self.targets)):
				if i == rxn_layer:
					e_lost += self.targets[i].GetEnergyLossHalf(zp, ap, new_energy, theta)
					new_energy = initial_energy - e_lost
				else:
					e_lost = self.targets[i].GetEnergyLossTotal(zp, ap, new_energy, theta)
					new_energy = initial_energy - e_lost
		else:
			print("Invalid kind at LayeredTarget::GetEnergyLoss")
		return e_lost

	def GetReverseEnergyLoss(self, zp, ap, final_energy, theta, rxn_layer):
		if rxn_layer < 0 or rxn_layer > len(self.targets):
			print("Bad reaction layer at LayeredTarget::GetReverseEnergyLoss")
			return 0.0

		e_lost = 0.0
		new_energy = final_energy
		for i in reversed(range(rxn_layer, len(self.targets))):
			if i == rxn_layer:
				e_lost += self.targets[i].GetReverseEnergyLossHalf(zp, ap, new_energy, theta)
				new_energy  = final_energy + e_lost
			else:
				e_lost += self.targets[i].GetReverseEnergyLossTotal(zp, ap, new_energy, theta)
				new_energy = final_energy + e_lost
		return e_lost

