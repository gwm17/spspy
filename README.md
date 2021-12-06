# SPSPy
SPSPy is a Python based package of tools for use with the Super-Enge Split-Pole Spectrograph at FSU. Much of the code here is based on Java programs originally written at Yale University by D.W. Visser, C.M. Deibel, and others. Currently the package contains spsplot, a tool aimed at informing users which states should appear at the focal plane of the SESPS, and spanc, a tool for calibrating the position spectra from the focal plane.

# Depencencies and Requirements
SPSPy requires the Python packages qtpy (along with a functional Qt distriubtion for python), matplotlib, numpy, lxml, and scipy to guarantee full functionality. The most straightforward way to intstall all dependencies is by using either pip or having a distribution such as Anaconda.

Spsplot also requires that the user have an internet connection.

## spsplot
This tool is intended to be used for guiding the settings of the SPS to show specific states on the focal plane detector. The user gives the program reaction information, and the program runs through the kinematics to calculate the energies of ejecta into the the SESPS. To evaluate different states, the program scrapes a list of levels from www.nndc.bnl.gov, and these levels are then passed on to the reaction handler. These levels are then shown on the screen with labels. The labels can be modified to show either the excitation energy of the state, or the kinetic energy of the ejectile.

## spanc
SPANC is the program used to calibrate SESPS focal plane spectra. It works by the user specifying a target, reaction, calibration peaks, and output peaks. The target is a description of the physical target foil used in the SPS, which is used to calculate energy loss effects. The target must contain the isotope used as the target in the reaction description. The reaction indicates to the program what type of ejecta are expected, as well as the settings of the spectrograph. Calibration data is given as centroids from a spectrum with correspoding excitation energies, as well as associated uncertainties. The calibration peaks are then fit using the scipy ODR package (see scipy ODR for more documentation). The fit is plotted, and the results are shown in a table. Additionally, residuals are plotted and shown in a table. The user can then feed the program an output peak, or a peak for which the user would like to calculate the excitation energy of a state using the calibration fit. The peak excitation energy will then be reported, with uncertainty. The user can also give a FWHM to be converted from focal plane position to energy. 

# Running the tools
Use `./bin/spanc` or `./bin/spsplot`. Note that they should be run from the SPSPy directory, as there are some file paths which need to be maintained.

### Known issues
	1. NNDC sometimes puts annoying characters in the ENDSF list; each of these "special characters" needs to be added to a list of exclusions
	2. Not really an issue but with high level density reactions, spsplot becomes quite crowded. Working on implementing level removal.
	3. Debian -- mostly relevant to SPS DAQ machine, but Qt on debian running with a TightVNC instance causes a crash of the VNC server. Current fix is to implement a virtual env for a ssh into the DAQ machine from which the tools will be used, while leaving the VNC window free from the Qt related code.
