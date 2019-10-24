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
           #(1,'GreenBay','Chicago',-3),
           #(1,'Atlanta','Minnesota',-3.5),
           #(1,'Buffalo','NYJets',-3),
           #(1,'Washington','Philadelphia',-10),
           #(1,'Baltimore','Miami',7),
           #(1,'SanFrancisco','TampaBay',1),
           #(1,'KansasCity','Jacksonville',3.5),
           #(1,'Tennessee','Cleveland',-6),
           #(1,'LARams','Carolina',3),
           #(1,'Detroit','Arizona',2.5),
           #(1,'Cincinnati','Seattle',-9),
           #(1,'Indianapolis','LAChargers',-6.5),
           #(1,'NYGiants','Dallas',-7.5),
           #(1,'Pittsburgh','NewEngland',-5.5),
           #(1,'Houston','NewOrleans',-6.5),
           #(1,'Denver','Oakland',1),

           #(2,'TampaBay','Carolina',-7),
           #(2,'SanFrancisco','Cincinnati',-1),
           #(2,'LAChargers','Detroit',1.5),
           #(2,'Minnesota','GreenBay',-3),
           #(2,'Indianapolis','Tennessee',-3),
           #(2,'NewEngland','Miami',19),
           #(2,'Buffalo','NYGiants',2),
           #(2,'Seattle','Pittsburgh',-3.5),
           #(2,'Dallas','Washington',6),
           #(2,'Arizona','Baltimore',-13),
           #(2,'Jacksonville','Houston',-9),
           #(2,'KansasCity','Oakland',7),
           #(2,'Chicago','Denver',2),
           #(2,'NewOrleans','LARams',-2),
           #(2,'Philadelphia','Atlanta',2),
           #(2,'Cleveland','NYJets',7),

           #(3,'Tennessee','Jacksonville',1.5),
           #(3,'Cincinnati','Buffalo',-6),
           #(3,'Miami','Dallas',-21.5),
           #(3,'Denver','GreenBay',-7.5),
           #(3,'Atlanta','Indianapolis',-1.5),
           #(3,'Baltimore','KansasCity',-6.5),
           #(3,'Oakland','Minnesota',-9),
           #(3,'NYJets','NewEngland',-22.5),
           #(3,'Detroit','Philadelphia',-6),
           #(3,'Carolina','Arizona',0),
           #(3,'NYGiants','TampaBay',-6.5),
           #(3,'Houston','LAChargers',-3),
           #(3,'Pittsburgh','SanFrancisco',-6.5),
           #(3,'NewOrleans','Seattle',-4.5),
           #(3,'LARams','Cleveland',3.5),
           #(3,'Chicago','Washington',4),

           #(4,'Philadelphia','GreenBay',-5),
           #(4,'Tennessee','Atlanta',-4),
           #(4,'NewEngland','Buffalo',7),
           #(4,'KansasCity','Detroit',6.5),
           #(4,'Oakland','Indianapolis',-6.5),
           #(4,'LAChargers','Miami',16),
           #(4,'Washington','NYGiants',-2.5),
           #(4,'Cleveland','Baltimore',-7),
           #(4,'Carolina','Houston',-4),
           #(4,'TampaBay','LARams',-10),
           #(4,'Seattle','Arizona',5),
           #(4,'Minnesota','Chicago',-2.5),
           #(4,'Jacksonville','Denver',-3),
           #(4,'Dallas','NewOrleans',2.5),
           #(4,'Cincinnati','Pittsburgh',-4),

            (5,'LARams','Seattle',1.5),
            (5,'Arizona','Cincinnati',-3),
            (5,'Buffalo','Tennessee',-3),
            (5,'Chicago','Oakland',5),
            (5,'TampaBay','NewOrleans',-3),
            (5,'Minnesota','NYGiants',5.5),
            (5,'NYJets','Philadelphia',-14),
            (5,'Baltimore','Pittsburgh',3.5),
            (5,'NewEngland','Washington',15.5),
            (5,'Jacksonville','Carolina',-3.5),
            (5,'Atlanta','Houston',-4),
            (5,'Denver','LAChargers',-5.5),
            (5,'GreenBay','Dallas',-3.5),
            (5,'Indianapolis','KansasCity',-11),
            (5,'Cleveland','SanFrancisco',-4),

            (6,'NYGiants','NewEngland',-14.5),
            (6,'Carolina','TampaBay',-2),
            (6,'Seattle','Cleveland',-2.5),
            (6,'Houston','KansasCity',-8),
            (6,'Washington','Miami',5),
            (6,'Philadelphia','Minnesota',-3),
            (6,'NewOrleans','Jacksonville',-2),
            (6,'Cincinnati','Baltimore',-10),
            (6,'SanFrancisco','LARams',-4),
            (6,'Atlanta','Arizona',3),
            (6,'Tennessee','Denver',1.5),
            (6,'Dallas','NYJets',2.5),
            (6,'Pittsburgh','LAChargers',-5.5),
            (6,'Detroit','GreenBay',-6),

            (7,'KansasCity','Denver',4),
            (7,'LARams','Atlanta',1.5),
            (7,'Miami','Buffalo',-4.5),
            (7,'Jacksonville','Cincinnati',1),
            (7,'Minnesota','Detroit',1.5),
            (7,'Oakland','GreenBay',-8.5),
            (7,'Houston','Indianapolis',-4),
            (7,'Arizona','NYGiants',-4),
            (7,'SanFrancisco','Washington',-1),
            (7,'LAChargers','Tennessee',4),
            (7,'NewOrleans','Chicago',-1.5),
            (7,'Baltimore','Seattle',-4),
            (7,'Philadelphia','Dallas',-2.5),
            (7,'NewEngland','NYJets',6),

            (8,'Washington','Minnesota',-8),
            (8,'Seattle','Atlanta',0),
            (8,'TampaBay','Tennessee',-5.5),
            (8,'Arizona','NewOrleans',-14.5),
            (8,'Cincinnati','LARams',-13),
            (8,'NYJets','Jacksonville',-4.5),
            (8,'Philadelphia','Buffalo',3),
            (8,'LAChargers','Chicago',-3),
            (8,'NYGiants','Detroit',-3),
            (8,'Oakland','Houston',-7),
            (8,'Carolina','SanFrancisco',-2.5),
            (8,'Cleveland','NewEngland',-7),
            (8,'Denver','Indianapolis',-7),
            (8,'GreenBay','KansasCity',-6.5),
            (8,'Miami','Pittsburgh',-10.5),

            (9,'SanFrancisco','Arizona',3.5),
            (9,'Houston','Jacksonville',0),
            (9,'Washington','Buffalo',-3.5),
            (9,'Minnesota','KansasCity',-7),
            (9,'NYJets','Miami',1),
            (9,'Chicago','Philadelphia',-3.5),
            (9,'Indianapolis','Pittsburgh',-2.5),
            (9,'Tennessee','Carolina',-3.5),
            (9,'Detroit','Oakland',-3),
            (9,'TampaBay','Seattle',-7.5),
            (9,'Cleveland','Denver',-1),
            (9,'GreenBay','LAChargers',-3.5),
            (9,'NewEngland','Baltimore',2.5),
            (9,'Dallas','NYGiants',3),

            (10,'LAChargers','Oakland',4),
            (10,'Detroit','Chicago',-8),
            (10,'Baltimore','Cincinnati',1),
            (10,'Buffalo','Cleveland',-6.5),
            (10,'Carolina','GreenBay',-5),
            (10,'KansasCity','Tennessee',3.5),
            (10,'Atlanta','NewOrleans',-7),
            (10,'NYGiants','NYJets',-3),
            (10,'Arizona','TampaBay',-4.5),
            (10,'Miami','Indianapolis',-9.5),
            (10,'LARams','Pittsburgh',1.5),
            (10,'Minnesota','Dallas',-3),
            (10,'Seattle','SanFrancisco',-2.5),

            (11,'Pittsburgh','Cleveland',-3),
            (11,'Dallas','Detroit',2.5),
            (11,'Jacksonville','Indianapolis',-6.5),
            (11,'Buffalo','Miami',-1.5),
            (11,'Denver','Minnesota',-6),
            (11,'NewOrleans','TampaBay',4),
            (11,'NYJets','Washington',-1),
            (11,'Atlanta','Carolina',-2.5),
            (11,'Houston','Baltimore',-3),
            (11,'Arizona','SanFrancisco',-8.5),
            (11,'Cincinnati','Oakland',-3.5),
            (11,'NewEngland','Philadelphia',-1.5),
            (11,'Chicago','LARams',-4.5),
            (11,'KansasCity','LAChargers',2.5),

            (12,'Indianapolis','Houston',-2),
            (12,'TampaBay','Atlanta',-7),
            (12,'Denver','Buffalo',-3),
            (12,'NYGiants','Chicago',-9.5),
            (12,'Pittsburgh','Cincinnati',3),
            (12,'Miami','Cleveland',-8),
            (12,'Carolina','NewOrleans',-8.5),
            (12,'Oakland','NYJets',-3),
            (12,'Detroit','Washington',-2),
            (12,'Jacksonville','Tennessee',-3),
            (12,'Dallas','NewEngland',-6.5),
            (12,'GreenBay','SanFrancisco',1),
            (12,'Seattle','Philadelphia',-3.5),
            (12,'Baltimore','LARams',-7),

            (13,'Chicago','Detroit',3),
            (13,'Buffalo','Dallas',-7),
            (13,'NewOrleans','Atlanta',3),
            (13,'NYJets','Cincinnati',-1.5),
            (13,'Tennessee','Indianapolis',-7),
            (13,'Oakland','KansasCity',-13),
            (13,'Philadelphia','Miami',4),
            (13,'GreenBay','NYGiants',3.5),
            (13,'Washington','Carolina',-5),
            (13,'TampaBay','Jacksonville',-5),
            (13,'SanFrancisco','Baltimore',-3.5),
            (13,'LARams','Arizona',8),
            (13,'LAChargers','Denver',1),
            (13,'Cleveland','Pittsburgh',-3.5),
            (13,'NewEngland','Houston',3),
            (13,'Minnesota','Seattle',-3),

            (14,'Dallas','Chicago',-3.5),
            (14,'Carolina','Atlanta',-4.5),
            (14,'Baltimore','Buffalo',1),
            (14,'Cincinnati','Cleveland',-8),
            (14,'Washington','GreenBay',-9),
            (14,'Detroit','Minnesota',-8),
            (14,'SanFrancisco','NewOrleans',-8),
            (14,'Miami','NYJets',-6),
            (14,'Indianapolis','TampaBay',3),
            (14,'Denver','Houston',-5.5),
            (14,'LAChargers','Jacksonville',0),
            (14,'Tennessee','Oakland',-1),
            (14,'KansasCity','NewEngland',-3),
            (14,'Pittsburgh','Arizona',3.5),
            (14,'Seattle','LARams',-7),
            (14,'NYGiants','Philadelphia',-8.5),

            (15,'NYJets','Baltimore',-6),
            (15,'NewEngland','Cincinnati',7),
            (15,'TampaBay','Detroit',-2.5),
            (15,'Chicago','GreenBay',-2.5),
            (15,'Houston','Tennessee',-1),
            (15,'Denver','KansasCity',-9.5),
            (15,'Miami','NYGiants',-3),
            (15,'Buffalo','Pittsburgh',-7),
            (15,'Philadelphia','Washington',3.5),
            (15,'Seattle','Carolina',-3),
            (15,'Jacksonville','Oakland',1),
            (15,'Cleveland','Arizona',3),
            (15,'LARams','Dallas',1),
            (15,'Atlanta','SanFrancisco',-1.5),
            (15,'Minnesota','LAChargers',-4),
            (15,'Indianapolis','NewOrleans',-5),

            (16,'Detroit','Denver',-4.5),
            (16,'Buffalo','NewEngland',-13),
            (16,'Oakland','LAChargers',-9),
            (16,'LARams','SanFrancisco',3),
            (16,'Houston','TampaBay',2),
            (16,'Jacksonville','Atlanta',-5),
            (16,'NewOrleans','Tennessee',3),
            (16,'Baltimore','Cleveland',-3),
            (16,'Carolina','Indianapolis',-6),
            (16,'Cincinnati','Miami',-1.5),
            (16,'Pittsburgh','NYJets',2.5),
            (16,'NYGiants','Washington',-3),
            (16,'Dallas','Philadelphia',-4),
            (16,'Arizona','Seattle',-12),
            (16,'KansasCity','Chicago',-1.5),
            (16,'GreenBay','Minnesota',-3),
        ]
        self.PICKED = [
             'Philadelphia',
             'Baltimore',
             'Dallas',
             'LAChargers',
        ]
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
