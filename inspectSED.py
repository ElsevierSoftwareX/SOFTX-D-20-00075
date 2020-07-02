#!/usr/bin/env python3

import argparse
from sed_input import read_ascii, read_cleaned, read_spectrum, magToJy, JyToLamFlam
import sys, os
import matplotlib.pyplot as plt
from matplotlib.pyplot import errorbar, loglog
import numpy as np
from plot import pltSED

description = \
"""
description:
    Read in photometric and spectroscopic data and plot it
    so that spurious data points may be rejected
    from the final data file. 
    
"""
epilog = \
"""
examples:
    inspectPhot.py --phot=AKSco/AKSco_phot.dat
     --spec=AKSco/28902101_sws.fit,AKSco/cassis_yaaar_spcfw_12700160t.fits
     --pltR=0.1,1000

"""

parser = argparse.ArgumentParser(description=description,epilog=epilog,
         formatter_class=argparse.RawDescriptionHelpFormatter)
parser.add_argument("--phot",dest="phot",default='',type=str,
                    help='Full path to photometry data file.')
parser.add_argument("--spec",dest='spec',default='',type=str,
                    help='Full path to the Spitzer spectrum file.')
parser.add_argument("--scale",dest='specScale',default='',type=str,
                    help='Scale factor to be applied to spectral flux')
parser.add_argument("--pltR",dest='plt_range',default='[]',type=str,
                    help='X-range (in microns) for plot window (free by default)')
parser.add_argument("--savePlt",dest='saveplt',default=False,type=bool,
                    help='Save a .pdf copy of the full and cleaned SEDs (default False)')

argopt = parser.parse_args()

if argopt.specScale != '':
    if len(argopt.specScale.split(',')) != len(argopt.spec.split(',')):
        print('Error: options parsed to --spec and to --scale ')
        print('must have the same length!')
        sys.exit()

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

# If provided, read in the spectroscopic data:
if argopt.spec != '':
    specFiles = argopt.spec.split(',')
    if argopt.specScale != '':
        specS = [float(s) for s in argopt.specScale.split(',')]
    else:
        specS = [1]*len(specFiles)
else:
    specFiles = None
    specS = None

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
# 5. Plot SED:
############
if argopt.plt_range != '[]':
    try:
        x_range = argopt.plt_range.split(',')
    except:
        print('Error: format of plot limits not recognised')
        print('Defaults will be used instead')
        x_range = 'default'
else:
    x_range = 'default'

if argopt.saveplt == True:
    pltSED(infile, x_range, f, ef, wvlen, specFiles, specS, interactive=False)
    if infile[0] == '/':
        sedOutF = '/'+'/'.join(infile.split('/')[:-1])+'/'+infile.split('/')[-1].split('_')[0]+'_sed.pdf'
    else:
        sedOutF = '/'.join(infile.split('/')[:-1])+'/'+infile.split('/')[-1].split('_')[0]+'_sed.pdf'
    k = 0
    while os.path.exists(sedOutF.replace('sed.pdf', 'sed_'+str(k)+'.pdf')):
        k += 1 # avoids over-writing existing files
    plt.savefig(sedOutF.replace('sed.pdf', 'sed_'+str(k)+'.pdf'))
    
print('')
print('-----------------------------------------------')
print('| The plot displays your input SED data.      |')
print('|                                             |')
if argopt.saveplt == True:
    print('| A copy of this plot has been saved to       |')
    print('| '+sedOutF.replace('sed.pdf', 'sed_'+str(k)+'.pdf'))
    print('|                                             |')
print('| Please click on any photometry points you   |')
print('| wish to remove from the final data set.     |')
print('|                                             |')
print('| The x and y positions, together with the    |')
print('| waveband of each data point you click will  |')
print('| be printed to the terminal screen.          |')
print('|                                             |')
print('| When you are finished, please close the     |')
print('| plot window.                                |')
print('-----------------------------------------------')
fig = pltSED(infile, x_range, f, ef, wvlen, specFiles, specS, interactive=True)

indices = []

def on_pick(event):
    global indices
    artist = event.artist
    xmouse, ymouse = event.mouseevent.xdata, event.mouseevent.ydata
    x, y = artist.get_xdata(), artist.get_ydata()
    ind = event.ind
    indices.append(ind[0])
    print('')
    print('Detected mouse click at:')
    print('x=', x[ind[0]], 'm; y=', y[ind[0]], 'W/m^2')
    print('Corresponding to waveband:',wband[ind[0]])
    print('')

plt.connect('pick_event', on_pick)

plt.show()

############
# 5. Write retained photometric data to file:
############
if 'cleaned' not in infile.split('/')[-1] or indices != []:
    print('')
    print('Writing cleaned data to new file:')
    if 'cleaned' not in infile.split('/')[-1]:
        outfile = '.'.join(infile.split('.')[:-1])+'_cleaned_'
    else:
        outfile = '.'.join(infile.split('.')[:-1])[:-1]
    j = 0
    while os.path.exists(outfile+str(j)+'.dat'):
        j += 1 # avoids over-writing other attempts to clean data file

    print(outfile+str(j)+'.dat') # name of file to be written
    print('')
    with open(outfile+str(j)+'.dat','w') as f_out:
        with open(infile, 'r') as f_in:
            for line in f_in:
                try:
                    a = float(line[0])
                except ValueError:
                    f_out.write(line.replace('mag','lamFlam').replace('m -- -- --','m -- W/m^2 W/m^2'))
        for i in range(0, len(wvlen)):
            if i not in indices:
                f_out.write(' '.join([str(x) for x in [wvlen[i], # wavelength in m
                                                       wband[i], # waveband 
                                                       f[i],     # flux in W/m^2
                                                       ef[i],    # flux error in W/m^2
                                                       flag[i],  # flag on flux
                                                       beam[i],  # beam size (may be dummy value)
                                                       ref[i]]])+'\n') # reference for original data

############
# 6. Save cleaned version of SED plot to file
############
if argopt.saveplt == True and indices != []:
    # read in cleaned data:
    wvlen,wband,f,ef,flag,beam,ref = read_cleaned(outfile+str(j)+'.dat')
    
    pltSED(infile, x_range, f, ef, wvlen, specFiles, specS, interactive=False)
    h = 0
    while os.path.exists(sedOutF.replace('sed.pdf', 'sed_cleaned_'+str(h)+'.pdf')):
        h += 1 # avoids over-writing existing files
    plt.savefig(sedOutF.replace('sed.pdf', 'sed_cleaned_'+str(h)+'.pdf'))
    print('')
    print('Info: Plot of cleaned SED saved to '+sedOutF.replace('sed.pdf', 'sed_cleaned_'+str(h)+'.pdf'))
    print('')

