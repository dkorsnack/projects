# $Id: minimumtorsion.py 33644 2013-11-14 16:45:55Z korsnack $
#!/bin/python

__all__ = ["effective_bets", "torsion", "maximum_effective_bets"]

import sys
import numpy as np
from scipy import linalg, random

def effective_bets(Sigma, weights=None, t=None, model='minimum-torsion'):
    n = len(Sigma)
    if np.any(np.isnan(Sigma)):
        return None
    if weights is None:
        weights = np.array([1./n]*n)
    if t is None:
        t = np.linalg.eig(Sigma)[1].T
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
    max_iter=30
):
    n = len(Sigma)
    if model == 'pca':
        evals, evecs = np.linalg.eig(Sigma)
        t = evecs.T
    elif model == 'minimum-torsion':
        sigma = np.diag(Sigma)**0.5
        isigma = np.diag(1./sigma)
        Rho = np.dot(isigma, Sigma).dot(isigma) 
        c = linalg.sqrtm(Rho)
        if method == "exact":
            d = np.identity(n)
            f = np.zeros(max_iter)
            for i in range(max_iter):
                U = np.dot(d.dot(Rho), d)
                u = linalg.sqrtm(U)
                q = np.linalg.solve(u, d.dot(c))
                d = np.diag(np.diag(q.dot(c)))
                pi = d.dot(q)
                f[i] = np.linalg.norm(c-pi)
                t = np.dot(np.diag(sigma), pi).dot(
                    np.linalg.solve(c, isigma))
                if i+1 == max_iter:
                    raise Exception("Reached Maximum Iteration")
                    break
                if i and abs(1-f[i-1]/f[i]) < 1e-6*n:
                    break
        elif method == "approximate":
            t = np.diag(sigma).dot(np.linalg.solve(c,isigma))
        else:
            raise Exception("Method %s is not supported." % method + \
                " The available options are exact and approximate." 
            )
    else:
        raise Exception("Model %s is not supported." % model + \
            " The available options are pca and minimum-torsion" 
        )
    return t.real

def maximum_effective_bets(
    Sigma,
    model="minimum-torsion",
    method="exact",
    budget=None,
    shorting="allowed",
    max_iter=30
):
    """
    Returns the portfolio weight vector (for the original factors) 
    which maximizes the effective number of bets
    """
    n = len(Sigma)
    if np.any(np.isnan(Sigma)):
        return np.array([1./n]*n)
    if budget == None:
        budget = np.ones(len(Sigma))
    t = torsion(Sigma, model=model, method=method, max_iter=max_iter)
    b = np.diag(budget).dot(1/np.sqrt(np.diag(np.dot(t,Sigma).dot(t.T))))
    if shorting != "allowed" and np.any(t.T.dot(b) < 0):
        d = np.sqrt(np.diag(t.dot(Sigma).dot(t.T)))
        c = b * d
        def E(c):
            return np.sum( - c**2 * np.log(c**2))
        def normalize(c):
            return c / np.sqrt(np.sum(c**2))
        A = t.T.dot(np.diag(1/d))
        def project(c):
            return np.linalg.solve(A,A.dot(c)*(A.dot(c)>0))
        def gradE(c):
            return -2*c*(np.log(c**2)+1) 
        c = normalize(np.linalg.solve(A,np.ones(n)))
        for exponent in reversed(range(-20,1)):
            delta = 2.0**(exponent)
            cnew = project(normalize(c + delta * gradE(c)))
            cntr = 1
            while E(cnew) > E(c) and cntr <= 100:
                c = cnew
                cnew = project(normalize(c + delta * gradE(c)))
                cntr += 1
        b = c/d
    weights = t.T.dot(np.diag(budget).dot(b))
    if shorting != "allowed":
        weights = weights * (weights > 0)
    return np.real(weights*(np.abs(weights) > 1e-10)/np.sum(weights))

def random_example(n):
    R = random.rand(n,n)*2-1
    Sigma = R.dot(R.T)
    sigma = np.diag(Sigma)**0.5
    isigma = np.diag(1./sigma)
    Rho = np.dot(isigma, Sigma).dot(isigma)
    meb = maximum_effective_bets(Sigma)
    print("\n\n".join(map(str, [Sigma, Rho, meb])))

def simple_example():
    Sigma = np.array([
        [ 0.01, 0.02,-0.03],
        [ 0.02, 0.04,-0.06],
        [-0.03,-0.06, 0.09],
    ])
    sigma = np.diag(Sigma)**0.5
    isigma = np.diag(1./sigma)
    Rho = np.dot(isigma, Sigma).dot(isigma)
    print(sigma)
    print(Rho)
    print(maximum_effective_bets(Sigma)) 

def loop_example():
    weights = np.ones(2)/2.
    for i in range(-6,7):
        cov = i/100.+1e-10 if i<0 else i/100.-1e-10 
        Sigma = np.array([
            [0.040,   cov],
            [  cov, 0.090],
        ])
        pca = torsion(Sigma, model="pca")
        amt = torsion(Sigma, method="approximate")
        emt = torsion(Sigma)
        enb_pca = effective_bets(Sigma, weights, pca, model="pca")
        enb_amt = effective_bets(Sigma, weights, amt)
        enb_emt = effective_bets(Sigma, weights, emt)
        print("%8.5f "*4 % (cov, enb_pca, enb_amt, enb_emt))

def backtest_example():
    from lib.config import STRATEGIES, ROLL_KWARGS
    from lib.tslib.Backtest import Backtest
    from lib.tslib.Calendar import Calendar
    from lib.tslib.Curve import Curve
    from lib.tslib.Future import Future
    from lib.tslib.WeightedPortfolio import WeightedPortfolio
    cal = Calendar("US").dates()
    B = Backtest(path=STRATEGIES['RBS']).exposure()
    underliers = set([
        k.split("-FUT-")[0] for k in B.rotate().keys() if "-FUT-" in k
    ])
    synthmap = {u: Future.splice(u, **ROLL_KWARGS[u]) for u in underliers}
    data = []
    for (dt, wp) in B.series():
        WP = WeightedPortfolio(dict([
            (synthmap[k.underlier.dn] if issubclass(type(k), Future) else k,v)
            for (k,v) in wp.items() if v > 1e-6
        ]))
        data.append((
            len(WP.keys()),
            WP.enb(dt0=cal[cal.index(dt)-63], dt1=dt, model="pca"),
            WP.enb(dt0=cal[cal.index(dt)-63], dt1=dt, method='approximate'),
            WP.enb(dt0=cal[cal.index(dt)-63], dt1=dt),
        ))
    curves = [Curve(B.dts, z) for z in zip(*data)]
    curves[0].plot(
        "backtest_torsion.png",
        compare=curves[1:],
        plot_title = "Backtest Results",
        legend=["Assets Held", "PCA", "Approx MLT", "Exact MLT"],
    )
    return 0

if __name__ == "__main__":
    sys.exit(random_example(int(sys.argv[1])))
