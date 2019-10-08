#!/usr/bin/python3

import sys
import subprocess
import numpy as np
import pandas as pd
from lib.graphics import * 

def calc(df):
    r = (1+df.mean())**252-1
    s = 252**0.5*df.std()
    h = r/s
    return (100*r, 100*s, h)

def main(args):
    if len(args) > 1:
        csvs = args[1].split(",")
    else:
        csvs = subprocess.Popen(
            ["ls *.csv"],
            stdout=subprocess.PIPE,
            shell=True
        ).communicate()[0].decode().split(".csv\n")[:-1]
    for csv in csvs:
        security = pd.read_csv(
            csv+".csv",
            parse_dates=['Date'],
            index_col='Date'
        ).loc["1996-01-01":]
        line_plot(security['Close']/security['Open']-1, csv+'d.png')
        security['lOpen'] = np.log(security['Open']).shift(-1)
        security['lClose'] = np.log(security['Close'])
        security['sClose'] = security['lClose'].shift(-1)
        security["cto"] = security["lOpen"]-security["lClose"]
        security["otc"] = security["sClose"]-security["lOpen"]
        security["ctc"] = security["sClose"]-security["lClose"]
        print(security.tail())
        #security["ata"] = np.log(security["Adj Close"]).diff()
        #dudes = security[["cto", "otc", "ctc", "ata"]].dropna()
        dudes = security[["cto", "otc", "ctc"]].dropna()
        print(len(dudes), (dudes == 0).sum())
        cum_ret_plot(dudes, csv+".png", 252)
        scatter(
            dudes["cto"].values,
            dudes["otc"].values,
            csv+"s.png",
            xlabel="cto",
            ylabel="otc",
            trendline=1,
        )
    return 

if __name__ == "__main__":
    sys.exit(main(sys.argv))
