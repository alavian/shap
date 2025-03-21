import shap
from ..common import convert_name
import matplotlib.pyplot as pl
from mpl_toolkits.mplot3d import Axes3D  
import numpy as np


def compute_bounds(xmin, xmax, xv):
    """ Handles any setting of xmax and xmin.
    
    Note that we handle None, float, or "percentile(float)" formats.
    """
    
    if xmin is not None or xmax is not None:
        if type(xmin) == str and xmin.startswith("percentile"):
            xmin = np.nanpercentile(xv, float(xmin[11:-1]))
        if type(xmax) == str and xmax.startswith("percentile"):
            xmax = np.nanpercentile(xv, float(xmax[11:-1]))

        if xmin is None or xmin == np.nanmin(xv):
            xmin = np.nanmin(xv) - (xmax - np.nanmin(xv))/20
        if xmax is None or xmax == np.nanmax(xv):
            xmax = np.nanmax(xv) + (np.nanmax(xv) - xmin)/20
            
    return (xmin, xmax)

def partial_dependence_plot(ind, model, features, xmin="percentile(0)", xmax="percentile(100)",
                            npoints=None, nsamples=100, feature_names=None, hist=True,
                            ylabel=None, ice=False, opacity=None, linewidth=None, show=True):
    
    # convert from DataFrames if we got any
    if str(type(features)).endswith("'pandas.core.frame.DataFrame'>"):
        if feature_names is None:
            feature_names = features.columns
        features = features.values
        
    if feature_names is None:
        feature_names = ["Feature %d" % i for i in range(features.shape[1])]
    
    # this is for a 1D partial dependence plot
    if type(ind) is not tuple:
        ind = convert_name(ind, None, feature_names)
        xv = features[:,ind]
        xmin, xmax = compute_bounds(xmin, xmax, xv)
        npoints = 100 if npoints is None else npoints
        xs = np.linspace(xmin, xmax, npoints)
        
        features_tmp = features.copy()
        if not ice:
            vals = np.zeros(npoints)
            for i in range(npoints):
                features_tmp[:,ind] = xs[i]
                vals[i] = model(features_tmp).mean()
            if linewidth is None:
                linewidth = 2
            if opacity is None:
                opacity = 1
        else:
            vals = np.zeros((npoints, features.shape[0]))
            for i in range(npoints):
                features_tmp[:,ind] = xs[i]
                vals[i,:] = model(features_tmp)
            if linewidth is None:
                linewidth = 1
            if opacity is None:
                opacity = 0.5
        

        
            
        # the histogram of the data
        fig, ax1 = pl.subplots()

        ax1.plot(xs, vals, color=shap.plots.colors.blue_rgb, linewidth=linewidth, alpha=opacity)

        ax2 = ax1.twinx()

        if hist:
            n, bins, patches = ax2.hist(xv, 50, density=False, facecolor='black', range=(xmin, xmax))

        ax2.set_ylim(0,features.shape[0])#ax2.get_ylim()[0], ax2.get_ylim()[1] * 4)
        ax1.set_xlabel(feature_names[ind], fontsize=13)
        if ylabel is None:
            if not ice:
                ylabel = "E[f(x) | "+ str(feature_names[ind]) + "]"
            else:
                ylabel = "f(x) | "+X_trainb.columns[find]
        ax1.set_ylabel(ylabel, fontsize=13)
        ax1.xaxis.set_ticks_position('bottom')
        ax1.yaxis.set_ticks_position('left')
        ax1.spines['right'].set_visible(False)
        ax1.spines['top'].set_visible(False)
        ax1.tick_params(labelsize=11)

        ax2.xaxis.set_ticks_position('bottom')
        ax2.yaxis.set_ticks_position('left')
        ax2.yaxis.set_ticks([])
        ax2.spines['right'].set_visible(False)
        ax2.spines['top'].set_visible(False)
        if show:
            pl.show()
        else:
            return fig,ax1
        
        
    # this is for a 2D partial dependence plot
    else:
        ind0 = convert_name(ind[0], None, feature_names)
        ind1 = convert_name(ind[1], None, feature_names)
        xv0 = features[:,ind0]
        xv1 = features[:,ind1]
        
        xmin0 = xmin[0] if type(xmin) is tuple else xmin
        xmin1 = xmin[1] if type(xmin) is tuple else xmin
        xmax0 = xmax[0] if type(xmax) is tuple else xmax
        xmax1 = xmax[1] if type(xmax) is tuple else xmax
        
        xmin0, xmax0 = compute_bounds(xmin0, xmax0, xv0)
        xmin1, xmax1 = compute_bounds(xmin1, xmax1, xv1)
        npoints = 20 if npoints is None else npoints
        xs0 = np.linspace(xmin0, xmax0, npoints)
        xs1 = np.linspace(xmin1, xmax1, npoints)
        
        features_tmp = features.copy()
        x0 = np.zeros((npoints, npoints))
        x1 = np.zeros((npoints, npoints))
        vals = np.zeros((npoints, npoints))
        for i in range(npoints):
            for j in range(npoints):
                features_tmp[:,ind0] = xs0[i]
                features_tmp[:,ind1] = xs1[j]
                x0[i, j] = xs0[i]
                x1[i, j] = xs1[j]
                vals[i, j] = model(features_tmp).mean()
                
        fig = pl.figure()
        ax = fig.add_subplot(111, projection='3d')


#         x = y = np.arange(-3.0, 3.0, 0.05)
#         X, Y = np.meshgrid(x, y)
#         zs = np.array(fun(np.ravel(X), np.ravel(Y)))
#         Z = zs.reshape(X.shape)

        ax.plot_surface(x0, x1, vals, cmap=shap.plots.colors.red_blue_transparent)

        ax.set_xlabel(feature_names[ind0], fontsize=13)
        ax.set_ylabel(feature_names[ind1], fontsize=13)
        ax.set_zlabel("E[f(x) | "+ str(feature_names[ind0]) + ", "+ str(feature_names[ind1]) + "]", fontsize=13)

        if show:
            pl.show()
        else:      
            return fig, ax
