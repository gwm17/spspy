#!/usr/bin/env python3

import numpy as np 
from scipy.odr import RealData, ODR, polynomial

class Fit:
	def __init__(self, order):
		self.poly_order = order
		self.model = polynomial(order)
		self.x_data = None
		self.y_data = None
		self.x_errors = None
		self.y_errors = None
		self.fit_data = None
		self.fitter = None
		self.output = None
		self.parameters = None

	def __getstate__(self):
		return self.x_data, self.y_data, self.x_errors, self.y_errors, self.parameters, self.poly_order

	def __setstate__(self, state):
		self.x_data, self.y_data, self.x_errors, self.y_errors, self.parameters, self.poly_order = state
		self.model = polynomial(self.poly_order)

	def RunFit(self, xarray, yarray, y_errors, x_errors):
		self.x_data = xarray
		self.y_data = yarray
		self.x_errors = x_errors
		self.y_errors = y_errors
		self.fit_data = RealData(self.x_data, y=self.y_data, sx=self.y_errors, sy=self.x_errors)
		self.fitter = ODR(self.fit_data, self.model)

		self.output = self.fitter.run()
		self.parameters = self.output.beta

	def GetParameterError(self, par_index):
		return self.output.sd_beta[par_index]

	def GetNDF(self):
		return len(self.x_data) - self.poly_order+1

class LinearFit(Fit):
	def __init__(self):
		super().__init__(1)

	def EvaluateFunction(self, x):
		return self.parameters[0] + self.parameters[1]*x

	def EvaluateFunctionDeriv(self, x):
		return self.parameters[1]

	def EvaluateFunctionParamDeriv(self, x, par_index):
		if par_index == 0:
			return 1.0
		elif par_index == 1:
			return x
		else:
			return 0.0

	def ReducedChiSquare(self):
		ndf = len(self.x_data)-len(self.parameters)
		y_eff_errors = np.zeros(len(self.x_data))
		for i in range(len(self.x_data)):
			y_eff_errors[i] = np.sqrt(self.y_errors[i]**2.0 + (self.x_errors[i]*self.EvaluateFunctionDeriv(self.x_data[i]))**2.0)

		chisq = np.sum(((self.y_data - self.EvaluateFunction(self.x_data))/y_eff_errors)**2.0)
		if ndf > 0:
			return chisq/ndf
		else:
			return 0

class QuadraticFit(Fit):
	def __init__(self):
		super().__init__(2)

	def EvaluateFunction(self, x):
		return self.parameters[0] + self.parameters[1]*x + self.parameters[2]*x**2.0

	def EvaluateFunctionDeriv(self, x):
		return self.parameters[1] + 2.0*self.parameters[2]*x

	def EvaluateFunctionParamDeriv(self, x, par_index):
		if par_index == 0:
			return 1.0
		elif par_index == 1:
			return x
		elif par_index == 2:
			return x**2.0
		else:
			return 0.0

	def ReducedChiSquare(self):
		ndf =  len(self.x_data) - len(self.parameters)
		y_eff_errors = np.zeros(len(self.x_data))
		for i in range(len(self.x_data)):
			y_eff_errors[i] = np.sqrt(self.y_errors[i]**2.0 + (self.x_errors[i]*self.EvaluateFunctionDeriv(self.x_data[i]))**2.0)

		chisq = np.sum(((self.y_data - self.EvaluateFunction(self.x_data))/y_eff_errors)**2.0)
		if ndf >= 0:
			return chisq/ndf
		else:
			return 0

class CubicFit(Fit):
	def __init__(self):
		super().__init__(3)

	def EvaluateFunction(self, x):
		return self.parameters[0] + self.parameters[1]*x + self.parameters[2]*x**2.0 + self.parameters[3]*x**3.0

	def EvaluateFunctionDeriv(self, x):
		return self.parameters[1] + 2.0*self.parameters[2]*x + 3.0*self.parameters[3]*x**2.0

	def EvaluateFunctionParamDeriv(self, x, par_index):
		if par_index == 0:
			return 1.0
		elif par_index == 1:
			return x
		elif par_index == 2:
			return x**2.0
		elif par_index == 3:
			return x**3.0
		else:
			return 0.0

	def ReducedChiSquare(self):
		ndf =  len(self.x_data) - len(self.parameters)
		y_eff_errors = np.zeros(len(self.x_data))
		for i in range(len(self.x_data)):
			y_eff_errors[i] = np.sqrt(self.y_errors[i]**2.0 + (self.x_errors[i]*self.EvaluateFunctionDeriv(self.x_data[i]))**2.0)

		chisq = np.sum(((self.y_data - self.EvaluateFunction(self.x_data))/y_eff_errors)**2.0)
		if ndf >= 0:
			return chisq/ndf
		else:
			return 0


def main():
	ndata = 100
	x = np.zeros(ndata)
	y = np.zeros(ndata)
	dy = np.zeros(ndata)
	dx = np.zeros(ndata)
	for i in range(ndata):
		x[i] = i
		y[i] = i+0.0001*i*i+7.0
		dy[i] = 0.1
		dx[i] = 0.1

	my_fit = LinearFit()
	print("Testing SPANC fitting routine using test data and linear function...")
	my_fit.RunFit(x, y, dy, dx)
	print("Results from fit with y-errors: param[0] =",my_fit.parameters[0],"param[1] =",my_fit.parameters[1],"Reduced chi-sq =",my_fit.ReducedChiSquare())

if __name__ == '__main__':
	main()