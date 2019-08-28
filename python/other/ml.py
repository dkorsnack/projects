# $Id: ml.py 96 2014-07-20 19:57:56Z korsnack $
#!/bin/python

import sys
from itertools import combinations

def calc(B):
    P = [100/(100+b) if b>0 else b/(b-100) for b in B]
    sm = sum(P)
    Q = [p/sm for p in P]
    F = [(1-q)/q if q<0.5 else q/(q-1) for q in Q]
    for i in range(len(B)):
        print(("%5.2f "*4) % (B[i], P[i], Q[i], F[i]))
    print("%5s %5.2f %5.2f %5s\n" % ("", sm, 1, ""))

def main(args):
    lines = list(map(float, args[1:]))
    for B in combinations(lines, 2):
        calc(B)
    if len(lines) > 2:
        calc(lines)

if __name__ == "__main__":
    sys.exit(main(sys.argv))
