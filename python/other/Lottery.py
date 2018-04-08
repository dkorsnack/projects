#!/bin/python

__all__ = ["PowerBall", "MegaMillions"]

import numpy as np
import sys
from mathutils import nCr

TAXES = 0.6

class Lottery(object):

    def __init__(self, n, k, p, jp):
        cmbn = lambda b,p: p*nCr(k, b)*nCr(n-k, k-b)
        total = p*nCr(n, k)
        # accounting for more than one winner, http://www.circlemud.org/jelson/megamillions/table-explanation.html
        self.exp_jackpot = jp*TAXES*(1-np.exp(-jp/total))
        self.prizes_p = np.array([cmbn(*args) for args in (
            (5,1),(5,p-1),(4,1),(4,p-1),(3,1),(3,p-1),(2,1),(1,1),(0,1)
        )], dtype=float)/total
        
    def expectation(self):
        self.exp = self.prizes.dot(self.prizes_p)/2-1
        self.b_exp = self.prizes_p.dot(
            self.bonus_prizes.dot(self.bonus_prizes_p)
        )/3-1 

class PowerBall(Lottery):

    def __init__(self, jp):
        super(PowerBall, self).__init__(69, 5, 26, jp)
        self.name = "PowerBall"
        self.prizes = np.array([
            self.exp_jackpot, 1000000*TAXES, 50000*TAXES, 100, 100, 7, 7, 4, 4,
        ])
        self.bonus_prizes = np.array([
            [self.exp_jackpot]*4,
            [2000000]*4,
        ]+[
            [self.prizes[i]*m for m in (2,3,4,5)] for i in range(2, len(self.prizes))
        ])
        self.bonus_prizes_p = 1/np.array([1.75, 3.23, 14, 21])
        self.expectation()

class MegaMillions(Lottery):

    def __init__(self, jp):
        super(MegaMillions, self).__init__(70, 5, 25, jp)
        self.name = "MegaMillions"
        self.prizes = np.array([
            self.exp_jackpot, 1000000*TAXES, 10000*TAXES, 500, 200, 10, 10, 4, 2,
        ])
        self.bonus_prizes = np.array([
            [self.exp_jackpot]*4,
        ]+[
            [self.prizes[i]*m for m in (2,3,4,5)] for i in range(1, len(self.prizes))
        ])
        self.bonus_prizes_p = 1/np.array([5.5, 3.75, 5, 2.5])
        self.expectation()

def main(args):
    jp = float(args[1])
    for O in (PowerBall, MegaMillions):
        o = O(jp)
        print("%-15s %i%% %i%%" % (
            o.name, 100*o.exp, 100*o.b_exp,
        ))

if __name__ == "__main__":
    sys.exit(main(sys.argv))
