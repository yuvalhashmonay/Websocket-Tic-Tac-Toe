from .game import TicTacToe
from .player import HumanPlayer, RobotPlayer

class GameSeries:
    def __init__(self, number_of_human_players, player1_name=None, player2_name=None):
        if not number_of_human_players in {1, 2}:
            raise Exception(f"Number of human players must best 1 or 2, received {number_of_human_players}")
        self.number_of_human_players = number_of_human_players
        self.player1 = HumanPlayer(player1_name)
        if number_of_human_players == 2:
            self.player2 = HumanPlayer(player2_name, number=2)
        else:
            self.player2 = RobotPlayer("Computer", number=2)
        self.total_number_of_games = 0
        self.ties = 0
        self.create_new_game()

    def create_new_game(self):
        self.game = TicTacToe(self)

    def add_game_results(self):
        """
        This method adds the winner's points via the game object,
        but it's ok cause the game series also has the references to the player objects,
        so it persists through all future game. 
        """
        if self.game.winner:
            self.game.winner.wins += 1
        else:
            self.ties += 1
        self.total_number_of_games += 1

    def get_score_str(self):
        return \
            f"""{self.player1.name}\t({self.player1.mark}):\tWins = {self.player1.wins}
            {self.player2.name}\t({self.player2.mark}):\tWins = {self.player2.wins}
            Draws = {self.total_number_of_games - self.player1.wins - self.player2.wins}"""
    def print_score(self):
        print(self.get_score_str())