from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
import matplotlib

matplotlib.rcParams["axes.facecolor"] = "#0F1016"
matplotlib.rcParams["figure.facecolor"] = "#0F1016"
matplotlib.rcParams["axes.labelcolor"] = "w"
matplotlib.rcParams["axes.edgecolor"] = "w"
matplotlib.rcParams["xtick.color"] = "w"
matplotlib.rcParams["ytick.color"] = "w"
matplotlib.rcParams["text.color"] = "w"

class MPLCanvas(FigureCanvasQTAgg):
	def __init__(self, parent=None, width=5, height=4, dpi=100):
		self.fig = Figure(figsize=(width, height), dpi=dpi, edgecolor="black",linewidth=0.5)
		self.axes = self.fig.add_subplot(111)
		self.axes.spines['top'].set_visible(False)
		super(MPLCanvas, self).__init__(self.fig)