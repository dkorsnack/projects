# $Id: jof.py 45 2013-10-06 15:57:20Z korsnack $
#!/bin/python

"""
simplified jam or fold poker:
two players heads up given uniformly randomly
distributed "hands" in [0,1] where highest number wins

s = stack size; number of big blinds
x = P(Attacker jam)
y = P(Defender call)
x > y

<Attacker, jam> = y*(-s)+(1-y)*(+1)
<Attacker, fold> = -0.5
y = 3/(2*s+2)

<Defender, call> = (1-y/x)*(s)+(y/x)*(-s)
<Defender, fold> = -1
x = 2*s*y/(s+1)
x = 3*s/(s+1)**2

since no holdem heads up match has less than 30% equity,
substiture s/3 for a more holdem-like result

x = 9*s/(s+3)**2
y = 9/(2*s+6)
"""

import sys
from LogFile import LogFile
from Cards import Holdem

def main(args):

    with open("holdem.csv", 'r') as fh:
        data = [l.split(",")[0:2] for l in fh.readlines()]

    headsup = sorted([(float(v),k) for (k,v) in data], reverse=True)
    H = Holdem()
    cdf = []; c = 0
    for (v, k) in headsup:
        q = H.pdf[k]
        c += q
        cdf.append((k, c))

    s = float(args[1])
    x = 9.*s/(s+3)**2
    y = 9./(2*s+6)
    hx = [k for (k, v) in cdf if v <= x]
    hy = [k for (k, v) in cdf if v <= y]
    printstr = "%-3s"+" %-3s"*12+"\n"
    LogFile().info("\n".join([
        "\nAttacker: %0.5f" % (x,),
        printstr % tuple(hx[-13:]),
        H.__str__([x if x in hx else "." for x in H.startinghands]),
        "\nDefender: %0.5f" % (y,),
        printstr % tuple(hy[-13:]),
        H.__str__([y if y in hy else "." for y in H.startinghands])
    ]))

if __name__ == "__main__":
    sys.exit(main(sys.argv))
