from urllib import request
import subprocess
import os
from datetime import date
import astropy.coordinates as coord
from astropy import units as u

def queryCASSIS(objN, RA, DEC, searchR=str(20)):
    """
    Query CASSIS using an object's RA and Dec (=RA and 
    Dec, respectively; units = decimal degrees), 
    together with a search radius (=searchR; default=20 
    arcsec)
    
    - objN is the object name. It is used to build the 
      directory in which to save the retrieved files.
    """
    baseURL = 'https://cassis.sirtf.com/'
    baseDir = os.getcwd()+'/'+objN.replace(" ", "")
    ws = '/atlas/cgi/radec.py?ra='+RA+'&dec='+DEC+'&radius='+searchR
    lines = request.urlopen(baseURL+ws).readlines()
    
    for line in lines:
        if 'SMART</i> FITS' in str(line):
            w = str(line).strip()
            try:
                wantF.append(w.split("'")[1])
            except:
                wantF = [w.split("'")[1]]
            del w
    
    try:
        l = len(wantF) # if no results were returned from CASSIS, the try
        #                statement will fail here and the code will skip
        #                to the except NameError line below.
        # Ensure that the object directory already exists (and make it
        # if it doesn't exist):
        subprocess.call('mkdir -p '+baseDir, shell=True)
        print(' ---------------------------------------------------------')
        print('| Info: ',l,'low resolution spectra retrieved from CASSIS:')
        print('| the Combined Atlas of Sources with Spitzer IRS Spectra.')
        print('|',baseURL)
        print('| ')
        print('| Saved file(s):')
        i = 1
        for wf in wantF:
            # download each fits file to the default local directory (=gotF[0]):
            gotF = request.urlretrieve(baseURL+wf)
            # retrieve original name of fits file:
            outFile = gotF[1]._headers[[h[0] for h in gotF[1]._headers].index('Content-disposition')][1].split('=')[1]
            # move the file from the default local directory to the object directory:
            subprocess.call('mv '+gotF[0]+' '+baseDir+'/'+outFile, shell=True)
            print('|',i,':',objN+'/'+outFile)
            i += 1
        print(' ---------------------------------------------------------')
        bibrefCASSIS(objN)
    except UnboundLocalError:
        print(' ----------------------------------------------------------')
        print('| Info: CASSIS query returned zero results                 ')
        print('| Possible reasons (provided by CASSIS):                   ')
        print('|   - The target/AORkey/program ID is not valid            ')
        print('|   - The target was not observed by Spitzer/IRS           ')
        print('|   - The target was not intentionally observed            ')
        print('|    (serendipitous sources are not yet included in CASSIS)')
        print('|   - The requested observation corresponds to a           ')
        print('|    high-resolution spectrum (only low-resolution spectra ')
        print('|    are available to date)                                ')
        print('|   - The requested observation corresponds to a spectral  ')
        print('|    map)                                                  ')
        print(' ----------------------------------------------------------')

def queryISO(objN, oRA, oDEC, searchR=str(20)):
    """
    Function to query Gregory C Sloan's SWS Atlas
    and retrieve calibrated ISO spectra.
    - oRA and oDEC (the object Right Ascension and Declination)
      must be provided in units of degrees (as strings)
    - searchR is the search radius used to consider an entry
      in the online database as a match (in arcsec).
    """
    baseDir = os.getcwd()+'/'+objN.replace(" ", "")
    baseURL = 'https://users.physics.unc.edu/~gcsloan/library/swsatlas/'
    ws = 'aot1.html'
    lines = request.urlopen(baseURL+ws).readlines()
    
    # search for instances of 'NOBR' which are nested around the coordinates
    found_match = 'False'
    i = 1
    for line in lines:
        if found_match == 'True':
            # download the sws fits file:
            if '_sws.fit' in str(line):
                if i == 1:
                    # ensure object directory exists:
                    subprocess.call('mkdir -p '+baseDir, shell=True)
                    print(' ---------------------------------------------------------')
                    print('| Info: ISO spectra retrieved from:')
                    print("| Gregory C Sloan's SWS Atlas.")
                    print('|',baseURL)
                    print('| ')
                    print('| Saved file(s):')
                
                gotF = request.urlretrieve(baseURL+str(line).split('"')[1])
                # Retrieve original name of file:
                outFile = str(line).split('"')[1]           
                # move the file from the default download location to the object directory:
                subprocess.call('mv '+gotF[0]+' '+baseDir+'/'+outFile, shell=True)
                print('|',i,':',objN+'/'+outFile)
                # return found_match to False:
                found_match = 'False'
                i += 1
        
        if '<NOBR>' in str(line):
            eRA = str(line).split('<NOBR>')[1].split('</NOBR>')[0] # entry Right Ascension
            eDEC = str(line).split('<NOBR>')[2].split('</NOBR>')[0] # entry Declination
            ePos = coord.SkyCoord(eRA+' '+eDEC, unit=(u.hourangle, u.deg))
            # Check whether these are within 'searchR' arcseconds of object RA and Dec:
            oPos = coord.SkyCoord(oRA+' '+oDEC, unit=(u.deg, u.deg))
            if ePos.separation(oPos).arcsecond <= float(searchR):
                # if they are, make found_match = 'True'
                found_match = 'True'
    
    if i == 1:
        print(' ----------------------------------------------------------')
        print('| Info: ISO SWS Atlas query returned zero results          ')
    else:
        bibrefISO(objN)
    print(' ---------------------------------------------------------')
        
    

def bibrefCASSIS(objN):
    with open(os.getcwd()+'/'+objN.replace(" ", "")+'/sedbuilder.bib', 'a') as outFile:
        outFile.write('Acknowledge CASSIS by (1) specifying the AORkey(s) of your data ')
        outFile.write('(provided in the header of each fits file) and the date this ')
        outFile.write('data was retrieved: '+str(date.today()))
        outFile.write(' and (2) cite the low resolution atlas using the following paper:\n\n')
        outFile.write('@ARTICLE{2011ApJS..196....8L,\n')
        outFile.write('   author = {{Lebouteiller}, V. and {Barry}, D.~J. and {Spoon}, ')
        outFile.write('H.~W.~W. and\n    {Bernard-Salas}, J. and {Sloan}, G.~C. and ')
        outFile.write('{Houck}, J.~R. and\n    {Weedman}, D.~W.},\n')
        outFile.write('   title = "{CASSIS: The Cornell Atlas of Spitzer/Infrared ')
        outFile.write('Spectrograph Sources}",\n')
        outFile.write('   journal = {\\apjs},\n')
        outFile.write('   keywords = {atlases, catalogs, infrared: general, methods: data ')
        outFile.write('analysis, techniques: spectroscopic, Astrophysics - Instrumentation')
        outFile.write(' and Methods for Astrophysics, Astrophysics - Cosmology and ')
        outFile.write('Nongalactic Astrophysics, Astrophysics - Astrophysics of Galaxies, ')
        outFile.write('Astrophysics - Solar and Stellar Astrophysics},\n')
        outFile.write('   year = 2011,\n')
        outFile.write('   month = sep,\n')
        outFile.write('   volume = {196},\n')
        outFile.write('   number = {1},\n')
        outFile.write('   eid = {8},\n')
        outFile.write('   pages = {8},\n')
        outFile.write('   doi = {10.1088/0067-0049/196/1/8},\n')
        outFile.write('   archivePrefix = {arXiv},\n')
        outFile.write('   eprint = {1108.3507},\n')
        outFile.write('   primaryClass = {astro-ph.IM},\n')
        outFile.write('   adsurl = {https://ui.adsabs.harvard.edu/abs/2011ApJS..196....8L},\n')
        outFile.write('   adsnote = {Provided by the SAO/NASA Astrophysics Data System}\n')
        outFile.write('}\n\n')
        outFile.write('The following footnote may also be used, where appropriate:\n')
        outFile.write(' The Combined Atlas of Sources with Spitzer IRS Spectra (CASSIS) is')
        outFile.write(' a product of the IRS instrument team, supported by NASA and JPL.')
        outFile.write(' CASSIS is supported by the "Programme National de Physique Stellaire"')
        outFile.write(' (PNPS) of CNRS/INSU co-funded by CEA and CNES and through the')
        outFile.write(' "Programme National Physique et Chimie du Milieu Interstellaire"')
        outFile.write(' (PCMI) of CNRS/INSU with INC/INP co-funded by CEA and CNES.\n\n')

def bibrefISO(objN):
    with open(os.getcwd()+'/'+objN.replace(" ", "")+'/sedbuilder.bib', 'a') as outFile:
        outFile.write('Acknowledge the ISO SWS spectral Atlas by citing the following')
        outFile.write(' paper:\n\n')
        outFile.write('@ARTICLE{2003ApJS..147..379S,\n')
        outFile.write('   author = {{Sloan}, G.~C. and {Kraemer}, Kathleen E. and {Price},')
        outFile.write(' Stephan D. and {Shipman}, Russell F.},\n')
        outFile.write('   title = "{A Uniform Database of 2.4-45.4 Micron Spectra from the')
        outFile.write(' Infrared Space Observatory Short Wavelength Spectrometer}",\n')
        outFile.write('   journal = {\\apjs},\n')
        outFile.write('   keywords = {Atlases, Infrared: General, Methods: Data Analysis, ')
        outFile.write('Techniques: Spectroscopic},\n')
        outFile.write('   year = 2003,\n')
        outFile.write('   month = aug,\n')
        outFile.write('   volume = {147},\n')
        outFile.write('   number = {2},\n')
        outFile.write('   pages = {379-401},\n')
        outFile.write('   doi = {10.1086/375443},\n')
        outFile.write('   adsurl = {https://ui.adsabs.harvard.edu/abs/2003ApJS..147..379S},\n')
        outFile.write('   adsnote = {Provided by the SAO/NASA Astrophysics Data System}\n')
        outFile.write('}\n\n')

