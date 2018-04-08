# $Id: wwf.py 74 2014-01-08 00:37:10Z korsnack $
#!/bin/python

import sys, datetime
from itertools import permutations

keys = 'abcdefghijklmnopqrstuvwxyz'
values = (1,4,4,2,1,4,3,3,1,10,5,2,4,2,1,4,10,1,1,1,2,5,4,8,3,10)
TILES = {k:v for (k,v) in zip(keys, values)}

f = open("util/wwf", "r")
DICT = set([l[:-1] for l in f.readlines()])
f.close()

def wwf(letters):
    lts, pms = [letters], set()
    for i in range(letters.count(".")):
        lts += [letters.replace(".", t) for t in TILES]
    for l in [lt for lt in lts if "." not in lts]:
        for r in range(2, len(l)+1):
            for p in permutations(l, r):
                pms.add("".join(p))
    results = []
    for word in DICT.intersection(pms):
        ltrs = letters
        points = 0 if len(word) < 7 else 30
        for w in word:
            if w in ltrs:
                ltrs = ltrs.replace(w,"",1)
                points += TILES[w]
            else:
                ltrs = ltrs.replace(".","",1)
        results.append((points, word, ltrs))
    return sorted(results)

def main(args):
    start = datetime.datetime.now()
    res = "\n".join(["%2s %s %s" % (r) for r in wwf(args[1])])
    end = datetime.datetime.now()
    print(res+"\n"+str(end-start))

if __name__ == "__main__":
    sys.exit(main(sys.argv))
