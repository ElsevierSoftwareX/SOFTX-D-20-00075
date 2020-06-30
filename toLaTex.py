#!/usr/bin/env python3

from citing import getBibTeX
import random
import string
from sed_input import read_ascii, read_cleaned, magToJy, JyToLamFlam
import argparse
import sys
import numpy as np

description = \
"""
description:
    Read in photometric data and output it in
    a LaTeX-ready tabulated format with 
    corresponding .bib file
    
"""
epilog = \
"""
examples:
    toLaTex.py --phot=AKSco/AKSco_phot.dat

"""

parser = argparse.ArgumentParser(description=description,epilog=epilog,
         formatter_class=argparse.RawDescriptionHelpFormatter)
parser.add_argument("--phot",dest="phot",default='',type=str,
                    help='Full path to photometry data file.')

argopt = parser.parse_args()

############
# 1. Read in the photometric data:
############
infile = argopt.phot
if infile.split('.')[-1] == 'dat':
    if 'cleaned' not in infile.split('/')[-1]:
        wvlen,wband,jy,ejy,flag,unit,beam,ref = read_ascii(infile)
    else:
        wvlen,wband,f,ef,flag,beam,ref = read_cleaned(infile)
        jy = None
else:
    print('')
    print('File name error: this function is limited to plotting ascii files output by queryDB.py.')
    print('')
    sys.exit()

############
# 2. Convert photometry data to W/m^2 (lamFlam): 
############
if jy:
    for i in range(0, len(jy)):
        if ejy[i] == '--':
            ejy[i] = np.nan
        else:
            ejy[i] = float(ejy[i])
    
        if unit[i] == 'mag':
            jy[i], ejy[i] = magToJy(jy[i],ejy[i], wband[i])
            unit[i] = 'Jy'
        elif unit[i] == 'mJy':
            jy[i] = jy[i]*1e-3
            ejy[i] = ejy[i]*1e-3
            unit[i] = 'Jy'
    
    f, ef = [], []
    for i in range(0, len(wvlen)):
        f.append(JyToLamFlam(jy[i],ejy[i],wvlen[i])[0])
        ef.append(JyToLamFlam(jy[i],ejy[i],wvlen[i])[1])

############
# 3. Collect bibref and write to file:
############
outFile = '/'.join(infile.split('/')[:-1])+'/sedbuilder.bib'
with open(outFile.replace('.bib', '.tex'), 'a') as o:
    o.write('Wavelength & $\\lambda F_{\\lambda}$ & Reference\n')
    o.write('$\\mu$m     & $10^{-13}$\,W\\,m$^{-2}$           &   \n')
    o.write('\\hline \n')

bibDict = {'bibtag' : 'authorYYYY'}
uniqueRef = list(set(ref))
for r in range(0, len(uniqueRef)):
    # generate random tag_suf for each reference to avoid any instances of same auth+year
    # combinations.
    tag_suf = random.choice(string.ascii_lowercase)+random.choice(string.ascii_lowercase)
    # download the bibtex entry and edit the bibtag:
    bibtag = getBibTeX(uniqueRef[r],tag_suf,outFile)
    bibDict[uniqueRef[r]] = bibtag

inds = np.array(wvlen).argsort()
sort_wv = np.array(wvlen)[inds]
sort_f  = np.array(f)[inds]
sort_ef = np.array(ef)[inds]
sort_ref = np.array(ref)[inds]

for r in range(0, len(sort_ref)):
    # output a table of wavelength, flux, reference to file:
    with open(outFile.replace('.bib', '.tex'), 'a') as o:
        wv = '{:.2f}'.format(sort_wv[r]*1e6)
        fr = '{:.3e}'.format(sort_f[r])
        if np.isnan(float(sort_ef[r])):
            f_exp = '{:.3e}'.format(float(sort_f[r])).split('e')[1]
            d = max(int(abs(-13-int(f_exp)))+1, 4)
            f_fmt = '{:0='+str(d)+'.'+str(d-1)+'f}e-13'
            ffr = f_fmt.format(float(sort_f[r])*1e13)
            o.write(wv+' & $'+ffr.split('e')[0]+'$ & \\citet{'+bibDict[sort_ref[r]]+'} \\\\ \n')
        else:
            # Get flux measurement and its error to same power of ten:
            ef_exp = '{:.3e}'.format(float(sort_ef[r])).split('e')[1]
            d = max(int(abs(-13-int(ef_exp)))+1, 4)
            ef_fmt = '{:0='+str(d)+'.'+str(d-1)+'f}e-13'
            efr = ef_fmt.format(float(sort_ef[r])*1e13)
            ffr = ef_fmt.format(float(sort_f[r])*1e13)
            if efr == ffr:
                # Catch instances where the value is an upper limit on the flux density.
                o.write(wv+' & $<'+ffr.split('e')[0]+'$ & \\citet{'+bibDict[sort_ref[r]]+'} \\\\ \n')
            else:
                o.write(wv+' & $'+ffr.split('e')[0]+'\\pm'+efr.split('e')[0]+'$ & \\citet{'+bibDict[sort_ref[r]]+'} \\\\ \n')

with open(outFile.replace('.bib', '.tex'), 'a') as o:
    o.write('\\hline \n\n\n')