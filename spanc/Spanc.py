#!/usr/bin/env python3

from Reaction import Reaction
from LayeredTarget import LayeredTarget, Target
from IngoFit import SpancFit, LinearFunction, QuadraticFunction, CubicFunction
from Fitter import LinearFit, QuadraticFit, CubicFit
import numpy as np 

class Peak :
	def __init__(self):
		self.Ex = 0.0
		self.uEx = 0.0
		self.x = 0.0
		self.ux_sys = 0.0
		self.ux_stat = 0.0
		self.rho = 0.0
		self.urho = 0.0
		self.fwhm_x = 0.0
		self.ufwhm_x = 0.0
		self.fwhm_Ex = 0.0
		self.ufwhm_Ex = 0.0
		self.reaction = ""

class Spanc:
	def __init__(self):
		self.reactions = {}
		self.targets = {}
		self.calib_peaks = {}
		self.output_peaks = {}
		self.fitters = {}
		self.InitFits()

	def WriteConfig(self):
		return

	def ReadConfig(self):
		return

	def InitFits(self):
		"""
		self.fitters["linear"] = SpancFit(LinearFunction())
		self.fitters["quadratic"] = SpancFit(QuadraticFunction())
		self.fitters["cubic"] = SpancFit(CubicFunction())
		"""
		self.fitters["linear"] = LinearFit()
		self.fitters["quadratic"] = QuadraticFit()
		self.fitters["cubic"] = CubicFit()

	def PerformFits(self):
		xarray = np.empty(0)
		yarray = np.empty(0)
		uxarray = np.empty(0)
		uyarray = np.empty(0)

		for peak in self.calib_peaks.values():
			xarray = np.append(xarray, peak.x)
			uxarray = np.append(uxarray, np.sqrt(peak.ux_sys**2.0 + peak.ux_stat**2.0))
			yarray = np.append(yarray, peak.rho)
			uyarray = np.append(uyarray, peak.urho)

		for key in self.fitters.keys():
			#self.fitters[key].Fit(xarray, yarray, uyarray, uxarray)
			self.fitters[key].RunFit(xarray, yarray, uyarray, uxarray)

		return xarray, yarray, uxarray, uyarray

	def CalculateResiduals(self, fit_name):
		fit = self.fitters[fit_name]
		npeaks = len(self.calib_peaks)

		resids = np.empty(npeaks)
		student_resids = np.empty(npeaks)
		xarray = np.empty(npeaks)
		counter=0
		for peak in self.calib_peaks.values():
			fval = fit.EvaluateFunction(peak.x)
			dval = peak.rho

			resids[counter] = (dval - fval)
			xarray[counter] = peak.x
			counter += 1

		mean_x = np.average(xarray)/npeaks
		rmse = np.sqrt(np.sum(resids**2.0)/fit.GetNDF())


		#get leverage
		counter=0
		sq_diff=0
		for peak in self.calib_peaks.values():
			sq_diff += (peak.x - mean_x)**2.0
		sq_diff = sq_diff/npeaks
		for peak in self.calib_peaks.values():
			leverage = 1.0/npeaks +  (peak.x - mean_x)/sq_diff
			student_resids[counter] = resids[counter]/(rmse*np.sqrt(1.0 - leverage))
			counter += 1


		return xarray, resids, student_resids


	def AddCalibrationPeak(self, rxn_name, cal_name, position, ux_stat, ux_sys, ex, uex) :
		new_peak = Peak()
		new_peak.x = position
		new_peak.reaction = rxn_name
		new_peak.ux_stat = ux_stat
		new_peak.ux_sys	= ux_sys
		new_peak.Ex = ex
		new_peak.uEx = uex
		new_peak.rho = self.reactions[rxn_name].GetEjectileRho(ex)
		new_peak.urho = abs(self.reactions[rxn_name].GetEjectileRho(ex+uex)-new_peak.rho)
		self.calib_peaks[cal_name] = new_peak

	def AddOutputPeak(self, rxn_name, out_name, position, ux_stat, ux_sys, fwhm_x, ufwhm_x) :
		new_peak = Peak()
		new_peak.x = position
		new_peak.ux_stat = ux_stat
		new_peak.ux_sys = ux_sys
		new_peak.reaction = rxn_name
		new_peak.fwhm_x = fwhm_x
		new_peak.ufwhm_x = ufwhm_x
		self.output_peaks[out_name] = new_peak

	def CalculateRhoUncertainty(self, peak, fit, deltax=0.0, udeltax=0.0):
		urho = 0
		for i in range(len(fit.parameters)):
			urho += (fit.EvaluateFunctionParamDeriv(peak.x+deltax, i)*fit.GetParameterError(i))**2.0
		urho += (fit.EvaluateFunctionDeriv(peak.x+deltax)*np.sqrt(peak.ux_stat**2.0 + peak.ux_sys**2.0 + udeltax**2.0))**2.0
		urho = np.sqrt(urho)
		return urho


	def CalculateOutputs(self, fit_name):
		fit = self.fitters[fit_name]
		for output in self.output_peaks.values():
			output.rho = fit.EvaluateFunction(output.x)
			output.urho = self.CalculateRhoUncertainty(output, fit)
			output.Ex = self.reactions[output.reaction].GetResidualExcitation(output.rho)
			output.uEx = abs(self.reactions[output.reaction].GetResidualExcitation(output.rho + output.urho) - output.Ex)
			
			if output.fwhm_x == 0:
				output.fwhm_Ex = 0
				output.ufwhm_Ex = 0
			else:
				rhoLo = fit.EvaluateFunction(output.x - output.fwhm_x/2.0)
				urhoLo = self.CalculateRhoUncertainty(output, fit, deltax=-1.0*output.fwhm_x/2.0, udeltax=output.ufwhm_x/2.0)
				rhoHi = fit.EvaluateFunction(output.x + output.fwhm_x/2.0)
				urhoHi = self.CalculateRhoUncertainty(output, fit, deltax=output.fwhm_x/2.0, udeltax=output.ufwhm_x/2.0)
				exLo = self.reactions[output.reaction].GetResidualExcitation(rhoLo)
				uexLo = abs(self.reactions[output.reaction].GetResidualExcitation(rhoLo+urhoLo) - exLo)
				exHi = self.reactions[output.reaction].GetResidualExcitation(rhoHi)
				uexHi = abs(self.reactions[output.reaction].GetResidualExcitation(rhoHi+urhoHi) - exHi)
				output.fwhm_Ex = abs(exHi - exLo)
				output.ufwhm_Ex = output.ufwhm_x/output.fwhm_x*output.fwhm_Ex

	def CalculateCalibrations(self):
		for peak in self.calib_peaks.values():
			peak.rho = self.reactions[peak.reaction].GetEjectileRho(peak.Ex)
			peak.urho = abs(self.reactions[peak.reaction].GetEjectileRho(peak.Ex+peak.uEx) - peak.rho)


