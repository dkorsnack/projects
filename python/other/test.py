# $Id: test.py 45 2013-10-06 15:57:20Z korsnack $
#!bin/python

import sys

from FiveDice import *
from Gambler import *
from Supervisor import *

def main(n):
    dkwin = 0
    for i in range(n):
        dk = Gambler(Threes())
        jf = Gambler(Threes())
        S = Supervisor([jf,dk])
        #S = Supervisor([dk,jf])
        S.play()
        if dk.bankroll[-1] >= 200:
            dkwin += 1
    print("dkwin", dkwin)

if __name__ == "__main__":
    sys.exit(main(int(sys.argv[1])))
