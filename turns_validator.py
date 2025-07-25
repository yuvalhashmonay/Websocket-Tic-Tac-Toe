import logging
class TurnsValidator:

    def __init__(self, game):
        self.game = game

    def get_move(self, turn_request_data: dict):
        # Validate general request format
        if not turn_request_data.keys() == {'player_number', 'move'}:
            logging.warning(f"Failed in keys")
            return None
        # Validate correct player (Player number trusted since it comes form the session)
        if turn_request_data['player_number'] != self.game.current_player.number:
            logging.warning("Failed in player")
            return None
        # Validate move format
        if not self.game.move_format_is_correct(turn_request_data['move']):
            return None
        # Parse input to move
        move = self.game.parse_move(raw_move=turn_request_data['move'])
        # Validate move's legality
        if not self.game.move_is_legal(move):
            return None
        return move

