import subprocess

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
    print('')

def addToCat(outlist, localDB_trunk):
    """
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
    print(' > git commit -m "added '+outlist[0]+' to list of queried VizieR catalogs" ')
    print(' > git push')
    print('')
    print('You will be prompted for your git username to confirm your changes.')
    print('')

