import numpy as np
from numpy.typing import NDArray
from numpy.polynomial import Polynomial
from scipy import odr
from dataclasses import dataclass
from typing import Optional

INVALID_FIT_RESULT = np.inf
INVALID_NDF = -1

@dataclass
class FitPoint:
    x: float = 0.0
    y: float = 0.0
    xError: float = 0.0
    yError: float = 0.0

def convert_fit_points_to_arrays(data: list[FitPoint]) -> tuple[NDArray[np.float64], NDArray[np.float64], NDArray[np.float64], NDArray[np.float64]]:
    xArray = np.empty(len(data))
    yArray = np.empty(len(data))
    xErrorArray = np.empty(len(data))
    yErrorArray = np.empty(len(data))
    for index, point in enumerate(data):
        xArray[index] = point.x
        yArray[index] = point.y
        xErrorArray[index] = point.xError
        yErrorArray[index] = point.yError
    return xArray, yArray, xErrorArray, yErrorArray

@dataclass
class FitResidual:
    x: float = 0.0
    residual: float = 0.0
    studentizedResidual: float = 0.0

def convert_resid_points_to_arrays(data: list[FitResidual]) -> tuple[NDArray[np.float64], NDArray[np.float64], NDArray[np.float64]]:
    xArray = np.empty(len(data))
    residArray = np.empty(len(data))
    studentResidArray = np.empty(len(data))
    for index, point in enumerate(data):
        xArray[index] = point.x
        residArray[index] = point.residual
        studentResidArray[index] = point.studentizedResidual
    return xArray, residArray, studentResidArray

class Fitter:
    def __init__(self, order: int =1):
        self.polynomialOrder: int = order
        self.fitResults: Optional[odr.Output] = None
        self.fitData: Optional[list[FitPoint]] = None
        self.function: Optional[Polynomial] = None

    def set_polynomial_order(self, order: int) -> None:
        self.polynomialOrder = order

    def run(self, data: list[FitPoint] = None) -> None:
        if data is not None:
            self.fitData = data
        
        if self.fitData is not None:
            xArray, yArray, xErrorArray, yErrorArray = convert_fit_points_to_arrays(self.fitData)
            modelData = odr.RealData(xArray, y=yArray, sx=xErrorArray, sy=yErrorArray)
            model = odr.polynomial(self.polynomialOrder)
            self.fitResults = odr.ODR(modelData, model).run()
            self.function = Polynomial(self.fitResults.beta)
        else:
            print("Cannot run fitter without setting data to be fit!")

    def get_parameters(self) -> NDArray[np.float64] :
        if self.fitResults is not None:
            return self.fitResults.beta
        return np.array({INVALID_FIT_RESULT})

    def get_parameter_errors(self) -> NDArray[np.float64] :
        if self.fitResults is not None:
            return self.fitResults.sd_beta
        return np.array({INVALID_FIT_RESULT})

    def get_ndf(self) -> int:
        if self.fitResults is not None:
            return len(self.fitData) - 1
        return INVALID_NDF

    def evaluate(self, x: float) -> float:
        if self.function is not None:
            return self.function(x)
        return INVALID_FIT_RESULT

    def evaluate_derivative(self, x: float) -> float:
        if self.function is not None:
            return self.function.deriv()(x)
        return INVALID_FIT_RESULT

    def evaluate_param_derivative(self, x: float, index: int) -> float:
        if self.fitResults is not None and len(self.fitResults.beta) > index:
            return x**index
        return INVALID_FIT_RESULT

    def get_chisquare(self) -> float:
        if self.function is not None:
            yEffErrorArray = [np.sqrt(point.yError**2.0 + (point.xError * self.evaluate_derivative(point.x))**2.0) for point in self.fitData]
            chisq = 0.0
            for index, point in enumerate(self.fitData):
                chisq = ((point.y - self.evaluate(point.x)) / yEffErrorArray[index])**2.0
            return chisq
        return INVALID_FIT_RESULT

    def get_reduced_chisquare(self) -> float:
        ndf = self.get_ndf()
        chisq = self.get_chisquare()
        if chisq == INVALID_FIT_RESULT or ndf == INVALID_NDF:
            return INVALID_FIT_RESULT
        else:
            return chisq/ndf

    def get_residuals(self) -> list[FitResidual]:
        if self.fitData is not None:
            fitResiduals = [FitResidual(point.x, point.y - self.evaluate(point.x), 0.0) for point in self.fitData]

            #compute the leverage and studentize
            xMean = 0.0
            rmse = 0.0
            npoints = len(fitResiduals)
            for resid in fitResiduals:
                xMean += resid.x
                rmse += resid.residual**2.0
            xMean /= npoints
            rmse /= self.get_ndf()

            meanDiffSq = 0.0
            for resid in fitResiduals:
                meanDiffSq += (resid.x - xMean) ** 2.0
            meanDiffSq /= npoints
            for resid in fitResiduals:
                leverage = 1.0/npoints + (resid.x - xMean)/meanDiffSq
                resid.studentizedResidual = resid.residual / (rmse * np.sqrt(1.0 - leverage))
            return fitResiduals
        return []
