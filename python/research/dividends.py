import sys
import datetime
import pandas as pd
import numpy as np
import pandas_datareader.data as pdd
from lib.graphics import line_plot

def main(args):
    tickers = args[1].split(",")
    n = len(tickers)
    m = int(args[2])
    weights = np.array([float(w) for w in args[3].split(",")])/100
    mdt = datetime.date(1,1,1)
    dfs,divs = [],[]
    for ticker in tickers:
        ps = pdd.DataReader(ticker, 'yahoo', start=datetime.date(2000,1,1))
        ds = pdd.DataReader(ticker, 'yahoo-dividends', start=datetime.date(2000,1,1))
        mdt = max(mdt, ps.index.date[0])
        df = ps.join(ds, how='outer')
        df[ticker+'_tr'] = df['Adj Close'].pct_change()
        df[ticker+'_rs'] = df['Close'].pct_change()
        df[ticker+'_d'] = df['Dividends']/df['Close'].shift()
        dfs.append(df[[ticker+'_rs',ticker+'_tr']])
        divs.append(df[[ticker+'_d']])
    df = dfs[0].join(dfs[1:], how='outer').loc[mdt:]
    df['P_tr'] = df[[c for c in df.columns if '_tr' in c]].dot(weights)
    df['P_rs'] = df[[c for c in df.columns if '_rs' in c]].dot(weights)
    div = divs[0].join(divs[1:], how='outer').loc[mdt:].groupby(pd.Grouper(freq="M")).sum().fillna(0)
    div['P_d'] = div.dot(weights)
    line_plot(m*(1+df[['P_rs']]).cumprod().fillna(1,limit=1), 'out.png', scale=252)
    line_plot(m*div[['P_d']], 'out1.png')
    print(div.groupby(pd.Grouper(freq="Y")).sum())
    return

if __name__ == "__main__":
    sys.exit(main(sys.argv))
