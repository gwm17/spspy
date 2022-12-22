import os
os.environ["QT_API"] = "pyside6"
from spspy.SPSPlotUI import run_spsplot_ui
from spspy.SpancUI import run_spanc_ui
from spspy.Launcher import run_launcher

#run_spsplot_ui()
#run_spanc_ui()
run_launcher()