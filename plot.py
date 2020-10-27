from numpy import ndarray, where, array, zeros, ones, float64
import matplotlib.pyplot as plt
from sed_input import read_spectrum
import warnings
from pathlib import Path

warnings.filterwarnings('ignore', category=RuntimeWarning)

def fixaxis(data,err,lolims):
    """
    Convert x and y data (and associated measurement
    uncertainties) to logarithmic scale for plotting.
    
    """
    boundscale = 0.5
    data=array(data,dtype=float64)
    zeroinds=where(data <=0)[0]
    nonzeroinds=where(data > 0)[0]
    if err is None:
        #TODO:something smarter with the zeros?
        data[zeroinds]=boundscale*min(data[nonzeroinds])
        return data,None,lolims
    else:
        err=array(err)
        try:
            len(err)
        except:
            err=array([err])
        if len(err)==1: #single-symmetric errorbars
            newerr=ndarray((len(data),2))
            newerr.fill(err[0])
        elif len(err.shape) == 1: #vector symmetric errorbars
            newerr=ndarray((len(data),2))
            newerr[:,0]=err
            newerr[:,1]=err
        elif err.shape[0] == 2 : # vector asymmetric errorbars
            newerr=err.copy().T
        else:
            raise ValueError('Unrecognized form for error bars')
        
        lolims=array(lolims)
        try:
            len(lolims)
        except:
            lolims=array([lolims])
        if len(lolims)==1:
            lim=lolims[0]
            lolims=ndarray(len(data))
            lolims.fill(lim)
        assert len(lolims) == len(data), 'data and lower limits not same length'
        #first correct for data points that are zero by having them be upper limits
        data[zeroinds]=newerr[zeroinds,0]
        zeroerrs=zeros((len(zeroinds),2))
        zeroerrs[:,0]=data[zeroinds]*(boundscale)
        newerr[zeroinds]=zeroerrs
        lolims[zeroinds]=ones(len(zeroinds))
        #now replace errorbars that extend below zero with boundscale upper bounds
        negerrs=where(data-newerr[:,0] <= 0)[0]
        newerr[negerrs,0]=data[negerrs]*(boundscale)
        lolims[negerrs]=ones(len(negerrs))
        
        return data,newerr.T,lolims

def pltSED(infile, x_range, f, ef, wvlen, specFiles=None, specS=None, interactive=False):
    """
    Function to plot spectral energy distribution in log-log
    space.
    - specS is a vertical scaling to apply to the spectral
      flux information.
    """
    fig1 = plt.figure(1, figsize=(6., 4.))
    ax1 = plt.subplot2grid((1,1), (0,0))
    ax1.set_xlabel("${\lambda}$ [${\mu}m$]")
    ax1.set_ylabel("${\lambda}\,F_{\lambda}$ [W m$^{-2}$]")
    ax1.set_title(infile.name.split('_')[0])
    if x_range != 'default':
        ax1.set_xlim(float(x_range[0]), float(x_range[1]))
    if specFiles:
        for sF in range(0, len(specFiles)):
            wave_s, flux_s, eflux_s, colS = read_spectrum(Path(specFiles[sF]))
            x1,xerr1,xlolims1=fixaxis(wave_s,None,False)
            y1,yerr1,uplims1=fixaxis([fx*specS[sF] for fx in flux_s],[fx*specS[sF] for fx in eflux_s],False)
            ax1.errorbar(x1,y1,yerr1,xerr1,color=colS,ms=5,ls='-')

    
    ax1.loglog()
    yuplim = []
    for fl in range(0, len(f)):
        if float(f[fl]) == float(ef[fl]):
            yuplim.append(1)
        else:
            yuplim.append(0)
    
    x,xerr,xlolims=fixaxis([w*1e6 for w in wvlen],None,False)
    y,yerr,uplims=fixaxis(f,ef,yuplim) # convert flux and its error to log space
    if interactive == True:
        ax1.errorbar(x,y,yerr,xerr,uplims=uplims,xlolims=xlolims,color='k',marker='o',ms=5,
                     ls='none',picker=2)
        return fig1
    else:
        ax1.errorbar(x,y,yerr,xerr,uplims=uplims,xlolims=xlolims,color='k',marker='o',ms=5,
                     ls='none')
