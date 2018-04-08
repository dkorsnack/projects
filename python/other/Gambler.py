# $Id: Gambler.py 45 2013-10-06 15:57:20Z korsnack $
#!/bin/python

import datetime
import numpy as np
from LogFile import LogFile

class RuleSet(object):
    def __init__(
        self,
        keep = [],
        qualify = False,
        optimal = True
    ):
        self.keep = keep
        self.qualify = False
        self.optimal = True

class Gambler(object):
    def __init__(
        self,
        game,
        wallet = 100,
        name = ''
    ):
        if not name:
            now = datetime.datetime.now()
            name = '%i%i%i%i' % (
                now.hour,
                now.minute,
                now.second,
                now.microsecond
            )
        self.lg = LogFile()
        self.game = game
        self.wallet = wallet
        self.scores = []
        self.name = name
        self.bankroll = [self.wallet]

    def play(self, n):
        start = datetime.datetime.now()
        for i in range(n):
            self.scores.append(self.game.play())
        stop = datetime.datetime.now()
        self.lg.info(stop-start)

    def distribution(self, l = None):
        import scipy.stats as stats
        head = " X     PDF     CDF\n"
        cdf = 0
        for i in range(self.game.maxscore+1):
            ln = float(len(self.scores))
            c = self.scores.count(i)
            cdf += c
            head += "%2s %0.5f %0.5f\n" % (i, c/ln, cdf/ln)
        a = np.array(l) if l else np.array(self.scores)
        mde = stats.mode(a)
        self.lg.info("\n".join([
            head,
            "N: %i" % (len(a),),
            "mean: %0.5f" % (a.mean(),),
            "medn: %0.5f" % (np.median(a),),
            "mode: %0.5f" % (mde[0],),
            "stdv: %0.5f" % (a.std(),),
            "skew: %0.5f" % (stats.skew(a),),
            "kurt: %0.5f" % (stats.kurtosis(a),)
        ]))

    def scorehist(self, **kwargs):
        from matplotlib import pyplot as plt
        bins = list(range(self.game.minscore, self.game.maxscore+2))
        hist, bins = np.histogram(self.scores, bins = bins)
        center = (bins[:-1]+bins[1:])/2
        plt.bar(center, hist, align="center", width=1, alpha=0.75)
        plt.xticks(bins[:-1], rotation=90)
        plt.title(kwargs.get("title", ""))
        plt.xlabel(kwargs.get("xlabel", ""))
        plt.ylabel(kwargs.get("ylabel", ""))
        plt.show()
