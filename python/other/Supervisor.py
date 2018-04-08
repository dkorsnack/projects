# $Id: Supervisor.py 45 2013-10-06 15:57:20Z korsnack $
#!/bin/python

import datetime
from random import shuffle

class Supervisor(object):
    def __init__(
        self,
        Gamblers,
        bet = 1,
        exp = 1,
        randstart = False
     ):
        assert len(set(map(type, Gamblers))) == 1
        self.Players = Gamblers
        self.Gamblers = Gamblers
        self.bet = bet
        self.exp = exp
        self.randstart = randstart
        self.reverse = True
        self.worstscore = self.Gamblers[0].game.maxscore
        if self.Gamblers[0].game.evaluate == max:
            self.reverse = False
            self.worstscore = self.Gamblers[0].game.minscore
        if self.randstart:
            shuffle(self.Players)

    def sort(self, unlimited=False):
        if unlimited:
            return zip(*sorted(
                [(P.scores[-1], P) for P in self.Players],
                reverse = self.reverse
            ))[1]
        else:
            return zip(*sorted(
                [(P.scores[-1], P) for P in self.Players if P.bankroll[-1] >= self.bet],
                reverse = self.reverse
            ))[1]

    def play(self, n = 0):
        start = datetime.datetime.now()
        if self.randstart:
            print("starting: "+" ".join([P.name for P in self.Players]))
        if n:
            for i in range(n):
                self.hand(unlimited=True)
        else:
            while len(self.Players) > 1:
                self.hand()
        stop = datetime.datetime.now()
        print(stop-start)

    def hand(self, unlimited=False):
        pot = 0
        bet = self.bet
        bscore = self.worstscore
        [P.bankroll.append(P.bankroll[-1]) for P in self.Players]
        while True:
            for P in self.Players:
                P.bankroll[-1] -= self.bet
                pot += self.bet
                P.scores.append(P.game.play(h = bscore))
                bscore = P.game.evaluate(P.scores[-1], bscore)
            bet *= self.exp
            if [P.scores[-1] for P in self.Players].count(bscore) == 1:
                [P for P in self.Players
                 if P.scores[-1] == bscore][0].bankroll[-1] += pot
                break
            else:
                bscore = self.worstscore
        self.Players = self.sort(unlimited)

    def bankrollplot(self, **kwargs):
        from matplotlib import pyplot as plt
        for G in self.Gamblers:
            plt.plot(G.bankroll)
        plt.legend([G.name for G in self.Gamblers], loc="best", frameon=False)
        plt.title(kwargs.get("title", ""))
        plt.xlabel(kwargs.get("xlabel", ""))
        plt.ylabel(kwargs.get("ylabel", ""))
        plt.show()
