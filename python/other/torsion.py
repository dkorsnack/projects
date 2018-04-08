# $Id: torsion.py 81 2014-01-23 01:12:33Z korsnack $
#!/bin/python

__all__ = ["effectiveBets", "torsion", "maximumEffectiveBets"]

import sys
import numpy as np
from scipy import linalg as splinalg

def effectiveBets(Sigma, weights, t, model='minimum-torsion'):
    n = len(Sigma)
    if type(weights) == list:
        weights = np.array(weights)
    if model == 'minimum-torsion':
        num = np.linalg.solve(t.T, weights)*np.dot(t.dot(Sigma), weights)
    else:
        num = t.dot(weights)*np.dot(t.dot(Sigma), weights)
    p = num/np.dot(weights.dot(Sigma), weights)
    return np.exp(-sum([0 if x==0 else x*np.log(x) for x in p]).real)

def torsion(
    Sigma,
    model='minimum-torsion',
    method='exact',
    max_iter=20
):
    n = len(Sigma)
    if model == 'pca':
        evals, evecs = np.linalg.eig(Sigma)
        t = evecs.T
    elif model == 'minimum-torsion':
        sigma = np.diag(Sigma)**0.5
        isigma = np.diag(1./sigma)
        Rho = np.dot(isigma, Sigma).dot(isigma) 
        c = splinalg.sqrtm(Rho)
        if method == "exact":
            d = np.identity(n)
            f = np.zeros(max_iter)
            for i in range(max_iter):
                U = np.dot(d.dot(Rho), d)
                u = splinalg.sqrtm(U)
                q = np.linalg.solve(u, d.dot(c))
                d = np.diag(np.diag(q.dot(c)))
                pi = d.dot(q)
                f[i] = np.linalg.norm(c-pi)
                t = np.dot(np.diag(sigma), pi).dot(
                    np.linalg.solve(c, isigma))
                if i+1 == max_iter:
                    print("Reached Maximum Iteration")
                    break
                if i and abs(1-f[i-1]/f[i]) < 1e-6*n:
                    break
        elif method == "approximate":
            t = np.diag(sigma).dot(np.linalg.solve(c,isigma))
    return t

def maximumEffectiveBets(
    Sigma,
    model="minimum-torsion",
    method="exact",
    max_iter=20
):
    t = torsion(Sigma, model=model, method=method, max_iter=max_iter)
    weights = t.T.dot(1/np.sqrt(np.diag(np.dot(t,Sigma).dot(t.T))))
    return np.real(weights/np.sum(weights))

def demo():
    Sigma = np.array([
        [0.04, 0.01, 0.03],
        [0.01, 0.09, 0.04],
        [0.03, 0.04, 0.12]
    ])
    wts = maximumEffectiveBets(Sigma)
    print(wts)
    print(effectiveBets(Sigma, wts, torsion(Sigma)))

if __name__ == "__main__":
    sys.exit(demo())
