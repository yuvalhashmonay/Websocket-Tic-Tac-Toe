from abc import ABC, abstractmethod
from turns_validator import TurnsValidator # later make just make TurnsValidator something an attribute of the TurnsGame abstract parent class
from enum import Enum, auto


class TurnsGame(ABC):
    class GameStatus(Enum):
        AWAITING_START = auto()
        IN_PROGRESS = auto()
        ENDED = auto()

    def __init__(self):
        self.turns_validator = TurnsValidator(self)
        self.status = TurnsGame.GameStatus.AWAITING_START

    def get_current_player(self):  # NOTE - The child has to have self.current_player
        return self.current_player
    @abstractmethod
    def move_format_is_correct(self):
        pass
    @abstractmethod
    def move_is_legal(self):
        pass

    @abstractmethod
    def parse_move(self):
        pass



