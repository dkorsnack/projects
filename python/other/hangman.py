# $Id: hangman.py 45 2013-10-06 15:57:20Z korsnack $
#!/bin/python

import os, sys, datetime

ABC = "abcdefghijklmnopqrstuvwxyz"
#LOC = "/usr/share/dict/wwf"
LOC = "/usr/share/dict/words"
FMT = "%-5s %s"

def fetch(args):
    known = args[1].replace(".", "[a-z]")
    used = args[1].replace(".", "")
    if len(args) > 2:
        used += args[2]
    if used:
        known = known.replace("[a-z]", "[^%s]" % (used))
    grep = list(set(os.popen("grep '^%s$' %s" % (known, LOC)).readlines()))
    total = len(grep)
    print(FMT % (total, " "))
    if len(args) > 3 or total < 11:
        print("".join(sorted(grep))[:-1])
    answer = []
    for a in set(ABC)-set(used):
        count = len([w for w in grep if a in w])
        if count:
            answer.append((count, a))
    return sorted(answer, reverse=True)

def main(args):
    start = datetime.datetime.now()
    result = "\n".join([FMT % f for f in fetch(args)])
    end = datetime.datetime.now()
    print(result+"\n"+str(end-start))

if __name__ == "__main__":
    sys.exit(main(sys.argv))
