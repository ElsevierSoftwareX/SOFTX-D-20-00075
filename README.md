# SEDBYS

[![astropy](http://img.shields.io/badge/powered%20by-AstroPy-orange.svg?style=flat)](http://www.astropy.org/)

SEDBYS: SED builder for Young Stars

1. Requirements:

SEDBYS uses existing functions from astropy and other standard python packages. You are recommended to install python3 using anaconda: [www.anaconda.com](https://www.anaconda.com/) which includes all packages used by SEDBYS as standard. 


2. Setting up:

Clone a version of SEDBYS to your local machine using git clone. If you are new to git, see 
[gitLab basics: start using git](https://docs.gitlab.com/ee/gitlab-basics/start-using-git.html) to get started.

Save the SEDBYS directory path as environment variable `$SED_BUILDER` on your local machine. E.g. in your .bashrc file:

`export SED_BUILDER=/path/to/SEDBYS/on/local/machine`

or in your .cshrc file:

`setenv SED_BUILDER /path/to/SEDBYS/on/local/machine`

To ensure that the SEDBYS scripts `queryDB.py` and `inspectSED.py` can be run from anywhere on your local machine, you will also need to add the SEDBYS directory to your $PATH and $PYTHONPATH. e.g. in your .cshrc file:

`setenv PATH $SED_BUILDER:$PATH`

`setenv PYTHONPATH $SED_BUILDER:$PYTHONPATH`

(Remember: you will need to source your .bashrc or .cshrc file for these changes to become active).



3. Compiling photometric data from the online and local databases

Use the `queryDB.py` script to retrieve photometry from the online and local databses. For example, running
`queryDB.py --obj=HD_283571 --rad=10s`
will search for photometry for young stellar object HD 283571. A cone search radius of 10 arcseconds will be used when querying the online database.

Additional optional arguments for `queryDB.py`:
*  `--getSpect`: set to 'True' to additionally retrieve fully processed, flux-calibrated infrared spectra from ISO/SWS and Spitzer
*  `--closest`: set to True to automatically retrieve the closest entry in an online catalog when multiple entries are found within the search radius. This avoids the (default) user interactivity to select the best match and is particularly useful when running `queryDB.py` in batch mode.
*  `--queryAll`: details provided below.  

For each search, a new directory will be created in the current working directory. The directory name is taken from the object name parsed to `--obj` i.e., in the above example, a HD283571/ directory will be created.

The collated photometry will be saved to file in this new directory. In the above example, this is called HD283571_phot.dat.

Any retrieved spectra wll also be saved (in .fits format) to this directory. The original file names used in the ISO/SWS and CASSIS atlases are retained. 


4. Inspecting the collated photometry and building the SED
 
Use the `inspectSED.py` script to flux convert the photometry and inspect the compiled SED. For example, running

`inspectSED.py --phot=HD283571/HD283571_phot.dat --spec=HD283571/cassis_yaaar_spcfw_26141184t.fits`

will display the following plot:

![examples/HD283571_sed.pdf](examples/HD283571_sed.pdf)

From this plot, we can clearly see that the SED for HD 283571 is contaminated. We can clean this plot, and remove contaminant photometry which may be saturated or arising from an incorrect cross-match, for instance. The plot that is displayed when running `inspectSED.py` is interactive and clicking on erreanous data points will flag them for removal. You can see if a click is registered by monitoring the terminal output which will provide details of the waveband of the respective data. 

A cleaned version of the photometry will be saved to file in the object directory. In the above example, this file is called HD283571_phot_cleaned_0.dat. The numerical index at the end of the filename is used to avoid previous attempts being over-written. If file HD283571_phot_cleaned_0.dat has already existed, file HD283571_phot_cleaned_1.dat would have been created instead.

Running `inspectSED.py --phot=HD283571_phot_cleaned_0.dat` then displays our cleaned SED:

![examples/HD283571_sed_cleaned.pdf](examples/HD283571_sed_cleaned.pdf)

(Note that HD 283571 is a variable YSO so different measures of the optical and infrared flux density have been retained in our example case.)

Additional optional arguments for `inspectSED.py`:
*  `--scale`: a scale factor which may be used to shift the spectral data in the y-direction where necessary.
*  `--pltR`: comma-separated lower and upper limits to the x-axis for plotting in case the user wishes the zoom-in on a particular region or produce plots with uniform axes across a sample or target stars.
  


5. Adding new entries to the local and online databases

(details to be provided soon)
