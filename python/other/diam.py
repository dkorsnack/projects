# $Id: diam.py 45 2013-10-06 15:57:20Z korsnack $
#!/bin/python

import sys
from LogFile import LogFile
from optparse import OptionParser

lg = LogFile()
COLOR = {'k':-1, 'j':0, 'i':1, 'h':2, 'g':3, 'f':4, 'e':5, 'd':6}
CLARITY = {'si2':0,'si1':1,'vs2':2,'vs1':3,'vvs2':4,'vvs1':5,'if':6,'fl':7}

def diamond(cr, cl, ct, rd, p):
    # using R for multivariate linear regression
    """
    > diamonds <- read.csv('bluenile.csv', header=TRUE, sep=',')
    > fit <- lm('price~0+carat+color+clarity+round', data=diamonds)
    > summary(fit)
        
    Call:
    lm(formula = "price~0+round+carat+color+clarity", data = diamonds)

    Residuals:
       Min     1Q Median     3Q    Max 
    -11134  -2053   -181   1940   8774 

    Coefficients:
            Estimate Std. Error t value Pr(>|t|)    
    round    5653.99      91.41   61.85   <2e-16 ***
    carat    5862.97      56.24  104.26   <2e-16 ***
    color    1530.65      23.78   64.36   <2e-16 ***
    clarity  1527.82      27.19   56.19   <2e-16 ***
    ---

    Residual standard error: 2869 on 4892 degrees of freedom
    Multiple R-squared:  0.9844,    Adjusted R-squared:  0.9844 
    F-statistic: 7.701e+04 on 4 and 4892 DF,  p-value: < 2.2e-16
    """
    ep = 1e3*(5.7*(rd+cr)+1.5*(COLOR[cl]+CLARITY[ct]))
    return (ep, p-ep, 100*p/ep-100)

def parse_args(args):
    p = OptionParser("")
    p.add_option("-c", "--Carat", type=float, default=2.87)
    p.add_option("-l", "--Color", default="g")
    p.add_option("-y", "--Clarity", default="vs1")
    p.add_option("-p", "--Price", type=int, default=0)
    p.add_option("-r", "--Round", action="store_true")
    o, a = p.parse_args(args)
    return o

def main(args):
    o = parse_args(args)
    lg.info("$%0.2f $%0.2f %0.2f%%" % diamond(
        o.Carat,
		o.Color,
		o.Clarity,
		1 if o.Round else 0,
		o.Price,
    ))

if __name__ == "__main__":
    sys.exit(main(sys.argv))
