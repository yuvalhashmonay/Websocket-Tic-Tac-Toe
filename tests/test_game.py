from tic_tac_toe.game_series import GameSeries
import unittest
class TestGame(unittest.TestCase):

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

    def test_move_is_legal(self):
        game_series = GameSeries(number_of_human_players=2)
        moves = {(0, 0), (0, 1), (2, 1)}
        for move in moves:
            game_series.game.board[move[0]][move[1]] = game_series.player1.mark

        for i in range(len(game_series.game.board)):
            for j in range(len(game_series.game.board[i])):
                move = (i,j)
                if move in moves:
                    self.assertFalse(game_series.game.move_is_legal(move))
                else:
                    self.assertTrue(game_series.game.move_is_legal(move))


if __name__ == '__main__':
    unittest.main()



