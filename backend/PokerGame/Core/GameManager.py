from Core.Game import Game
from enum import Enum
# import asyncio

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
        self.round = GamePhase.WAITING_FOR_PLAYERS  # Start with the Waiting For players
    
    def start_game(self):
        """Start game by goin to pre flop and dealing stuff out"""
        if self.round != GamePhase.WAITING_FOR_PLAYERS:
            raise RuntimeError("Cannot start game: game is not in WAITING_FOR_PLAYERS phase.")
        
        if len(self.game.players) < 2:
            raise RuntimeError("Cannot start game: not enough players. Must be at least 2.")
        
        self.next_round()
        
    def next_round(self):
        """move on to the next round by dealing blind cards or dealing community cards"""
        self.game.start_new_round()
        if self.round == GamePhase.WAITING_FOR_PLAYERS:
            self.round = GamePhase.PRE_FLOP
            self.game.deal_cards()
            self.game.deal_blinds()
            
        elif self.round == GamePhase.PRE_FLOP:
            self.round = GamePhase.FLOP
            self.game.deal_community_cards(3)
        
        elif self.round == GamePhase.FLOP:
            self.round = GamePhase.TURN
            self.game.deal_community_cards(1)
        
        elif self.round == GamePhase.TURN:
            self.round = GamePhase.RIVER
            self.game.deal_community_cards(1)
        
        elif self.round == GamePhase.RIVER:
            self.start_new_game()
class GamePhase(Enum):
    WAITING_FOR_PLAYERS = 0
    PRE_FLOP = 1
    FLOP = 2
    TURN = 3
    RIVER = 4