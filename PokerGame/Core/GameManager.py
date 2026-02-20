from Core.Game import Game
from enum import Enum

class GameManager:
    def __init__(self):
        self.game: Game = Game()
        self._round: GamePhase = GamePhase.WAITING_FOR_PLAYERS
    
    @property
    def round(self):
        return self._round
    
    @round.setter
    def round(self, value: GamePhase | int):
        if isinstance(value, GamePhase):
            self._round = value
        elif isinstance(value, int):
            try:
                self._round = GamePhase(value)
            except ValueError:
                raise ValueError(f"Invalid round value: {value}. Must be an integer corresponding to a GamePhase.")
        else:
            raise TypeError(f"Round must be set to a GamePhase enum member or an integer, got {type(value)}")
    
    def start_new_game(self):
        """Start a new game by resetting the game state and setting the round to PRE_FLOP."""
        self.game.new_game()  # Reset the game state for a new game
        self.round = GamePhase.PRE_FLOP  # Start with the pre-flop phase
        
    def play_pre_flop(self):
        """Handle the pre-flop phase of the game."""
        self.game.deal_cards()  # Deal hole cards to players
        self.game.deal_blinds()  # Handle blinds for the pre-flop phase

class GamePhase(Enum):
    WAITING_FOR_PLAYERS = 0
    PRE_FLOP = 1
    FLOP = 2
    TURN = 3
    RIVER = 4