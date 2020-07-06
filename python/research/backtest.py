#!/usr/local/bin/python3

import os
import sys
import datetime
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from optparse import OptionParser
from itertools import combinations as cmb
from lib.graphics import * 
from lib.risk_optimizations import optimizer, min_var, min_corr, risk_budget
from lib.torsion import effective_bets, maximum_effective_bets

np.set_printoptions(
    linewidth=200,
    formatter={'float': '{: 8.2f}'.format},
)

PATH = os.environ['PYTHONPATH']+'/research'
N = 0
EW = None
SCALE = 252
(DSD,RSD,RED) = (None,None,None)
VIX = None

plot_str = r'{0}: {1:0.2f}%, $\mu$={2:0.2f}%, $\wedge$={3:0.2f}%, $\vee$={4:0.2f}%'

def describe(rs, tag, window):
    cum_ret_plot(rs, 'cr'+tag+'.png', SCALE)
    drawdown_plot(rs, 'dd'+tag+'.png')
    roll = rs.rolling(window=window)
    years = rs.groupby(pd.Grouper(freq='Y'))
    ar = 100*years.apply(lambda x: np.prod(1+x)-1)
    line_plot(
        ar, 
        'ar'+tag+'.png',
        title='Realized Annual Returns',
        ylabel='Annual Return %',
        style='o-.',
        legend = [
            plot_str.format(k, v[-1], v.mean(), v.min(), v.max())
            for (k,v) in ar.items()
        ],
    )
    keys = rs.keys()
    M = len(keys)
    ew = np.array([1./M]*M)
    cor = roll.corr().unstack(level=1)
    cov = roll.cov().unstack(level=1)
    cov['C'] = [c.reshape(M,M) for c in cov.values]
    cov['R'] = [r.reshape(M,M) for r in cor.values]
    rho = pd.DataFrame()
    cmbns = [(keys[0],keys[0])] if M<2 else cmb(keys,2)
    for (n,(i,j)) in enumerate(cmbns):
        rho[i+'-'+j] = cor[i][j]
        scatter(rs[i], rs[j], "s"+str(n)+tag+".png", xlabel=i, ylabel=j, trendline=1, eigen=True)
    div = pd.DataFrame()
    div['Avg Corr'] = cov['R'].apply(lambda r: r.sum()/M**2)
    div['# of Bets'] = cov['C'].apply(lambda c: effective_bets(c))
    line_plot(
        div,
        'div'+tag+'.png',
        title='Diversification Measures',
        ylabel='Diversification Metric',
        legend = [
            plot_str.format(k, v[-1], v.mean(), v.min(), v.max())
            for (k,v) in div.items()
        ],
        handlelength=0,
    )
    line_plot(
        rho,
        'corr'+tag+'.png',
        title='Realized Rolling Correlation',
        ylabel='Correlation',
        legend = [
            plot_str.format(k, v[-1], v.mean(), v.min(), v.max())
            for (k,v) in rho.items()
        ],
    )
    vol = 100*roll.std()*SCALE**0.5
    #vol['^VIX'] = VIX
    volatility_plot(vol, 'v'+tag+'.png')
    histogram(
        100*rs,
        'h'+tag+'.png',
        log=True,
        alpha=0.5,
        bin_size=0.1,
        title="Return Distribution",
        xlabel="Return %",
        ylabel="Frequency (log scale)",
    )
    return

def edge_data(csvs):
    import subprocess
    import pandas_datareader.data as pdd
    ed = datetime.date.today()-datetime.timedelta(days=1)
    if not csvs:
        p = subprocess.Popen(
            'ls '+PATH+'/*.csv', stdout=subprocess.PIPE, shell=True
        )
        (output, err) = p.communicate()
        csvs = [
            o.strip(PATH)[:-1]
            for o in output.decode().split("\n")[:-1]
        ]
    else:
        csvs = csvs.split(',')
    for csv in csvs:
        path = PATH+'/'+csv+'.csv'
        with open(path) as fl:
            raw = fl.readlines()
        begin = raw[-1].split(',')[0]
        sd = datetime.datetime.strptime(begin, '%Y-%m-%d').date()+datetime.timedelta(1)
        try:
            all_data = pdd.DataReader(csv, 'yahoo', start=sd, end=ed)
            lines = '\n'.join(all_data.to_csv().split('\n')[1:])
            with open(path, 'a') as fl:
                fl.write(lines)
            print("WROTE ", csv)
        except Exception as e:
            print(e)
    return

def generate_C(rs, window):
    roll = rs.rolling(window=window)
    cov = roll.cov().unstack(level=1)
    rho = roll.corr().unstack(level=1)
    df = pd.DataFrame()
    df['C'] = [c.reshape(N,N) for c in cov.values]
    df['R'] = [r.reshape(N,N) for r in rho.values]
    df.index = cov.index
    print('VOL:')
    print(100*SCALE**0.5*df.C.values[-1].diagonal()**0.5)
    print('COR:')
    for r in df.R.values[-1]:
        print(100*r)
    return df[['C','R']]

def diversify(rs, window, optimization, vol_center, max_leverage=10):
    keys = rs.keys()
    df = generate_C(rs, window)
    df['X'] = [EW]+[optimization(C) for C in df.C.shift().dropna()]
    df['V'] = [SCALE**0.5*w.dot(c.dot(w))**0.5 for (w,c) in zip(df.X, df.C)]
    if vol_center:
        vc = vol_center
        df['L'] = [
            1 if np.isnan(v) else min(max_leverage, vc/v)
            for v in df.V.shift()
        ]
        """
        df['VIX'] = VIX.shift()
        df['L'] = [vol_center/v for v in df.VIX]
        """
        """
        df['VIX'] = VIX
        df['L'] = [1]+[
            vol_center/(v*r.mean()**0.5)
            for (_,v,r) in df[['VIX','R']].shift().dropna().to_records()
        ]
        """
        df['X'] *= df.L
        df['V'] = [
            SCALE**0.5*w.dot(c.dot(w))**0.5 for (w,c) in zip(df.X, df.C)
        ]
    print('EXP:')
    print(100*df.X.values[-1])
    print('pVOL: {0: 0.2f}%'.format(100*df.V.values[-1]))
    for i in range(N):
        df[keys[i]] = [x[i] for x in df.X.values]
    return df[keys]

def collect_data(csvs, intraday, ret=True):
    col_names=['Date','Open','Close','Adj Close']
    securities = []
    for csv in csvs:
        security = pd.read_csv(
            PATH+'/'+csv+'.csv',
            usecols=col_names,
            parse_dates=['Date'],
            index_col='Date',
        )
        security.index = [dt.replace(hour=16) for dt in security.index]
        security.columns = [csv+'_'+c for c in col_names[1:]]
        if intraday:
            op = pd.DataFrame()
            op[csv+'_Adj Close'] = security[csv+'_Open']*security[csv+'_Adj Close']/security[csv+'_Close']
            op.index = [dt.replace(hour=9, minute=30) for dt in op.index]
            sec = pd.DataFrame(pd.concat([op[csv+'_Adj Close'], security[csv+'_Adj Close']]).sort_index())
        else:
            sec = security[[csv+'_Adj Close']]
        sec.columns = [csv]
        securities.append(sec)
    assets = securities[0].join(securities[1:], how='inner')
    if ret:
        return assets[csvs].pct_change().dropna()
    else:
        return assets[csvs]

def backtest(
    csvs,
    intraday,
    window,
    optimization,
    vol_center,
    static,
    riskfree,
):
    tickers = csvs+[static] if static else csvs
    rs = collect_data(tickers+[riskfree], intraday)[DSD:]
    xx = diversify(
        rs[csvs],
        window,
        optimization,
        vol_center,
    )
    xx[riskfree] = xx.apply(lambda x: max(0, 1-sum(x)), axis=1)
    exposure_plot(xx[RSD:RED], 'x.png')
    if static:
        benchmark = static
    else:
        benchmark = 'Static (EW)'
        rs[benchmark] = sum([rs[csvs[i]]/N for i in range(N)])
    rs['Backtest'] = sum([xx[csvs[i]]*rs[csvs[i]] for i in range(N)])
    describe(rs[csvs][RSD:RED], '', window)
    #describe(rs[csvs+[riskfree]][RSD:RED], '', window)
    describe(rs[[benchmark,'Backtest']][RSD:RED], 'd', window)
    return rs

def parseOptions(args):
    p = OptionParser('')
    p.add_option(
        '-w',
        '--window',
        dest='window',
        type=int,
        default=100,
    )
    p.add_option(
        '-v',
        '--vol_center',
        dest='vol_center',
        default=0.1,
        type=float,
    )
    p.add_option(
        '-e',
        '--edge',
        dest='edge',
        action='store_true',
        default=False,
    )
    p.add_option(
        '-c',
        '--csvs',
        dest='csvs',
        default="SPY,IEF",
    )
    p.add_option(
        '-r',
        '--riskfree',
        dest='riskfree',
        default="SHY",
    )
    p.add_option(
        '-i',
        '--intraday',
        dest="intraday",
        action="store_false",
        default=True,
    )
    p.add_option(
        '-s',
        '--static',
        dest='static',
        default='VBINX',
    )
    p.add_option(
        '-o',
        '--optimization',
        dest='optimization',
        default="RB:3,1",
    )
    p.add_option(
        '-d',
        '--dates',
        dest='dates',
        default='1990-01-01|1990-01-01|2021-01-01',
        help='data_start|report_start|report_end',
    )
    (o,a) = p.parse_args(args)
    return o

def main(args):
    o = parseOptions(args)
    params = "|"+"|".join([
        "c."+o.csvs,
        "s."+o.static,
        "w."+str(o.window)+("i" if o.intraday else ""),
        "o."+o.optimization,
        "v."+str(o.vol_center),
    ])+"|"
    print(o)
    if o.edge:
        edge_data(o.csvs)
        return
    csvs = o.csvs.split(',') 
    #global VIX, DSD, RSD, RED, N, EW, SCALE
    #VIX = collect_data(['^VIX'], o.intraday, False)
    global DSD, RSD, RED, N, EW, SCALE
    if o.dates:
        DSD, RSD, RED = o.dates.split("|")
    if o.intraday:
        SCALE *= 2
    N += len(csvs)
    EW = np.array([1./N]*N)    
    sopt = o.optimization.split(":")
    if len(sopt) > 1:
        B = np.array([int(i) for i in sopt[1].split(",")])
    else:
        B = None
    optimization = {
        'EW': lambda C: EW,
        'MV': lambda C: min_var(C),
        'MVc': lambda C: optimizer('MVc',C),
        'MC': lambda C: min_corr(C),
        'MCc': lambda C: optimizer('MCc',C),
        'MD': lambda C: optimizer('MD',C),
        'MDc': lambda C: optimizer('MDc',C),
        'RB': lambda C: risk_budget(C, B),
        'RBc': lambda C: optimizer('RBc', C, B, tol=1e-20, options={'maxiter':1000}),
        'TT': lambda C: tangency(C, M=B),
        'TTc': lambda C: optimizer('TTc', C, M=B),
        'MB': lambda C: maximum_effective_bets(C, shorting='allowed'),
        'MBc': lambda C: maximum_effective_bets(C, shorting=False),
    }[sopt[0]]
    rs = backtest(
        csvs,
        o.intraday,
        o.window,
        optimization,
        o.vol_center,
        o.static,
        o.riskfree,
    )
    with open("backtest.tex", "r") as fl, open("bt.tex", "w") as nfl:
        ofl = []
        for line in fl:
            if "BT-PARAMS" in line:
                line = line.replace("BT-PARAMS", params)
            if "DATES" in line:
                line = line.replace("DATES", "|".join([
                    rs.index[0].date().isoformat(),
                    RSD,
                    rs.index[-1].date().isoformat(),
                ]))
            ofl.append(line)
        nfl.write("\n".join(ofl))
    os.system((
        "pdflatex bt.tex && "
        "mv bt.pdf backtest.pdf && "
        "rm *.png *.aux *.out *.log"
    ))
    return

if __name__ == '__main__':
    sys.exit(main(sys.argv))
