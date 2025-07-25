import random
from abc import ABC, abstractmethod
class Player(ABC):

    def __init__(self, name=None, number=1):
        if name is None:
            name = "player" + str(number)
        self.name = name
        self.number = number
        self.wins = 0
        self.mark = 'X' if self.number == 1 else 'O'

    def __eq__(self, other):
        return self.number == other.number

    @abstractmethod
    def choose_square(self):
        pass

class HumanPlayer(Player):

    def __init__(self, name=None, number=1):
        super().__init__(name=name, number=number)
        self._next_move = None

    def choose_square(self):
        return self.next_move
    @property
    def next_move(self):
        return self._next_move
    @next_move.setter
    def next_move(self, move):
        self._next_move = move

class RobotPlayer(Player):

    def set_game(self, game):
        self.game = game
    def choose_square(self):
        game = self.game

        if game.turns_played == 0:
            # To make the game more fun, the computer will choose a random square if the first turn of the game is its.
            return [random.randint(0,2), random.randint(0,2)]
        player_index = 1  # 1 is for current player (computer) and -1 is for the other human/computer player
        if game.current_player.number == 1:
            self.players_dict = {1: game.player1, -1: game.player2}
        else:
            self.players_dict = {1: game.player2, -1: game.player1}

        player = self.players_dict[player_index]
        board = game.board
        best_score = float('-inf')  # When maximizing
        level = 1
        self.minimum_levels_took_for_the_player_to_find_a_win_from_the_first_window = float('inf')
        best_square = None
        for i in range(3):
            for j in range(3):
                if board[i][j] == game.available_mark:
                    #  It's ok to change the original board and just cancel the marking in this iteration because we're
                    #  not continuing to the next round of the loop until all the recursion windows close.
                    board[i][j] = player.mark

                    if game.player_won(board, player, do_prints=False) or game.ended_in_tie(board, do_prints=False):
                        return [i, j]

                    score, number_of_levels_took_to_end_game = self.minimax(game, board, -player_index, level=level+1)
                    board[i][j] = game.available_mark

                    if score > best_score or best_square is None: # Shouldn't this if statement be true at least once?
                        # No, because sometimes we return -infinity
                        best_score = score
                        best_square = [i, j]

                        if score == 1:
                            self.minimum_levels_took_for_the_player_to_find_a_win_from_the_first_window = number_of_levels_took_to_end_game
                    elif score == best_score and number_of_levels_took_to_end_game < self.minimum_levels_took_for_the_player_to_find_a_win_from_the_first_window:
                        best_square = [i, j]
                        if score == 1:
                            self.minimum_levels_took_for_the_player_to_find_a_win_from_the_first_window = number_of_levels_took_to_end_game
        return best_square


    def minimax(self, game, board, player_index, level):

        player = self.players_dict[player_index]
        best_score = float('-inf') * player_index
        minimum_levels_took_for_player_in_current_recursion_call_to_get_current_best_score = float('inf')
        # if level < self.minimum_levels_took_for_the_player_to_find_a_win_from_the_first_window: # the call count is the same even without this statement
        for i in range(3):
            for j in range(3):
                if board[i][j] == game.available_mark:
                    # It's ok to change the original board and just cancel the marking in this round because we're not
                    # continuing to the next round of the loop until all the recursion windows close.
                    board[i][j] = player.mark

                    if game.player_won(board, player, do_prints=False):
                        board[i][j] = game.available_mark  # Erasing the change made to the board
                        return player_index, level  # We return 1 and -1 depending on the player and we also used these
                        # numbers to choose the correct player each time, so we can just return the index.

                    elif game.ended_in_tie(board, do_prints=False):
                        score, number_of_levels_took_to_end_game = 0, level
                        board[i][j] = game.available_mark

                    else:
                        score, number_of_levels_took_to_end_game = self.minimax(game, board, -player_index, level=level+1)
                        board[i][j] = game.available_mark


                    if score * player_index > best_score * player_index:
                        best_score = score
                        minimum_levels_took_for_player_in_current_recursion_call_to_get_current_best_score = number_of_levels_took_to_end_game

                    elif score == best_score and number_of_levels_took_to_end_game < minimum_levels_took_for_player_in_current_recursion_call_to_get_current_best_score:
                        minimum_levels_took_for_player_in_current_recursion_call_to_get_current_best_score = number_of_levels_took_to_end_game

        return best_score, minimum_levels_took_for_player_in_current_recursion_call_to_get_current_best_score



 