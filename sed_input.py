import os
from math import log
import numpy as np
from astropy.io import fits as pyfits

def read_ascii(file):
    wvlen, band, mag, emag, fmag, unit, beam, ref = [], [], [], [], [], [], [], []
    with open(file, 'r') as f_in:
        for line in f_in:
            try:
                # ensure line contains data:
                a = float(line[0])
            except ValueError:
                a = 'dummy'
            try:
                # ensure mag or flux entry is not '--'
                m = float(line.split(' ')[2])
            except ValueError:
                m = 'dummy'
            
            if isinstance(a, float) and isinstance(m, float):
                wvlen.append(float(line.strip().split(' ')[0])) # in metres
                band.append(line.strip().split(' ')[1])
                mag.append(float(line.strip().split(' ')[2]))
                emag.append(line.strip().split(' ')[3])
                fmag.append(line.strip().split(' ')[4])
                unit.append(line.strip().split(' ')[5])
                beam.append(line.strip().split(' ')[6])
                ref.append(line.strip().split(' ')[7])
    
    return wvlen, band, mag, emag, fmag, unit, beam, ref

def read_cleaned(file):
    wvlen, band, lamFlam, elamFlam, flamFlam, beam, ref = [], [], [], [], [], [], []
    with open(file, 'r') as f_in:
        for line in f_in:
            try:
                # ensure line contains data:
                a = float(line[0])
            except ValueError:
                a = 'dummy'
            try:
                # ensure mag or flux entry is not '--'
                m = float(line.split(' ')[2])
            except ValueError:
                m = 'dummy'
            
            if isinstance(a, float) and isinstance(m, float):
                wvlen.append(float(line.strip().split(' ')[0])) # in metres
                band.append(line.strip().split(' ')[1])
                lamFlam.append(float(line.strip().split(' ')[2]))
                elamFlam.append(line.strip().split(' ')[3])
                flamFlam.append(line.strip().split(' ')[4])
                beam.append(line.strip().split(' ')[5])
                ref.append(line.strip().split(' ')[6])
    
    return wvlen, band, lamFlam, elamFlam, flamFlam, beam, ref
    

def read_zp(file):
    with open(file) as f_in:
        head = f_in.readline()
        units = f_in.readline()
        for line in f_in:
            try:
                zpWave[line.split(' ')[0].replace('"', '')] = float(line.split(' ')[1])
                zpF0[line.split(' ')[0].replace('"', '')] = float(line.split(' ')[2])
                
            except NameError:
                zpWave = {line.split(' ')[0].replace('"', '') : float(line.split(' ')[1])}
                zpF0   = {line.split(' ')[0].replace('"', '') : float(line.split(' ')[2])}
    
    return zpWave, zpF0

def magToJy(mag, emag, wband, zpFile=os.environ['SED_BUILDER']+'/zero_points.dat'):
    zpWave, zpF0 = read_zp(zpFile)
    F0 = zpF0[wband]
    jy = (10**(-float(mag)/2.5))*F0
    if emag != '--':
        ejy = (float(emag)/2.5)*jy*log(10)
    else:
        ejy = np.nan
    
    return jy, ejy

def JyToLamFlam(jy,ejy,wave):
    # this assumes wave is provided in metres
    c_light = 299792458.0 # m/s
    
    lamFlam = jy*1e-26*c_light*(1/wave)
    elamFlam = ejy*1e-26*c_light*(1/wave)
    return lamFlam, elamFlam



def read_spectrum(specfile):
    """
    Function for reading wavelength, flux and its error
    from files returned from CASSIS Spitzer Atlas or the 
    ISO SWS spectral Atlas.     
    - Data in column 1 is wavelength;
    - Data in column 2 is flux;
    - Data in column 3 is the error on the flux 
     (rms plus systematic for CASSIS)
    - Data in column 4 is the error on the flux
     (statistical and normalisation for ISO)
    """
    hdu = pyfits.open(specfile)
    w = [a[0] for a in hdu[0].data]
    f     = [a[1] for a in hdu[0].data]
    if 'cassis' in specfile:
        ef    = [a[2] for a in hdu[0].data]
        colS = 'b'
    elif 'sws' in specfile:
        ef    = [a[3] for a in hdu[0].data]
        colS = 'g'
    
    f2, ef2 = [], []
    for i in range(0, len(f)):
        f2.append(JyToLamFlam(f[i],ef[i],w[i]*1e-6)[0])
        ef2.append(JyToLamFlam(f[i],ef[i],w[i]*1e-6)[1])
    
    wvlen = [a[0] for a in sorted(zip(w,f2))]
    flux  = [a[1] for a in sorted(zip(w,f2))]
    eflux = [a[1] for a in sorted(zip(w,ef2))]
    
    return wvlen,flux,eflux,colS
    