from .Deck import Deck
from .Card import Card
from .Player import Player
from enum import Enum

# TODO: Implement the logic for pre-flop, flop, turn, and river rounds, including betting and hand evaluation.

class Game:
    def __init__(self):
        self.players = []
        self._deck = Deck()
        self._round: GamePhase = GamePhase.WAITING_FOR_PLAYERS
        self.pot = 0
        self._current_bets: dict[Player, int] = {}
        self._total_bets: dict[Player, int] = {}
        self._community_cards: list[Card] = []
        
    @property
    def round(self):
        return self._round
    
    @round.setter
    def round(self, value):
        if isinstance(value, GamePhase):
            self._round = value
        elif isinstance(value, int):
            try:
                self._round = GamePhase(value)
            except ValueError:
                raise ValueError(f"Invalid round value: {value}. Must be an integer corresponding to a GamePhase.")
        else:
            raise TypeError(f"Round must be set to a GamePhase enum member or an integer, got {type(value)}")
    
    def bets_are_equal(self):
        """Check if all players have equal bets in the current round."""
        if not self.players:
            return True  # No players, so bets are trivially equal
        
        if len(self._current_bets) < 2:
            return True  # Only one player, so bets are trivially equal)
        
        for bet in self._current_bets.values():
            if bet != self._current_bets[self.players[0]]:
                return False  # Found a bet that is different from the first player's bet
        
        return True  # All bets are equal
        
    def _nextRound(self):
        """Advance to the next round in the game."""
        if self._round == GamePhase.RIVER:
            raise ValueError("Already at the final round (RIVER). Cannot advance further.")
        
        self._round = GamePhase(self._round.value + 1)
        self._resetBets()  # Reset bets for the new round
        self.pot = 0  # Reset the pot for the new round
        
    def _resetBets(self):
        """Reset the current bets for all players."""
        self._current_bets = {player: 0 for player in self.players}
    
    def newGame(self):
        """Start a new round of the game, resetting necessary state."""
        self._deck.reset()
        self.pot = 0
        self.round = GamePhase.PRE_FLOP  # Start at the pre-flop round for a new game
    
    def startGame(self):
        if len(self.players) < 2:
                raise ValueError("Not enough players to start the game. At least 2 players are required.")        
        else:
            self._nextRound()  # Move to the pre-flop round to start the game
        
    def playRound(self):
        """Placeholder for the logic to play through a round of the game."""
        if round == GamePhase.WAITING_FOR_PLAYERS:    
            self.startGame()
        elif round == GamePhase.PRE_FLOP:
            pass # implement pre-flop logic here
        
        pass
                
    def addPlayer(self, player: Player):
        """Add a player to the game."""
        self.players.append(player)
        
class GamePhase(Enum):
    WAITING_FOR_PLAYERS = 0
    PRE_FLOP = 1
    FLOP = 2
    TURN = 3
    RIVER = 4
    
__all__ = ["Game", "GamePhase"]