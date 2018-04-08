#!/usr/local/bin/python3

import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from optparse import OptionParser
from lib.graphics import * 
from lib.risk_optimizations import optimizer
from dynamic import collect_data

FIGSIZE=(8,2.3)

def prcm(intraday, window, scale):
    label = 'Intraday' if intraday else 'Daily'
    rs = collect_data(['SPY','^VIX'], intraday, True)
    px = collect_data(['SPY','^VIX'], intraday, False)
    cum_ret_plot(rs[['SPY']], 'SPY.png', scale, figsize=FIGSIZE)
    volatility_plot(
        px[['^VIX']],
        '^VIX.png',
        figsize=FIGSIZE,
        title='CBOE Volatility Index (^VIX Index)',
        ylabel=label+' Level',
    )
    scatter(
        100*rs['SPY'].values,
        100*rs['^VIX'].values,
        'rv.png',
        title='SPY & ^VIX Are Negatively Correlated',
        trendline=1,
        ylabel=label+' % Change in ^VIX',
        xlabel=label+' % Change in SPY',
        figsize=FIGSIZE,
        #splitx=0,
    )
    scatter(
        px['^VIX'].values[:-1],
        px['^VIX'].values[1:],
        'acorr.png',
        title='VIX Exhibits Strong Positive Autocorrelation',
        trendline=1,
        xlabel=r'^$VIX_{t}$',
        ylabel=r'^$VIX_{t+1}$',
        figsize=FIGSIZE,
    )
    tag = '^VIX Managed'
    xx = (20/px['^VIX']).apply(lambda x: min(2,x)).shift().dropna()
    exposure_plot(
        xx.to_frame().rename(columns={'^VIX':tag+' Exposure'}),
        'xx.png',
        figsize=FIGSIZE
    )
    rs[tag] = xx*rs['SPY']
    compares = ['SPY',tag]
    cum_ret_plot(rs[compares], 'cr.png', scale, figsize=FIGSIZE)
    drawdown_plot(rs[compares], 'dd.png', figsize=FIGSIZE)
    roll = rs[compares].rolling(window=window)
    vol = 100*roll.std()*scale**0.5
    volatility_plot(vol, 'v.png', figsize=FIGSIZE)
    volatility_plot(vol[['SPY']], 'vv.png', figsize=FIGSIZE)
    scatter(
        vol['SPY'].values[window:], 
        px['^VIX'].values[window+1:],
        'vr.png',
        title='A Significant Component of ^VIX is Realized Volatility',
        trendline=1,
        xlabel='Realized SPY Volatility',
        ylabel='^VIX Index Level',
    )
    xlx = ['XL'+x for x in 'BEFIKPUVY']
    srs = collect_data(xlx, intraday, True)
    cum_ret_plot(srs, 'XLX.png', scale, figsize=FIGSIZE)
    sroll = srs.rolling(window=window)
    cor = sroll.corr().unstack(level=1)
    cov = sroll.cov().unstack(level=1)
    cov['C'] = [x.reshape(9,9) for x in cov.values] 
    cov['R'] = [x.reshape(9,9) for x in cor.values] 
    weights = np.array([25,32,67,70,71,34,28,61,84])/472.
    print(cov.index[-1])
    print("VOL:\n", 100*scale**0.5*np.diag(cov['C'].values[-1])**0.5)
    print("CORR:")
    for r in cov['R'].values[-1]:
        print(r)
    svol = cov['C'].apply(
        lambda C: 100*scale**0.5*weights.dot(C.dot(weights))**0.5
    )
    scor = cov['R'].apply(
        lambda R: 100*weights.dot(R.dot(weights))
    )
    volatility_plot(
        svol.dropna().to_frame().rename(columns={'C':r'$\sigma$'}),
        'sr.png',
        figsize=FIGSIZE,
    )
    volatility_plot(
        scor.dropna().to_frame().rename(columns={'R':r'$\overline{\rho}}$'}),
        'sc.png',
        title='Realized Average Correlation',
        ylabel='Correlation %',
        figsize=FIGSIZE,
    )
    scatter(
        scor.values,
        svol.values,
        'ss.png',
        title='Diversification Potential Changes Across Volatility Regimes',
        xlabel='Realized Average Correlation',
        ylabel='Realized Volatility',
    )   
    B = np.array([1]*9)
    def function(C):
        w = optimizer('MCc',C,B)
        l = 0.15/(scale**0.5*w.dot(C.dot(w))**0.5)
        return min(2,l)*w
    rb = cov['C'].shift().dropna().apply(function)
    xx = pd.DataFrame()
    for i in range(9):
        xx[xlx[i]] = rb.apply(lambda x: x[i])
    exposure_plot(xx, 'sx.png', figsize=FIGSIZE)
    compares = ['SPY','^VIX Managed', r'$\mathbf{\Sigma}$ Managed']
    rs[r'$\mathbf{\Sigma}$ Managed'] = sum([xx[xlx[i]]*srs[xlx[i]] for i in range(9)])
    sd = srs.index[0]
    cum_ret_plot(rs[compares][sd:], 'foo.png', scale, figsize=FIGSIZE)
    drawdown_plot(rs[compares][sd:], 'sdd.png', figsize=FIGSIZE)
    roll = rs[compares][sd:].rolling(window=window)
    vol = 100*roll.std()*scale**0.5
    volatility_plot(vol, 'svv.png', figsize=FIGSIZE)
    return
    
def parseOptions(args):
    p = OptionParser('')
    p.add_option(
        '-i',
        '--intraday',
        action='store_true',
        default=False,
    )
    p.add_option(
        '-w',
        '--window',
        default=60,
        type=int,
    )
    (o,a) = p.parse_args(args)
    return o

def main(args):
    o = parseOptions(args)
    prcm(o.intraday, o.window, 504 if o.intraday else 252)
    return

if __name__ == '__main__':
    sys.exit(main(sys.argv))
