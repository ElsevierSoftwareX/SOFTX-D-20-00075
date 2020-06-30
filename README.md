# SEDBYS

[![astropy](http://img.shields.io/badge/powered%20by-AstroPy-orange.svg?style=flat)](http://www.astropy.org/)

SEDBYS: SED builder for Young Stars

1. Requirements:

SEDBYS uses existing functions from astropy and other standard python packages. You are recommended to install python3 using anaconda: [www.anaconda.com](https://www.anaconda.com/) which includes all packages used by SEDBYS as standard. 


2. Setting up:

Clone a version of SEDBYS to your local machine. If you are new to git, see 
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

will search for photometry for young stellar object HD 283571. A cone search radius of 10 arcseconds around the object's RA and Dec (retrieved from SIMBAD) will be used when querying the online catalogs. If multiple entries are found in the same catalog within the search cone radius, the user will be prompted to enter the "_r" value corresponding to their target. This "_r" value is the separation between the search coordinates of the object and the coordinates of the match in the catalog (in arcseconds). Using optional argument `--closest=True` (see below) is recommended if the user wishes to automatically retrieve the closest entry to the search coordinates. 

The object name provided (together with all aliases retrieved from SIMBAD, where applicable - see note below on the object name restrictions), will be used when querying the local database. The cone search radius is not used here. 

Additional optional arguments for `queryDB.py`:
*  `--getSpect`: set to 'True' to additionally retrieve fully processed, flux-calibrated infrared spectra from ISO/SWS and Spitzer
*  `--closest`: set to True to automatically retrieve the closest entry in an online catalog when multiple entries are found within the search radius. This avoids the (default) user interactivity to select the best match and is particularly useful when running `queryDB.py` in batch mode.
*  `--queryAll`: details provided below.  

For each search, a new directory will be created in the current working directory. The directory name is taken from the object name parsed to `--obj` i.e., in the above example, a HD283571/ directory will be created.

The collated photometry will be saved to file in this new directory. In the above example, this is called HD283571_phot.dat. The header of this photometry file contains the object name used in the search, the RA and Dec retrieved from SIMBAD, and the cone search radius used.

Any retrieved spectra wll also be saved (in .fits format) to this directory. The original file names used in the ISO/SWS and CASSIS atlases are retained. 


4. Inspecting the collated photometry and building the SED
 
Use the `inspectSED.py` script to flux convert the photometry and inspect the compiled SED. For example, running

`inspectSED.py --phot=HD283571/HD283571_phot.dat --spec=HD283571/cassis_yaaar_spcfw_26141184t.fits`

will display the following plot:

![examples/HD283571_sed.pdf](examples/HD283571_sed.pdf)

NB: all errorbars are plotted where measurement errors are available. In some cases, these are smaller than the size of the data points. Upper limits (recognised as entries where measurement value = measurement uncertainty) are indicated by downward arrows. 

From this plot, we can clearly see that the SED for HD 283571 is contaminated. We can clean this plot, and remove contaminant photometry which may be saturated or arising from an incorrect cross-match, for instance. The plot that is displayed when running `inspectSED.py` is interactive and clicking on erreanous data points will flag them for removal. You can see if a click is registered by monitoring the terminal output which will provide details of the waveband of the respective data. 

If you have trouble selecting a data point for removal due to it being in close proximity to another data point, try limiting the x-axis plotting range using optional argument `--pltR` (see below).

A cleaned version of the photometry will be saved to file in the object directory. In the above example, this file is called HD283571_phot_cleaned_0.dat. The numerical index at the end of the filename is used to avoid existing files being over-written. If file HD283571_phot_cleaned_0.dat had already existed, file HD283571_phot_cleaned_1.dat would have been created instead.

Running `inspectSED.py --phot=HD283571_phot_cleaned_0.dat` will display the cleaned SED (see plot below) should the process need to be repeated.

![examples/HD283571_sed_cleaned.pdf](examples/HD283571_sed_cleaned.pdf)

(Note that HD 283571 is a variable YSO so different measures of the optical and infrared flux density have been retained in our example case.)

Additional optional arguments for `inspectSED.py`:
*  `--scale`: a scale factor which may be used to shift the spectral data in the y-direction where necessary.
*  `--pltR`: comma-separated lower and upper limits to the x-axis (in microns) for plotting in case the user wishes the zoom-in on a particular region or produce plots with uniform axes across a sample or target stars (e.g. --pltR=0.1,1000).
*  `--savePlt`: a boolean (default = False) instructing the script whether to automatically save plots of the full and cleaned SED. If True, the file naming is handled automatically. In our example above, the full SED would be saved as HD283571_sed_0.pdf and the cleaned SED would be saved as HD283571_sed_cleaned_0.dat. As before, the numerical indexes are used to ensure that existing files are not over-written.
  


5. Adding new entries to the local and online databases

(details to be provided soon)


6. Object name restrictions

The database relies on being able to cross-match common object names and aliases from different catalogs using SIMBAD. All entries in the local database are thus SIMBAD-compatible and, moreover, are entered as they appear in full on SIMBAD. For instance, entries for our example case above may appear as HD 283571 or as V* RY Tau, but not as the short-hand name RY Tau. However, as, in this instance, the short-hand name is recognised by SIMBAD, parsing `--obj=RY_Tau` when using `queryDB.py` will work.

Some photometry exists in the local database for objects that are not in SIMBAD. These have been assumed to be the individual components of a binary or higher order multiple system. These objects appear in the local database using the SIMBAD-compatible name of their parent star with a suffix (e.g. ' A', ' Aa' or ' B+C') which relates to their multiplicity. For example, the individual components of the binary young stellar object XZ Tau would appear in the local database as V* XZ Tau A and V* XZ Tau B. If individual component photometry is available in the local database, this is will not be automatically retrieved when conducting a search for the parent star (e.g. XZ Tau). Instead, a warning will be printed to screen to make the user aware that photometry exists for individual components of this system, alerting the user to conduct a separate search for these components individually if necessary. 

**CAUTION: the identification of a binary component as primary or secondary etc may be wavelength or time dependent or simply vary between studies. The user is advised to check the references provided to ensure the naming is consistent between studies.**
