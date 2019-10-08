import sys
from random import random
from matplotlib import pyplot as plt

def game(p):
    return 1 if random() <= p else -1

def series(n, plot=False):
    p = 0.52
    v = 0.01
    f = (2*p-1)/v
    b = 100
    k = 100
    br = [b]
    kr = [k]
    for i in range(n):
         g = game(p)
         b += 300*v*g if b>0 else 0
         br.append(b)
         k += k*f*v*g if k>0 else 0
         kr.append(k)
    if plot:
        plt.plot(list(zip(br, kr)))
        plt.axhline(0, color='k')
        plt.grid(True)
        plt.savefig('out.png')
    return (b,k) 

def main(args):
    n = int(args[1])
    series(n, True)
    return
    """
    m = int(args[2])
    results = list(zip(*[
        series(n) for i in range(m)
    ]))
    print(min(results[0]), min(results[1]))
    plt.hist(results, bins=100, histtype='stepfilled', alpha=0.5)
    plt.savefig('out.png')
    return
    """
        

if __name__ == "__main__":
    sys.exit(main(sys.argv))
