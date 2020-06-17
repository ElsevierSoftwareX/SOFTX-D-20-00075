from numpy import ndarray, where, array, zeros, ones, float64

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
