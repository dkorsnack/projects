# $Id: Midnight.py 45 2013-10-06 15:57:20Z korsnack $
#!/bin/python

from Die import Die
from Gambler import RuleSet

# Qualification Probabilities
"""
P(#,#) = P(#s Qualified --> #s Qualified)
P(0,0) = (5/6)^5 = 3125/7776
P(0,1) = (5^5-4^5)/6^5 = 2101/7776
P(0,2) = (5^5-4^5-4^5+3^5)/6^5 = 1320/7776
P(0,3) = 1-P(0,0)-P(0,1)-P(0,2) = 1230/7776
P(1,1) = (5/6)^4 = 625/1296
P(1,2) = (5^4-4^4)/6^4 = 369/1296
P(1,3) = 1-P(1,1)-P(1,2) = 302/1296
P(2,2) = (5/6)^3 = 125/216
P(2,3) = 1-P(2,2) = 91/216

import numpy as np
np.set_printoptions(precision = 5)

TM = np.matrix([
[3125./7776, 2101./7776, 1320./7776, 1230./7776],
[0., 625./1296, 369./1296, 302./1296],
[0., 0., 125./216, 91./216],
[0., 0., 0., 1.],
])

TM**1
    0        1        2        3
0 [ 0.40188  0.27019  0.16975  0.15818]
1 [ 0.       0.48225  0.28472  0.23302]
2 [ 0.       0.       0.5787   0.4213 ]
3 [ 0.       0.       0.       1.     ]

TM**3
    0        1        2        3
0 [ 0.06491  0.15884  0.23628  0.53998]
1 [ 0.       0.11216  0.24103  0.64681]
2 [ 0.       0.       0.19381  0.80619]
3 [ 0.       0.       0.       1.     ]
"""
# Game Expectations
"""
d = [1,2,3,4,5,6]
dd = [sorted([i,j], reverse=True) for i in d for j in d]
ddd = [sorted([i,j,k], reverse=True) for i in d for j in d for k in d]
dddd = [sorted([i,j,k,l], reverse=True) for i in d for j in d for k in d for l in d]
ddddd = [sorted([i,j,k,l,m], reverse=True) for i in d for j in d for k in d for l in d for m in d]

<d> = sum(d)/float(len(d)) = 21/6. = 3.5
<d,d> = sum([max(i, 3.5) for i in d])/len(d) = 25.5/6 = 4.25
<dd> = sum([i+j for i,j in dd])/len(dd) = 252./36 = 7
<dd|s> = sum([max(i+j, i+3.5, 7) for i,j in dd])/len(dd) = 306./36 = 8.5

q03 = [q for q in ddddd if 6 in q and 5 in q and 4 in q]
for x in q03: x.remove(6); x.remove(5); x.remove(4)
<0,3|t> = sum([i+j for i,j in q03])/float(len(q03)) = 7440/1230. = 6.04878
<0,3|s> = sum([max(i+j, i+3.5, 7) for i,j in q03])/len(q03) = 9870./1230 = 8.02439
<0,3|f> = sum([max(i+j, i+4.25, 8.5) for i,j in q03])/len(q03) = 11155./1230 = 9.06910

q13 = [q for q in dddd if 5 in q and 4 in q]
for x in q13: x.remove(5); x.remove(4)
<1,3|t> = sum([i+j for i,j in q13])/float(len(q13)) = 1998/302. = 6.61589
<1,3|s> = sum([max(i+j, i+3.5, 7) for i,j in q13])/len(q13) = 2538./302 = 8.40397

q23 = [q for q in ddd if 4 in q]
for x in q23: x.remove(4)
<2,3|t> = sum([i+j for i,j in q23])/float(len(q23)) = 629./91 = 6.91209
<2,3|s> = sum([max(i+j, i+3.5, 7) for i,j in q23])/len(q23) = 777.5/91 = 8.54396

<0,3> = 9.06910*0.15818 + 8.02439*(0.40188*0.15818) + 6.04878*(0.40188**2*0.15818) = 2.09919
<1,3> = 8.40397*(0.27019*0.23302) + 6.61589*(0.40188*0.27019*0.23302+0.27019*0.48225*0.23302) = 0.89738
<2,3> = 8.54396*(0.16975*0.4213) + \
        6.91209*(0.40188*0.16975*0.4213 + 0.16975*0.5787*0.4213 + 0.27019*0.28472*0.4213) = 1.31977

<G> = 2.09919 + 0.89738 + 1.31977 = 4.31634
"""

H = {12:6, 11:6, 10:5, 9:5, 8:4, 7:4}

class Midnight(Die):
    def __init__(self, RS = RuleSet()):
        Die.__init__(self)
        self.RS = RS
        self.evaluate = max
        self.minscore, self.maxscore = 0, 12

    def play(self, h = None):
        if not h:
            h = self.minscore
        score = 0
        dice = [9,9,9,9,9]
        si, fi, fo = False, False, False
        for r in range(1,4):
            if not dice:
                break
            dice = sorted(self.roll(len(dice)), reverse=True)
            if not si and dice.count(6):
                dice.remove(6)
                si = True
            if si and not fi and dice.count(5):
                dice.remove(5)
                fi = True
            if si and fi and not fo and dice.count(4):
                dice.remove(4)
                fo = True
            if si and fi and fo:
                if r == 3:
                    score += sum(dice)
                    break
                if self.RS.keep:
                    n = H.get(h, h)
                    p = sum([d for d in dice if (d in self.RS.keep and d >= n)])
                    dice = [d for d in dice if not (d in self.RS.keep and d >= n)]
                if self.RS.optimal:
                    n = max(6-r, H.get(h, h))
                    p = sum([d for d in dice if d >= n])
                    dice = [d for d in dice if d < n]
                score += p
                h -= p
        return score
