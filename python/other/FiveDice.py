# $Id: FiveDice.py 45 2013-10-06 15:57:20Z korsnack $
#!/bin/python

import operator
from Die import Die
from Gambler import RuleSet

__all__ = ["FiveDice", "Threes", "HighDice"]

"""HUGE BOOBOO:
This doesn't stop if you can take an immediate win...
"""

class FiveDice(Die):
    def __init__(
        self,
        die = [1,2,3,4,5,6],
        name = "FiveDice",
        RS = RuleSet(),
        evaluate = min,
        expectations = None
    ):
        Die.__init__(self, die)
        self.name = name
        self.RS = RS
        self.evaluate = evaluate
        self.expectations = expectations
        self.operator = {min: operator.lt, max: operator.gt}[self.evaluate]
        self.reverse = {min: False, max: True}[self.evaluate]
        self.minscore = 0
        self.maxscore = 30
        if not self.expectations:
            self.d = self.die
            self.dd = sorted(self.prod(2), reverse=self.reverse)
            self.ddd = sorted(self.prod(3), reverse=self.reverse)
            self.dddd = sorted(self.prod(4), reverse=self.reverse)
            self.ddddd = sorted(self.prod(5), reverse=self.reverse)
            ed = sum(self.d)/float(6)
            edd = sum(
                [i+self.evaluate(j, ed) for (i,j) in self.dd]
            )/float(6**2)
            eddd = sum(
                [i+self.evaluate(j+k, j+ed, edd)
                    for (i,j,k) in self.ddd])/float(6**3)
            edddd = sum(
                [i+self.evaluate(j+k+l, j+k+ed, k+edd, eddd)
                    for (i,j,k,l) in self.dddd])/float(6**4)
            eddddd = sum(
                [i+self.evaluate(j+k+l+m, j+k+l+ed, j+k+edd, j+eddd, edddd)
                    for (i,j,k,l,m) in self.ddddd])/float(6**5)
            self.expectations = (ed, edd, eddd, edddd, eddddd)

    def play(self, h = None):
        ed, edd, eddd, edddd = self.expectations[:4]
        if not h:
            h = self.minscore if self.reverse else self.maxscore
        score = 0
        dice = ['X']*5 # make this generic so everyting uses this play module
        while True:
            if not dice:
                break
            dice = sorted(self.roll(len(dice)), reverse = self.reverse)
            score += dice[0]
            dice = dice[1:]
            h -= score
            if self.RS.keep:
                score += sum([d for d in dice if d in self.RS.keep])
                dice = [d for d in dice if d not in self.RS.keep]
                h -= score
            if self.RS.optimal:
                l = len(dice)
                if l == 1:
                    n = self.evaluate(ed, h)
                    if self.operator(dice[0], n):
                        score += dice[0]
                        break
                elif l == 2:
                    n = self.evaluate(edd, h)
                    one,two = dice
                    if self.operator(one+two, n):
                        score += one+two
                        break
                    elif self.operator(one+ed, n):
                        score += one
                        dice = [two]
                elif l == 3:
                    n = self.evaluate(h, eddd)
                    one,two,three = dice
                    if self.operator(one+two+three, n):
                        score += one+two+three
                        break
                    elif self.operator(one+two+ed, n):
                        score += one+two
                        dice = [three]
                    elif self.operator(one+edd, n):
                        score += one
                        dice = [two, three]
                elif l == 4:
                    n = self.evaluate(h, edddd)
                    one,two,three,four = dice
                    if self.operator(one+two+three+four, n):
                        score += one+two+three+four
                        break
                    elif self.operator(one+two+three+ed, n):
                        score += one+two+three
                        dice = [four]
                    elif self.operator(one+two+edd, n):
                        score += one+two
                        dice = [three, four]
                    elif self.operator(one+eddd, n):
                        score += one
                        dice = [two, three, four]
                h -= score
        return score

class Threes(FiveDice):
    def __init__(self, RS = RuleSet()):
        FiveDice.__init__(
            self,
            RS = RS,
            name = "Threes",
            die = [1,2,0,4,5,6],
            expectations = (
                3.00000,
                4.38889,
                5.23380,
                5.83386,
                6.25398
            )
        )

class HighDice(FiveDice):
    def __init__(self, RS = RuleSet()):
        FiveDice.__init__(
            self,
            RS = RS,
            name = "HighDice",
            evaluate = max,
            expectations = (
                3.50000,
                8.23611,
                13.42490,
                18.84364,
                24.43605
            )
       )
