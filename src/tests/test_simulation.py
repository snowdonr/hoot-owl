'''
Created on Dec. 30, 2021

@author: Ryan
'''
import unittest

from owl import board
from owl import rules


class Test(unittest.TestCase):
    ruleset = None

    def setUp(self):
        self.ruleset = rules.Rules()
        self.deck = board.Deck(self.ruleset)
        self.deck.create()
        self.board = board.Board(self.ruleset)

    def tearDown(self):
        pass

    def test_integration_play(self):
        self.board