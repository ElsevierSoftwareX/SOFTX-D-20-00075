#!/usr/bin/env python3

from astroquery.simbad import Simbad
from astroquery.vizier import Vizier
from cat_setup import src_localDB, src_onlineDB
from buildDB import addData
import sys, os
import csv
from more_itertools import locate
import argparse
import subprocess

# for the spectrum search:
from astropy import units as u
import astropy.coordinates as coord
from getSpect import queryCASSIS, queryISO

# Describe the script:
description = \
"""
description:
    script to pull photometry from set catalogs in VizieR 
    (specified in cat_setup.py) and from local database of
    data tables not presently in VizieR.
"""
epilog = \
"""
examples:
    queryDB.py --obj=HD_283571 --rad=120s --ldb=./ --queryAll=True
"""

parser = argparse.ArgumentParser(description=description,epilog=epilog,
         formatter_class=argparse.RawDescriptionHelpFormatter)
parser.add_argument("--obj",dest="obj",default='',type=str,
                    help='Object name')
parser.add_argument("--rad",dest="rad",default='10s',type=str,
                    help='Search radius for VizieR catalog query')
parser.add_argument("--ldb",dest='ldb',default='',type=str,
                    help='')
parser.add_argument("--getSpect",dest="getSpect",default=False,type=bool,
                    help='Choose whether to query CASSIS for IRS spectra (default False)')
parser.add_argument("--closest",dest="closest",default=False,type=bool,
                    help='Retreive closest entry from VizieR catalogs (default False)')
parser.add_argument("--queryAll",dest="query",default='True',type=str,
                    help='Choose whether to query full database ("all") or specific catalog')

argopt = parser.parse_args()

obj     = argopt.obj.replace('_', ' ')
searchR = argopt.rad


# Check that the local database can be found:
localDB_trunk = check_ldb(argopt.ldb)

qu = argopt.query
# Read in the details of the VizieR catalogs to be queried: 
if qu == 'True':
    catN, catR, catW, catA, catM, catE, catU, catB = src_onlineDB('simbad')
else:
    # Expect to be given one catalog to query
    try:
        catN,catR,catW,catA,catM,catE,catU,catB = [{qu:item[qu]} for item in src_onlineDB('simbad')]
    except KeyError:
        print('No online catalog matching keyword ',qu)
        catN,catR,catW,catA,catM,catE,catU,catB = [[]]*8

# Read in the details of the local catalogs to be queried:
if qu == 'True':
    try:
        ldbN, ldbR, ldbW, ldbA, ldbM, ldbE, ldbU, ldbB = src_localDB(localDB_trunk)
    except TypeError:
        print('Error: local database files not found!')
        print('Please check local database directory trunk before continuing.')
        print('')
        sys.exit()
else:
    try:
        ldbN,ldbR,ldbW,ldbA,ldbM,ldbE,ldbU,ldbB = [{qu:item[qu]} for item in src_localDB(localDB_trunk)]
    except KeyError:
        print('No local catalog matching keyword ',qu)
        if catN == []:
            print('Exiting...')
            sys.exit()
        ldbN,ldbR,ldbW,ldbA,ldbM,ldbE,ldbU,ldbB = [[]]*8


print('')
print('---------------------------------------------')
print('| Running queryDB.py                        |')
print('|                                           |')
print('| If you use this script as part of your    |')
print('| research, please include                  |')
print('| Claire L. Davies (c.davies3@exeter.ac.uk) |')
print('| as a co-author.                           |')
print('|___________________________________________|')
print('')

##########
# Initialise outputs:
##########
wvlen, band, mag, emag, units = ['m'], ['--'], ['--'], ['--'], ['--']
beam, ref = ['arcsec'], ['--']

##########
# Collect SIMBAD names and VizieR catalog matches
##########

# Create custom SIMBAD (cS) query 
cS = Simbad() 
cS.add_votable_fields('flux(J)', 'flux(H)', 'flux(K)')
cS.add_votable_fields('flux_error(J)', 'flux_error(H)', 'flux_error(K)')
cS.add_votable_fields('flux_bibcode(J)', 'flux_bibcode(H)', 'flux_bibcode(K)')
cS.remove_votable_fields('coordinates')
objsim = cS.query_object(obj)
if not objsim:
    print('Error: object name not recognised by SIMBAD!')
    print('Please check spelling or try an alias.')
    print('')
    sys.exit

for o in catN:
    resM, resE = [], []
    found = ''
    print('Retrieving photometry from '+o+' ('+catR[o]+') ...')
    if o == '2MASS':
        for t in range(0, 3):
            if catR[o] in str(objsim[catN[o][t]][0]):
                addData(objsim[catM[o][t]][0], objsim[catE[o][t]][0], catB[o][t], 
                        catW[o][t], catA[o][t], catU[o][t], catR[o], opt=o, m=mag, 
                        em=emag, b1=band, u=units, b2=beam, r=ref, w=wvlen)
            else:
                print('No match')
    else:
        res = Vizier(columns=['**', '+_r'], catalog=catN[o])
        result = res.query_region(obj, radius=searchR)
        try:
            l_tmp = result[catN[o]]
        except TypeError:
            found = 'No match'
        if result.keys() and found != 'No match':
            if len(result[catN[o]]) > 1 and argopt.closest == False:
                # Get the user to specify the matching catalog entry for the object:
                print('Multiple results returned by Vizier within search radius')
                print(result[catN[o]])
                print('')
                obj_r = input('Enter "_r" value for required target:  ')
                # Retrieve row number:
                for r in range(0, len(result[catN[o]])):
                    if (result[catN[o]][r]['_r'] == float(obj_r)):
                        row = r
            elif len(result[catN[o]]) > 1 and argopt.closest == True:
                # Retrieve the entry with smallest _r
                print('Multiple results returned by Vizier within search radius')
                print(result[catN[o]])
                print('')
                q_r = min([r['_r'] for r in result[catN[o]]])
                # Retrieve row number:
                print('Closest entry has _r =',q_r)
                for r in range(0, len(result[catN[o]])):
                    if result[catN[o]][r]['_r'] == q_r:
                        row = r
            else:
                row = 0
            # Retrieve mag/flux and its error from the catalog, given the row number
            #for mm in catM[o]:
            for m in range(0, len(catM[o])):
                # Retrieve each of the mag/flux measurements...
                try:
                    if '--' not in str(result[catN[o]][row][catM[o][m]]):
                        resM = result[catN[o]][row][catM[o][m]]
                    else:
                        resM = '--'
                except KeyError:
                    print('Warning: potential flux column name change in VizieR!')
                    print(result[catN[o]][row])
                    print (catM[o][m])
                    raise KeyError
                
                # ... and their errors...
                if o == 'IRAS':
                    t_resM = result[catN[o]][row][catE[o][m]]
                    resE = result[catN[o]][row][catM[o][m]]*0.01*t_resM
                elif isinstance(catE[o][m], str):
                    if '--' not in str(result[catN[o]][row][catE[o][m]]):
                        resE = result[catN[o]][row][catE[o][m]]
                    else:
                        resE = '--'
                else:
                    resE = catE[o][m] * result[catN[o]][row][catM[o][m]]
                
                # And add it to the data to be written to file:
                addData(resM, resE, catB[o][m], catW[o][m], catA[o][m], catU[o][m],
                        catR[o], opt='vizier', m=mag, em=emag, b1=band, u=units, 
                        b2=beam, r=ref, w=wvlen)
        else:
            print('No match.')

##########
# Account for specific case of Vieira+2003 which provides mag + colour table
# and object ID in PDS format:
##########

altIDs = [a[0] for a in Simbad.query_objectids(obj)]
if qu == 'True':
    cmN = {'Vieira03' : 'J/AJ/126/2971/table2'}
    cmR = {'Vieira03' : '2003AJ....126.2971V'}
    cmW = {'Vieira03' : [540e-9, 442e-9, 364e-9, 647e-9, 786.5e-9]}
    cmA = {'Vieira03' : [(1.22*w/0.60)*206265 for w in cmW['Vieira03']]}
    cmM = {'Vieira03' : ['Vmag', 'B-V', 'U-B', 'V-Rc', 'Rc-Ic']}
    cmE = {'Vieira03' : ['--', '--', '--', '--', '--']}
    cmU = {'Vieira03' : ['mag', 'mag', 'mag', 'mag', 'mag']}
    cmB = {'Vieira03' : ['Johnson:V', 'Johnson:B', 'Johnson:U', 'Cousins:Rc', 'Cousins:Ic']}

    
    print('Retrieving photometry from Vieira et al. ('+cmR['Vieira03']+') ...')
    if any('PDS' in b for b in altIDs):
        indices = [i for i, s in enumerate(altIDs) if 'PDS' in s]
        p_obj = altIDs[indices[0]]
        # Ensure pds_obj is just numeric and has leading zeros so that len = 3
        if len(p_obj.split()[1]) == 1:
            pds_obj = '00'+p_obj.split()[1]
        elif len(p_obj.split()[1]) == 2:
            pds_obj = '0'+p_obj.split()[1]
        elif len(p_obj.split()[1]) == 3:
            pds_obj = p_obj.split()[1]
        else:
            print('Format of PDS identifier not recognised: '+p_obj)
            print('Exiting...')
            sys.exit()
    
        result = Vizier.get_catalogs(cmN['Vieira03'])
        ind = [i for i, s in enumerate([a for a in result[0]['PDS']]) if pds_obj in s]
        if len(ind) > 1:
            jvmag = result[0]['Vmag'][ind]
            jbmag = result[0]['B-V'][ind] + jvmag
            jumag = result[0]['U-B'][ind] + jbmag
            crmag = jvmag - result[0]['V-Rc'][ind]
            cimag = crmag - result[0]['Rc-Ic'][ind]
            vieira_m = [jvmag, jbmag, jumag, crmag, cimag]
            for m in range(0, len(vieira_m)):
                addData(vieira_m[m], cmE['Vieira03'][m], cmB['Vieira03'][m], cmW['Vieira03'][m],
                        cmA['Vieira03'][m], cmU['Vieira03'][m], cmR['Vieira03'], opt='V03', 
                        m=mag, em=emag, b1=band, u=units, b2=beam, r=ref, w=wvlen)
        else:
            print('No match.')
    else:
        print('No match.')


##########
# Then deal with local data base of tables not on VizieR:
##########

for o in ldbN:
    print('Retrieving photometry from '+o+' ('+ldbR[o]+') ...')
    with open(ldbN[o]) as f_in:
        reader = csv.DictReader(f_in, delimiter=',')
        entries = [a for a in reader]
    
    targs = [row['Target'] for row in entries]
    match = list(set(targs).intersection([a.replace('  ', ' ') for a in altIDs]))
    if len(match) == 0:
        print('No match.')
    else:
        for ind in list(locate(targs, lambda a: a == match[0])):
            resM = []
            resE = []
            for mm in ldbM[o]:
                # Retrieve each of the mag/flux measurements...
                resM.append(entries[ind][mm])
            for me in ldbE[o]:
                # ... and their errors
                resE.append(entries[targs.index(match[0])][me])
            for m in range(0, len(resM)):
                addData(resM[m], resE[m], ldbB[o][m], ldbW[o][m], ldbA[o][m], ldbU[o][m],
                        ldbR[o], opt='vizier', m=mag, em=emag, b1=band, u=units, 
                        b2=beam, r=ref, w=wvlen)

##############
# Write output to ascii file:
##############
subprocess.call('mkdir -p '+os.getcwd()+'/'+obj.replace(" ", ""), shell = True)
output = os.getcwd()+'/'+obj.replace(" ", "")+'/'+obj.replace(" ", "")+'_phot.dat'
if os.path.exists(output) == True and qu == 'True':
    print('File '+output.split('/')[-1]+' already exists in '+os.getcwd()+'/'+obj.replace(" ", "")+ '...')
    print('Exiting...')
    sys.exit()
elif os.path.exists(output) == True and qu != 'True':
    f = open(output, mode='a')
    f.write('#New photometry obtained using search radius of '+searchR+'\n')
    for i in range(1, len(wvlen)):
        oLINE = str(wvlen[i])+' '+str(band[i])+' '+str(mag[i])+' '+str(emag[i])+' -- '+str(units[i])+' '+str(beam[i])+' '+str(ref[i])
        f.write(oLINE+"\n")

else:
    f = open(output, mode='w')
    f.write('#Photometry obtained for '+obj+' using search radius of '+searchR+'\n')
    f.write("lam band mag e_mag f_mag u_mag beam ref\n")
    for i in range(0, len(wvlen)):
        oLINE = str(wvlen[i])+' '+str(band[i])+' '+str(mag[i])+' '+str(emag[i])+' -- '+str(units[i])+' '+str(beam[i])+' '+str(ref[i])
        f.write(oLINE+"\n")

f.close()

if argopt.getSpect == True:
    # objRA = str(65.48922), objDEC = str(28.443204)
    resS = Simbad.query_object(obj)
    objPos = coord.SkyCoord(resS['RA'][0]+' '+resS['DEC'][0], unit=(u.hourangle, u.deg))
    RA = objPos.ra.value
    DEC = objPos.dec.value
    queryCASSIS(obj, str(RA), str(DEC), searchR=str(20))
    queryISO(obj, str(RA), str(DEC), searchR=str(20))

print('...done')
print('')





