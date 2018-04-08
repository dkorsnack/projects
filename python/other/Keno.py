# $Id: Keno.py 65 2013-12-12 00:48:31Z korsnack $
#!/bin/python

import sys
from random import random, shuffle, sample
from mathutils import nCr, mean, variance
from optparse import OptionParser

class Keno(object):

    def __init__(self, state = "CA", taxes = 0.4):
        self.PAY_TABLE = {
            'CA': {
                1 : {1:2},
                2 : {2:9},
                3 : {3:26, 2:2},
                4 : {4:75, 3:5, 2:1},
                5 : {5:450, 4:16, 3:2},
                6 : {6:900, 5:60, 4:5, 3:1},
                7 : {7:2000, 6:150, 5:10, 4:3, 3:1},
                8 : {8:10000, 7:575, 6:75, 5:10, 0:1},
                9 : {9:30000, 8:2750, 7:125, 6:25, 5:5, 0:1},
                10: {10:100000, 9:5000, 8:575, 7:40, 6:15, 5:2, 0:3},
            },
            'MA': {
                1 : {1:2.5},
                2 : {2:5, 1:1},
                3 : {3:25, 2:2.5},
                4 : {4:100, 3:4, 2:1},
                5 : {5:450, 4:20, 3:2},
                6 : {6:1600, 5:50, 4:7, 3:1},
                7 : {7:5000, 6:100, 5:20, 4:3, 3:1},
                8 : {8:15000, 7:1000, 6:50, 5:10, 4:2},
                9 : {9:40000, 8:4000, 7:200, 6:25, 5:5, 4:1},
                10: {10:100000, 9:10000, 8:500, 7:80, 6:20, 5:2, 0:2},
                11: {11:500000, 10:15000, 9:1500, 8:250, 7:50, 6:10, 5:1, 0:2},
                12: {12:1000000, 11:25000, 10:2500, 9:1000, 8:150, 7:25, 6:5, 0:4},
            },
            'OH': {
                1 : {1:2},
                2 : {2:11},
                3 : {3:27, 2:2},
                4 : {4:72, 3:5, 2:1},
                5 : {5:410, 4:18, 3:2},
                6 : {6:1100, 5:57, 4:7, 3:1},
                7 : {7:2000, 6:100, 5:11, 4:5, 3:1},
                8 : {8:10000, 7:300, 6:50, 5:15, 4:2},
                9 : {9:25000, 8:2000, 7:100, 6:20, 5:5, 4:2},
                10: {10:100000, 9:5000, 8:500, 7:50, 6:10, 5:2, 0:5}
            }
        }[state]
        self.BONUS_TABLE = {
            'MA': {1: 1/1.75, 3: 1/3., 4: 1/15., 5: 1/40., 10: 1/234.},
            'OH': {1: 1/2.3, 2: 1/2.5, 3: 1/16., 4: 1/16., 5: 1/27., 10: 1/80.},
            'CA': {1:1},
        }[state]
        self.N = list(range(1,81))
        self.taxes = taxes

    def kprb(self, spt, n):
        return float(nCr(spt,n)*nCr(80-spt,20-n))/nCr(80,20)

    def phit(self, spt):
        return sum([self.kprb(spt, n) for n in self.PAY_TABLE[spt]])

    def pdf(self, spt, bonus = False):
        x = 2. if bonus else 1.
        items = list(self.BONUS_TABLE.items()) if bonus else [(1,1)]
        pdf = []
        for n in range(spt+1):
            for (m,p) in items:
                t = self.PAY_TABLE[spt].get(n, 0)*m
                pdf.append((
                    p*self.kprb(spt,n),
                    t/x-1 if t < 5000 else (1-self.taxes)*t/x-1
                ))
        return pdf

    def deal(self, n = 20):
        shuffle(self.N)
        return self.N[:n]

    def hand(self, spt, bonus = False):
        x = 0
        r = random()
        w = self.PAY_TABLE[spt].get(
            len(set(self.deal(spt)) & set(self.deal())),
            0
        )
        if bonus:
            for (k,v) in list(self.BONUS_TABLE.items()):
                x += v
                if r < x:
                    return w*k-2.
        else:
            return w-1.

    @classmethod
    def choose(cls, n):
        print(" ".join(map(str, sorted(sample(list(range(1,81)), n))))) 

    def __str__(self):
        spots = list(range(1, len(self.PAY_TABLE)+1))
        prnt = ["SPT   P(Hit)     Mean    Stdev"]
        for s in spots:
            for b in (False, True):
                pw = self.phit(s)
                pdf = self.pdf(s, b)
                prnt.append("%2s%s %8.5f %8.5f %8.5f" % (
                    s,
                    "*" if b else " ",
                    pw,
                    mean(*list(zip(*pdf))),
                    variance(*list(zip(*pdf)))
                ))
        return "\n".join(prnt)

def parse_args(args):
    p = OptionParser("")
    p.add_option(
        "-s",
        "--state",
        default = 'CA'
    )
    p.add_option(
        "-t",
        "--taxes",
        type = float,
        default = 0.4
    )
    p.add_option(
        "-c",
        "--choose",
        type = int,
        default = 0,
    )
    (o,a) = p.parse_args(args)
    return o

def main(args):
    o = parse_args(args)
    print(Keno(o.state, o.taxes))
    if o.choose:
        Keno.choose(o.choose)

if __name__ == "__main__":
    main(sys.argv)
