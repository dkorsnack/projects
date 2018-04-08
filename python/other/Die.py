# $Id: Die.py 45 2013-10-06 15:57:20Z korsnack $
#!/bin/python

from random import choice
from itertools import product

class Die(object):

    def __init__(
        self,
        die = [1,2,3,4,5,6],
    ):
        self.die = die

    def roll(self, n):
        return [choice(self.die) for i in range(n)]

    def prod(self, m):
        return [p for p in product(self.die, repeat=m)]
