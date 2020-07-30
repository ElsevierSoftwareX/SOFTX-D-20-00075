import urllib.request
import string
import os, sys
from datetime import date

def getBibTeX(bibref,tag_suf,outFile):
    """
    Function to retrieve BibTex entry from NASA ADS,
    given a bibref. The tag is amended so that it follows
    author last name + year + 'tag_suf'. 
    """
    if bibref == '1988iras....1.....B':
        bibtex = ['>@article{1988iras....1.....B,\n',
                  '       title={Infrared astronomical satellite (IRAS) catalogs and atlases. Volume 1: Explanatory supplement},\n',
                  '       keywords = {All Sky Photography, Catalogs, Indexes (Documentation), Infrared Astronomy Satellite, Cosmology, Galaxies, Star Formation, Stellar Evolution, Astrophysics},\n',
                  '       author={Beichman, CA and Neugebauer, G and Habing, HJ and Clegg, PE and Chester, Thomas J},\n',
                  '       year=1988,\n',
                  '       volume = {1},\n', 
                  '       month = jan,\n', 
                  '       adsurl = {https://ui.adsabs.harvard.edu/abs/1988iras....1.....B},\n'
                  '}\n']
    else:
        baseURL = 'https://ui.adsabs.harvard.edu/abs/'
        suf = '/exportcitation'
        lines = urllib.request.urlopen(baseURL+bibref+suf).readlines()
        lines = [l.decode('utf-8') for l in lines] # remove additional webpage encoding
    
        bibtex = []
        for l in range(0, len(lines)):
            if 'export-textarea ' in str(lines[l]):
                bibtex.append(str(lines[l]))
                t = l+1
    
        while '</textarea>' not in str(lines[t+1]):
            bibtex.append(str(lines[t])) 
            t += 1
    
    for item in bibtex:
        if 'author' in item.split('=')[0]:
            auth = item.split('=')[1].split(',')[0]
            for i in string.punctuation:
                auth = auth.replace(i, '')
                auth = auth.replace(' ', '')
        if 'year' in item.split('=')[0]:
            yr = item.split('=')[1].split(',')[0]
            yr = yr.replace(' ', '')
    
    try:
        bibtex[0] = bibtex[0].split('>')[1].split('{')[0]+'{'+auth+yr+tag_suf+',\n'
    except UnboundLocalError as ule:
        print(bibtex)
        print('')
        print(ule)
        sys.exit()
    
    with open(outFile, 'a') as o:
        for item in bibtex:
            item = item.replace('&#34;', '"')
            item = item.replace('&#39;', "'")
            item = item.replace('&amp;', "&")
            o.write(item)
        o.write('\n')
    
    return auth+yr+tag_suf


def bibrefCASSIS(objN):
    with open(os.getcwd()+'/'+objN.replace(" ", "")+'/sedbuilder.tex', 'a') as outFile:
        outFile.write('Acknowledge CASSIS by (1) specifying the AORkey(s) of your data ')
        outFile.write('(provided in the header of each fits file) and the date this ')
        outFile.write('data was retrieved: '+str(date.today()))
        outFile.write(' and (2) cite the low resolution atlas: \\citet{Lebouteiller2011zp}\n\n')
        outFile.write('The following footnote may also be used, where appropriate:\n')
        outFile.write(' The Combined Atlas of Sources with Spitzer IRS Spectra (CASSIS) is')
        outFile.write(' a product of the IRS instrument team, supported by NASA and JPL.')
        outFile.write(' CASSIS is supported by the "Programme National de Physique Stellaire"')
        outFile.write(' (PNPS) of CNRS/INSU co-funded by CEA and CNES and through the')
        outFile.write(' "Programme National Physique et Chimie du Milieu Interstellaire"')
        outFile.write(' (PCMI) of CNRS/INSU with INC/INP co-funded by CEA and CNES.\n\n')
    with open(os.getcwd()+'/'+objN.replace(" ", "")+'/sedbuilder.bib', 'a') as outFile:
        outFile.write('@ARTICLE{Lebouteiller2011zp,\n')
        outFile.write('   author = {{Lebouteiller}, V. and {Barry}, D.~J. and {Spoon}, ')
        outFile.write('H.~W.~W. and\n    {Bernard-Salas}, J. and {Sloan}, G.~C. and ')
        outFile.write('{Houck}, J.~R. and\n    {Weedman}, D.~W.},\n')
        outFile.write('   title = "{CASSIS: The Cornell Atlas of Spitzer/Infrared ')
        outFile.write('Spectrograph Sources}",\n')
        outFile.write('   journal = {\\apjs},\n')
        outFile.write('   keywords = {atlases, catalogs, infrared: general, methods: data ')
        outFile.write('analysis, techniques: spectroscopic, Astrophysics - Instrumentation')
        outFile.write(' and Methods for Astrophysics, Astrophysics - Cosmology and ')
        outFile.write('Nongalactic Astrophysics, Astrophysics - Astrophysics of Galaxies, ')
        outFile.write('Astrophysics - Solar and Stellar Astrophysics},\n')
        outFile.write('   year = 2011,\n')
        outFile.write('   month = sep,\n')
        outFile.write('   volume = {196},\n')
        outFile.write('   number = {1},\n')
        outFile.write('   eid = {8},\n')
        outFile.write('   pages = {8},\n')
        outFile.write('   doi = {10.1088/0067-0049/196/1/8},\n')
        outFile.write('   archivePrefix = {arXiv},\n')
        outFile.write('   eprint = {1108.3507},\n')
        outFile.write('   primaryClass = {astro-ph.IM},\n')
        outFile.write('   adsurl = {https://ui.adsabs.harvard.edu/abs/2011ApJS..196....8L},\n')
        outFile.write('   adsnote = {Provided by the SAO/NASA Astrophysics Data System}\n')
        outFile.write('}\n\n')

def bibrefISO(objN):
    with open(os.getcwd()+'/'+objN.replace(" ", "")+'/sedbuilder.tex', 'a') as outFile:
        outFile.write('Acknowledge the ISO SWS spectral Atlas by citing \citet{Sloan2003tj}.\n\n')
    with open(os.getcwd()+'/'+objN.replace(" ", "")+'/sedbuilder.bib', 'a') as outFile:
        outFile.write('@ARTICLE{Sloan2003tj,\n')
        outFile.write('   author = {{Sloan}, G.~C. and {Kraemer}, Kathleen E. and {Price},')
        outFile.write(' Stephan D. and {Shipman}, Russell F.},\n')
        outFile.write('   title = "{A Uniform Database of 2.4-45.4 Micron Spectra from the')
        outFile.write(' Infrared Space Observatory Short Wavelength Spectrometer}",\n')
        outFile.write('   journal = {\\apjs},\n')
        outFile.write('   keywords = {Atlases, Infrared: General, Methods: Data Analysis, ')
        outFile.write('Techniques: Spectroscopic},\n')
        outFile.write('   year = 2003,\n')
        outFile.write('   month = aug,\n')
        outFile.write('   volume = {147},\n')
        outFile.write('   number = {2},\n')
        outFile.write('   pages = {379-401},\n')
        outFile.write('   doi = {10.1086/375443},\n')
        outFile.write('   adsurl = {https://ui.adsabs.harvard.edu/abs/2003ApJS..147..379S},\n')
        outFile.write('   adsnote = {Provided by the SAO/NASA Astrophysics Data System}\n')
        outFile.write('}\n\n')

