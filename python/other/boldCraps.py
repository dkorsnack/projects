# $Id: boldCraps.py 45 2013-10-06 15:57:20Z korsnack $
# $Id: boldCraps.py 45 2013-10-06 15:57:20Z korsnack $
#!/bin/python
"""
Inspired by 'Improving on Bold Play at Craps' by S. N. Ethier,
Operations Research Vol. 35, No. 6 Nov - Dec 1987
1. Don't risk overshooting your goal
2. Maximize the useage of free odds
3. Choose initial stake small enough that you can take/lay odds
   for the largest amount allowable without violating #1
4. Choose initial stake large enough that, following #3, there
   is positive conditional probability that you will reach your
   goal or zero upon resolution of the bet
5. Choose the line bet that, if you follow #1 - #4, maximizes
   the probability that you will reach your goal or zero upon
   resolution of the bet
"""
from optparse import OptionParser
from math import ceil, floor
from mathutils import ruin
from datetime import timedelta as td

# time statistics {num_players: rolls}
PER_HOUR = {1: 249, 2: 232, 3: 216, 4: 180, 5: 144, 6: 139,
            7: 135, 8: 129, 9: 123, 10: 113, 11: 102}

# dissecting the command line arguments
parser = OptionParser()
parser.add_option("-b", "--Bankroll", type = 'int', default = 500)
parser.add_option("-g", "--Goal", type = 'int', default = 1000)
parser.add_option("-o", "--Odds", type = 'string', default = '3,4,5')
parser.add_option("-m", "--Minbet", type = 'int', default = None)
parser.add_option("-n", "--NumPlayers", type = 'int', default = 8)
options, args = parser.parse_args()

# global variables
O,B,G,M,N = [options.Odds, options.Bankroll, options.Goal,
             options.Minbet, options.NumPlayers]
PAY = {'4,T': (2.,1.), '5,9': (3.,2.), '6,8': (6.,5.)}
KEYS, WAYS = [sorted(PAY.keys()), [6., 8., 10.]]
ODDS = dict(list(zip(KEYS, list(map(float, O.split(','))))))
MAX_ODDS = max(ODDS.values())

# helpful functions
def up(v, p): return v if v % p == 0 else ceil(v/p)*p

def pstake(w, s, k):
    scale = PAY[k][0]/PAY[k][1]
    if w == 'PASS':
        p = PAY[k][1]
        a,b,c,d = [ODDS[k]*s, B-s, (G-B-s)/scale, MAX_ODDS*s]
    else:
        p = PAY[k][0]
        a,b,c,d = [scale*ODDS[k]*s, B-s, (G-B-s)*scale, MAX_ODDS*s*6/5]
    return max(0, min(d, up(a, p), up(b, p), up(c, p)))

def pwin(w, ps, k):
    scale = PAY[k][0]/PAY[k][1]
    if w == 'PASS': return ps*scale
    else: return ps/scale

# bet optimally, i.e. max(P(Bn(-L, W) = W) at each coup
MAX_ODDS = max(ODDS.values())
threshold = (5+5*MAX_ODDS)/(10+11*MAX_ODDS)
if B < threshold*G:
    wager = 'PASS'
    bBp = 1+sum([ODDS[x]*y/36 for (x, y) in zip(KEYS, WAYS)])
    edge = (-7./495)/bBp
    stake = min(B/(1+MAX_ODDS), (G-B)/(1+MAX_ODDS*6/5))
else:
    wager = 'DONT'
    bBp = 1+sum([ODDS[x]*(PAY[x][0]/PAY[x][1])*y/35
                 for (x, y) in zip(KEYS, WAYS)])
    edge = (-27./1925)/bBp
    stake = min((G-B)/(1+MAX_ODDS), B/(1+MAX_ODDS*6/5))
if M: stake = floor(max(float(M), stake))
pstakes = [pstake(wager, stake, k) for k in KEYS]
pwins = [pwin(wager, ps, k) for (ps, k) in zip(pstakes, KEYS)]
pB, eN = ruin(G-B, B, 0.5+edge, stake*bBp)
eR = eN*557/165
eT = td(minutes=int(eR/(PER_HOUR[N]/60.)))

# pretty print the results
print("\n".join([
    "Line: %s, lay $%.2f to win $%.2f",
     "Odds 4,T: lay $%.2f to win $%.2f",
     "Odds 5,9: lay $%.2f to win $%.2f",
     "Odds 6,8: lay $%.2f to win $%.2f",
     "Edge: %.2f%% ($%.2f)",
     "P(Goal before 0): %.2f%%",
     "<Coups>: %i",
     "<Rolls>: %i",
     "<Time>: %s"
  ]) % (
      wager, stake, stake,
      pstakes[0], pwins[0],
      pstakes[1], pwins[1],
      pstakes[2], pwins[2],
      edge*100, B*edge,
      pB*100, eN, eR, eT
))
