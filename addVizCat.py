from buildDB import addToCat
from cat_setup import src_localDB, src_onlineDB
from astroquery.vizier import Vizier
import sys, os
import argparse
import urllib

# Describe the script:
description = \
"""
description:
    Script to add catalog to list of VizieR catalogs that are
    queried by the queryDB.py script. 
"""
epilog = \
"""
examples:
    addLocal.py --nam=TYCHO-2 --cat='I/259/tyc2' 
     --ref='2000A&A...355L..27H' --wav=426e-9,532e-9 
     --res=0.37,0.462 --fna=BTmag,VTmag --ena=e_BTmag,e_VTmag
     --una=mag,mag --bna=HIP:BT,HIP:VT
"""

parser = argparse.ArgumentParser(description=description,epilog=epilog,
         formatter_class=argparse.RawDescriptionHelpFormatter)
parser.add_argument("--nam",dest='nam',default='',type=str,
                    help='Label for the python dictionary.')
parser.add_argument("--cat",dest='cat',default='',type=str,
                    help='VizieR catalog code.')
parser.add_argument("--ref",dest='ref',default='',type=str,
                    help='Bibliographic reference for catalog.')
parser.add_argument("--wav",dest='wav',default='',type=str,
                    help='Wavelength or list of wavelengths (microns) in catalog.')
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

######
# pre-checks:
######
# 1. Has sedbys been correctly set up?
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

# 2. Does the catalog exist in VizieR?
attempt = Vizier.get_catalogs(argopt.cat)
if len(attempt.keys()) < 1:
    print('Error: VizieR catalog "'+argopt.cat+'" not found!')
    print('')
    sys.exit()

# 3. Is the bibref compatible with nasa ads?
try:
    bibCheck = urllib.urlopen('https://ui.adsabs.harvard.edu/abs/'+argopt.ref)
except urllib.error.HTTPError:
    print('Error: reference not found on NASA ADS!')
    print('Please ensure the reference is a NASA ADS-compatible bibref.')
    print('')
    sys.exit()

# 4. Is the catlog already in cat_setup.py?
catN = src_onlineDB('simbad')[0], src_onlineDB('simbad')[1]
ldbN = src_localDB(localDB_trunk)[0], src_localDB(localDB_trunk)[1]
if argopt.cat in [catN+ldbN]:
    print('Error: catalog '+argopt.cat+' already included!')
    print('')
    sys.exit()

# 5. Is the catalog identifier truly unique
if argopt.nam in catN.keys() or argopt.nam in ldbN.keys():
    print('Error: catalog identifier '+argopt.nam+' already in use!')
    print('')
    sys.exit()



######
# Build the python dictionary:
######
dID = "'"+argopt.nam+"' : " # unique catalog identifier for dict (make it end in ' : ')
oP = "'"+argopt.cat+"'"     # VizieR catalog reference code
oR = "'"+argopt.ref+"'"     # reference 
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

# Check that flux and flux error column names are as in the vizier catalog
colnames = fluxN+fluxE
res = Vizier(columns=['**', '+_r'], catalog=argopt.cat)
catalog = res.get_catalogs(argopt.cat)
endhere = False
for i in range(0, len(colnames)):
    if colnames[i] not in catalog[argopt.cat].keys():
        print('Error: column name '+colnames[i]+' not found in '+argopt.cat)
        endhere = True

if endhere == True:
    print('Available column names for '+argopt.cat+':')
    print(catalog[argopt.cat].keys())
    print()
    sys.exit()


fluxU = [b.strip().replace('[', '').replace(']', '') for b in argopt.Una.split(',')]
# Check that the flux or magnitude unit is recognised
if not set(fluxU).issubset(['mag', 'mJy', 'Jy']):
    print('Error: units not supported!')
    print("Must be one of 'mag', 'mJy', 'Jy'")
    print('')
    sys.exit()
oU = "['"+"','".join(fluxU)+"']" # units or list of units for flux/mag

fluxB = [b.strip().replace('[', '').replace(']', '') for b in argopt.Bna.split(',')]
# Check that, if the unit on a measurement is 'mag', the corresponding filter entry is
# also in the zero_points.dat lookup table:
filNames = []
with open(localDB_trunk+'/zero_points.dat') as zpF:
    head1 = zpF.readline()
    head2 = zpF.readline()
    for line in zpF:
        filNames.append(line.split()[0])

endhere = False
for f in range(0, len(fluxU)):
    if fluxU[f] == 'mag' and fluxB[f] not in filNames:
        print('Error: filter name '+fluxB[f]+' not found in zero_points.dat!')
        endhere = True

if endhere == True:
    print('')
    print('Please add the zero points for the missing filters')
    print(' to zero_points.dat before continuing.')
    print('')
    sys.exit()

oB = "['"+"','".join(fluxB)+"']" # waveband name to match with zeropoints table

######
# Final checks:
######
# 1. Are the lists of flux, error, units and resolution the same length?
lists = [oW.split(','), oA.split(','), oM.split(','), oE.split(','), oU.split(','), oB.split(',')]
it = iter(lists)
the_len = len(next(it))
if not all(len(l) == the_len for l in it):
    print('Error: not all entries have same length!')
    print('Please fix before continuing')
    print('')
    sys.exit()


######
# Finish:
######
# 1. make changes to cat_setup.py
outlist = [dID+oP, dID+oR, dID+oW, dID+oA, dID+oM, dID+oE, dID+oU, dID+oB]
addToCat(outlist, localDB_trunk)
