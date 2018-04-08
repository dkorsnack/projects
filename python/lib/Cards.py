# $Id: Cards.py 93 2014-05-10 20:27:11Z korsnack $
#!/bin/python

__all__ = ["Deck", "Holdem", "Poker", "Skat"]

from random import randint, sample, shuffle
from LogFile import LogFile

class Deck(object):

    def __init__(self):
        self.suit = 'cdhs'
        self.denomination = 'A23456789TJQK'
        self.deck = tuple([d+s for s in self.suit for d in self.denomination])

    def __str__(self):
        return  (("%3s"*13+"\n")*4)[:-1] % self.deck

    def shuffle(self):
        shuffle(self.deck)

    def hand(self, n = 5):
        return sample(self.deck, n)

    def getDenomination(self, hand = None):
        if not hand:
            hand = self.hand()
        return sorted(zip(*hand)[1])

    def getSuit(self, hand = None):
        if not hand:
            hand = self.hand()
        return sorted(zip(*hand)[0])

class Holdem(object):

    def __init__(self):
        self.startinghands = [
"AA" ,"AK" ,"AQ" ,"AJ" ,"AT" ,"A9" ,"A8" ,"A7" ,"A6" ,"A5" ,"A4" ,"A3" ,"A2" ,
"AKo","KK" ,"KQ" ,"KJ" ,"KT" ,"K9" ,"K8" ,"K7" ,"K6" ,"K5" ,"K4" ,"K3" ,"K2" ,
"AQo","KQo","QQ" ,"QJ" ,"QT" ,"Q9" ,"Q8" ,"Q7" ,"Q6" ,"Q5" ,"Q4" ,"Q3" ,"Q2" ,
"AJo","KJo","QJo","JJ" ,"JT" ,"J9" ,"J8" ,"J7" ,"J6" ,"J5" ,"J4" ,"J3" ,"J2" ,
"ATo","KTo","QTo","JTo","TT" ,"T9" ,"T8" ,"T7" ,"T6" ,"T5" ,"T4" ,"T3" ,"T2" ,
"A9o","K9o","Q9o","J9o","T9o","99" ,"98" ,"97" ,"96" ,"95" ,"94" ,"93" ,"92" ,
"A8o","K8o","Q8o","J8o","T8o","98o","88" ,"87" ,"86" ,"85" ,"84" ,"83" ,"82" ,
"A7o","K7o","Q7o","J7o","T7o","97o","87o","77" ,"76" ,"75" ,"74" ,"73" ,"72" ,
"A6o","K6o","Q6o","J6o","T6o","96o","86o","76o","66" ,"65" ,"64" ,"63" ,"62" ,
"A5o","K5o","Q5o","J5o","T5o","95o","85o","75o","65o","55" ,"54" ,"53" ,"52" ,
"A4o","K4o","Q4o","J4o","T4o","94o","84o","74o","64o","54o","44" ,"43" ,"42" ,
"A3o","K3o","Q3o","J3o","T3o","93o","83o","73o","63o","53o","43o","33" ,"32" ,
"A2o","K2o","Q2o","J2o","T2o","92o","82o","72o","62o","52o","42o","32o","22" 
        ]
        self.ppair = 1./221
        self.psuited = 2./663
        self.punsuited = 2./221
        self.pdf = {}
        for h in self.startinghands:
            if h[0] == h[1]:
                self.pdf[h] = self.ppair
            elif h[-1] == 'o':
                self.pdf[h] = self.punsuited
            else:
                self.pdf[h] = self.psuited

    def __str__(self, hands = None):
        if not hands:
            hands = self.startinghands
        return  (("%-4s"*13+"\n")*13)[:-1] % tuple(hands)

class Poker(Deck):

    def __init__(self):
        Deck.__init__(self)

    def summv(self, count):
        return [sum(z) for z in zip(
            count[0], count[1], count[2], count[3], count[4]
        )]

    def dmv(self, hand = None):
        if not hand:
            hand = self.hand()
        denomination = self.getDenomination(hand)
        count = [
            [1 if d == D else 0 for D in self.denomination]
            for d in denomination
        ]
        total = self.summv(count)
        dv = [total.count(r) for r in range(5)]
        return tuple(dv)

    def smv(self, hand = None):
        if not hand:
            hand = self.hand()
        sts = self.getSuit(hand)
        count = [[1 if s == S else 0 for S in self.suit] for s in sts]
        total = self.summv(count)
        sv = [total.count(r) for r in range(6)]
        return tuple(sv)

    def rank(self, hand = None):
        if not hand:
            hand = self.hand()
        # {dmv: term} # ways P(dmv)
        RANK = {
            (11, 1, 0, 0, 1): "four_of_a_kind",  # 624     0.00024
            (11, 0, 1, 1, 0): "full_house",      # 3744    0.00144
            (10, 2, 0, 1, 0): "three_of_a_kind", # 54912   0.02112
            (10, 1, 2, 0, 0): "two_pair",        # 123552  0.04753
            (9, 3, 1, 0, 0):  "one_pair",        # 1098240 0.42256
            (8, 5, 0, 0, 0):  "no_pair",         # 1317888 0.50708
        }
        return (" ".join(hand), RANK[self.dmv(hand)])

class Skat(Deck):

    def __init__(self):
        Deck.__init__(self)
        self.value = [11,2,3,4,5,6,7,8,9,10,10,10,10]
        self.deck = [(v,s) for s in self.suit for v in self.value]
        self.initial_distribution = [
            # (3-same, 0-same, 2-same, total) #score pdf cdf
            (  0,    4,    0),# 2 0.00018 0.00018
            (  0,   28,    0),# 3 0.00127 0.00145
            (  0,   76,    0),# 4 0.00344 0.00489
            (  0,  148,  156),# 5 0.01376 0.01864
            (  0,  244,  156),# 6 0.01810 0.03674
            (  0,  364,  312),# 7 0.03059 0.06733
            (  0,  508,  312),# 8 0.03710 0.10443
            (  4,  676,  468),# 9 0.05195 0.15638
            (  4, 4864,  468),#10 0.24145 0.39783
            (  8, 1876,  624),#11 0.11348 0.51131
            ( 12,    0, 1092),#12 0.04995 0.56127
            ( 16,    0, 1248),#13 0.05719 0.61846
            ( 20,    0, 1092),#14 0.05032 0.66878
            ( 40,    0, 1092),#15 0.05122 0.72000
            ( 44,    0,  936),#16 0.04434 0.76434
            ( 60,    0,  936),#17 0.04507 0.80941
            ( 64,    0,  780),#18 0.03819 0.84760
            ( 76,    0,  780),#19 0.03873 0.88633
            ( 76,    0, 1092),#20 0.05285 0.93919
            ( 88,    0,  624),#21 0.03222 0.97140
            ( 96,    0,    0),#22 0.00434 0.97575
            (104,    0,    0),#23 0.00471 0.98045
            ( 88,    0,    0),#24 0.00398 0.98443
            ( 88,    0,    0),#25 0.00362 0.98805
            ( 64,    0,    0),#26 0.00290 0.99095
            ( 60,    0,    0),#27 0.00271 0.99367
            ( 44,    0,    0),#28 0.00199 0.99566
            ( 40,    0,    0),#29 0.00181 0.99747
            ( 32,    0,    0),#30 0.00145 0.99891
            ( 24,    0,    0),#31 0.00109 1.00000
        #1144  8788  12168
        #0.5 2.6 2.4
        ]

    def score(self, hand = None):
        if not hand:
            hand = self.hand(3)
        match = set(self.getSuit(hand))
        if len(match) == 1:
            return sum(zip(*hand)[0])
        elif len(match) == 3:
            return max(zip(*hand)[0])
        else:
            counts = dict(
                [(self.getSuit(hand).count(s), s) for s in self.suit]
            )
            suit = counts[max(counts)]
            return sum([v for (v,s) in hand if s == suit])

    def brute_force(self, n): #2.40717
        from itertools import combinations
        hands = [h for h in combinations(self.deck, 3) if len(set(zip(*h)[1])) == n]
        ev = 0
        for hnd in hands:
            score = self.score(hnd)
            deck = [d for d in self.deck if d not in hnd]
            x = 0
            for d in deck:
                x += max(0, max([self.score(y) for y in ([hnd[0],hnd[1],d],[hnd[0],d,hnd[2]],[d,hnd[1],hnd[2]])])-score)
            ev += x/49.
        LogFile().info("%0.5f %0.5f" % (ev, ev/22100.))
