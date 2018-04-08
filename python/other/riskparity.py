# $Id: riskparity.py 50 2013-11-16 15:54:11Z korsnack $
#!/bin/python

__all__ = ["solveRiskParity"]

import numpy as np
import random

def solveRiskParity(retseries, risk_wts=None, maxiterations=1000):
    c = np.cov(retsseries).tolist()
    n = len(c)
    eq_wts = [1./n]*n
    if not risk_wts:
        risk_wts = eq_wts
    w = np.array(risk_wts).reshape(n, 1)
    x = (np.ones((1,n))*np.array(eq_wts)).transpose()
    prevguess = [[x[i][0],0] for i in range(len(x))]
    l = 0.5
    badcount = 0
    badcount_lim = 50
    iters_since_last_reset = 0
    iter_lim = 20
    for it in range(maxiterations):
        iters_since_last_reset += 1
        F = np.vstack(
            [np.dot(c, x) - l*w/x, sum(x)[0]-1.]
        )
        J = np.vstack([
            np.hstack([c+np.diag((l*w/x**2).flatten()), -1.*w/x]), 
            [1.]*n +[0.]
        ])
        deltax = np.linalg.solve(J, -F)
        x += np.array(deltax[:-1])
        l += deltax[-1][0]
        norm = np.linalg.norm(deltax)
        if iters_since_last_reset>iter_lim and badcount>badcount_lim:
            iters_since_last_reset = 0
            x = (np.ones((1,n))*np.array([
                random.uniform(0,1) for i in range(n)
            ])).transpose()
        if any(i[0] < 0. or i[0] > 1. for i in x) and badcount<badcount_lim:
            badcount += 1
            iters_since_last_reset = 0
            for i in range(len(x)):
                if x[i][0] <= 0 or x[i][0] >= 1:
                    x[i][0] = random.uniform(
                        0.0, (1./n)*pow(0.5,prevguess[i][1])
                    )
                    prevguess[i][0] = x[i][0]
                    prevguess[i][1] += 1
                else:
                    x[i][0] = prevguess[i][0]
        if norm < n*1.0e-6:
            break
    return x.flatten().tolist()
