#!/bin/python

from Die import Die
import sys
from LogFile import LogFile

class Backgammon(Die):

    def __init__(self):
        Die.__init__(self)
        self.rolls = [
            (x,y,x+y) if x!=y else (x,2*x,3*x,4*x) for (x,y) in self.prod(2)
        ]

def main(n):
    bg = Backgammon().rolls
    if len(n) < 2:
        return sum([b.count(n[0]) for b in bg])
    else:
        return sum([
            b.count(n[0])+b.count(n[1])
            for b in bg if not (n[0] in b and n[1] in b)
        ])

if __name__ == "__main__":
    LogFile().info(main(list(map(int, sys.argv[1].split(",")))))
