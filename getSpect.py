from urllib import request
import subprocess
import os
from datetime import date
import astropy.coordinates as coord
from astropy import units as u
from citing import bibrefCASSIS, bibrefISO

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
