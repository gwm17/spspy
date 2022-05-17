#!/usr/bin/env python3

import numpy as np
import requests
import lxml.html as xhtml


class MassTable:
	def __init__(self):
		file = open("./etc/mass.txt","r")
		self.mtable = {}
		u2mev = 931.4940954
		me = 0.000548579909
		self.etable = {}

		file.readline()
		file.readline()

		for line in file:
			entries = line.split()
			n = entries[0]
			z = entries[1]
			a = entries[2]
			element = entries[3]
			massBig = float(entries[4])
			massSmall = float(entries[5])

			key = '('+z+','+a+')'
			value = ((massBig+massSmall*1e-6) - float(z)*me)*u2mev
			self.mtable[key] = value
			self.etable[key] = element
		file.close()

	def GetMass(self, z, a):
		key = '('+str(z)+','+str(a)+')'
		if key in self.mtable:
			return self.mtable[key]
		else:
			return 0

	def GetSymbol(self, z, a):
		key = '('+str(z)+','+str(a)+')'
		if key in self.etable:
			return str(a)+self.etable[key]
		else:
			return 'none'

Masses = MassTable()

def GetExcitations(symbol):
	levels = np.array(np.empty(0))
	text = ''

	site = requests.get("https://www.nndc.bnl.gov/nudat2/getdatasetClassic.jsp?nucleus="+symbol+"&unc=nds")
	contents = xhtml.fromstring(site.content)
	tables = contents.xpath("//table")
	rows = tables[2].xpath("./tr")
	for row in rows[1:-2]:
		entries = row.xpath("./td")
		if len(entries) != 0:
			entry = entries[0]
			data = entry.xpath("./a")
			if len(data) == 0:
				text = entry.text
			else:
				text = data[0].text
			text = text.replace('?', '')
			text = text.replace('\xa0\xa0≈','')
			levels = np.append(levels, float(text)/1000.0)
	return levels
