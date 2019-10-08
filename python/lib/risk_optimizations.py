#!/bin/python

import sys
import numpy as np
from random import random as rnd
from scipy.optimize import minimize
from lib.torsion import maximum_effective_bets

__all__ = [
    "optimizer",
    "min_var",
    "min_corr",
    "risk_budget",
    "naive_risk_parity",
    "tangency",
    "maximum_effective_bets",
]

np.set_printoptions(
    linewidth=200,
    formatter={'float': '{: 8.2f}'.format},
)

# individual asset return assumption
sharpe = 1

# risk free rate assumption
rf = 0

def optimizer(tag, C, B=None, M=None, **kwargs):
    n = C.shape[0]
    k = 1./n
    ones = np.ones(n)
    if np.any(np.isnan(C)):
        return np.array([1./n]*n)
    if tag.startswith('MC'):
        C = cov_to_corr(C)
    if B is None:
        B = ones/n
    if M is None:
        M = sharpe*C.diagonal()**0.5-rf
    constr = (
        {'type':'eq', 'fun': lambda X: ones.dot(X)-1.},
    )
    if len(tag)>2:
        constr += ({'type': 'ineq', 'fun': lambda X: X,},)
    opt = minimize({
            'MV': lambda X: X.dot(C.dot(X))**0.5,
            'MC': lambda X: X.dot(C.dot(X)),
            'MD': lambda X: X.dot(C.dot(X))/X.dot(C.diagonal())-1.,
            'RB': lambda X: sum(abs(X*C.dot(X)-B*(X.dot(C.dot(X))))),
            'TT': lambda X: -(X.dot(M)-rf)/(X.dot(C.dot(X)))**0.5
        }[tag[:2]],
        ones/n,
        method='SLSQP',
        constraints=constr,
        **kwargs
    )
    return opt.x

def cov_to_corr(C):
    n = C.shape[0]
    V = C.diagonal()**0.5
    I = V.reshape(C.shape[0],1)**-1
    return I*C*I.T

def corr_to_cov(R,V):
    return R*np.outer(V,V)

def pprint(tag, C, X=None):
    pstr = "%2s %3s: %s %8.2f"
    n = C.shape[0]
    V = C.diagonal()**0.5
    if X is None:
        corr = cov_to_corr(C) 
        print("VOL    : {}\n".format(100*252**0.5*V))
        for i in range(n):
            print("CORR  {}: {}".format(i, corr[i]))
    else:
        trc = X*X.dot(C)
        cov = X.dot(C.dot(X))
        mu = sharpe*X.dot(252**0.5*V)
        sig = 252**0.5*cov**0.5
        print("\n"+"\n".join([
            pstr % (tag, "X", 100*X, 100*sum(abs(X))),
            (pstr+" %8.2f %8.2f") % (
                tag, "TRC", 100*trc/cov, 100*mu, 100*sig, mu/sig
            ),
        ]))

def minimize_matrix(M):
    n = M.shape[0]
    ones = np.ones(n).reshape(n,1)
    if np.any(np.isnan(M)):
        return np.array([1./n]*n)
    br = np.append(ones, 0.).reshape(1,n+1)
    A = np.vstack([np.hstack([M, ones]), br])
    B = np.array([0.]*n+[1.])
    return np.linalg.solve(A, B)[:-1]

def min_var(C):
    return minimize_matrix(C)

def min_corr(C):
    return minimize_matrix(cov_to_corr(C))

def tangency(C,M=None):
    n = C.shape[0]
    ones = np.ones(n)
    if M is None:
        M = sharpe*C.diagonal()**0.5-rf
    I = np.linalg.inv(C)
    top = I.dot(M)
    return top/ones.dot(top)

def risk_budget(C,B=None):
    n = C.shape[0]
    ones = np.ones(n).reshape(n,1)
    weights = np.array([1./n]*n)
    if np.any(np.isnan(C)):
        return weights
    if B is None:
        B = ones/n
    B = B.reshape(n,1)
    br = np.append(ones, 0.).reshape(1,n+1)
    X = ones/n
    k = 1./n
    for i in range(20):
        F = np.vstack([C.dot(X)-k*B/X, sum(X)[0]-1.])
        J = np.vstack([np.hstack([C+np.diag((k*B/X**2).flatten()), -B/X]), br])
        D = np.linalg.solve(J, -F)
        X += np.array(D[:-1])
        k += D[-1][0]
        if all(abs(D) < 1e-5):
            return X.flatten()
    raise Exception("REACHED ITERATION LIMIT")
    return weights

def naive_risk_parity(C):
    V = C.diagonal()**-0.5
    return V/sum(V)

def main(args):
    if len(args) < 2:
        """
        # Daily ~1988-2017 [SPX, HYG, TLT, LQD]
        B = np.array([0.6, 0.2, 0.1, 0.1])
        C = np.array([
            [ 2.382e-04,  4.345e-05, -1.667e-05,  3.112e-06],
            [ 4.345e-05,  5.048e-05, -8.001e-06,  1.197e-05],
            [-1.667e-05, -8.001e-06,  1.428e-04,  1.590e-05],
            [ 3.112e-06,  1.197e-05,  1.590e-05,  2.521e-05],
        ])
        n = len(B)
        """
        n = 4
        s = 252**0.5
        # TB, MB, CB
        #B = np.ones(n)
        B = np.array([0.95, .05/3, .05/3, .05/3])
        V = np.array([0.15,0.02, 0.04, 0.05])/s
        R = np.array([
            [1,0,0,0],
            [0,1,0.35,0.25],
            [0,0.35,1,0.2],
            [0,0.25,0.2,1],
        ])
        C = corr_to_cov(R,V)
    else:
        n = int(args[1])
        o = np.random.normal(0, 0.005, size=(n,n))
        B = np.ones(n)/n
        C = np.dot(o, o.T)
    e,v = np.linalg.eigh(C)
    pprint("   ", C, None)
    pprint("EW ", C, np.ones(n)/n)
    pprint("MV ", C, min_var(C))
    pprint("MVo", C, optimizer('MV',C))
    pprint("MVc", C, optimizer('MVc',C))
    pprint("MC ", C, min_corr(C))
    pprint("MCo", C, optimizer('MC',C))
    pprint("MCc", C, optimizer('MCc',C))
    pprint("MDo", C, optimizer('MD',C))
    pprint("MDc", C, optimizer('MDc',C))
    pprint("NR ", C, naive_risk_parity(C))
    pprint("RB ", C, risk_budget(C,B))
    pprint("RBo", C, optimizer('RB',C,B,tol=1e-20,)),#options={'maxiter':1000}))
    pprint("RBc", C, optimizer('RBc',C,B,tol=1e-20,)),#options={'maxiter':1000}))
    pprint("TT ", C, tangency(C))
    pprint("TTo", C, optimizer('TT',C))
    pprint("TTc", C, optimizer('TTc',C))
    pprint("MB ", C, maximum_effective_bets(C, shorting=True))
    pprint("MBc", C, maximum_effective_bets(C, shorting=False))
    return

if __name__ == "__main__":
    sys.exit(main(sys.argv))
