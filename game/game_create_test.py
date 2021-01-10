import unittest
import random
from mafia import Game, Player, generate_code

class TestGame(unittest.TestCase):
    def setUp(self):
        self.game = Game()

    def test_addPlayers(self):
        self.test_size = random.randint(1, 20)
        for i in range(self.test_size):
            player = Player(i, generate_code(8))
            self.game.addPlayer(player)
        self.assertEqual(self.game.size, self.test_size)