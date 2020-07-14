import os, sys
from buildDB import addToLocal, check_ldb, check_fmt, check_date
import argparse
import subprocess
from astroquery.simbad import Simbad

import warnings

warnings.filterwarnings('ignore', category=UserWarning)


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
    python3 addLocal.py --nam=HERSCHEL1 --fil=database/herschel_phot.csv 
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
                    help='Wavelength or list of wavelengths (metres) in file.')
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

# 1. Has SEDBYS been correctly set up on the local machine?
localDB_trunk = check_ldb(argopt.ldb)

######
# Re-format the parsed values in preparation to build the python dictionary:
######
print('Locating file '+argopt.fil+'...')
if not os.path.exists(argopt.fil):
    # no it doesn't
    # Does it exist in the localDB?
    if not os.path.exists(localDB_trunk+'/'+argopt.fil):
        # no
        # raise error cos we can't find the file:
        print('')
        print('Error: file '+argopt.fil+'not found')
        print('')
        sys.exit()
    else:
        # yes, and it is in the correct format to be written to the database
        file = '/'+argopt.fil
else:
    # yes, it does 
    # is the local database directory in the file path?
    if localDB_trunk not in argopt.fil:
        # no
        # copy the file to the local DB:
        nfile = localDB_trunk+'/database/.'.replace('//','/')
        subprocess.call('cp '+argopt.fil+' '+nfile, shell=True)
        file = '/database/'+'/'.join(argopt.fil.split('/')[-1:])
    else:
        # yes but the local DB part of the file path needs removing
        file = argopt.fil.replace(localDB_trunk, '')

print('   Passed: check complete.')

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


######
# Formatting and database checks:
######

# 1. Is the file in the right format?...
print('')
print('Ensuring file contents are correctly formatted...')
endhere = False
fc = []
# a) read in the data:
with open(localDB_trunk+file) as inp:
    head = inp.readline()
    for line in inp:
        fc.append(line)

# b) First entry in column name has to be 'Target'
if head[:6] != 'Target':
    print('')
    print('Error: First column name not "Target"')
    endhere = True

# c) The columns have to be comma separated (no spaces)
if any([', ' in f for f in [head]+fc]):
    print('')
    print('Error: Please remove spaces between column entries!')
    print('Info: Column entries should be comma-separated.')
    endhere = True

# d) All lines should have the same number of entries as the header:
it1 = iter([h.split(',') for h in [head]+fc])
th_len = len(next(it1))
if not all(len(l) == th_len for l in it1):
    print('')
    print('Error: lines in file have different lengths!')
    endhere = True

# e) Each target name should be as-in SIMBAD (or as in SIMBAD plus a binary identifier):
for f in fc:
    objID = Simbad.query_objectids(f.split(',')[0])
    if not objID:
        print('')
        print('Warning: object name '+f.split(',')[0]+' not recognised by SIMBAD!')
        # Try treat it as photometry of binary component (expect e.g. A or A+B label)
        print(' - blindly assuming multiplicity: check '+' '.join(f.split(',')[0].split(' ')[:-1]))
        try:
            obj = [a[0] for a in Simbad.query_objectids(' '.join(f.split(',')[0].split(' ')[:-1]))]
            print(' - '+' '.join(f.split(',')[0].split(' ')[:-1])+' recognised by SIMBAD')
            if ' '.join(f.split(',')[0].split(' ')[:-1]) not in [' '.join(o.split()) for o in obj]:
                print(' but object name appears differently in SIMBAD!')
                for o in obj:
                    if ' '.join(f.split(',')[0].split(' ')[:-1]) in ' '.join(o.split()):
                        o1 = ' '.join(o.split())
                        print('Suggestion: use '+o1+' '+f.split(',')[0].split(' ')[-1]+' instead.')
                endhere = True
            else:
                print(' and we are fine to continue...')
        except TypeError:
            print('Error: not multiple. Object name not registered in SIMBAD!')
            endhere = True
    else:
        objIDs = [a[0] for a in Simbad.query_objectids(f.split(',')[0])]
        if f.split(',')[0] not in [' '.join(o.split()) for o in objIDs]:
            print('Error: object name '+f.split(',')[0]+' appears differently in SIMBAD!')
            for o in objIDs:
                if f.split(',')[0] in ' '.join(o.split()):
                    o1 = ' '.join(o.split())
                    print(' - Suggestion: use '+o1+' instead.')
            endhere = True

# f) Observation date column should exist:
if head.strip().split(',')[-1] != 'ObsDate':
    print('')
    print('Error: observation date column header ("ObsDate") not found in file!')
    print('Info: Expect this to be the final column header.')
    print('Suggestion: If observation date is unknown, use "unknown".')
    endhere = True

# g) Observation date should be in format YYYYMmmDD or be 'unknown' or 'averaged':
for f in fc:
    obsD = check_date(f.strip().split(',')[-1])
    if obsD == 'fail':
        if f.strip().split(',')[-1] not in ['unknown', 'averaged']:
            print('Error:'+f.strip().split(',')[-1]+' is in incorrect date format!')
            print('Info: required format is YYYYMmmDD')
            endhere = True

if endhere == True:
    print('Please fix the above errors before continuing')
    sys.exit()
else:
    print('   Passed: check complete.')


# 2. do the parsed column names for the flux (and its error) match the header?
endhere = False
print('')
print('Ensuring column names for measuremnts (and their errors) exist in file header...')
colnames = fluxN+fluxE
for i in range(0, len(colnames)):
    if colnames[i] not in head.split(','):
        print('')
        print('Error: column name '+colnames[i]+' not found in file header!')
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
addToLocal(outlist, localDB_trunk)
