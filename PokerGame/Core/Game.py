from .Deck import Deck
from .Card import Card
from .Player import Player
from enum import Enum

# TODO: Implement the logic for pre-flop, flop, turn, and river rounds, including betting and hand evaluation.
# TODO: Implement checking for what hand each player has based on their hole cards and the community cards (e.g., pair, two pair, three of a kind, straight, flush, full house, four of a kind, straight flush, royal flush).

class Game:
    def __init__(self, small_blind: int = 10, big_blind: int = 20):
        self.players: list[Player] = []
        self.players_in_round: list[Player] = []  # Track players still active in the current round
        
        self.deck: Deck = Deck()
        self._round: GamePhase = GamePhase.WAITING_FOR_PLAYERS
        
        self.pot: int = 0
        self.current_bets: dict[Player, int] = {}
        
        self.community_cards: list[Card] = []
        
        self.dealer_position: int = -1  # Index of the dealer in the players list
        
        self.small_blind: int = small_blind
        self.big_blind: int = big_blind

    @property
    def readyPlayers(self):
        """Return a list of players who are ready to play."""
        return [player for player in self.players if player.ready]
    
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
    
    def betsAreEqual(self):
        """Check if all players have equal bets in the current round."""
        if not self.players_in_round or not self.current_bets:
            raise ValueError("No players in the game to compare bets.")
        
        if len(self.current_bets) < 2:
            return True  # Only one player, so bets are trivially equal)
        
        for bet in self.current_bets.values():
            if bet != self.current_bets[self.players[0]]:
                return False  # Found a bet that is different from the first player's bet
        
        return True  # All bets are equal
    
    def addPlayer(self, player: Player):
        """Add a player to the game."""
        self.players.append(player)
        
    def newGame(self):
        """Start a new game by resetting the deck, pot, and player states."""
        self.deck = Deck()  # Reset the deck for a new game
        self.current_bets.clear()
        self.community_cards.clear()
        
        self.players_in_round = self.readyPlayers  # Only players who are ready can participate in the new game
        self.current_bets = {player: 0 for player in self.players_in_round}  # Reset bets for all players in the round
        
        self.round = GamePhase.PRE_FLOP  # Start with the pre-flop phase
        self.dealer_position += 1  # Move the dealer position to the next player for the new game
        
    def nextRound(self):
        """Advance to the next round of the game."""
        if self.round == GamePhase.PRE_FLOP:
            self.round = GamePhase.FLOP
        elif self.round == GamePhase.FLOP:
            self.round = GamePhase.TURN
        elif self.round == GamePhase.TURN:
            self.round = GamePhase.RIVER
        else:
            raise ValueError("Cannot advance round beyond RIVER. Start a new game instead.")
    
    def addBet(self, player: Player, amount: int):
        """Add a bet for a player and update the pot."""
        if player not in self.players_in_round:
            raise ValueError(f"{player.name} is not currently active in the round and cannot bet.")
        
        bet_amount = player.place_bet(amount)  # This will deduct the chips from the player
        
        # Update current bets and total bets for the player
        self.current_bets[player] = self.current_bets.get(player, 0) + bet_amount
        
    def dealCards(self):
        """deal player hands"""
        if not self.players_in_round:
            raise ValueError("No active players in the round to deal cards to.")
        elif len(self.players_in_round) < 2:
            raise ValueError("Not enough active players in the round to deal cards.")
        
        for player in self.players_in_round:
            card1 = self.deck.draw_card()
            card2 = self.deck.draw_card()
            
            player.receive_cards(card1, card2)
            
    def dealCommunityCards(self, number: int):
        """Deal community cards to the table."""
        if number < 1 or number > 5:
            raise ValueError("Number of community cards must be between 1 and 5.")
        elif len(self.community_cards) + number > 5:
            raise ValueError("Cannot deal more than 5 community cards in total.")
        
        for _ in range(number):
            card = self.deck.draw_card()
            self.community_cards.append(card)
        
    def dealBlinds(self):
        """Handle the posting of blinds by the appropriate players."""
        if len(self.players) < 2:
            raise ValueError("Not enough players to post blinds.")
        
        small_blind_player = self.players_in_round[(self.dealer_position + 1) % len(self.players_in_round)]
        big_blind_player = self.players_in_round[(self.dealer_position + 2) % len(self.players_in_round)]
        
        self.addBet(small_blind_player, self.small_blind)
        self.addBet(big_blind_player, self.big_blind)
            
class GamePhase(Enum):
    WAITING_FOR_PLAYERS = 0
    PRE_FLOP = 1
    FLOP = 2
    TURN = 3
    RIVER = 4
    
__all__ = ["Game", "GamePhase"]