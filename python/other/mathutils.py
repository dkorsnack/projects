# $Id: mathutils.py 68 2014-01-04 17:51:05Z korsnack $
#!/bin/python

from math import log, factorial

__all__ = [
    "product",
    "nPr",
    "nCr",
    "binom",
    "mean",
    "variance",
    "skew",
    "kurtosis",
    "moments",
]

def product(lst):
    p = 1
    for l in lst:
        p *= l
    return p

def nPr(n, k):
    return product(range(n-k+1, n+1))

def nCr(n, k):
    return nPr(n,k)/factorial(k)

def binom(n, p, k, cdf=False):
    if not cdf:
        return nCr(n,k)*p**k*(1-p)**(n-k)
    else:
        c = 0
        for i in range(k+1):
            c += binom(n, p, i)
        return c

def mean(pv, rv):
    return sum([p*r for (p,r) in zip(pv, rv)])

def variance(pv, rv):
    m = mean(pv, rv)
    return sum([p*(r-m)**2 for (r,p) in zip(rv, pv)])**0.5

def skew(pv, rv):
    m = mean(pv,rv)
    v = variance(pv, rv)
    return sum([p*((r-m)/v)**3 for (r, p) in zip(rv, pv)])

def kurtosis(pv, rv):
    m = mean(pv,rv)
    v = variance(pv, rv)
    return sum([p*((r-m)/v)**4 for (r, p) in zip(rv, pv)])

def moments(pv, rv):
    return (mean(pv, rv), variance(pv, rv), skew(pv, rv), kurtosis(pv, rv))

def derivative(f, h=1e-10):
    """
    >>> def g(x): return x*x
    >>> dg = deriv(g)
    >>> [g(x) for x in range(10)]
    [0, 1, 4, 9, 16, 25, 36, 49, 64, 81]
    >>> [int(dg(x)) for x in range(10)]
    [0, 2, 4, 6, 8, 10, 12, 14, 16, 18]
    """
    def df(x):
        return (f(x+h)-f(x))/h
    return df

def integral(f, h=1e-10):
    def intf(b, a=0):
        sm = 0
        x = a
        while x <= b:
            sm += h*(f(x+h)+f(x))/2.
            x += h
        return sm
    return intf

#TODO: GamblersRuin class similar to TVM

# given w, l and pW, what is P(Bn(-L, W) = W) --> pB?
def p_ruin(w, l, pW, b = 1, pD = 0):
    W = float(w) / b
    L = float(l) / b
    pL = 1 - pW - pD
    if pW == pL:
        return float(L) / (L + W)
    else:
        return float((pL/pW)**L-1.)/float((pL/pW)**(L+W)-1.)

# given w, l and pW, what is E[N(-L, W)] --> eN?
def n_ruin(w, l, pW, b = 1, pD = 0):
    W = float(w) / b
    L = float(l) / b
    pL = 1. - pW - pD
    if pW == pL: return (W * L) / (pW + pL)
    else:
        pB = p_ruin(w, l, pW, b, pD)
        return (W + L) / (pL - pW) * (L / float(L + W) - pB)

# given w, l and pW, what is pB and eN?
def ruin(w, l, pW, b = 1, pD = 0):
    return (p_ruin(w, l, pW, b, pD), n_ruin(w, l, pW, b, pD))

# given pB and l, what is w?
def niur_p(pB, l, pW, b = 1, pD = 0):
    L = float(l) / b
    pL = 1. - pW - pD
    if pW == pL:
        w = b * (L / pB - L)
        return (w, n_ruin(w, l, pB, b, pD))
    else:
        w = b*(log(((pL/pW)**L-1)/pB+1)/log(pL/pW)-L)
        return (w, n_ruin(w, l, pB, b, pD))

#===================
# betting

# optimal bet
def kbet(pv, rv):
    ll = 1e4
    eq = "+".join(["%s*log(1+%s*%s)" % (p, '%s', r) for (r, p) in zip(rv, pv)])
    minf = -1. / max(rv) if max(rv) != 0 else 0
    maxf = -1. / min(rv) if max(rv) != 0 else 0
    ln = len(pv)
    return max([(eval(eq % tuple([f/ll]*ln)), f/ll)
               for f in range(int(ll*minf), int(ll*maxf), 1)])

# optimal bet (calced using functions; a bit slower)
def kBET(pv, rv):
    ll = 1e4
    string = "+".join(["%s*(1+x*%s)" % (p, r) for (r, p) in zip(rv, pv)])
    def gMax(x): return eval(string)
    dg = deriv(gMax)
    minf = -1. / max(rv) if max(rv) != 0 else 0
    maxf = -1. / min(rv) if max(rv) != 0 else 0
    brute = [((r/ll), dg(r/ll)) for r in range(int(ll*minf), int(ll*maxf))]
    fs = [f for (f, g) in brute if g < 0.00001 and g > -0.00001]
    fstar = sum(fs) / len(fs)
    return (gMax(fstar), fstar)

# optimal bet, simultaneous wagers
def qq(k, data): return sum([p for (p, a) in data[:k]])

def bb(k, data): return sum([1./(a+1) for (p, a) in data[:k]])

def ww(k, data):
    return (1.-qq(k, data))/(1.-bb(k, data)) if bb(k, data) != 1 else 0

def kbets(prbV, payV):
    ln = len(prbV)
    if max([p * (a + 1) for (p, a) in zip(prbV, payV)]) <= 1:
        return [(0, 0)]
    else:
        data = sorted(zip(prbV, payV), reverse = True)
        kVect = [qq(k, data)+(1.-bb(k, data))*(data[k][1]+1.)*data[k][0]
                 for k in range(ln)]
        k0 = max([i + 1 if kVect[i] > 1 else 0 for i in range(ln)])
        wk0 = ww(k0, data)
        fVect = [data[j][0]-wk0/(1.+data[j][1]) if j <= k0-1 else 0
                 for j in range(ln)]
        m = sum([data[i][0]*log(data[i][0]*(data[i][1] + 1))
                 for i in range(k0)])
        mu = m if wk0 == 0 else m+(1-qq(k0, data))*log(wk0)
        v = sum([data[i][0]*log(data[i][0]*(data[i][1] + 1))**2
                 for i in range(k0)])
        var = v-mu**2 if wk0 == 0 else v+(1-qq(k0, data))*log(wk0)**2-mu**2
        return [(mu, var ** 0.5)] + \
               [(d, f) for (d, f) in zip(data, fVect) if f > 0]

def factor(n): return [i for i in fctr(n)]

def fctr(n):
    p = 2
    lmt = n**0.5
    while p <= lmt:
        if n % p == 0:
            yield p
            n /= p
            lmt = n**0.5
        else:
            p += 1
    if n > 1:
        yield n
