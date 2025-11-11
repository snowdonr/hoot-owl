"""Basic tests for the exhaustive-min-moves solver.

These tests use a reduced number of owls to keep the search small and
deterministic for test runs.
"""
import unittest

from owl import rules, board, simulation


class TestSimulation(unittest.TestCase):
	def test_min_moves_small_board(self):
		r = rules.Rules()
		# reduce owl count to make exhaustive search cheap
		r.number_of_owls = 2
		b = board.Board(r)
		# search with a modest depth cap; should find a solution
		moves = simulation.min_moves_to_finish_all(b, target_finished=2, max_depth=50)
		self.assertIsNotNone(moves)
		self.assertIsInstance(moves, int)
		self.assertTrue(moves >= 0)

	def test_min_moves_with_deck(self):
		r = rules.Rules()
		# make deck small and remove suns to avoid early failure in test
		r.number_of_owls = 2
		r.number_of_suns = 0
		r.card_color_multiple = 2
		r.hand_size = 3
		b = board.Board(r)
		d = board.Deck(r)
		d.create()
		# don't shuffle: deterministic order
		# seed a hand from deck and run solver
		moves = simulation.min_moves_with_deck(b, d, target_finished=2, max_depth=200, rules=r)
		self.assertIsNotNone(moves)
		self.assertIsInstance(moves, int)
		self.assertTrue(moves >= 0)


if __name__ == "__main__":
	unittest.main()

