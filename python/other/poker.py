# $Id: poker.py 45 2013-10-06 15:57:20Z korsnack $
#!/bin/python

from Cards import Deck

D = Deck()

# sum multiplicity vector
def summv(count):
    return [
        sum(z) for z in zip(count[0], count[1], count[2], count[3], count[4])
    ]

# two card absolute sequence differences
def tcd(ranks):
    return [
        abs(ranks[0]-ranks[1]), abs(ranks[0]-ranks[2]),
        abs(ranks[0]-ranks[3]), abs(ranks[0]-ranks[4]),
        abs(ranks[1]-ranks[2]), abs(ranks[1]-ranks[3]),
        abs(ranks[1]-ranks[4]), abs(ranks[2]-ranks[3]),
        abs(ranks[2]-ranks[4]), abs(ranks[3]-ranks[4]),
    ]

# denomination multiplicity vector
def dmv(hand):
    denomination = D.getDenomination(hand)
    count = [
        [1 if d == x else 0 for x in D.denomination] for d in denomination
    ]
    total = summv(count)
    dv = [total.count(r) for r in range(5)]
    assert sum(dv) == 13
    assert sum([dv[r]*r for r in range(5)]) == 5
    return tuple(dv)

# suit multiplicity vector
def smv(hand):
    sts = D.getSuit(hand)
    count = [[1 if s == x else 0 for x in D.suit] for s in sts]
    total = summv(count)
    sv = [total.count(r) for r in range(6)]
    assert sum(sv) == 4
    assert sum([sv[r]*r for r in range(6)]) == 5
    return tuple(sv)

# sequence multiplicity vector
def seqmv(hand):
    dr = dict(list(zip(D.denomination, list(range(13)))))
    denomination = D.getDenomination(hand)
    ranks = [dr[d] for d in denomination]
    if denomination.count('A') == 0:
        total = tcd(ranks)
    else:
        total_AL = tcd(ranks)
        ranks_AH = [r if r != 1 else 14 for r in ranks]
        total_AH = tcd(ranks_AH)
        total = [min(tAL, tAH) for (tAL, tAH) in zip(total_AL, total_AH)]
    sq = [total.count(r) for r in range(1, 12)]
    return tuple(sq)

# ranking hands
# total ways: cmbin(52, 5) = 2598960

# ranking tables:
#  - using denomination:
RANK = {
#   {_____dmv:______________term____________ways_____P(dmv)}
    (11, 1, 0, 0, 1): "four_of_a_kind",  # 624     0.00024
    (11, 0, 1, 1, 0): "full_house",      # 3744    0.00144
    (10, 2, 0, 1, 0): "three_of_a_kind", # 54912   0.02112
    (10, 1, 2, 0, 0): "two_pair",        # 123552  0.04753
    ( 9, 3, 1, 0, 0): "one_pair",        # 1098240 0.42256
    ( 8, 5, 0, 0, 0): "no_pair",         # 1317888 0.50708
}

#  - using suits and sequences
NOPAIR = {
#   {(Flush, Straight):___term___________ways_____P(F, S)}
    ( True,  True): "straight_flush",  # 40      0.00002
    ( True, False): "flush",           # 5108    0.00196
    (False,  True): "straight",        # 10200   0.00392
    (False, False): "nothing",         # 1302540 0.50117
}

def rank(hand):
    dv = dmv(hand)
    if RANK[dv] != "no_pair":
        return RANK[dv]
    sv = smv(hand)
    sq = seqmv(hand)
    flushStraight = (
        True if sv == (3, 0, 0, 0, 0, 1) else False,
        True if sq == (4, 3, 2, 1, 0, 0, 0, 0, 0, 0, 0) else False
    )
    return NOPAIR[flushStraight]

# regressing the hand probabilities
if __name__ == '__main__':
    num = 1000000
    hnds = [rank(D.hand()) for i in range(num)]
    terms = list(RANK.values()) + list(NOPAIR.values())
    output = [(t, float(hnds.count(t)) / num) for t in terms if t != "no_pair"]
    total_p = sum([o[1] for o in output])
    assert total_p < 1.00001 and total_p > 0.99999
    for o in sorted(output):
        print("%-16s %0.5f" % o)
