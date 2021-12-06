#!/usr/bin/env python3
import NuclearRxn as rxn 

class SPSPlot:
	def __init__(self) :
		self.reactions = {}
		self.configfile = ""
		self.rhoMin = 0
		self.rhoMax = 99
		self.beamKE = 0
		self.Bfield = 0
		self.angle = 0

	def ReadConfig(self, filename) :
		self.reactions.clear()

		self.configfile = filename
		file = open(filename, "r")

		line = file.readline()
		entries = line.split()
		self.beamKE = float(entries[1])

		line = file.readline()
		entries = line.split()
		self.Bfield = float(entries[1])

		line = file.readline()
		entries = line.split()
		self.angle = float(entries[1])

		line = file.readline()
		entries = line.split()
		self.rhoMin = float(entries[1])
		self.rhoMax = float(entries[3])

		line = file.readline()

		for line in file:
			entries = line.split()
			reac = rxn.Reaction(int(entries[0]), int(entries[1]), int(entries[2]), int(entries[3]), int(entries[4]), int(entries[5]), self.beamKE, self.angle, self.Bfield)
			self.reactions[reac.Name] = reac

		file.close()

	def WriteConfig(self, filename) :
		file = open(filename, "w")
		line = "BeamEnergy(MeV): "+str(self.beamKE)+"\n"
		file.write(line)
		line = "B-field(kG): "+str(self.Bfield)+"\n"
		file.write(line)
		line = "Angle(deg): "+str(self.angle)+"\n"
		file.write(line)
		line = "RhoMin: "+str(self.rhoMin)+" RhoMax: "+str(self.rhoMax)+"\n"
		file.write(line)
		line = "ZT AT ZP AP ZE AE\n"
		file.write(line)
		for rxnName in self.reactions :
			reaction = self.reactions[rxnName]
			line = str(reaction.Target.Z)+" "+str(reaction.Target.A)+" "+str(reaction.Projectile.Z)+" "+str(reaction.Projectile.A)+" "+str(reaction.Ejectile.Z)+" "+str(reaction.Ejectile.A)+"\n"
			file.write(line)
		file.close()

	def ChangeReactionParameters(self, bke, theta, bf) :
		self.beamKE = bke
		self.Bfield = bf
		self.angle = theta
		for rxnName in self.reactions :
			self.reactions[rxnName].ChangeReactionParameters(bke, theta, bf)

	def AddReaction(self, zt, at, zp, ap, ze, ae) :
		reac =  rxn.Reaction(zt, at, zp, ap, ze, ae, self.beamKE, self.Bfield, self.angle)
		self.reactions[reac.Name] = reac

	def AddLevel(self, name, level) :
		self.reactions[name].AddLevel(level)