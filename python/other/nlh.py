# $Id: nlh.py 45 2013-10-06 15:57:20Z korsnack $
#!/bin/python

import pickle
from pokereval import PokerEval

# map each staritng hand into a playable hand for evaluation
PLAYABLE_STARTING_HANDS = []
for c in STARTING_HANDS:
    if c[-1] == "o": PLAYABLE_STARTING_HANDS.append((c[0]+"c", c[1]+"s"))
    else:
        if c[0] == c[1]: PLAYABLE_STARTING_HANDS.append((c[0]+"c", c[1]+"s"))
        else: PLAYABLE_STARTING_HANDS.append((c[0]+"c", c[1]+"c"))

# helpful functions
def simulate(h, num_o = 1, iter = 100000):
    result = pokereval.poker_eval(game = "holdem",
                                  iterations = iter,
                                  pockets = [[h[0], h[1]]]+[["__", "__"]]*num_o,
                                  board = ["__"] * 5
                                  )
    return result['eval'][0]['scoop']/\
           float(result['info'][0]) # -result['eval'][0]['tiehi'])

# assessing each starting hand against N opponents to the showdown
pokereval = PokerEval()
ALL = []
for r in range(1, 9):
    ALL.append(dict([(STARTING_HANDS[i],
                      simulate(PLAYABLE_STARTING_HANDS[i], num_o = r))
                     for i in range(len(STARTING_HANDS))]))


fh = open("holdem.pkl", 'wb')
pickle.dump(ALL, fh)
fh.close()

# graphical representations
from numpy import array
from mpl_toolkits.mplot3d.axes3d import Axes3D
import matplotlib.pyplot as plt
from matplotlib import cm

ff = open("holdem.pkl", "r")
ALL = pickle.load(ff)
ff.close()

fig = plt.figure()
ax = Axes3D(fig)

for a in ALL:
    plots = (array([range(13)]*13),
              array([[12-i]*13 for i in range(13)]),
              array([[a[s]*100 for s in STARTING_HANDS[0:13]],
                    [a[s]*100 for s in STARTING_HANDS[13:26]],
                    [a[s]*100 for s in STARTING_HANDS[26:39]],
                    [a[s]*100 for s in STARTING_HANDS[39:52]],
                    [a[s]*100 for s in STARTING_HANDS[52:65]],
                    [a[s]*100 for s in STARTING_HANDS[65:78]],
                    [a[s]*100 for s in STARTING_HANDS[78:91]],
                    [a[s]*100 for s in STARTING_HANDS[91:104]],
                    [a[s]*100 for s in STARTING_HANDS[104:117]],
                    [a[s]*100 for s in STARTING_HANDS[117:130]],
                    [a[s]*100 for s in STARTING_HANDS[130:143]],
                    [a[s]*100 for s in STARTING_HANDS[143:156]],
                    [a[s]*100 for s in STARTING_HANDS[156:169]]
                    ]))
    ax.plot_surface(plots[0], plots[1], plots[2],
                    rstride=1, cstride=1, cmap=cm.jet)
plt.show()
