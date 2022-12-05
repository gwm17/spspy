# SPSPy
SPSPy is a Python based package of tools for use with the Super-Enge Split-Pole Spectrograph at FSU. Much of the code here is based on Java programs originally written at Yale University by D.W. Visser, C.M. Deibel, and others. Currently the package contains SPSPlot, a tool aimed at informing users which states should appear at the focal plane of the SESPS, and SPANC, a tool for calibrating the position spectra from the focal plane.

## Depencencies and Requirements
The requirements for running SPSPy are outlined in the requirements.txt file located in the repository. It is recommended to install these to a local virtual environment using `pip install -r requirements.txt`. For conda use the environments.yml file to create a conda environment for SPSPy. Simply run `conda env create -f environment.yml` from the SPSPy directory. conda will make a new virtual environment named spsenv with the dependencies outlined in environments.yml. If you already have an environment named spsenv or would like to change the name simply edit the first line of the enviornments.yml.

The recommended install for SPSPy dependencies is via pip. 

### Creating a virtual environment with pip
To create a virtual environment with pip in the terminal for MacOS or Linux use `python3 -m venv env` to create a local virtual environment named `env` (or whatever name you'd like), or on Windows use `py -m venv env` to do the same. To activate your new environment run `source env/bin/activate` in MacOS or Linux, or `.\env\Scripts\activate`. Now you can run the above `pip` command to install all dependencies to the virtual environment. To leave the virtual environment use the command `deactivate` in your terminal.

## SPSPlot
This tool is intended to be used for guiding the settings of the SPS to show specific states on the focal plane detector. The user gives the program reaction information, and the program runs through the kinematics to calculate the energies of ejecta into the the SESPS. To evaluate different states, the program scrapes a list of levels from [NNDC](https://www.nndc.bnl.gov/), and these levels are then passed on to the reaction handler. These levels are then shown on the screen with labels. The labels can be modified to show either the excitation energy of the state, the kinetic energy of the ejectile, or the focal plane z-offset for a state. Note that since levels are obtained from NNDC, SPSPlot requires an internet connection.

## SPANC
SPANC is the program used to calibrate SESPS focal plane spectra. It works by the user specifying a target, reaction, calibration peaks, and output peaks. The target is a description of the physical target foil used in the SPS, which is used to calculate energy loss effects. The target must contain the isotope used as the target in the reaction description. The reaction indicates to the program what type of ejecta are expected, as well as the settings of the spectrograph. Calibration data is given as centroids from a spectrum with correspoding excitation energies, as well as associated uncertainties. The calibration peaks are then fit using the scipy ODR package (see scipy ODR for more documentation). The fit is plotted, and the results are shown in a table. Additionally, residuals are plotted and shown in a table. The user can then feed the program an output peak, or a peak for which the user would like to calculate the excitation energy of a state using the calibration fit. The peak excitation energy will then be reported, with uncertainty. The user can also give a FWHM to be converted from focal plane position to energy. 

## Running the tools
Activate the environment containing the requirements and then simply `python main.py` from the repository. This will bring up a launcher from which you can select a tool.

### Known issues
	1. NNDC sometimes puts annoying characters in the ENDSF list; each of these "special characters" needs to be added to a list of exclusions
	2. Not really an issue but with high level density reactions, spsplot becomes quite crowded. Working on implementing level removal.
