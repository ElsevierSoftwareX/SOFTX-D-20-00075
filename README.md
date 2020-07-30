# SEDBYS

[![astropy](http://img.shields.io/badge/powered%20by-AstroPy-orange.svg?style=flat)](http://www.astropy.org/)

SEDBYS: SED builder for Young Stars

1. **Requirements and set-up:**

A. SEDBYS uses existing functions from astropy and other standard python packages. You are recommended to install python3 using anaconda: [www.anaconda.com](https://www.anaconda.com/) which includes all packages used by SEDBYS as standard. 


B. Clone a version of SEDBYS to your local machine. If you are new to git, see 
[gitLab basics: start using git](https://docs.gitlab.com/ee/gitlab-basics/start-using-git.html) to get started.

Save the SEDBYS directory path as environment variable `$SED_BUILDER` on your local machine. E.g. in your .bashrc file:

`export SED_BUILDER=/path/to/SEDBYS/on/local/machine`

or in your .cshrc file:

`setenv SED_BUILDER /path/to/SEDBYS/on/local/machine`

To ensure that the SEDBYS scripts `queryDB.py` and `inspectSED.py` can be run from anywhere on your local machine, you will also need to add the SEDBYS directory to your $PATH and $PYTHONPATH. e.g. in your .cshrc file:

`setenv PATH $SED_BUILDER:$PATH`

`setenv PYTHONPATH $SED_BUILDER:$PYTHONPATH`

(Remember: you will need to source your .bashrc or .cshrc file for these changes to become active).



2. **Compiling photometric data from the online and local databases**

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



3. **Inspecting the collated photometry and building the SED**
 
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
  

4. **Creating a LaTeX table (and corresponding bibTeX file) from the retrieved photometry**

The `toLaTex.py` script in SEDBYS is designed to create a LaTeX table (saved to a .tex file in the object directory) and corresponding bibTeX file (saved to a corresponding .bib file in the object directory) from the photometry files output by `queryDB.py` or `inspectSED.py`. To generate these files, use e.g.

`toLaTex.py --phot=HD283571/HD283571_phot.dat`

Example files `sedbys_HD283571.tex` and `sedbys_HD283571.bib` are provided in ![examples/sedbys_HD283571.tex](examples/sedbys_HD283571.tex) and ![examples/sedbys_HD283571.bib](examples/sedbys_HD283571.bib), respectively.


5. **Adding new entries to the local and online databases**

You may add new catalogs to the database using `addLocal.py` (to import a table to the local database) or `addVizCat.py` (to add metadata for a new VizieR catalog). For example, to add the TYCHO-2 catalog to the list of VizieR catalogs queried by `queryDB.py`, you would run the following from within the SEDBYS directory on your machine.

`python3 addVizCat.py --nam=TYCHO2 --cat='I/259/tyc2' --ref='2000A&A...355L..27H' --wav=426e-9,532e-9 --res=0.37,0.462 --fna=BTmag,VTmag --ena=e_BTmag,e_VTmag --una=mag,mag --bna=HIP:BT,HIP:VT`

Here, 

* `--nam` is used to assign a unique identifier to this catalog
* `--cat` is the catalog extension on VizieR
* `--ref` is the bibref for the paper accompanying the catalog
* `--wav` is a comma separated list of wavelengths (in metres) of the measurements in the catalog
* `--res` is a comma separated list of angular resolutions (i.e. the diffraction limit of the telescope used or the effective beam of interferometric measurements)
* `--fna` is a comma separated list of column headers used to locate the flux/magnitude information in the VizieR catalog
* `--ena` is the same as `--fna` but for the measurement uncertainty
* `--una` is a comma separated list of measurement units (i.e. one of 'mag', 'mJy' or 'Jy' for each measurement)
* `--bna` is a comma separated list of waveband names. If `--una=mag` for any measurement, these must correspond to a waveband name in the SEDBYS zero_points.dat file. 

A number of checks are built into `addVizCat.py` to try make this procedure failsafe. Messages will be printed to screen to help guide you should you have formatting issues.


To import a table to the local database, you must first collate the data into a SEDBYS-compatible format:

* The file must be comma separated
* The first line of the file acts as a header. It must follow the format "Target,...,...,ObsDate" where "...,..." are a user-defined list of flux/magnitude measurement column headers and measurement uncertainty column headers. 
* Each target name must be SIMBAD-compatible or, for components of binary or multiple systems which lack their own SIMBAD entry, must comprise a SIMBAD-compatible name plus a suffix which denotes its position in the binary/multiple system. For example, the secondary component of the XZ Tau system appears as V* XZ Tau B (see below for further details on object name restrictions).
* The observation date must be provided in YYYYMmm or YYYYMmmDD format (or appear as 'unknown' or 'averaged').

Then, to add this new table to the local database, you can run the following command from the SEDBYS directory on your local machine. 

`python3 addLocal.py --nam=HERSCHEL1 --fil=herschel_phot.csv --ref='2016A&A...586A...6P' --wav=70e-6,100e-6,160e-6 --res=5.033,7.190,11.504 --fna=F70,F100,F160 --ena=eF70,eF100,eF160 --una=Jy,Jy,Jy --bna=Herschel:PACS:F70,Herschel:PACS:F100,Herschel:PACS:F160`

Most of the parser arguments are the same for `addLocal.py` as for `addVizCat.py` (see above) with the following exceptions:

* `--fil` is the full file path from your current working directory to the file you wish to add to the SEDBYS local database. In the above example, it is assumed this file is in the current working directory. SEDBYS will copy this file into the SEDBYS `database/` directory.
* `--fna` and `--ena` should match the column headers used in the file to mark the measurements and their uncertainties, respectively.

On completion, `addLocal.py` and `addVizCat.py` will prompt you to commit your changes to git so that these new catalogs can be used by all SEDBYS users. Please follow the instructions printed on the screen to do this.



6. **Object name restrictions**

SEDBYS relies on being able to cross-match common object names and aliases from different catalogs using SIMBAD. All entries in the local database are thus SIMBAD-compatible and, moreover, are entered as they appear in full on SIMBAD. For instance, local database entries for our example case above (Section 3) may appear as HD 283571 or as V* RY Tau, but not as the short-hand name RY Tau. However, as, in this instance, the short-hand name is recognised by SIMBAD, parsing `--obj=RY_Tau` when using `queryDB.py` will still retrive data for this object.

Some photometry exists in the local database for objects that are not in SIMBAD. These have been assumed to be the individual components of a binary or multiple system. These objects appear in the local database using the SIMBAD-compatible name of their parent star with a suffix (e.g. ' A', ' Aa' ' BC' etc) which relates to their multiplicity. For example, the individual components of the binary young stellar object XZ Tau would appear in the local database as V* XZ Tau A and V* XZ Tau B. If individual component photometry is available in the local database, this is will not be automatically retrieved when conducting a search for the parent star (e.g. XZ Tau). Instead, an alert is printed to screen saying that photometry exists for individual components of this system, prompting the user to conduct a separate search for these components individually if necessary. 

**CAUTION: the identification of a binary component as primary or secondary etc may be wavelength or time dependent or simply vary between studies. The user is advised to check the references provided to ensure the naming is consistent between studies.**
