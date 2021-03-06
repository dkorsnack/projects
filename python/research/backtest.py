#!/usr/local/bin/python3

import os
import sys
import datetime
import pickle
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
ETF_DICT = {
    #ETF: (IB_Ticker, Asset_Class),
    'EEM': ('MXEA', 'Equity'),
    'EFA': ('MXEF', 'Equity'),
    'GLD': ('MGC', 'Commodity'),
    'IEF': ('ZN', 'Bond'),
    'IWM': ('M2K', 'Equity'),
    'QQQ': ('MNQ', 'Equity'),
    'SHY': ('ZT', 'Cash'),
    'SLV': ('SIL', 'Commodity'),
    'SPY': ('MES', 'Equity'),
    'TLT': ('ZB', 'Bond'),
    #'LQD': ('LQD', 'Credit'),
    #'HYG': ('HYG', 'Credit'),
    'XLB': ('XLB', 'Equity'),
    'XLE': ('XLE', 'Equity'),
    'XLF': ('XLF', 'Equity'),
    'XLI': ('XLI', 'Equity'),
    'XLK': ('XLK', 'Equity'),
    'XLP': ('XLP', 'Equity'),
    'XLU': ('XLU', 'Equity'),
    'XLV': ('XLV', 'Equity'),
    'XLY': ('XLY', 'Equity'),
    'VBINX': ('60/40', 'Blend'),
}
IB_RENAME = {}
ASSET_CLASS = {}
for (etf,(ib,ac)) in ETF_DICT.items():
    IB_RENAME[etf] = ib
    ASSET_CLASS[etf] = ac

plot_str = r'{0}: Last={1:0.2f}% [Avg={2:0.2f}%, Min={3:0.2f}%, Max={4:0.2f}%]'

def describe(df, tag, window, csv):
    if csv:
        foo = ['VBINX', 'Backtest', 'SHY']
        df = pd.read_csv(
            "lppl.csv",
            index_col='datetime',
            parse_dates=['datetime'],
            usecols=['datetime']+[f+'_r' for f in foo],
        ).rename(columns={f+'_r':f for f in foo}) 
    rs = df.rename(columns=IB_RENAME)
    #pickle.dump(rs, open("rs3.pkl", "wb"))
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
    cor = roll.corr().unstack(level=1)
    cov = roll.cov().unstack(level=1)
    cov['C'] = [c.reshape(M,M) for c in cov.values]
    cov['R'] = [r.reshape(M,M) for r in cor.values]
    rho = pd.DataFrame()
    cmbns = [(keys[0],keys[0])] if M<2 else cmb(keys,2)
    for (n,(i,j)) in enumerate(cmbns):
        rho[i+'-'+j] = cor[i][j]
        #scatter(rs[i], rs[j], "s"+str(n)+tag+".png", xlabel=i, ylabel=j, trendline=1, eigen=True)
    div = pd.DataFrame()
    div['Avg Corr'] = cov['R'].apply(lambda r: r.sum()/M**2)
    div['# of Bets'] = cov['C'].apply(lambda c: effective_bets(c))
    line_plot(
        div,
        'div'+tag+'.png',
        title='Diversification Measures',
        ylabel='Diversification Metric',
        legend = [
            plot_str.replace("%","").format(k, v[-1], v.mean(), v.min(), v.max())
            for (k,v) in div.items()
        ],
        handlelength=0,
    )
    line_plot(
        rho,
        'corr'+tag+'.png',
        title='Realized Rolling Correlation',
        ylabel='Correlation',
        legend = [] if len(rho.columns) > 10 else [
            plot_str.replace("%","").format(k, v[-1], v.mean(), v.min(), v.max())
            for (k,v) in rho.items()
        ],
    )
    vol = 100*roll.std()*SCALE**0.5
    vol['^VIX'] = VIX
    volatility_plot(vol, 'v'+tag+'.png')
    """
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
    """
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
        print(csv)
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

def diversify(rs, window, optimization, vol_target, vol_lookback, max_leverage):
    keys = rs.keys()
    df = generate_C(rs, window)
    df['X'] = [EW]+[optimization(C) for C in df.C.shift().dropna()]
    df['cV'] = [SCALE**0.5*w.dot(c.dot(w))**0.5 for (w,c) in zip(df.X, df.C)]
    df['R'] = [w.dot(r.dot(w)) for (w,r) in zip(df.X, df.R)]
    if vol_lookback:
        lb = vol_lookback*390
        vf = pd.read_csv(
            "spy.gz",
            index_col='Date',
            compression='gzip',
            parse_dates=['Date']
        )
        vf['SPYr'] = vf.SPY.pct_change().shift()
        vf['SPYs'] = (252*390)**0.5*vf.SPYr.rolling(window=lb).std()
        df = df.join(vf[['SPYs']], how='inner')
        df['lV'] = df.SPYs
        #df['V'] = df.lV
        df['V'] = df.R**0.5*df.lV
        df['VIX'] = VIX/100
        foo = df.dropna()[['VIX','cV','lV','V']]
        line_plot(foo, 'out.png')
        scatter(foo.VIX, foo.V, 'out1.png', trendline=1)
    else:
        df['V'] = df.cV
    if vol_target:
        vc = vol_target
        df['L'] = [
            1 if np.isnan(v) else min(max_leverage, vc/v)
            for v in df.V.shift()
        ]
        """
        df['VIX'] = VIX.shift()
        df['L'] = [vol_target/v for v in df.VIX]
        """
        """
        df['VIX'] = VIX
        df['L'] = [1]+[
            vol_target/(v*r.mean()**0.5)
            for (_,v,r) in df[['VIX','R']].shift().dropna().to_records()
        ]
        """
        df['X'] *= df.L
    else:
        df['X'] = 1
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
            op.index = [dt.replace(hour=9, minute=31) for dt in op.index]
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
    vol_target,
    vol_lookback,
    static,
    riskfree,
    max_leverage,
):
    tickers = csvs+[static] if static else csvs
    rs = collect_data(tickers+[riskfree], intraday)[DSD:]
    xx = diversify(
        rs[csvs],
        window,
        optimization,
        vol_target,
        vol_lookback,
        max_leverage,
    )
    xx[riskfree] = xx.apply(lambda x: max(0, 1-sum(x)), axis=1)
    xxx = pd.DataFrame()
    for ac in sorted(set(ASSET_CLASS.values())):
        if ac not in ('Blend',):
            xxx[ac] = xx[[c for c in xx.columns if ASSET_CLASS[c] == ac]].sum(axis=1)
    exposure_plot(xxx.rename(columns=IB_RENAME)[RSD:RED], 'x.png')
    if static:
        benchmark = static
    else:
        benchmark = 'Static (EW)'
        rs[benchmark] = sum([rs[csvs[i]]/N for i in range(N)])
    xx['Backtest_x'] = xx.sum(axis=1)
    jn = rs.join(xx, how='inner', lsuffix='_r', rsuffix='_x')
    #jn.fillna(method='ffill', inplace=True)
    jn['Backtest_r'] = sum([jn[csvs[i]+"_r"]*jn[csvs[i]+"_x"] for i in range(N)])
    #jn.to_csv('backtest.csv')
    jn.rename(columns={c:c[:-2] for c in jn.columns if '_r' in c}, inplace=True)
    describe(jn[csvs+[riskfree]][RSD:RED], '', window, False)
    describe(jn[[benchmark,'Backtest', riskfree]][RSD:RED], 'd', window, False)
    """
    rs['Backtest'] = sum([xx[csvs[i]]*rs[csvs[i]] for i in range(N)])
    describe(rs[csvs+[riskfree]][RSD:RED], '', window, False)
    describe(rs[[benchmark,'Backtest', riskfree]][RSD:RED], 'd', window, False)
    jn = rs.join(xx, how='outer', lsuffix='_r', rsuffix='_x').to_csv('backtest.csv')
    """
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
        '--vol_target',
        dest='vol_target',
        default='10-0d',
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
        default="SPY,IWM,QQQ,GLD,IEF",
        #default="SPY,IWM,QQQ,XLE,GLD,IEF",
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
        default="RB:2,2,2,1,1",
        #default="RB:3,3,3,3,2,2",
    )
    p.add_option(
        '-d',
        '--dates',
        dest='dates',
        default='1990-01-01|1990-01-01|2021-12-31',
        help='data_start|report_start|report_end',
    )
    p.add_option(
        "-l",
        "--max_leverage",
        dest="max_leverage",
        default='10',
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
        "v."+o.vol_target,
        "l."+o.max_leverage,
    ])+"|"
    print(o)
    if o.edge:
        edge_data(o.csvs)
        return
    csvs = o.csvs.split(',') 
    global VIX, DSD, RSD, RED, N, EW, SCALE
    VIX = collect_data(['^VIX'], o.intraday, False)
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
    sv = o.vol_target.split("-")
    rs = backtest(
        csvs,
        o.intraday,
        o.window,
        optimization,
        float(sv[0])/100,
        int(sv[1][:-1]),
        o.static,
        o.riskfree,
        int(o.max_leverage),
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
        "rm bt.tex bt.pdf *.aux *.out *.log" #*.png"
    ))
    return

if __name__ == '__main__':
    sys.exit(main(sys.argv))
