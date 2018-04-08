# $Id$
#!/bin/python

import sys
import time
from LogFile import LogFile
from random import random
from optparse import OptionParser

class RPS(object):

    def __init__(self, weights):
        self.weights = weights
        self.rps = list(zip('RPS', weights))

    def choose(self, n):
        rnd = []
        for i in range(n):
            r = random()
            for (k,v) in self.rps:
                r -= v
                if r < 0:
                    rnd.append(k)
                    break
        return rnd

def parseOptions(args):
    p = OptionParser("")
    p.add_option(
        '-c',
        '--choose',
        dest = 'choose',
        type = int,
        default = 5
    )
    p.add_option(
        '-w',
        '--weights',
        dest = 'weights',
        default = '1,1,1'
    )
    (o,a) = p.parse_args(args)
    return o

def main(args):
    o = parseOptions(args)
    lg = LogFile()
    wts = list(map(int, o.weights.split(",")))
    sm = float(sum(wts))
    R = RPS([w/sm for w in wts])
    rnd = R.choose(o.choose)
    lg.info("".join(rnd))
    return

if __name__ == "__main__":
    sys.exit(main(sys.argv))
