#!/usr/local/bin/python3

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import ScalarFormatter
from scipy import stats

__all__ = [
    'moment_str',
    'histogram',
    'scatter',
    'line_plot',
    'cum_ret_plot',
    'drawdown_plot',
    'exposure_plot',
    'volatility_plot',
    'probability_plot',
    'acorr_plot',
]

FONTSIZE=8

def line_plot(data, handle, **kwargs):
    fig = data.plot(
        kind='line',
        logy=kwargs.get('logy',False),
        alpha=kwargs.get('alpha'),
        style=kwargs.get('style'),
        figsize=kwargs.get('figsize'),
        grid=True,
        title=kwargs.get('title'),
        ylim=kwargs.get('ylim'),
    )
    if 'yticklabels' in kwargs:
        fig.set_yticks(kwargs['yticklabels'])
        fig.set_yticklabels([str(i) for i in kwargs['yticklabels']])
    if 'ylabel' in kwargs:
        fig.set_ylabel(kwargs['ylabel'])
    if 'legend' in kwargs:
        fig.legend(kwargs['legend'], loc='best', fontsize=FONTSIZE)
    if 'hline_plot' in kwargs:
        fig.axhline_plot(y=kwargs['hline_plot'], color='black', line_plotwidth=1)
    if 'logy' in kwargs:
        fig.minorticks_off()
    if 'minor' in kwargs:
        fig.grid(True, which='minor')
    fig.set_xlabel('Date')
    fig.get_figure().savefig(handle)
    print('line_plot '+handle)
    plt.clf()

def scatter(x, y, handle, **kwargs):
    legend=[]
    def generate_trendline(x,y,deg):
        rsq = np.corrcoef(x,y)
        z = np.polyfit(x=x, y=y, deg=kwargs['trendline'])
        p = np.poly1d(z)
        plt.plot(x, p(x), 'k-', linewidth=1)
        legend.append('\n'.join([
                '$Y={0:0.2f}\%*X+{1:0.2f}\%+\epsilon$',
                '$N={2:d}$',
                '$R^2={3:0.2f}$',
            ]).format(z[0],z[1],len(x),rsq[0,1]**2)
        )
    def generate_eigen(x,y,colors=('red','green')):
        xm = x.mean()
        ym = y.mean()
        S = np.cov(x,y)
        e,v = np.linalg.eigh(S)
        se = sum(e)
        for (i,c) in zip((1,0),'rg'):
            plt.quiver(xm, ym, v[i][0], v[i][1], color=c, scale=1) 
            legend.append(
                'PC{0} Explains {1: 0.2f}% of the Variance'.format(i, e[i]/se)
            )
    plt.scatter(x, y, s=2, c=range(len(x)), cmap='Blues')
    if 'title' in kwargs:
        plt.title(kwargs['title'])
    if 'xlim' in kwargs:
        plt.xlim(kwargs['xlim'])
    if 'ylim' in kwargs:
        plt.ylim(kwargs['ylim'])
    if 'xlabel' in kwargs:
        plt.xlabel(kwargs['xlabel'])
    if 'ylabel' in kwargs:
        plt.ylabel(kwargs['ylabel'])
    if 'trendline' in kwargs:
        generate_trendline(x, y, kwargs['trendline'])
    if 'splitx' in kwargs and 'trendline' in kwargs:
        import operator as op
        s = kwargs['splitx']
        zp = list(zip(x,y))
        for (f,c) in ((op.lt,'red'), (op.ge,'green')):
            x,y = zip(*[(a,b) for (a,b) in zp if f(a,s)]) 
            generate_trendline(x,y,kwargs['trendline'])
    if 'eigen' in kwargs:
        generate_eigen(x,y)
    plt.legend(legend, loc='best', fontsize=FONTSIZE)
    plt.grid(True)
    plt.savefig(handle)
    print('scatter '+handle)
    plt.clf()

def dist_legend(x):
    mu = np.mean(x)
    sig = np.std(x)
    return moment_str.replace(', ','\n').format(
        '', '', len(x), 100*mu, 100*sig, mu/sig, stats.skew(x), stats.kurtosis(x)
    )

def histogram(data, handle, **kwargs):
    fig = data.plot(
        kind='hist',
        bins=kwargs.get('bins',100),
        log=kwargs.get('log',False),
        alpha=kwargs.get('alpha'),
        figsize=kwargs.get('figsize'),
        grid=kwargs.get('grid',True),
        legend=False,
    )
    plt.legend(
        [dist_legend(data.values)],
        loc='best',
        fontsize=FONTSIZE,
        handlelength=0,
    )
    fig.yaxis.set_major_formatter(ScalarFormatter())
    fig.get_figure().savefig(handle)
    print('histogram '+handle)
    plt.clf()

def probability_plot(x, handle, **kwargs):
    fig = plt.figure()
    ax = fig.add_subplot(111)
    stats.probplot(x, dist=kwargs.get('dist','norm'), rvalue=True, plot=plt)
    plt.grid(True)
    ax.annotate(dist_legend(x), xy=(25,200), xycoords='axes points', size=FONTSIZE)
    ax.get_lines()[0].set_color('k')
    ax.get_lines()[0].set_markersize(4)
    if 'ylim' in kwargs:
        plt.ylim(kwargs['ylim'])
    plt.savefig(handle)
    print('probability_plot '+handle)
    plt.clf()

def acorr_plot(data, handle, **kwargs):
    from pandas.plotting import autocorrelation_plot
    fig = autocorrelation_plot(data).get_figure()
    if 'title' in kwargs:
        plt.title(kwargs['title'])
    if 'xlim' in kwargs:
        plt.xlim(kwargs['xlim'])
    fig.savefig(handle)
    print('acorr_plot '+handle)
    fig.clf()

moment_str = ', '.join([
    r'N={2}',
    r'$\mu$={3:0.2f}%',
    r'$\sigma$={4:0.2f}%',
    r'$\mu/\sigma$={5:0.2f}',
    r'$\lambda$={6:0.2f}',
    r'$\kappa$={7:0.2f}',
])

def cum_ret_legend(cum, rs, scale):
    legend = []
    for (k,v) in cum.items():
        r = (1+rs[k].mean())**scale-1
        s = scale**0.5*rs[k].std()
        legend.append((r'{0}: {1:0.2f} ['+moment_str+']').format(
            k, v[-1], len(rs[k]), 100*r, 100*s, r/s, rs[k].skew(), rs[k].kurtosis())
        )
    return legend

def cum_ret_plot(rs, handle, scale, **kwargs):
    cum = np.exp(np.log1p(rs).cumsum())
    line_plot(
        cum,
        handle,
        logy=True,
        ylabel='Growth of $1 (Log Scale)',
        title='Cumulative Performance',
        yticklabels=range(1, int(np.ceil(cum.max().max())+1)),
        legend = cum_ret_legend(cum, rs, scale),
        **kwargs
    )

def drawdown_plot(rs, handle, **kwargs):
    cum = np.exp(np.log1p(rs).cumsum())
    dd = 100*(cum/cum.cummax()-1)
    line_plot(
        dd,
        handle,
        ylabel='Drawdown %',
        title='Drawdowns',
        legend = [
            '{0}: {1:0.2f}% [$\wedge$={2:0.2f}]'.format(k, v[-1], v.min())
            for (k,v) in dd.items()
        ],
        **kwargs
    )

def exposure_plot(ex, handle, **kwargs):
    exp_str = '{0}: {1:0.2f}% [$\mu$={2:0.2f}%; $\mu\Delta$={3:0.2f}%, $\\vee\Delta$={4:0.2f}%]'
    xxa = 100*ex
    xxd = abs(xxa.diff()).fillna(0)
    leg = [exp_str.format(
        col, xxa[col][-1], xxa[col].mean(), xxd[col].mean(), xxd[col].max(),
    ) for col in xxa.columns]
    if len(ex.columns)>1:
        xxat = xxa.sum(axis=1).values
        xxdt = xxd.sum(axis=1).values
        xxa['Total'] = xxat
        leg += [exp_str.format( 
            'Total', xxat[-1], xxat.mean(), xxdt.mean(), xxdt.max()
        )]
    line_plot(
        xxa,
        handle,
        ylabel='Gross Exposure %',
        title='Gross Exposure Profile',
        legend = leg, 
        **kwargs
    )

def volatility_plot(vol, handle, **kwargs):
    line_plot(
        vol,
        handle, 
        title=kwargs.pop('title', 'Realized Rolling Volatility'),
        ylabel=kwargs.pop('ylabel', 'Volatility %'),
        legend = [
            '{0}: {1:0.2f}% [$\mu$={2:0.2f}%, $\wedge$={3:0.2f}%, $\\vee$={4:0.2f}%]'.format(
                k, v[-1], v.mean(), v.min(), v.max()
            ) for (k,v) in vol.items()
        ],
        **kwargs
    )
