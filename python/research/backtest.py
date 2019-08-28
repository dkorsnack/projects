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

plot_str = r'{0}: {1:0.2f}%, $\mu$={2:0.2f}%, $\wedge$={3:0.2f}%, $\vee$={4:0.2f}%'

def describe(rs, tag, window):
    cum_ret_plot(rs[RSD:RED], 'cr'+tag+'.png', SCALE)
    drawdown_plot(rs[RSD:RED], 'dd'+tag+'.png')
    roll = rs.rolling(window=window)
    years = rs.groupby(pd.Grouper(freq='Y'))
    ar = 100*years.apply(lambda x: np.prod(1+x)-1)
    line_plot(
        ar[RSD:RED], 
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
    for (i,j) in cmbns:
        rho[i+'-'+j] = cor[i][j]
    div = pd.DataFrame()
    div['Avg Corr'] = cov['R'].apply(lambda r: r.sum()/M**2)
    div['# of Bets'] = cov['C'].apply(lambda c: effective_bets(c))
    line_plot(
        div[RSD:RED],
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
        rho[RSD:RED],
        'corr'+tag+'.png',
        title='Realized Rolling Correlation',
        ylabel='Correlation',
        legend = [
            plot_str.format(k, v[-1], v.mean(), v.min(), v.max())
            for (k,v) in rho.items()
        ],
    )
    vol = 100*roll.std()*SCALE**0.5
    volatility_plot(vol[RSD:RED], 'v'+tag+'.png')
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
        print(csv, sd, ed)
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
    cov['C'] = [x.reshape(N,N) for x in cov.values]
    last_cov = cov['C'].values[-1]
    last_v = last_cov.diagonal()**0.5
    last_i = last_v.reshape(N,1)**-1
    last_c = last_i*last_cov*last_i.T
    print('VOL:')
    print(100*SCALE**0.5*last_v)
    print('COR:')
    for c in last_c:
        print(100*c)
    return cov['C']

def diversify(rs, window, optimization, vol_center, max_leverage=3):
    keys = rs.keys()
    cov = generate_C(rs, window)
    last_c = cov.values[-1]
    if vol_center:
        vc = float(vol_center)/100
        def function(C):
            w = optimization(C)
            l = vc/(SCALE**0.5*w.dot(C.dot(w))**0.5)
            if np.all(w == EW):
                return EW
            else:
                return min(max_leverage,l)*w
    else:
        def function(C):
            return optimization(C)
    xx = cov.shift().dropna().apply(function)
    last_x = xx.values[-1]
    print('EXP:')
    print(100*last_x)
    print('pVOL: {0: 0.2f}%'.format(
        100*SCALE**0.5*last_x.dot(last_c.dot(last_x))**0.5
    ))
    df = pd.DataFrame()
    for i in range(N):
        df[keys[i]] = xx.apply(lambda x: x[i])
    return df

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
            sec = security[csv+'_Adj Close'].to_frame()
        sec.columns = [csv]
        securities.append(sec)
    assets = securities[0].join(securities[1:], how='inner')
    if ret:
        return assets[csvs].pct_change().dropna()
    else:
        return assets[csvs]

def ensemble_vol(n=4):
    rng = [i for i in range(n)]
    weights = np.array([1./n]*n)
    df = pd.DataFrame(np.random.randn(50,n)/100)
    df['I'] = sum([weights[i]*df[i] for i in rng])
    C = df[rng].cov()
    print(100*SCALE**0.5*weights.dot(C.dot(weights))**0.5)
    print(100*SCALE**0.5*df['I'].std())
    return

def backtest(
    csvs,
    intraday,
    window,
    optimization,
    vol_center,
    static,
):
    tickers = csvs+[static] if static else csvs
    rs = collect_data(tickers, intraday)[DSD:]
    xx = diversify(
        rs[csvs],
        window,
        optimization,
        vol_center,
    )
    exposure_plot(xx[RSD:RED], 'x.png')
    if static:
        benchmark = static
    else:
        benchmark = 'Static (EW)'
        rs[benchmark] = sum([rs[csvs[i]]/N for i in range(N)])
    rs['Backtest'] = sum([xx[csvs[i]]*rs[csvs[i]] for i in range(N)])
    describe(rs[csvs], '', window)
    describe(rs[[benchmark,'Backtest']], 'd', window)
    return 0

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
        default="10",
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
        default="SPY,TLT",
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
        default='1990-01-01/1990-01-01/2020-01-01',
        help='data_start/report_start/report_end',
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
    global DSD, RSD, RED, N, EW, SCALE
    if o.dates:
        DSD, RSD, RED = o.dates.split("/")
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
    backtest(
        csvs,
        o.intraday,
        o.window,
        optimization,
        o.vol_center,
        o.static,
    )
    with open("backtest.tex", "r") as fl, open("bt.tex", "w") as nfl:
        ofl = []
        for line in fl:
            if "BT-PARAMS" in line:
                line = line.replace("BT-PARAMS", params)
            if "DATES" in line:
                line = line.replace("DATES", o.dates)
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
