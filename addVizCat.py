from buildDB import addToCat, check_ldb, check_fmt
from cat_setup import src_localDB, src_onlineDB
from astroquery.vizier import Vizier
import sys, os
import argparse

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
    python3 addVizCat.py --nam=TYCHO2 --cat='I/259/tyc2' 
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
                    help='Wavelength or list of wavelengths (in metres) in catalog.')
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
# Re-format the parsed values in preparation to build the python dictionary:
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

fluxU = [b.strip().replace('[', '').replace(']', '') for b in argopt.Una.split(',')]
oU = "['"+"','".join(fluxU)+"']" # units or list of units for flux/mag

fluxB = [b.strip().replace('[', '').replace(']', '') for b in argopt.Bna.split(',')]
oB = "['"+"','".join(fluxB)+"']" # waveband name to match with zeropoints table


######
# Formatting and database checks:
######
# 1. Has SEDBYS been correctly set up on the local machine?
localDB_trunk = check_ldb(argopt.ldb)

# 2. Does the parsed catalog exist in VizieR?...
print('')
print('Ensuring '+argopt.cat+' exists in VizieR...')
res = Vizier(columns=['**', '+_r'], catalog=argopt.cat)
attempt = res.get_catalogs(argopt.cat)
if len(attempt.keys()) == 0:
    print('')
    print('Error: catalog not found!')
    print('')
    sys.exit()
else:
    print('   Passed: check complete.')

# ...is it definitely not already in cat_setup.py?...
print('')
print('Ensuring '+argopt.cat+' is not already in the list of queried catalogs...')
catN = src_onlineDB('simbad')[0], src_onlineDB('simbad')[1]
ldbN = src_localDB(localDB_trunk)[0], src_localDB(localDB_trunk)[1]
if argopt.cat in [catN+ldbN]:
    print('')
    print('Error: catalog '+argopt.cat+' already included in cat_setup.py!')
    print('')
    sys.exit()
else:
    print('   Passed: check complete.')

# ...and are the flux and flux error column names provided correct?
print('')
print('Ensuring column names for measuremnts (and their errors) are correct...')
colnames = fluxN+fluxE
endhere = False
for i in range(0, len(colnames)):
    if colnames[i] not in attempt[argopt.cat].keys():
        print('')
        print('Error: column name '+colnames[i]+' not found in '+argopt.cat)
        endhere = True

if endhere == True:
    print('')
    print('The available column names for '+argopt.cat+' are:')
    print(catalog[argopt.cat].keys())
    print()
    sys.exit()
else:
    print('   Passed: check complete.')

# 3. Various checks on the formatting of the arguments:
check_fmt(argopt.ref, argopt.nam, localDB_trunk, fluxU, fluxB)

# 4. Are the lists of flux, error, units and resolution the same length?
print('')
print('Ensuring parsed lists have same length...')
lists = [oW.split(','), oA.split(','), oM.split(','), oE.split(','), oU.split(','), oB.split(',')]
it = iter(lists)
the_len = len(next(it))
if not all(len(l) == the_len for l in it):
    print('Error: not all entries have same length!')
    print('Please fix before continuing')
    print('')
    sys.exit()
else:
    print('   Passed: check complete.')


######
# Finish:
######
# 1. make changes to cat_setup.py
outlist = [dID+oP, dID+oR, dID+oW, dID+oA, dID+oM, dID+oE, dID+oU, dID+oB]
addToCat(outlist, localDB_trunk)
