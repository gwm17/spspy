#!/usr/bin/env python3

import numpy as np

class FitFunction :
	def __init__(self, nparams, numericFlag=True):
		self.nparams = nparams
		self.numericFlag = numericFlag

	def Evaluate(self, x, params):
		return None

	def EvaluateParamDeriv(self, x, params, this_param):
		return None

	def EvaluateDeriv(self, x, params):
		return None

	def NumericDeriv(self, x, y, dx, params):
		return (self.Evaluate(x+dx, params) - y)/dx

	def NumericParamDeriv(self, x, y, params, this_param, dpar):
		par_val = params[this_param]
		params[this_param] += dpar
		value = (self.Evaluate(x, params) - y)/dpar
		params[this_param] = par_val
		return value



class SpancFit:
	PRECISION = 1e-6
	MAX_ITERS = 100
	def __init__(self, func) :
		self.function = func
		self.nparams = func.nparams
		self.numericFlag = func.numericFlag
		self.covMatrix = np.zeros((self.nparams, self.nparams))
		self.xErrorFlag = False
		self.chiSq = 0
		self.ndf = 0
		self.redChiSq = 0
		self.Lambda = 0.1
		self.parameters = np.zeros(self.nparams)
		self.x_data = np.zeros(0)
		self.y_data = np.zeros(0)
		self.y_errors = np.zeros(0)
		self.x_errors = np.zeros(0)
		self.x_incr = np.zeros(0)
		self.param_incr = np.zeros(self.nparams)
		self.ndata = 0

	def EvaluateFunction(self, x):
		return self.function.Evaluate(x, self.parameters)

	def SetParamIncrement(self, func_vals): 
		vor = 0.0
		nach = 0.0
		zoom = 0
		index = 0
		for i in range(len(self.parameters)):
			zoom = 0
			self.param_incr[i] = abs(self.parameters[i]*1e-3)
			if self.param_incr[i] == 0.0:
				self.param_incr[i] = 1e-3

			for j in range(5):
				index = j*self.ndata/5
				nach = self.function.NumericParamDeriv(self.x_data[index], func_vals[index], self.parameters, i, self.param_incr[i])
				vor = 0
				while zoom <= 4 and abs(nach - vor) >= vor:
					zoom += 1
					vor = nach
					self.param_incr[i] *= 0.1
					nach = self.function.NumericParamDeriv(self.x_data[index], func_vals[index], self.parameters, i, self.param_incr[i])
				self.param_incr[i]*10.0

	def SetXIncrement(self, func_vals): 
		vor = 0.0
		nach = 0.0
		zoom = 0
		for i in range(self.ndata):
			zoom = 0
			self.x_incr[i] = abs(self.x_data[i]*1e-3)
			if self.x_incr[i] == 0.0:
				self.x_incr[i] = 1e-3

			nach = self.function.NumericDeriv(self.x_data[i], func_vals[i], self.x_incr[i], self.parameters)
			vor = 0
			while zoom <= 4 and abs(nach - vor) >= vor:
				zoom += 1
				vor = nach
				self.x_incr[i] *= 0.1
				nach = self.function.NumericDeriv(self.x_data[index], func_vals[index], self.x_incr[i], self.parameters)
			self.x_incr[i]*10.0

	def Fit(self, x_array, y_array, yerr_array, xerr_array=np.empty(0)):
		self.x_data = x_array
		self.y_data = y_array
		self.y_errors = yerr_array
		self.x_errors = xerr_array
		self.ndata = len(self.x_data)
		self.x_incr = np.zeros(self.ndata)
		self.ndf = self.ndata - self.nparams

		if len(xerr_array) == 0:
			self.xErrorFlag = False
		else:
			self.xErrorFlag = True

		self.CurveFit()

	def GetParameterError(self, param_index):
		return np.sqrt(abs(self.covMatrix[param_index][param_index]))

	def CalculateChiSquare(self, func_vals):
		y_eff_errors = np.zeros(self.ndata)
		if self.numericFlag:
			if self.xErrorFlag:
				for i in range(self.ndata):
					y_eff_errors[i] = np.sqrt(self.y_errors[i]**2.0 + (self.x_errors[i]*self.function.NumericDeriv(self.x_data[i], func_vals[i], self.x_incr[i], self.parameters))**2.0)
			else:
				y_eff_errors = self.y_errors
		elif self.xErrorFlag:
			for i in range(self.ndata):
				y_eff_errors[i] = np.sqrt(self.y_errors[i]**2.0 + (self.x_errors[i]*self.function.EvaluateDeriv(self.x_data[i], self.parameters))**2.0)
		else:
			y_eff_errors = self.y_errors

		chisq = np.sum(((self.y_data - func_vals)/y_eff_errors)**2.0)
		return chisq, y_eff_errors

	def CurveFit(self):
		hauptschritt=0
		sub_iters=0
		residuum = np.zeros(self.ndata)
		y = 0.0
		dy = 0.0
		chi_lastmain = 0.0
		chi_lastsub = 0.0
		chi_fit = 0.0
		schlechter = True

		b = np.zeros(self.nparams)
		abl = np.zeros(self.nparams)
		norm = np.zeros(self.nparams)

		func_vals = np.zeros(self.ndata)
		y_eff_errors = np.zeros(self.ndata)

		a = np.zeros((self.nparams, self.nparams))
		afaktor = np.zeros((self.nparams, self.nparams))
		inv = np.zeros((self.nparams, self.nparams))

		for i in range(self.ndata):
			func_vals[i] = self.function.Evaluate(self.x_data[i], self.parameters)

		if self.numericFlag:
			self.SetParamIncrement(func_vals)
			if self.xErrorFlag:
				self.SetXIncrement(func_vals)
				

		chi_lastsub, y_eff_errors = self.CalculateChiSquare(func_vals)
		chi_lastmain = chi_lastsub

		temp_params = np.zeros(self.nparams)

		#Main optimization loop

		while True:
			chi_fit = chi_lastmain
			for i in range(self.nparams):
				for j in range(self.nparams):
					a[i][j] = 0.0
				b[i] = 0.0

			residuum = (self.y_data - func_vals)/(y_eff_errors**2.0)
			for i in range(self.ndata):
				for j in range(self.nparams):
					if(self.numericFlag):
						abl[j] = self.function.NumericParamDeriv(self.x_data[i], func_vals[i], self.parameters, j, param_incr[j])
					else:
						abl[j] = self.function.EvaluateParamDeriv(self.x_data[i], self.parameters, j)
					b[j] += abl[j]*residuum[i]
				for j in range(self.nparams):
					for k in range(self.nparams):
						a[j][k] += abl[j]*abl[k]/(y_eff_errors[i]**2.0)

			for i in range(self.nparams):
				if a[i][i] < 1e-15:
					a[i][i] = 1e-15
				norm[i] = np.sqrt(a[i][i])

			temp_params = self.parameters

			#sub-loop looking for the best next step
			sub_iters=0
			while True:
				chi_lastsub = 0.0
				for i in range(self.nparams):
					for j in range(self.nparams):
						afaktor[i][j] = a[i][j]/(norm[i]*norm[j])
					afaktor[i][i] = 1.0 + self.Lambda


				inv = np.linalg.inv(afaktor)
				for i in range(self.nparams):
					for j in range(self.nparams):
						self.parameters[i] += b[j]*inv[i][j]/(norm[i]*norm[j])

				for i in range(self.ndata):
					func_vals[i] = self.function.Evaluate(self.x_data[i], self.parameters)

				chi_lastsub, y_eff_errors = self.CalculateChiSquare(func_vals)

				schlechter = (chi_lastsub - chi_lastmain > 1e-5) and self.Lambda != 0
				sub_iters += 1
				if sub_iters > self.MAX_ITERS:
					break
				elif schlechter:
					self.parameters = temp_params
					self.Lambda *= 10.0
				else:
					break
			#end sub-loop

			chi_lastmain = chi_lastsub
			if self.numericFlag:
				self.SetParamIncrement(func_vals)
			self.Lambda *= 0.1
			hauptschritt += 1

			if abs(chi_fit - chi_lastmain) < self.PRECISION*chi_fit or hauptschritt > self.MAX_ITERS or self.Lambda == 0.0:
				break
		#end main loop

		for i in range(self.nparams):
			for j in range(self.nparams):
				afaktor[i][j] = a[i][j]/(norm[i]*norm[j])

		self.covMatrix = np.linalg.inv(afaktor)
		self.chiSq = chi_lastmain
		if self.ndata > self.nparams:
			self.redChiSq = self.chiSq/self.ndf
		else:
			self.redChiSq = 0.0

		return hauptschritt			


class LinearFunction(FitFunction):
	def __init__(self):
		super().__init__(2, numericFlag=False)

	def Evaluate(self, x, params):
		return params[0] + x*params[1]

	def EvaluateDeriv(self, x, params):
		return params[1]

	def EvaluateParamDeriv(self, x, params, this_param):
		if this_param == 0:
			return 1.0
		elif this_param == 1:
			return x
		else:
			return 0.0

class QuadraticFunction(FitFunction):
	def __init__(self):
		super().__init__(3, numericFlag=False)

	def Evaluate(self, x, params):
		return params[0] + x*params[1] + (x**2.0)*params[2]

	def EvaluateDeriv(self, x, params):
		return params[1]+2.0*x*params[2]

	def EvaluateParamDeriv(self, x, params, this_param):
		if this_param == 0:
			return 1.0
		elif this_param == 1:
			return x
		elif this_param == 2:
			return x**2.0
		else:
			return 0.0

class CubicFunction(FitFunction):
	def __init__(self):
		super().__init__(4, numericFlag=False)

	def Evaluate(self, x, params):
		return params[0] + x*params[1] + (x**2.0)*params[2] + (x**3.0)*params[3]

	def EvaluateDeriv(self, x, params):
		return params[1]+2.0*x*params[2]+3.0*(x**2.0)*params[3]

	def EvaluateParamDeriv(self, x, params, this_param):
		if this_param == 0:
			return 1.0
		elif this_param == 1:
			return x
		elif this_param == 2:
			return x**2.0
		elif this_param == 3:
			return x**3.0
		else:
			return 0.0

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

	fit_func = LinearFunction()
	my_fit = SpancFit(fit_func)
	my_fit.parameters[0] = 1.0
	my_fit.parameters[1] = 1.0
	print("Testing SPANC fitting routine using test data and linear function...")
	my_fit.Fit(x, y, dy)
	print("Results from fit with y-errors: param[0] =",my_fit.parameters[0],"param[1] =",my_fit.parameters[1],"Reduced chi-sq =",my_fit.redChiSq)

if __name__ == '__main__':
	main()


