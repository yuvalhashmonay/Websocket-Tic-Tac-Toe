import random
import sys
import os
# Get the directory containing this file
current_dir = os.path.dirname(os.path.abspath(__file__))

# Add the parent directory to sys.path
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from turns_game import TurnsGame

class TicTacToe(TurnsGame):
    def __init__(self, game_series):
        super().__init__()
        self.available_mark = '_'
        self.board = [[self.available_mark, self.available_mark, self.available_mark] for _ in range(3)]
        self.game_series = game_series
        self.player1 = game_series.player1
        self.player2 = game_series.player2
        if self.game_series.number_of_human_players == 1:
            self.player2.set_game(self)
        self.players = [self.player1, self.player2]
        self.players_index = random.randint(0,1)
        self.current_player = self.players[self.players_index]
        self.turns_played = 0
        self.number_of_turns_to_execute = 1 + 2 - self.game_series.number_of_human_players
        self.is_over = False
        self.winner = None
        self.start()

    def __switch_current_player(self):
        self.players_index = not self.players_index
        self.current_player = self.players[self.players_index]

    def print_turn_info(self):
        print(f"\n\t***  {self.current_player.name} ({self.current_player.mark}) Turn ***")
        self.print_board()

    def execute_move(self):
        chosen_square = self.current_player.choose_square()
        row_index, column_index = chosen_square
        self.board[row_index][column_index] = self.current_player.mark

    def act(self, move):
        self.current_player.next_move = move  # (current_player in this line will always be human)
        for _ in range(self.number_of_turns_to_execute):
            self.execute_turn()
            if self.is_over:
                break
    def alternative_act(self, move):
        """
        This is a concept for an alternative act method that will even for a mix of more than 2 human and robot players.
          # THe signature doesn't have a move parameter, the current player's move that triggered this
         method was already set for the player object from outside.

       IMPORTANT NOTE
        For this to work, both HumanPlayer and RobotPlayer need to have the get_next_move method.
         For HumanPlayer, that method will just return the next_move attribute, which is set "manually" ourselves
         So it'll just be None if we didn't.
                 def choose_square(self):
                    return self.get_next_move()
                def get_next_move(self):
                    return self.next_move

         For RobotPlayer, get_next_move will always just be an intermediate to return what choose_square returns,
          so it will never return None.
              def get_next_move(self):
                return self.choose_square()

        We also need to change the execute_turn not to call choose_square again, instead we'll need to pass down the move
          value from the "act" method all the way down to the execute move method.
         or pass it to it .
        """
        self.current_player.next_move = move
        while True:
            move = self.current_player.next_move
            if move is None:  # Evaluates to True when the next player is Human
                break
            self.execute_turn()
            self.current_player.next_move = None
            if self.is_over:
                break


    def execute_turn(self):
        self.execute_move()
        self.turns_played += 1
        if self._is_over():
            self.status = TicTacToe.GameStatus.ENDED
            self.game_series.add_game_results()
            self.print_board()
            return
        self.__switch_current_player()

    def start(self):
        """
        This method is for handling a single player game, where the computer has the first move.
        """
        if self.game_series.number_of_human_players == 1 and self.current_player == self.player2:
            self.execute_turn()


    def player_won(self, board, player, do_prints=True):

        def completed_row_or_column():
            for i in range(3):
                # In this loop, self.board[i][i] is always the shared square between a row and a column.
                if board[i][i] != self.available_mark:
                    if board[i][0] == board[i][1] == board[i][2] or board[0][i] == board[1][i] == board[2][i]:
                        return True
            return False

        def completed_diagonal():
            if board[1][1] != self.available_mark:  # (The center square of the board is shared by the two diagonals.)
                if board[0][0] == board[1][1] == board[2][2] or board[0][2] == board[1][1] == board[2][0]:
                    return True
            return False

        if completed_row_or_column() or completed_diagonal():
            if do_prints:
                print(f"\n!!!!!!!!!\t{player.mark} wins\t!!!!!!!!!")
            self.winner = player
            return True
        return False

    def ended_in_tie(self, board, do_prints=True):
        """"
        (This is a simple method, it doesn't check if the game can only end in tie before the game is over)
        """
        for row in board:
            if self.available_mark in row:
                return False
        if do_prints:
            print(f"- - - - - - - - -\tGAME TIED\t- - - - - - - - -")
        self.winner = None
        return True

    def _is_over(self):
        if self.player_won(self.board, self.current_player) or self.ended_in_tie(self.board):
            self.is_over = True
        return self.is_over

    def print_instructions(self):
        print("§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§\tINSTRUCTIONS START\t§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§")
        print("To place your mark in a square, enter the number of row followed by the number of column. For example, putting an X at input '01' will give us:")
        print("     0   1   2\n    ___ ___ ___\n0  |___|_X_|___|\n1  |___|___|___|\n2  |___|___|___|\n\n\n")
        print("§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§\tINSTRUCTIONS END\t§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§")

    def move_is_legal(self, move: tuple):
        return self.square_is_available(move[0], move[1])

    def square_is_available(self, row, column):
        return self.board[row][column] == self.available_mark

    def move_format_is_correct(self, square_input):
        """Expecting a str like '01', '21', '00'...'"""
        return (type(square_input) == str and len(square_input) == 2 and square_input[0] in {'0', '1', '2'} and
                square_input[1] in {'0', '1', '2'})

    def parse_move(self, raw_move: str) -> tuple:
        return int(raw_move[0]), int(raw_move[1])

    def print_board(self):
        print("     0   1   2\n    ___ ___ ___")
        for i, line in enumerate(self.board):
            print(f"{i}  |_{line[0]}_|_{line[1]}_|_{line[2]}_|")