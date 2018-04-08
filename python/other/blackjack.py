#!/bin/python

import sys

TRANSLATE = {
    'H': 'hit',
    'S': 'stand',
    'Dh': 'double if allowed, otherwise hit',
    'Ds': 'double if allowed, otherwise stand',
    'P': 'split',
    'Ph': 'split if double after split is allowed, otherwise hit',
    'Rh': 'surrender if allowed otherwise hit'
}

STAND_ON_SOFT_SEVENTEEN = {
        #  2    3    4    5    6    7    8    9    T    A    Dealer / Player 
    'h': [                                                   #hard (no ace)
        [ 'H', 'H', 'H', 'H', 'H', 'H', 'H', 'H', 'H', 'H'], #4
        [ 'H', 'H', 'H', 'H', 'H', 'H', 'H', 'H', 'H', 'H'], #5
        [ 'H', 'H', 'H', 'H', 'H', 'H', 'H', 'H', 'H', 'H'], #6
        [ 'H', 'H', 'H', 'H', 'H', 'H', 'H', 'H', 'H', 'H'], #7
        [ 'H', 'H', 'H', 'H', 'H', 'H', 'H', 'H', 'H', 'H'], #8
        [ 'H','Dh','Dh','Dh','Dh', 'H', 'H', 'H', 'H', 'H'], #9
        ['Dh','Dh','Dh','Dh','Dh','Dh','Dh','Dh', 'H', 'H'], #10
        ['Dh','Dh','Dh','Dh','Dh','Dh','Dh','Dh','Dh', 'H'], #11
        [ 'H', 'H', 'S', 'S', 'S', 'H', 'H', 'H', 'H', 'H'], #12
        [ 'S', 'S', 'S', 'S', 'S', 'H', 'H', 'H', 'H', 'H'], #13
        [ 'S', 'S', 'S', 'S', 'S', 'H', 'H', 'H', 'H', 'H'], #14
        [ 'S', 'S', 'S', 'S', 'S', 'H', 'H', 'H','Rh', 'H'], #15
        [ 'S', 'S', 'S', 'S', 'S', 'H', 'H','Rh','Rh','Rh'], #16
        [ 'S', 'S', 'S', 'S', 'S', 'S', 'S', 'S', 'S', 'S'], #17
        [ 'S', 'S', 'S', 'S', 'S', 'S', 'S', 'S', 'S', 'S'], #18
        [ 'S', 'S', 'S', 'S', 'S', 'S', 'S', 'S', 'S', 'S'], #19
        [ 'S', 'S', 'S', 'S', 'S', 'S', 'S', 'S', 'S', 'S'], #20
    ],
    's': [                                                   #soft (has an ace)
        [ 'H', 'H', 'H','Dh','Dh', 'H', 'H', 'H', 'H', 'H'], #13
        [ 'H', 'H', 'H','Dh','Dh', 'H', 'H', 'H', 'H', 'H'], #14
        [ 'H', 'H','Dh','Dh','Dh', 'H', 'H', 'H', 'H', 'H'], #15
        [ 'H', 'H','Dh','Dh','Dh', 'H', 'H', 'H', 'H', 'H'], #16
        [ 'H','Dh','Dh','Dh','Dh', 'H', 'H', 'H', 'H', 'H'], #17
        [ 'S','Ds','Ds','Ds','Ds', 'S', 'S', 'H', 'H', 'H'], #18
        [ 'S', 'S', 'S', 'S', 'S', 'S', 'S', 'S', 'S', 'S'], #19
    ],
    'p': [                                                   #split
        ['Ph','Ph', 'P', 'P', 'P', 'P', 'H', 'H', 'H', 'H'], #2,2
        ['Ph','Ph', 'P', 'P', 'P', 'P', 'H', 'H', 'H', 'H'], #3,3
        [ 'H', 'H', 'H','Ph','Ph', 'H', 'H', 'H', 'H', 'H'], #4,4
        ['Dh','Dh','Dh','Dh','Dh','Dh','Dh','Dh', 'H', 'H'], #5,5
        ['Ph', 'P', 'P', 'P', 'P', 'H', 'H', 'H', 'H', 'H'], #6,6
        [ 'P', 'P', 'P', 'P', 'P', 'P', 'H', 'H', 'H', 'H'], #7,7
        [ 'P', 'P', 'P', 'P', 'P', 'P', 'P', 'P', 'P', 'P'], #8,8
        [ 'P', 'P', 'P', 'P', 'P', 'S', 'P', 'P', 'S', 'S'], #9,9
        [ 'S', 'S', 'S', 'S', 'S', 'S', 'S', 'S', 'S', 'S'], #T,T
        [ 'P', 'P', 'P', 'P', 'P', 'P', 'P', 'P', 'P', 'P'], #A,A
    ]
}

def number(card):
    return int({'T': 10, 'J': 10, 'Q': 10, 'K': 10, 'A': 11}.get(card, card))

def decide(args):
    hand_type, player, dealer = args[1:]
    if hand_type == 'h':
        i = 4
    elif hand_type == 's':
        i = 13
    elif hand_type == 'p':
        i = 2
    print(TRANSLATE[
        STAND_ON_SOFT_SEVENTEEN[hand_type][number(player)-i][number(dealer)-i]
    ])

if __name__ == "__main__":
    #$ python blackjack.py p 4 6 
    #$ python blackjack.py hand_type player dealer 
    #EV (dealer stands on soft 17, split up to 4 hands, double after split,
    #    double any two cards): -0.0043
    sys.exit(decide(sys.argv))
