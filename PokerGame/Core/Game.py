from Core.Deck import Deck
from Core.Card import Card
from Core.Player import Player
from enum import Enum

class Game:
    def __init__(self, small_blind: int = 10, big_blind: int = 20):
        self.players: list[Player] = []
        self.players_in_round: list[Player] = []  # Track players still active in the current round
        
        self.deck: Deck = Deck()
        
        self.pot: int = 0
        self.current_bets: dict[Player, int] = {}
        
        self.community_cards: list[Card] = []
        
        self.dealer_position: int = -1  # Index of the dealer in the players list
        
        self.small_blind: int = small_blind
        self.big_blind: int = big_blind

    @property
    def ready_players(self):
        """Return a list of players who are ready to play."""
        return [player for player in self.players if player.ready]
    
    @property
    def small_blind_player_index(self) -> int:
        """Return the player index in the players_in_round who is currently posting the small blind."""
        if not self.players_in_round:
            raise ValueError("No active players in the round to determine small blind.")
        
        # return the index of the player who is posting the small blind (the player immediately to the left of the dealer)
        return (self.dealer_position + 1) % len(self.players_in_round)
    
    def utg_player_index(self) -> int:
        """Return the player index in the players_in_round of who is currently in the Under the Gun (UTG) position."""
        if not self.players_in_round:
            raise ValueError("No active players in the round to determine UTG.")
        
        # return the index of the player who is in the UTG position (the player immediately to the left of the big blind)
        return (self.dealer_position + 3) % len(self.players_in_round)
    
    def bets_are_equal(self):
        """Check if all players have equal bets in the current round."""
        if not self.players_in_round or not self.current_bets:
            raise ValueError("No players in the game to compare bets.")
        
        if len(self.current_bets) < 2:
            return True  # Only one player, so bets are trivially equal)
        
        bets = list(self.current_bets.values())
        return all(bet == bets[0] for bet in bets)
    
    def add_player(self, player: Player):
        """Add a player to the game."""
        self.players.append(player)
        
    def new_game(self):
        """Start a new game by resetting the deck, pot, and player states."""
        self.deck = Deck()  # Reset the deck for a new game
        self.current_bets.clear()
        self.community_cards.clear()
        
        self.players_in_round = self.ready_players  # Only players who are ready can participate in the new game
        if len(self.players_in_round) < 2:
            raise ValueError("At least 2 players must be ready to start a new game.")
        
        self.current_bets = {player: 0 for player in self.players_in_round}  # Reset bets for all players in the round
        
        self.dealer_position += 1  # Move the dealer position to the next player for the new game
        
    def start_new_round(self):
        self.current_bets = {player: 0 for player in self.players_in_round}  # Reset bets for all players in the new round
    
    def add_bet(self, player: Player, amount: int):
        """Add a bet for a player and update the pot."""
        if player not in self.players_in_round:
            raise ValueError(f"{player.name} is not currently active in the round and cannot bet.")
        
        bet_amount = player.place_bet(amount)  # This will deduct the chips from the player
        
        # Update current bets and total bets for the player
        self.current_bets[player] = self.current_bets.get(player, 0) + bet_amount
        
        self.pot += bet_amount  # Add the bet to the pot
        
    def deal_cards(self):
        """deal player hands"""
        if not self.players_in_round:
            raise ValueError("No active players in the round to deal cards to.")
        elif len(self.players_in_round) < 2:
            raise ValueError("Not enough active players in the round to deal cards.")
        
        for player in self.players_in_round:
            card1 = self.deck.draw_card()
            card2 = self.deck.draw_card()
            
            player.receive_cards(card1, card2)
            
    def deal_community_cards(self, number: int):
        """Deal community cards to the table."""
        if number < 1 or number > 5:
            raise ValueError("Number of community cards must be between 1 and 5.")
        elif len(self.community_cards) + number > 5:
            raise ValueError("Cannot deal more than 5 community cards in total.")
        
        for _ in range(number):
            card = self.deck.draw_card()
            self.community_cards.append(card)
        
    def deal_blinds(self):
        """Handle the posting of blinds by the appropriate players."""
        if len(self.players_in_round) < 2:
            raise ValueError("Not enough players to post blinds.")
        
        small_blind_player = self.players_in_round[(self.dealer_position + 1) % len(self.players_in_round)]
        big_blind_player = self.players_in_round[(self.dealer_position + 2) % len(self.players_in_round)]
        
        self.add_bet(small_blind_player, self.small_blind)
        self.add_bet(big_blind_player, self.big_blind)
        
    def fold_player(self, player: Player):
        """Handle a player folding their hand."""
        if player not in self.players_in_round:
            raise ValueError(f"{player.name} is not currently active in the round and cannot fold.")
        
        self.players_in_round.remove(player)  # Remove the player from the active players in the round
    
__all__ = ["Game"]