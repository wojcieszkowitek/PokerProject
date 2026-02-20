from Core.Deck import Deck
from Core.Card import Card
from Core.Player import Player
from enum import Enum

class Game:
    def __init__(self, small_blind: int = 10, big_blind: int = 20):
        self.players: list[Player] = []
        self.playersInRound: list[Player] = []  # Track players still active in the current round
        
        self.deck: Deck = Deck()
        
        self.pot: int = 0
        self.currentBets: dict[Player, int] = {}
        
        self.communityCards: list[Card] = []
        
        self.dealerPosition: int = -1  # Index of the dealer in the players list
        
        self.smallBlind: int = small_blind
        self.bigBlind: int = big_blind

    @property
    def readyPlayers(self):
        """Return a list of players who are ready to play."""
        return [player for player in self.players if player.ready]
    
    @property
    def smallBlindPlayerIndex(self) -> int:
        """Return the player index in the players_in_round who is currently posting the small blind."""
        if not self.playersInRound:
            raise ValueError("No active players in the round to determine small blind.")
        
        # return the index of the player who is posting the small blind (the player immediately to the left of the dealer)
        return (self.dealerPosition + 1) % len(self.playersInRound)
    
    def utgPlayerIndex(self) -> int:
        """Return the player index in the players_in_round of who is currently in the Under the Gun (UTG) position."""
        if not self.playersInRound:
            raise ValueError("No active players in the round to determine UTG.")
        
        # return the index of the player who is in the UTG position (the player immediately to the left of the big blind)
        return (self.dealerPosition + 3) % len(self.playersInRound)
    
    def betsAreEqual(self):
        """Check if all players have equal bets in the current round."""
        if not self.playersInRound or not self.currentBets:
            raise ValueError("No players in the game to compare bets.")
        
        if len(self.currentBets) < 2:
            return True  # Only one player, so bets are trivially equal)
        
        for bet in self.currentBets.values():
            if bet != self.currentBets[self.players[0]]:
                return False  # Found a bet that is different from the first player's bet
        
        return True  # All bets are equal
    
    def addPlayer(self, player: Player):
        """Add a player to the game."""
        self.players.append(player)
        
    def newGame(self):
        """Start a new game by resetting the deck, pot, and player states."""
        self.deck = Deck()  # Reset the deck for a new game
        self.currentBets.clear()
        self.communityCards.clear()
        
        self.playersInRound = self.readyPlayers  # Only players who are ready can participate in the new game
        if len(self.playersInRound) < 2:
            raise ValueError("At least 2 players must be ready to start a new game.")
        
        self.currentBets = {player: 0 for player in self.playersInRound}  # Reset bets for all players in the round
        
        self.dealerPosition += 1  # Move the dealer position to the next player for the new game
        
    def startNewRound(self):
        self.currentBets = {player: 0 for player in self.playersInRound}  # Reset bets for all players in the new round
    
    def addBet(self, player: Player, amount: int):
        """Add a bet for a player and update the pot."""
        if player not in self.playersInRound:
            raise ValueError(f"{player.name} is not currently active in the round and cannot bet.")
        
        bet_amount = player.place_bet(amount)  # This will deduct the chips from the player
        
        # Update current bets and total bets for the player
        self.currentBets[player] = self.currentBets.get(player, 0) + bet_amount
        
        self.pot += bet_amount  # Add the bet to the pot
        
    def dealCards(self):
        """deal player hands"""
        if not self.playersInRound:
            raise ValueError("No active players in the round to deal cards to.")
        elif len(self.playersInRound) < 2:
            raise ValueError("Not enough active players in the round to deal cards.")
        
        for player in self.playersInRound:
            card1 = self.deck.draw_card()
            card2 = self.deck.draw_card()
            
            player.receive_cards(card1, card2)
            
    def dealCommunityCards(self, number: int):
        """Deal community cards to the table."""
        if number < 1 or number > 5:
            raise ValueError("Number of community cards must be between 1 and 5.")
        elif len(self.communityCards) + number > 5:
            raise ValueError("Cannot deal more than 5 community cards in total.")
        
        for _ in range(number):
            card = self.deck.draw_card()
            self.communityCards.append(card)
        
    def dealBlinds(self):
        """Handle the posting of blinds by the appropriate players."""
        if len(self.players) < 2:
            raise ValueError("Not enough players to post blinds.")
        
        small_blind_player = self.playersInRound[(self.dealerPosition + 1) % len(self.playersInRound)]
        big_blind_player = self.playersInRound[(self.dealerPosition + 2) % len(self.playersInRound)]
        
        self.addBet(small_blind_player, self.smallBlind)
        self.addBet(big_blind_player, self.big_blind)
    
__all__ = ["Game"]