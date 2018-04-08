# $Id: Regression.py 34019 2014-01-16 21:59:16Z korsnack $
#!/bin/python



__all__ = ['Regression']

from scipy import c_, ones, dot, stats, diff
from scipy.linalg import solve, inv
from numpy import array, log, pi, square, diagonal, diag
from numpy.random import randn, seed

"""
source: http://wiki.scipy.org/Cookbook/OLS
original author: Vincent Nijs at Northwestern University
"""

class Regression(object):

    def __init__(self, dependent, independents, method="OLS"):
        self.y = dependent
        l,w = independents.shape
        self.x = c_[ones(l), independents]
        self.x_varnm = ['Constant']+['x%i' % (i,) for i in range(w)]
        self.estimate(method)

    def estimate(self, method="OLS"):
        self.xx = dot(self.x.T,self.x)
        self.inv_xx = inv(self.xx)
        xy = dot(self.x.T,self.y)
        self.b = solve(self.xx,xy)
        self.e = self.y - dot(self.x,self.b)

        if method == "FGLS":
            OHI = diag(1/self.e**2)
            beta1 = solve(
                dot(dot(self.x.T,OHI),self.x),
                dot(dot(self.x.T,OHI),self.y)
            )
            residue2 = self.y - dot(self.x,beta1)
            OHI2 = diag(1/residue2**2)
            self.b = solve(
                dot(dot(self.x.T,OHI2),self.x),
                dot(dot(self.x.T,OHI2),self.y)
            )

        self.nobs = self.y.shape[0]
        self.ncoef = self.x.shape[1]
        self.df_e = self.nobs - self.ncoef
        self.df_r = self.ncoef - 1

        self.e = self.y - dot(self.x,self.b)
        self.sse = dot(self.e,self.e)/self.df_e
        self.se = diagonal(self.sse*self.inv_xx)**0.5
        self.t = self.b / self.se
        self.p = (1-stats.t.cdf(abs(self.t), self.df_e)) * 2

        self.R2 = 1 - self.e.var()/self.y.var()
        self.R2adj = 1-(1-self.R2)*((self.nobs-1)/(self.nobs-self.ncoef))

        self.F = (self.R2/self.df_r) / ((1-self.R2)/self.df_e)
        self.Fpv = 1-stats.f.cdf(self.F, self.df_r, self.df_e)
            

    def dw(self):
        de = diff(self.e,1)
        dw = dot(de,de) / dot(self.e,self.e);
        return dw

    def omni(self):
        return stats.normaltest(self.e) 
    
    def JB(self):
        skew = stats.skew(self.e) 
        kurtosis = 3 + stats.kurtosis(self.e) 
        JB = (self.nobs/6) * (square(skew) + (1/4)*square(kurtosis-3))
        JBpv = 1-stats.chi2.cdf(JB,2);
        return JB, JBpv, skew, kurtosis

    def ll(self):
        ll = -(self.nobs*1/2)*(1+log(2*pi))-(self.nobs/2)*log(
            dot(self.e,self.e)/self.nobs
        )
        aic = -2*ll/self.nobs + (2*self.ncoef/self.nobs)
        bic = -2*ll/self.nobs + (self.ncoef*log(self.nobs))/self.nobs
        return ll, aic, bic
    
    def summary(self, d_label=None, i_labels=None):
        ll, aic, bic = self.ll()
        JB, JBpv, skew, kurtosis = self.JB()
        omni, omnipv = self.omni()
        names = ['Constant']+i_labels if i_labels else self.x_varnm
        line = "="*79
        print("\n"+"\n".join([
line,
"Method: Least Squares",
"Dependent Variable: %s" % (d_label if d_label else 'y',),
'Observations: %i' % (self.nobs,),
'Variables: %i' % (self.ncoef,), 
line,
'%-15s %15s %15s %15s %15s' % (
    'Variable','Coefficient','Std. Error','T-Statistic','Prob(T-Stat)'
),
line,
"\n".join(['%-15s %15.6f %15.6f %15.6f %15.6f' % (
    names[i], self.b[i], self.se[i], self.t[i], self.p[i]
    ) for i in range(len(names))
]), 
line,
"%-41s%-38s" % ('Model Statistics','Residual Statistics'),
line,
'R-squared           %18.6f   Durbin-Watson stat  %18.6f' % (self.R2, self.dw()),
'Adjusted R-squared  %18.6f   Omnibus stat        %18.6f' % (self.R2adj, omni),
'F-statistic         %18.6f   Prob(Omnibus stat)  %18.6f' % (self.F, omnipv),
'Prob (F-statistic)  %18.6f   JB stat             %18.6f' % (self.Fpv, JB),
'Log likelihood      %18.6f   Prob(JB)            %18.6f' % (ll, JBpv),
'AIC criterion       %18.6f   Skew                %18.6f' % (aic, skew),
'BIC criterion       %18.6f   Kurtosis            %18.6f' % (bic, kurtosis),
line,
        ])+"\n")
