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
            (1, "Falcons", "Eagles", 1),
            (1, "Steelers", "Browns", 3.5),
            (1, "49ers", "Vikings", -6),
            (1, "Bengals", "Colts", -1),
            (1, "Bills", "Ravens", -9),
            (1, "Jaguars", "Giants", 3),
            (1, "Buccaneers", "Saints", -10),
            (1, "Texans", "Patriots", -6),
            (1, "Titans", "Dolphins", 0),
            (1, "Chiefs", "Chargers", -3.5),
            (1, "Seahawks", "Broncos", -3),
            (1, "Cowboys", "Panthers", -3),
            (1, "Redskins", "Cardinals", -2.51),
            (1, "Bears", "Packers", -7),
            (1, "Jets", "Lions", -6.5),
            (1, "Rams", "Raiders", 4.5),
            (2, "Ravens", "Bengals", 1),
            (2, "Panthers", "Falcons", -5.5),
            (2, "Chargers", "Bills", 3.5),
            (2, "Vikings", "Packers", -2.5),
            (2, "Texans", "Titans", 0),
            (2, "Browns", "Saints", -9),
            (2, "Dolphins", "Jets", -1),
            (2, "Chiefs", "Steelers", -4),
            (2, "Eagles", "Buccaneers", 6),
            (2, "Colts", "Redskins", -2.5),
            (2, "Cardinals", "Rams", -10.5),
            (2, "Lions", "49ers", -3),
            (2, "Raiders", "Broncos", 0),
            (2, "Patriots", "Jaguars", 2),
            (2, "Giants", "Cowboys", -3.5),
            (2, "Seahawks", "Bears", 0),
            (3, "Jets", "Browns", -2.5),
            (3, "Saints", "Falcons", -3),
            (3, "49ers", "Chiefs", -3),
            (3, "Raiders", "Dolphins", -1.5),
            (3, "Bills", "Vikings", -10),
            (3, "Colts", "Eagles", -10),
            (3, "Packers", "Redskins", -3),
            (3, "Bengals", "Panthers", -6),
            (3, "Titans", "Jaguars", -5),
            (3, "Broncos", "Ravens", -5.5),
            (3, "Giants", "Texans", -6),
            (3, "Chargers", "Rams", -3.5),
            (3, "Bears", "Cardinals", -1),
            (3, "Cowboys", "Seahawks", -1.5),
            (3, "Patriots", "Lions", -4),
            (3, "Steelers", "Buccaneers", -4),
            (4, "Vikings", "Rams", -3),
            (4, "Bengals", "Falcons", -7),
            (4, "Buccaneers", "Bears", -2.5),
            (4, "Lions", "Cowboys", -4),
            (4, "Bills", "Packers", -9.5),
            (4, "Eagles", "Titans", -1.5),
            (4, "Texans", "Colts", -3),
            (4, "Dolphins", "Patriots", -11),
            (4, "Jets", "Jaguars", -9.5),
            (4, "Browns", "Raiders", -7.5),
            (4, "Seahawks", "Cardinals", 0),
            (4, "Saints", "Giants", -2.5),
            (4, "49ers", "Chargers", -3.5),
            (4, "Ravens", "Steelers", -6),
            (4, "Chiefs", "Broncos", -1),
            (5, "Colts", "Patriots", -10.5),
            (5, "Titans", "Bills", 0),
            (5, "Dolphins", "Bengals", -2.5),
            (5, "Ravens", "Browns", -2.5),
            (5, "Packers", "Lions", -1),
            (5, "Jaguars", "Chiefs", -1),
            (5, "Broncos", "Jets", -1.5),
            (5, "Falcons", "Steelers", -4),
            (5, "Giants", "Panthers", -6),
            (5, "Raiders", "Chargers", -5),
            (5, "Vikings", "Eagles", -3.5),
            (5, "Cardinals", "49ers", -7),
            (5, "Rams", "Seahawks", -1),
            (5, "Cowboys", "Texans", -3),
            (5, "Redskins", "Saints", -7.5),
            (6, "Eagles", "Giants", -3),
            (6, "Buccaneers", "Falcons", -7),
            (6, "Steelers", "Bengals", -4),
            (6, "Chargers", "Browns", -4),
            (6, "Seahawks", "Raiders", -1.5),
            (6, "Bears", "Dolphins", -1.5),
            (6, "Cardinals", "Vikings", -10.5),
            (6, "Colts", "Jets", -1.5),
            (6, "Panthers", "Redskins", -1),
            (6, "Bills", "Texans", -6),
            (6, "Rams", "Broncos", -2.5),
            (6, "Jaguars", "Cowboys", -1),
            (6, "Ravens", "Titans", -2.5),
            (6, "Chiefs", "Patriots", -7),
            (6, "49ers", "Packers", -4),
            (7, "Broncos", "Cardinals", -1.5),
            (7, "Titans", "Chargers", -3),
            (7, "Patriots", "Bears", -5),
            (7, "Bills", "Colts", -2),
            (7, "Bengals", "Chiefs", -4.5),
            (7, "Lions", "Dolphins", -1),
            (7, "Vikings", "Jets", -4),
            (7, "Panthers", "Eagles", -6),
            (7, "Browns", "Buccaneers", -5.5),
            (7, "Texans", "Jaguars", -3),
            (7, "Saints", "Ravens", 0),
            (7, "Cowboys", "Redskins", -1),
            (7, "Rams", "49ers", -1),
            (7, "Giants", "Falcons", -6),
            (8, "Dolphins", "Texans", -7),
            (8, "Eagles", "Jaguars", 0),
            (8, "Jets", "Bears", -4.5),
            (8, "Buccaneers", "Bengals", -1.5),
            (8, "Seahawks", "Lions", -1.5),
            (8, "Broncos", "Chiefs", -4.5),
            (8, "Redskins", "Giants", -3.5),
            (8, "Browns", "Steelers", -10.5),
            (8, "Ravens", "Panthers", -2),
            (8, "Colts", "Raiders", -6),
            (8, "Packers", "Rams", -3),
            (8, "49ers", "Cardinals", -1.5),
            (8, "Saints", "Vikings", -4),
            (8, "Patriots", "Bills", -4.5),
            (9, "Raiders", "49ers", -4),
            (9, "Bears", "Bills", -1.5),
            (9, "Chiefs", "Browns", -3),
            (9, "Jets", "Dolphins", -4),
            (9, "Lions", "Vikings", -7),
            (9, "Falcons", "Redskins", -2.5),
            (9, "Buccaneers", "Panthers", -5.5),
            (9, "Steelers", "Ravens", 0),
            (9, "Texans", "Broncos", 0),
            (9, "Chargers", "Seahawks", 0),
            (9, "Rams", "Saints",  -2),
            (9, "Packers", "Patriots", -6),
            (9, "Titans", "Cowboys", -3.5),
            (10, "Panthers", "Steelers", -6.5),
            (10, "Lions", "Bears", -1),
            (10, "Saints", "Bengals", -3),
            (10, "Falcons", "Browns", -3),
            (10, "Dolphins", "Packers", -10.5),
            (10, "Patriots", "Titans", -3.5),
            (10, "Jaguars", "Colts", -4),
            (10, "Cardinals", "Chiefs", -6.5),
            (10, "Bills", "Jets", -1),
            (10, "Redskins", "Buccaneers", -3.5),
            (10, "Chargers", "Raiders", 0),
            (10, "Seahawks", "Rams", -7),
            (10, "Cowboys", "Eagles", -5.5),
            (10, "Giants", "49ers", -6.5),
            (11, "Packers", "Seahawks", -1),
            (11, "Cowboys", "Falcons", -3),
            (11, "Vikings", "Bears", -3),
            (11, "Panthers", "Lions", -2.5),
            (11, "Titans", "Colts", -1),
            (11, "Eagles", "Saints", -2),
            (11, "Buccaneers", "Giants", -3),
            (11, "Texans", "Redskins", -3),
            (11, "Bengals", "Ravens", -6),
            (11, "Raiders", "Cardinals", -1),
            (11, "Broncos", "Chargers", -4.5),
            (11, "Steelers", "Jaguars", -1),
            (11, "Chiefs", "Rams", -4.5),
            (12, "Bears", "Lions", -5),
            (12, "Redskins", "Cowboys", -6),
            (12, "Falcons", "Saints", -3.5),
            (12, "Jaguars", "Bills", -4.5),
            (12, "Browns", "Bengals", -5),
            (12, "Dolphins", "Colts", -2.5),
            (12, "Patriots", "Jets", -8.5),
            (12, "Giants", "Eagles", -8.5),
            (12, "49ers", "Buccaneers", -1),
            (12, "Seahawks", "Panthers", -3),
            (12, "Raiders", "Ravens", -5),
            (12, "Cardinals", "Chargers", -9),
            (12, "Steelers", "Broncos", -3),
            (12, "Packers", "Vikings", -3),
            (12, "Titans", "Texans", -3.5),
            (13, "Saints", "Cowboys", -1.5),
            (13, "Ravens", "Falcons", -3.5),
            (13, "Broncos", "Bengals", -1),
            (13, "Rams", "Lions", -2),
            (13, "Cardinals", "Packers", -11),
            (13, "Bills", "Dolphins", -1),
            (13, "Bears", "Giants", -3.5),
            (13, "Chargers", "Steelers", -4.5),
            (13, "Panthers", "Buccaneers", -1),
            (13, "Colts", "Jaguars", -7.5),
            (13, "Browns", "Texans", -10),
            (13, "Jets", "Titans", -8.5),
            (13, "Chiefs", "Raiders", -2.5),
            (13, "Vikings", "Patriots", -4.5),
            (13, "49ers", "Seahawks", -1),
            (13, "Redskins", "Eagles", -7.5),
            (14, "Jaguars", "Titans", -1),
            (14, "Jets", "Bills", -4),
            (14, "Rams", "Bears", -2.5),
            (14, "Panthers", "Browns", -2.5),
            (14, "Falcons", "Packers", -3.5),
            (14, "Ravens", "Chiefs",  -2),
            (14, "Patriots", "Dolphins", -6),
            (14, "Saints", "Buccaneers", -3),
            (14, "Giants", "Redskins", -1.5),
            (14, "Colts", "Texans", -7.5),
            (14, "Bengals", "Chargers", -7.5),
            (14, "Broncos", "49ers", -4.5),
            (14, "Eagles", "Cowboys", 0),
            (14, "Lions", "Cardinals", -1),
            (14, "Steelers", "Raiders", -3.5),
            (14, "Vikings", "Seahawks", -2),
            (15, "Chargers", "Chiefs", -2),
            (15, "Browns", "Broncos", -5.5),
            (15, "Texans", "Jets", -1.5),
            (15, "Cardinals", "Falcons", -7.5),
            (15, "Lions", "Bills", 0),
            (15, "Packers", "Bears", -3),
            (15, "Raiders", "Bengals", -1.5),
            (15, "Cowboys", "Colts", -3),
            (15, "Dolphins", "Vikings", -10),
            (15, "Titans", "Giants", -1.5),
            (15, "Redskins", "Jaguars", -8),
            (15, "Buccaneers", "Ravens", -6),
            (15, "Seahawks", "49ers", -3.5),
            (15, "Patriots", "Steelers", -1),
            (15, "Eagles", "Rams", -1),
            (15, "Saints", "Panthers", -1),
            (16, "Bengals", "Browns", -1),
            (16, "Buccaneers", "Cowboys", -6),
            (16, "Vikings", "Lions", -6.5),
            (16, "Redskins", "Titans", -5.5),
            (16, "Giants", "Colts", 0),
            (16, "Jaguars", "Dolphins", -3),
            (16, "Bills", "Patriots", -10.5),
            (16, "Packers", "Jets", -6),
            (16, "Texans", "Eagles", -5.5),
            (16, "Falcons", "Panthers", -1.5),
            (16, "Rams", "Cardinals", -3.5),
            (16, "Ravens", "Chargers", -3.5),
            (16, "Bears", "49ers", -6),
            (16, "Steelers", "Saints", -1),
            (16, "Chiefs", "Seahawks", -3),
            (16, "Broncos", "Raiders", -4),
        ]
        self.PICKED = tuple()
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

    def suboptimal(self):
        #TODO: Wrong!
        used, result = [], []
        for w in self.WEEKS:
            dude = sorted([
                x for x in self.REGSEASON
                if x[0] == w and x[2] not in used
            ], key=lambda x: x[-1])[0]
            used.append(dude[2])
            result.append(dude)
        return result

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
        print(" ".join([sep]+["%5s" % (team[:5],) for team in teams]))
        print(" ".join([stats]+["%5.1f" % (score,) for score in scores]))
    print(sep)
    so = S.suboptimal()
    print(" ".join([sep]+["%5s" % (x[2][:5],) for x in so]))
    print(" ".join([stats]+["%5.1f" % (x[-1],) for x in so]))
    print(sep)

if __name__ == "__main__":
    sys.exit(main(sys.argv))
