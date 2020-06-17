import os, sys
from buildDB import addToLocal
import argparse
import subprocess

# Describe the script:
description = \
"""
description:
    Script to add file to local database. It is expected
    that the files in the local database are not able to
    be queried directly via VizieR.
"""
epilog = \
"""
examples:
    addLocal.py --nam=HERSCHEL1 --fil=database/herschel_phot.csv 
     --ref='2016A&A...586A...6P' --wav=70e-6,100e-6,160e-6 
     --res=5.033,7.190,11.504 --fna=F70,F100,F160
     --ena=eF70,eF100,eF160 --una=Jy,Jy,Jy 
     --bna=Herschel:PACS:F70,Herschel:PACS:F100,Herschel:PACS:F160
"""

parser = argparse.ArgumentParser(description=description,epilog=epilog,
         formatter_class=argparse.RawDescriptionHelpFormatter)
parser.add_argument("--nam",dest='nam',default='',type=str,
                    help='Label for the python dictionary.')
parser.add_argument("--fil",dest='fil',default='',type=str,
                    help='Path to the file being added to local database.')
parser.add_argument("--ref",dest='ref',default='',type=str,
                    help='Bibliographic reference for file.')
parser.add_argument("--wav",dest='wav',default='',type=str,
                    help='Wavelength or list of wavelengths (microns) in file.')
parser.add_argument("--res",dest='res',default='',type=str,
                    help='Angular resolution / beam size for each measurement.')
parser.add_argument("--fna",dest='Fna',default='',type=str,
                    help='Column name or list of column names for flux/magnitude.')
parser.add_argument("--ena",dest='Ena',default='',type=str,
                    help='Column name or list of column names for flux/mag error.')
parser.add_argument("--una",dest='Una',default='',type=str,
                    help='Unit or list of units for flux/mag.')
parser.add_argument("--bna",dest='Bna',default='',type=str,
                    help='Waveband name or list of waveband names.')
parser.add_argument("--ldb",dest='ldb',default='',type=str,
                    help='')

argopt = parser.parse_args()

if argopt.ldb == '':
    localDB_trunk = os.getenv('SED_BUILDER')
    if localDB_trunk == None:
        print('Error: Local database directory trunk not specified!')
        print('Use option --ldb or set environment variable $SED_BUILDER')
        print('to specify full path to local database trunk.')
        print('')
        sys.exit()
elif not os.path.isdir(argopt.ldb):
    print('Error: Local database directory trunk does not exist!')
    print('Please fix this before continuing.')
    print('')
    sys.exit()
else:
    localDB_trunk = argopt.ldb

print('')
print('---------------------------------------------')
print('| Running addLocal.py                       |')
print('|                                           |')
print('| If you use this script as part of your    |')
print('| research, please include                  |')
print('| Claire L. Davies (c.davies3@exeter.ac.uk) |')
print('| as a co-author.                           |')
print('|___________________________________________|')
print('')

# Does file exist?
if not os.path.exists(argopt.fil):
    # no it doesn't
    # Does it exist in the localDB?
    if not os.path.exists(localDB_trunk+'/'+argopt.fil):
        # no
        # raise error cos we can't find the file:
        print('Error: file not found')
        print('Exiting')
        sys.exit()
    else:
        # yes, and it is in the correct format to be written to the database
        print('File '+argopt.fil+' located in '+localDB_trunk)
        file = '/'+argopt.fil
else:
    # yes, it does 
    # is the local database directory in the file path?
    if localDB_trunk not in argopt.fil:
        # no
        # copy the file to the local DB:
        nfile = localDB_trunk+'/database/.'.replace('//','/')
        subprocess.call('cp '+argopt.fil+' '+nfile, shell=True)
        print('File '+argopt.fil+' located and copied to '+nfile)
        file = '/'+'/'.join(argopt.fil.split('/')[-2:])
    else:
        # yes but the local DB part of the file path needs removing
        file = argopt.fil.replace(localDB_trunk, '')

# Is the file in the right format?:
fc = []
with open(localDB_trunk+file) as inp:
    head = inp.readline()
    for line in inp:
        fc.append(line)
if head[:6] != 'Target':
    # First entry in column name has to be 'Target'
    print('')
    print('Error: File not in required format!')
    print('First column name not "Target"')
    sys.exit()
if any([', ' in f for f in [head]+fc]):
    # The columns have to be comma separated (no spaces)
    print('')
    print('Error: File not in required format!')
    print('Please remove spaces between column entries before continuing')

dID = "'"+argopt.nam+"' : "# label for the dict (make it end in ' : ')

oP = "localDB+'"+file+"'" # path to local file
oR = "'"+argopt.ref+"'"   # reference 
if '[' not in argopt.wav:
    oW = '['+argopt.wav+']' # wavelength or list of wavelengths
else:
    oW = argopt.wav
if '[' not in argopt.res:
    oA = '['+argopt.res+']' # ang res / beam size
else:
    oA = argopt.res

fluxN = [b.strip().replace('[', '').replace(']', '') for b in argopt.Fna.split(',')]
oM = "['"+"','".join(fluxN)+"']" # column name for flux/mag

fluxE = [b.strip().replace('[', '').replace(']', '') for b in argopt.Ena.split(',')]
oE = "['"+"','".join(fluxE)+"']" # column name for error on flux/mag

fluxU = [b.strip().replace('[', '').replace(']', '') for b in argopt.Una.split(',')]
oU = "['"+"','".join(fluxU)+"']" # units or list of units for flux/mag

fluxB = [b.strip().replace('[', '').replace(']', '') for b in argopt.Bna.split(',')]
oB = "['"+"','".join(fluxB)+"']" # waveband name to match with zeropoints table

outlist = [dID+oP, dID+oR, dID+oW, dID+oA, dID+oM, dID+oE, dID+oU, dID+oB]

addToLocal(outlist, localDB_trunk)

print('Something something complete!')
