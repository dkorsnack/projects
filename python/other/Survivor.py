#!/bin/python

import sys
import numpy as np
from scipy.optimize import linear_sum_assignment
from optparse import OptionParser

np.set_printoptions(
    linewidth = 150,
    formatter = {'float': lambda x: "%5.1f" % (x,)},
)

class Survivor(object):

    def __init__(self, home_teams_only=False, up_to_week=None):
        self.REGSEASON = [
            (7, "Chiefs", "Raiders", -3),
            (7, "Buccaneers", "Bills", -3),
            (7, "Panthers", "Bears", 3.5),
            (7, "Titans", "Browns", 6),
            (7, "Saints", "Packers", 4),
            (7, "Jaguars", "Colts", 3),
            (7, "Cardinals", "Rams", -3),
            (7, "Jets", "Dolphins", -3),
            (7, "Ravens", "Vikings", -5.5),
            (7, "Bengals", "Steelers", -5),
            (7, "Cowboys", "49ers", 6.5),
            (7, "Broncos", "Chargers", 1),
            (7, "Seahawks", "Giants", 4),
            (7, "Falcons", "Patriots", -3.5),
            (7, "Redskins", "Eagles", -4.5),
            (8, "Dolphins", "Ravens", -4),
            (8, "Vikings", "Browns", 7),
            (8, "Raiders", "Bills", 1.5),
            (8, "Colts", "Bengals", -3),
            (8, "Chargers", "Patriots", -12.5),
            (8, "Bears", "Saints", -6),
            (8, "Falcons", "Jets", 7),
            (8, "49ers", "Eagles", -7.5),
            (8, "Panthers", "Buccaneers", -2.5),
            (8, "Texans", "Seahawks", -7.5),
            (8, "Cowboys", "Redskins", 2.5),
            (8, "Steelers", "Lions", 3),
            (8, "Broncos", "Chiefs", -4),
            (9, "Bills", "Jets", 2.5),
            (9, "Falcons", "Panthers", 1.5),
            (9, "Colts", "Texans", -3),
            (9, "Bengals", "Jaguars", 0),
            (9, "Buccaneers", "Saints", -1.5),
            (9, "Rams", "Giants", -8.5),
            (9, "Broncos", "Eagles", -1),
            (9, "Ravens", "Titans", -2.5),
            (9, "Cardinals", "49ers", 3.5),
            (9, "Redskins", "Seahawks", -8),
            (9, "Chiefs", "Cowboys", -4),
            (9, "Raiders", "Dolphins", 0),
            (9, "Lions", "Packers", -7.5),
            (10, "Seahawks", "Cardinals", 2.5),
            (10, "Saints", "Bills", -2),
            (10, "Packers", "Bears", 6.5),
            (10, "Browns", "Lions", -8.5),
            (10, "Steelers", "Colts", 3),
            (10, "Chargers", "Jaguars", -3),
            (10, "Jets", "Buccaneers", -8),
            (10, "Bengals", "Titans", -3),
            (10, "Vikings", "Redskins", -1.5),
            (10, "Texans", "Rams", 3),
            (10, "Cowboys", "Falcons", -3),
            (10, "Giants", "49ers", 4.5),
            (10, "Patriots", "Broncos", 4.5),
            (10, "Dolphins", "Panthers", -4),
            (11, "Titans", "Steelers", -7),
            (11, "Lions", "Bears", 1),
            (11, "Ravens", "Packers", -7),
            (11, "Jaguars", "Browns", 3),
            (11, "Cardinals", "Texans", -2.5),
            (11, "Rams", "Vikings", -7.5),
            (11, "Redskins", "Saints", -2.5),
            (11, "Chiefs", "Giants", -1),
            (11, "Bills", "Chargers", -2),
            (11, "Bengals", "Broncos", -3.5),
            (11, "Patriots", "Raiders", 4.5),
            (11, "Eagles", "Cowboys", -6),
            (11, "Falcons", "Seahawks", -3),
            (12, "Vikings", "Lions", -2.5),
            (12, "Chargers", "Cowboys", -7.5),
            (12, "Giants", "Redskins", -1.5),
            (12, "Buccaneers", "Falcons", -6.5),
            (12, "Browns", "Bengals", -8.5),
            (12, "Titans", "Colts", -3),
            (12, "Bills", "Chiefs", -6),
            (12, "Dolphins", "Patriots", -9),
            (12, "Panthers", "Jets", 3),
            (12, "Bears", "Eagles", -6),
            (12, "Saints", "Rams", 2),
            (12, "Seahawks", "49ers", 7.5),
            (12, "Jaguars", "Cardinals", -6.5),
            (12, "Broncos", "Raiders", -3),
            (12, "Packers", "Steelers", -3),
            (12, "Texans", "Ravens", -3),
            (13, "Redskins", "Cowboys", -7),
            (13, "Vikings", "Falcons", -5.5),
            (13, "Lions", "Ravens", -3),
            (13, "Patriots", "Bills", 7),
            (13, "49ers", "Bears", -4),
            (13, "Buccaneers", "Packers", -7),
            (13, "Colts", "Jaguars", 1),
            (13, "Broncos", "Dolphins", -1),
            (13, "Panthers", "Saints", -2.5),
            (13, "Chiefs", "Jets", 4.5),
            (13, "Texans", "Titans", -3),
            (13, "Browns", "Chargers", -7),
            (13, "Rams", "Cardinals", -8.5),
            (13, "Giants", "Raiders", -3),
            (13, "Eagles", "Seahawks", -7),
            (13, "Steelers", "Bengals", 2.5),
            (14, "Saints", "Falcons", -6.5),
            (14, "Colts", "Bills", -1.5),
            (14, "Vikings", "Panthers", -3),
            (14, "Bears", "Bengals", -6.5),
            (14, "Packers", "Browns", 9.5),
            (14, "49ers", "Texans", -9),
            (14, "Seahawks", "Jaguars", 4.5),
            (14, "Raiders", "Chiefs", -3),
            (14, "Lions", "Buccaneers", -3),
            (14, "Titans", "Cardinals", -3),
            (14, "Jets", "Broncos", -9),
            (14, "Redskins", "Chargers", -1.5),
            (14, "Eagles", "Rams", 1.5),
            (14, "Cowboys", "Giants", 2.5),
            (14, "Ravens", "Steelers", -6),
            (14, "Patriots", "Dolphins", 6.5),
            (15, "Broncos", "Colts", -3),
            (15, "Bears", "Lions", -6.5),
            (15, "Chargers", "Chiefs", -6),
            (15, "Dolphins", "Bills", -1.5),
            (15, "Packers", "Panthers", 2),
            (15, "Ravens", "Browns", 4),
            (15, "Texans", "Jaguars", 1),
            (15, "Bengals", "Vikings", -3),
            (15, "Jets", "Saints", -6.5),
            (15, "Eagles", "Giants", -3.5),
            (15, "Cardinals", "Redskins", -2),
            (15, "Rams", "Seahawks", -13.5),
            (15, "Patriots", "Steelers", 1.5),
            (15, "Titans", "49ers", 3),
            (15, "Cowboys", "Raiders", 1),
            (15, "Falcons", "Buccaneers", 1.5),
            (16, "Colts", "Ravens", -4),
            (16, "Vikings", "Packers", -7),
            (16, "Buccaneers", "Panthers", -3),
            (16, "Browns", "Bears", -4.5),
            (16, "Lions", "Bengals", -3),
            (16, "Dolphins", "Chiefs", -4.5),
            (16, "Bills", "Patriots", -11.5),
            (16, "Falcons", "Saints", 0),
            (16, "Chargers", "Jets", 0),
            (16, "Rams", "Titans", -7),
            (16, "Broncos", "Redskins", 1),
            (16, "Jaguars", "49ers", 1),
            (16, "Giants", "Cardinals", -2),
            (16, "Seahawks", "Cowboys", -3),
            (16, "Steelers", "Texans", 3.5),
            (16, "Raiders", "Eagles", -1),
        ]
        self.PICKED = (
            'Bills',
            'Raiders',
            'Patriots',
            'Falcons',
            'Steelers',
            'Texans',
        )
        week, home, away, spread = list(zip(*self.REGSEASON))
        assert set(home) == set(away), "SOMETHING IS MISSPELLED"
        self.TEAMS = sorted([
            t for t in list(set(home)) if t not in self.PICKED
        ])
        self.WEEKS = list(set(week))[:up_to_week]
        self.n = len(self.TEAMS)
        self.M = self.matrix(home_teams_only)

    def matrix(self, home_teams_only):
        mn = self.WEEKS[0]
        M = np.empty((self.n, len(self.WEEKS),))*np.nan
        for t in range(self.n):
            team = self.TEAMS[t]
            for i in self.WEEKS:
                for (week,away,home,spread) in self.REGSEASON:
                    if i == week:
                        if team == home:
                            M[t][i-mn] = spread
                        elif team == away:
                            if home_teams_only:
                                M[t][i-mn] = np.nan 
                            else:
                                M[t][i-mn] = -spread
        return M

    def solve(self):
        return tuple([
            (self.TEAMS[x], self.M[x,y]) for (x,y) in sorted(
                zip(*linear_sum_assignment(np.nan_to_num(self.M))), 
                key=lambda y: y[1]
        )])

    def __str__(self):
        return "\n".join([
            "%10s %s" % (self.TEAMS[i], self.M[i])
            for i in range(self.n)
        ])

def parse_args(args):
    p = OptionParser("")
    p.add_option(
        '-m',
        '--home_teams_only',
        dest = 'home_teams_only',
        action = 'store_true',
    )
    (o,a) = p.parse_args(args)
    return o

def main(args):
    o = parse_args(args)
    title = "|    SUM   MIN   MAX   AVG |"
    sep = "-"*len(title)
    S = Survivor(o.home_teams_only)
    print(S)
    print(sep+"\n"+title) 
    for i in range(len(S.WEEKS)):
        S = Survivor(o.home_teams_only, i+1)
        teams, scores = list(zip(*S.solve()))
        stats = "| %6.1f %5.1f %5.1f %5.1f |" % tuple([
            f(scores) for f in (sum,min,max,np.mean)
        ])
        print(" ".join([sep]+[team[:5] for team in teams]))
        print(" ".join([stats]+["%5.1f" % (score,) for score in scores]))

if __name__ == "__main__":
    sys.exit(main(sys.argv))
