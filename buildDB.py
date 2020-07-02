import subprocess, sys, os
import urllib.request
from cat_setup import src_localDB, src_onlineDB

def check_ldb(ldb):
    """
    Function to test whether SEDBYS has been installed and
    set-up correctly. 
    """
    
    class cd:
        """
        Context manager for changing the current working directory
        """
        def __init__(self, newPath):
            self.newPath = os.path.expanduser(newPath)

        def __enter__(self):
            self.savedPath = os.getcwd()
            os.chdir(self.newPath)

        def __exit__(self, etype, value, traceback):
            os.chdir(self.savedPath)
    
    if ldb == '':
        localDB_trunk = os.getenv('SED_BUILDER')
        if localDB_trunk == None:
            print('Error: Local database directory trunk not specified!')
            print('Use option --ldb or set environment variable $SED_BUILDER')
            print('to specify full path to local database trunk.')
            print('')
            sys.exit()
    elif not os.path.isdir(ldb):
        print('Error: Local database directory trunk does not exist!')
        print('Please fix this before continuing.')
        print('')
        sys.exit()
    elif not os.path.isdir(ldb+'/database'):
        print('Error: Local database directory trunk does not point to')
        print(' SEDBYS git repository directory!')
        print('Please fix this beofre continuing.')
    else:
        localDB_trunk = ldb
    
    with cd(localDB_trunk):
        print('Ensuring local SEDBYS git repo is up-to-date...')
        uptodate = subprocess.call('git pull', shell=True)
        if uptodate == 1:
            print('')
            print('Error: local changes clash with repository updates!')
            print('Please rectify these before continuing.')
            print('')
            sys.exit()
        else:
            print('   Passed: check complete.')
    
    return localDB_trunk


def check_fmt(ref, nam, ldb, fluxU, fluxB):
    # 1. Is the bibref compatible with nasa ads?
    print('')
    print('Ensuring '+ref+' is a valid bibcode...')
    try:
        bibCheck = urllib.request.urlopen('https://ui.adsabs.harvard.edu/abs/'+ref)
        print('   Passed: check complete.')
    except urllib.error.HTTPError:
        print('')
        print('Error: reference bibcode not found on NASA ADS!')
        print('Please ensure the reference is a NASA ADS-compatible bibref.')
        print('')
        sys.exit()
    
    # 2. Will the catalog identifier be unique to the database?...
    print('')
    print('Ensuring '+nam+' is a unique and valid identifier...')
    catN = src_onlineDB('simbad')[0]
    ldbN = src_localDB(ldb)[0]
    if nam in catN.keys() or nam in ldbN.keys():
        print('')
        print('Error: catalog identifier '+nam+' already in use!')
        print('')
        sys.exit()
    elif not nam.isalnum():
        # ...and does it contain only letters and numbers?
        print('')
        print('Error: non alphanumeric characters in '+nam)
        print('')
        sys.exit()
    else:
        print('   Passed: check complete.')
    
    # 3. Are the flux or magnitude units recognised?
    print('')
    print('Ensuring the units are compatible with SEDBYS...')
    if not set(fluxU).issubset(['mag', 'mJy', 'Jy']):
        print('')
        print('Error: units not supported!')
        print("Must be one of 'mag', 'mJy', 'Jy'")
        print('')
        sys.exit()
    else:
        print('   Passed: check complete.')
    
    # 4. Check that, if the unit on a measurement is 'mag', the corresponding filter entry is
    # also in the zero_points.dat lookup table:
    print('')
    print('Ensuring filter names are present in look-up table...')
    filNames = []
    with open(ldb+'/zero_points.dat') as zpF:
        head1 = zpF.readline()
        head2 = zpF.readline()
        for line in zpF:
            filNames.append(line.split()[0].replace('"', ''))
    
    endhere = False
    for f in range(0, len(fluxU)):
        if fluxU[f] == 'mag' and fluxB[f] not in filNames:
            print('')
            print('Error: filter name '+fluxB[f]+' not found in zero_points.dat!')
            endhere = True
        elif fluxU[f] != 'mag' and fluxB[f] not in filNames:
            print('')
            print(fluxB[f]+' not found but flux conversion not necessary. Skipping...')
    
    if endhere == True:
        print('')
        print('Please add the zero points for the missing filters')
        print(' to zero_points.dat before continuing.')
        print('')
        sys.exit()
    else:
        print('   Passed: check complete.')



def addData(catM, catE, catB, catW, catA, catU, catR, opt, m, em, b1, u, b2, r, w):
    """
    m, em, b1, u, b2, r and w are the arrays of existing cataloged data.
    This routine adds data to those arrays.
    """
    m.append(catM)  # magnitude
    em.append(catE)   # magnitude error 
    w.append(catW)   # wavelength
    b2.append(catA)  # angular resolution / beam size
    u.append(catU)    # unit of measurement (e.g. Jy, mag etc)
    b1.append(catB)
    r.append(catR)

def addToLocal(outlist, localDB_trunk):
    """
    Takes current local database file and adds new entry.
    
    - outlist follows the order:
     [ldbN, ldbR, ldbW, ldbA, ldbM, ldbE, ldbU, ldbB]
    """
    oldcat = []
    with open(localDB_trunk+'/cat_setup.py', 'r') as inp:
        for line in inp:
            oldcat.append(line)

    w = 0
    with open(localDB_trunk+'/cat_setup_edit.py', 'w') as output:
        for o in oldcat:
            if '}' not in o:
                output.write(o)
            else:
                s = o.split("'")[0] # leading spaces
                try:
                    # add the new entry
                    output.write(o.replace('}', ',')+s+outlist[w]+'}\n')
                    w += 1
                except IndexError:
                    # notice that we're not where we're want to be
                    output.write(o)
    
    subprocess.call('mv '+localDB_trunk+'/cat_setup_edit.py '+localDB_trunk+'/cat_setup.py', shell=True)
    print('')
    print('cat_setup.py successfully updated.')
    print('')
    print('-------------------------------------------------------------------')
    print('Please add your changes to the SEDBYS git repository e.g.')
    print('')
    print(' > cd '+localDB_trunk)
    print(' > git pull')
    print(' > git add cat_setup.py')
    print(' > git add database')
    print(' > git commit -m "added data from '+outlist[1]+' to local database" ')
    print(' > git push')
    print('')
    print('You will be prompted for your git username to confirm your changes.')
    print('-------------------------------------------------------------------')
    print('')

def addToCat(outlist, localDB_trunk):
    """
    Function to add entries to the python dictionary in
    cat_setup.py which controls which catalogs on VizieR are
    queried and stores catalog metadata so that SEDBYS knows
    how to retrieve and flux-convert the data in the catalog.
    """
    oldcat = []
    with open(localDB_trunk+'/cat_setup.py', 'r') as inp:
        for line in inp:
            oldcat.append(line)
    
    w = 0
    o = 0
    with open(localDB_trunk+'/cat_setup_edit.py', 'w') as output:
        # account for the fact that src_onlineDB is not the first 
        # function defined in cat_setup.py
        while 'def src_onlineDB(' not in oldcat[o]:
            output.write(oldcat[o])
            o += 1
        
        for i in range(o, len(oldcat)):
            if '}' not in oldcat[i]:
                output.write(oldcat[i])
            else:
                s = oldcat[i].split("'")[0] # leading spaces
                try:
                    # add the new entry
                    output.write(oldcat[i].replace('}', ',')+s+outlist[w]+'}\n')
                    w += 1
                except IndexError:
                    # notice that we're not where we're want to be
                    output.write(oldcat[i])
    
    subprocess.call('mv '+localDB_trunk+'/cat_setup_edit.py '+localDB_trunk+'/cat_setup.py', shell=True)
    print('')
    print('cat_setup.py successfully updated.')
    print('Please add your changes to the SEDBYS git repository e.g.')
    print('')
    print(' > cd '+localDB_trunk)
    print(' > git pull')
    print(' > git add cat_setup.py')
    print(' > git add database')
    print(' > git add zero_points.dat')
    print(' > git commit -m "added '+outlist[0]+' to list of queried VizieR catalogs" ')
    print(' > git push')
    print('')
    print('You will be prompted for your git username to confirm your changes.')
    print('')

