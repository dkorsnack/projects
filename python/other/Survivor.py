#!/bin/python

import sys
import numpy as np
from scipy.optimize import linear_sum_assignment
from optparse import OptionParser

np.set_printoptions(
    linewidth = 150,
    formatter = {'float': lambda x: "{:5.1f}".format(x)},
)

class Survivor(object):

    def __init__(self, home_teams_only, min_spread, up_to_week=None):
        self.home_teams_only = home_teams_only
        self.min_spread = min_spread
        self.up_to_week = up_to_week
        self.REGSEASON = [ 
            (1, "Houston", "KansasCity", -9.5),
            (1, "Chicago", "Detroit", -3),
            (1, "Indianapolis", "Jacksonville", 7.5),
            (1, "Philadelphia", "Washington", 6),
            (1, "NYJets", "Buffalo", -5.5),
            (1, "Miami", "NewEngland", -6),
            (1, "LasVegas", "Carolina", 3),
            (1, "GreenBay", "Minnesota", -3),
            (1, "Cleveland", "Baltimore", -8),
            (1, "Seattle", "Atlanta", 3.5),
            (1, "LAChargers", "Cincinnati", -7.5),
            (1, "Arizona", "SanFran", -7),
            (1, "TampaBay", "NewOrleans", -3.5),
            (1, "Dallas", "LARams", 3),
            (1, "Pittsburgh", "NYGiants", 5),
            (1, "Denver", "Tennessee", -1),

            (2, "Cincinnati", "Cleveland", -7.5),
            (2, "LARams", "Philadelphia", -3.5),
            (2, "Carolina", "TampaBay", -8),
            (2, "Denver", "Pittsburgh", -5.5),
            (2, "Atlanta", "Dallas", -7),
            (2, "SanFran", "NYJets", 6),
            (2, "Buffalo", "Miami", 3),
            (2, "Minnesota", "Indianapolis", -2.5),
            (2, "Detroit", "GreenBay", -6),
            (2, "NYGiants", "Chicago", -5.5),
            (2, "Jacksonville", "Tennessee", -11),
            (2, "Baltimore", "Houston", 5.5),
            (2, "KansasCity", "LAChargers", 6.5),
            (2, "NewEngland", "Seattle", -3),
            (2, "Washington", "Arizona", -6.5),
            (2, "NewOrleans", "LasVegas", 4.5),

            (3, "Miami", "Jacksonville", -1),
            (3, "Chicago", "Atlanta", -2),
            (3, "LARams", "Buffalo", -3),
            (3, "Washington", "Cleveland", -9),
            (3, "Tennessee", "Minnesota", -3.5),
            (3, "LasVegas", "NewEngland", -5.5),
            (3, "SanFran", "NYGiants", 7.5),
            (3, "Cincinnati", "Philadelphia", -10),
            (3, "Houston", "Pittsburgh", -5),
            (3, "NYJets", "Indianapolis", -7),
            (3, "Carolina", "LAChargers", -6.5),
            (3, "TampaBay", "Denver", 1),
            (3, "Detroit", "Arizona", -3),
            (3, "Dallas", "Seattle", -2.5),
            (3, "GreenBay", "NewOrleans", -5.5),
            (3, "KansasCity", "Baltimore", -2),

            (4, "Denver", "NYJets", -2.5),
            (4, "Indianapolis", "Chicago", -1.5),
            (4, "Jacksonville", "Cincinnati", -3.5),
            (4, "Cleveland", "Dallas", -4.5),
            (4, "NewOrleans", "Detroit", 5.5),
            (4, "Pittsburgh", "Tennessee", -2),
            (4, "Seattle", "Miami", 4),
            (4, "LAChargers", "TampaBay", -6.5),
            (4, "Baltimore", "Washington", 10),
            (4, "Arizona", "Carolina", 0),
            (4, "Minnesota", "Houston",0),
            (4, "NYGiants", "LARams", -7.5),
            (4, "NewEngland", "KansasCity", -8.5),
            (4, "Buffalo", "LasVegas", 1.5),
            (4, "Philadelphia", "SanFran", -5.5),
            (4, "Atlanta", "GreenBay", -6),

            (5, "TampaBay", "Chicago", -1),
            (5, "Carolina", "Atlanta", -6.5),
            (5, "Buffalo", "Tennessee", -2),
            (5, "LasVegas", "KansasCity", -12.5),
            (5, "Denver", "NewEngland", -6),
            (5, "Arizona", "NYJets", -1),
            (5, "Philadelphia", "Pittsburgh", -1.5),
            (5, "LARams", "Washington", 5),
            (5, "Cincinnati", "Baltimore", -14),
            (5, "Jacksonville", "Houston", -9),
            (5, "Miami", "SanFran", -13.5),
            (5, "Indianapolis", "Cleveland", -1),
            (5, "NYGiants", "Dallas", -7.5),
            (5, "Minnesota", "Seattle", -3),
            (5, "LAChargers", "NewOrleans", -10),

            (6, "KansasCity", "Buffalo", 3),
            (6, "Houston", "Tennessee", -4.5),
            (6, "Cincinnati", "Indianapolis", -9),
            (6, "Atlanta", "Minnesota", -6),
            (6, "Washington", "NYGiants", -5),
            (6, "Baltimore", "Philadelphia", 2),
            (6, "Cleveland", "Pittsburgh", -4.5),
            (6, "Chicago", "Carolina", 2.5),
            (6, "Detroit", "Jacksonville", 1.5),
            (6, "Miami", "Denver", -6),
            (6, "NYJets", "LAChargers", -4),
            (6, "GreenBay", "TampaBay", -2.5),
            (6, "LARams", "SanFran", -7),
            (6, "Arizona", "Dallas", -6.5),

            (7, "NYGiants", "Philadelphia", -5),
            (7, "Detroit", "Atlanta", -4),
            (7, "Cleveland", "Cincinnati", 3),
            (7, "LAChargers", "Miami", 0),
            (7, "Carolina", "NewOrleans", -13),
            (7, "Buffalo", "NYJets", 2.5),
            (7, "Dallas", "Washington", 6),
            (7, "Pittsburgh", "Baltimore", -7),
            (7, "GreenBay", "Houston", 0),
            (7, "Seattle", "Arizona", 2.5),
            (7, "KansasCity", "Denver", 5.5),
            (7, "SanFran", "NewEngland", -2),
            (7, "TampaBay", "LasVegas", 2.5),
            (7, "Chicago", "LARams", -3.5),

            (8, "Atlanta", "Carolina", 1.5),
            (8, "NewEngland", "Buffalo", -3),
            (8, "Tennessee", "Cincinnati", 1),
            (8, "LasVegas", "Cleveland", -5),
            (8, "Indianapolis", "Detroit", 1.5),
            (8, "Minnesota", "GreenBay", -3),
            (8, "NYJets", "KansasCity", 13),
            (8, "LARams", "Miami", 3),
            (8, "Jacksonville", "LAChargers", -7),
            (8, "NewOrleans", "Chicago", 2.5),
            (8, "SanFran", "Seattle", 0),
            (8, "Dallas", "Philadelphia", -2.5),
            (8, "TampaBay", "NYGiants", 0),

            (9, "GreenBay", "SanFran", -6.5),
            (9, "Denver", "Atlanta", -3.5),
            (9, "Seattle", "Buffalo", -2.5),
            (9, "Chicago", "Tennessee", -3),
            (9, "Baltimore", "Indianapolis", 2.5),
            (9, "Carolina", "KansasCity", -14.5),
            (9, "Detroit", "Minnesota", -7),
            (9, "NYGiants", "Washington", 0),
            (9, "Houston", "Jacksonville", 3),
            (9, "LasVegas", "LAChargers", -4.5),
            (9, "Pittsburgh", "Dallas", 3),
            (9, "Miami", "Arizona", -5),
            (9, "NewOrleans", "TampaBay", 1),
            (9, "NewEngland", "NYJets", 1.5),

            (10, "Indianapolis", "Tennessee", -2.5),
            (10, "Houston", "Cleveland", -2.5),
            (10, "Washington", "Detroit", -6),
            (10, "Jacksonville", "GreenBay", -11.5),
            (10, "Philadelphia", "NYGiants", 3.5),
            (10, "Cincinnati", "Pittsburgh", -9.5),
            (10, "TampaBay", "Carolina", 4.5),
            (10, "Denver", "LasVegas", -2.5),
            (10, "NYJets", "Miami", -1.5),
            (10, "Buffalo", "Arizona", 1),
            (10, "Seattle", "LARams", -1.5),
            (10, "SanFran", "NewOrleans", -2),
            (10, "Baltimore", "NewEngland", 2.5),
            (10, "Minnesota", "Chicago", 0),

            (11, "Arizona", "Seattle", -7.5),
            (11, "Philadelphia", "Cleveland", 0),
            (11, "GreenBay", "Indianapolis", -2.5),
            (11, "Atlanta", "NewOrleans", -9),
            (11, "Cincinnati", "Washington", -1.5),
            (11, "Detroit", "Carolina", -1),
            (11, "Pittsburgh", "Jacksonville", 6),
            (11, "Tennessee", "Baltimore", -8.5),
            (11, "NewEngland", "Houston", -2),
            (11, "LAChargers", "Denver", -2),
            (11, "Dallas", "Minnesota", -2.5),
            (11, "KansasCity", "LasVegas", 6),
            (11, "LARams", "TampaBay", -3.5),

            (12, "Houston", "Detroit", -1),
            (12, "Washington", "Dallas", -11),
            (12, "Baltimore", "Pittsburgh", 0),
            (12, "LasVegas", "Atlanta", -3.5),
            (12, "LAChargers", "Buffalo", -5),
            (12, "NYGiants", "Cincinnati", 0),
            (12, "Tennessee", "Indianapolis", -3),
            (12, "Carolina", "Minnesota", -9),
            (12, "Arizona", "NewEngland", -5.5),
            (12, "Miami", "NYJets", -4),
            (12, "Cleveland", "Jacksonville", -1),
            (12, "NewOrleans", "Denver", 3.5),
            (12, "SanFran", "LARams", 2.5),
            (12, "KansasCity", "TampaBay", 0),
            (12, "Chicago", "GreenBay", -4.5),
            (12, "Seattle", "Philadelphia", -2),

            (13, "Dallas", "Baltimore", -7),
            (13, "NewOrleans", "Atlanta", 3),
            (13, "Detroit", "Chicago", -5),
            (13, "Cleveland", "Tennessee", -4),
            (13, "Cincinnati", "Miami", -3.5),
            (13, "Jacksonville", "Minnesota", -11.5),
            (13, "LasVegas", "NYJets", -2),
            (13, "Washington", "Pittsburgh", -10),
            (13, "Indianapolis", "Houston", -2),
            (13, "LARams", "Arizona", 0),
            (13, "NYGiants", "Seattle", -9),
            (13, "Philadelphia", "GreenBay", -2.5),
            (13, "NewEngland", "LAChargers", 0),
            (13, "Denver", "KansasCity", -11.5),
            (13, "Buffalo", "SanFran", -7),

            (14, "NewEngland", "LARams", -4),
            (14, "Houston", "Chicago", -3.5),
            (14, "Dallas", "Cincinnati", 5),
            (14, "GreenBay", "Detroit", 2),
            (14, "KansasCity", "Miami", 7.5),
            (14, "Arizona", "NYGiants", 0),
            (14, "Minnesota", "TampaBay", -3),
            (14, "Denver", "Carolina", 1.5),
            (14, "Tennessee", "Jacksonville", 3.5),
            (14, "Indianapolis", "LasVegas", 2),
            (14, "NYJets", "Seattle", -8.5),
            (14, "NewOrleans", "Philadelphia", 0),
            (14, "Atlanta", "LAChargers", -2.5),
            (14, "Washington", "SanFran", -14.5),
            (14, "Pittsburgh", "Buffalo", -2.5),
            (14, "Baltimore", "Cleveland", 3.5),

            (15, "LAChargers", "LasVegas", -2),
            (15, "Buffalo", "Denver", 0),
            (15, "Carolina", "GreenBay", -10),
            (15, "Detroit", "Tennessee", -6),
            (15, "Houston", "Indianapolis", -4.5),
            (15, "NYJets", "LARams", -7),
            (15, "TampaBay", "Atlanta", 1),
            (15, "NewEngland", "Miami", 2.5),
            (15, "Chicago", "Minnesota", -4),
            (15, "Cleveland", "NYGiants", 1),
            (15, "Seattle", "Washington", 6),
            (15, "Jacksonville", "Baltimore", -16.5),
            (15, "Philadelphia", "Arizona", -1.5),
            (15, "KansasCity", "NewOrleans", -1.5),
            (15, "SanFran", "Dallas", 0),
            (15, "Pittsburgh", "Cincinnati", 4),

            (16, "Minnesota", "NewOrleans", -5.5),
            (16, "TampaBay", "Detroit", 2.5),
            (16, "Miami", "LasVegas", -1),
            (16, "Cleveland", "NYJets", 0),
            (16, "SanFran", "Arizona", 5),
            (16, "Denver", "LAChargers", -5),
            (16, "Atlanta", "KansasCity", -11),
            (16, "Indianapolis", "Pittsburgh", -2.5),
            (16, "Carolina", "Washington", -1),
            (16, "Chicago", "Jacksonville", -1.5),
            (16, "NYGiants", "Baltimore", -12.5),
            (16, "Cincinnati", "Houston", -6.5),
            (16, "LARams", "Seattle", -3.5),
            (16, "Philadelphia", "Dallas", -2),
            (16, "Tennessee", "GreenBay", -3.5),
            (16, "Buffalo", "NewEngland", -1.5),

            (17, "Miami", "Buffalo", -8),
            (17, "GreenBay", "Chicago", 0),
            (17, "Baltimore", "Cincinnati", 9),
            (17, "Pittsburgh", "Cleveland", -1),
            (17, "Minnesota", "Detroit", 2),
            (17, "Jacksonville", "Indianapolis", -10.5),
            (17, "LAChargers", "KansasCity", -11),
            (17, "NYJets", "NewEngland", -7),
            (17, "Dallas", "NYGiants", 3),
            (17, "Washington", "Philadelphia", -10.5),
            (17, "Atlanta", "TampaBay", -6.5),
            (17, "NewOrleans", "Carolina", 7.5),
            (17, "Tennessee", "Houston", -1),
            (17, "LasVegas", "Denver", -3.5),
            (17, "Arizona", "LARams", -6),
            (17, "Seattle", "SanFran", -6.5),
        ]

        self.PICKED = []
        week, home, away, spread = list(zip(*self.REGSEASON))
        assert set(home) == set(away), "SOMETHING IS MISSPELLED"
        self.TEAMS = sorted([
            t for t in list(set(home)) if t not in self.PICKED
        ])
        self.WEEKS = list(set(week))[:up_to_week]
        self.n = len(self.TEAMS)
        self.M = self.matrix()

    def matrix(self):
        mn = self.WEEKS[0]
        M = np.zeros((self.n, len(self.WEEKS)))
        for t in range(self.n):
            team = self.TEAMS[t]
            for i in self.WEEKS:
                for (week,away,home,spread) in self.REGSEASON:
                    if i == week:
                        if team == home:
                            M[t][i-mn] = spread
                        elif team == away:
                            if self.home_teams_only:
                                M[t][i-mn] = 0.
                            else:
                                M[t][i-mn] = -spread
        if self.min_spread:
            M[abs(M) < self.min_spread] = 0. 
        return M

    def solve(self):
        return tuple([
            (self.TEAMS[x], self.M[x,y]) for (x,y) in sorted(
                zip(*linear_sum_assignment(self.M)), 
                key=lambda y: y[1]
        )])

    def __str__(self):
        return "\n".join([
            "{:>25s} {}".format(self.TEAMS[i], self.M[i])
            for i in range(self.n)
        ])

    def suboptimal(self):
        used, result = self.PICKED[:], []
        for w in self.WEEKS:
            dudes = [
                (s,h) for (k,a,h,s) in self.REGSEASON if (
                    k == w and
                    h not in used and
                    s <= -self.min_spread
            )]
            if not self.home_teams_only:
                dudes += [
                    (-s,a) for (k,a,h,s) in self.REGSEASON if (
                        k == w and
                        a not in used and
                        -s <= -self.min_spread
                )]
            if dudes:
                dude = sorted(dudes)[0]
                used.append(dude[1])
                result.append(dude)
            else:
                return result
        return result

def parse_args(args):
    p = OptionParser("")
    p.add_option(
        '-H',
        '--home_teams_only',
        dest = 'home_teams_only',
        action = 'store_true',
    )
    p.add_option(
        '-m',
        '--min_spread',
        dest = 'min_spread',
        default=0.,
        type=float,
    )
    (o,a) = p.parse_args(args)
    return o

def main(args):
    o = parse_args(args)
    title = "    SUM   MIN   MAX   AVG "
    sep = " "*len(title)
    S = Survivor(o.home_teams_only, o.min_spread)
    print(S)
    print(sep+"\n"+title) 
    stat_str = " {:6.1f} {:5.1f} {:5.1f} {:5.1f} "
    for i in range(len(S.WEEKS)):
        S = Survivor(o.home_teams_only, o.min_spread, i+1)
        teams, scores = [], []
        for (t,s) in S.solve():
            if not s:
                break
            else:
                teams.append(t)
                scores.append(s)
        if not s:
            break
        stats = stat_str.format(*[f(scores) for f in (sum,min,max,np.mean)])
        print(" ".join([sep]+["{:5s}".format(team[:5]) for team in teams]))
        print(" ".join([stats]+["{:5.1f}".format(score) for score in scores]))
    print(sep)
    scores, teams = list(zip(*S.suboptimal()))
    stats = stat_str.format(*[f(scores) for f in (sum,min,max,np.mean)])
    print(" ".join([sep]+["{:5s}".format(team[:5]) for team in teams]))
    print(" ".join([stats]+["{:5.1f}".format(score) for score in scores]))
    print(sep)
    return

if __name__ == "__main__":
    sys.exit(main(sys.argv))
