#!/usr/local/bin/python3

import sys
import numpy as np
from dynamic import collect_data

np.set_printoptions(
    formatter={'float': '{: 0.10}'.format},
)

def main(args):
    tickers = ['SPY','IEF']
    n = len(tickers)
    rs = collect_data(tickers, False, True)
    w = np.array([1./n]*n)
    Rp = rs.dot(w) 
    S = rs.cov().as_matrix()
    v,E = np.linalg.eig(S) 
    L = np.diag(v)
    Ei = np.linalg.inv(E.T)
    Rt = rs.dot(Ei)
    wt = w.dot(Ei)
    var_cc = wt**2*v
    vol_cc = var_cc/Rp.std()
    div_cc = var_cc/Rp.var()
    return

if __name__ == "__main__":
    sys.exit(main(sys.argv))
