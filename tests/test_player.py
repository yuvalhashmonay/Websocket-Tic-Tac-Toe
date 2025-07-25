from tic_tac_toe.game import TicTacToe
from tic_tac_toe.game_series import GameSeries
from tic_tac_toe.player import HumanPlayer, RobotPlayer
import unittest


class TestPlayer(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        print('setupClass')

    @classmethod
    def tearDownClass(cls):
        print('teardownClass')

    def setUp(self):
        print('setUp')

    def tearDown(self):
        print('tearDown\n')
    def test_player_type(self):
        game_series = GameSeries(number_of_human_players=1)
        self.assertIs(type(game_series.player1), HumanPlayer)
        self.assertIs(type(game_series.player2), RobotPlayer)

        game_series = GameSeries(number_of_human_players=2)
        self.assertIs(type(game_series.player1), HumanPlayer)
        self.assertIs(type(game_series.player2), HumanPlayer)

    def test_marks_assignment(self):
        for number_of_human_players in range(1,3):
            game_series = GameSeries(number_of_human_players=number_of_human_players)
            self.assertNotEqual(game_series.player1.mark, game_series.player2.mark)
            self.assertNotEqual(game_series.player1.mark, game_series.game.available_mark)
            self.assertNotEqual(game_series.player2.mark, game_series.game.available_mark)


if __name__ == '__main__':
    unittest.main()



