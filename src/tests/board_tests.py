'''
Created on Dec. 12, 2021

@author: Ryan
'''
import unittest
import collections
from .owl import rules
from .owl import board


class Test(unittest.TestCase):
    deck = None

    def setUp(self):
        ruleset = rules.Rules()
        self.deck = board.Deck(ruleset)
        self.deck.create()

    def tearDown(self):
        pass


    def testGet(self):
        ''' Tests if cards can be drawn until None is returned
            with a total size < 60 (36+14=50 with default rules) '''

        counter = 0
        while True:
            single_card = self.deck.get_top_card()
            if single_card is None:
                break
            self.assertTrue(isinstance(single_card, board.Card))
            counter += 1
            self.assertFalse(counter > 60)

    def testCardCount(self):
        ''' Tests if default rules give the correct number of each type of card '''
        card_counter = collections.Counter()
        for single_card in self.deck:


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()