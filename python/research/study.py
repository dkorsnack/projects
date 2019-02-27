#!/usr/local/bin/python3

import sys
import pandas as pd
import numpy as np
from dynamic import collect_data
from lib.graphics import scatter

def main(args):
    spdrs = ["XL"+x for x in "BEFIKPUVY"]
    n = len(spdrs)
    rs = collect_data(['SPY']+spdrs)
    #months = rs.groupby(pd.Grouper(freq='M'))
    months = rs.rolling(window=60)
    spy = months['SPY']
    df = pd.DataFrame()
    df['r'] = spy.apply(lambda x: np.prod(1+x)-1).dropna()
    df['v'] = 252**0.5*spy.std().dropna()
    cor = months[spdrs].corr().unstack(level=1)
    cor['R'] = [c.reshape(n,n) for c in cor.values]
    df['c'] = cor['R'].apply(lambda x: x.sum()/n**2)
    scatter(df['v'].values, df['r'].values, "vr.png", trendline=1)
    scatter(df['c'].values, df['r'].values, "cr.png", trendline=1)
    scatter(df['c'].values, df['v'].values, "cv.png", trendline=1)
    d = 0.1
    rng = np.arange(0,1,d)
    for i in reversed(rng):
        print(i, ['{0:8.2f}'.format(100*df[(j<df['v']) & (df['v']<=j+d) & (i<df['c']) & (df['c']<=i+d)].mean()['r']) for j in rng])
        #print(i, ['{0:d}'.format(len(df[(j<df['v']) & (df['v']<=j+d) & (i<df['c']) & (df['c']<=i+d)])) for j in rng])
    return

if __name__ == "__main__":
    sys.exit(main(sys.argv))
