from .Deck import Deck
from .Card import Card

# TODO: implement checking what does every player has based on his hand and the community cards like pair, two pair, three of a kind, straight, flush, full house, four of a kind, straight flush, royal flush

class Player:
    def __init__(self, name: str, chips: int):
        self.name = name
        self.chips = chips
        self.hand: tuple[Card, Card] = (None, None)  # Players start with no cards in hand
        
    def receive_cards(self, card1: Card, card2: Card):
        """Give the player their two hole cards."""
        self.hand = (card1, card2)
        
    def place_bet(self, amount: int):
        """Place a bet by deducting chips from the player's total."""
        if amount > self.chips:
            raise ValueError(f"{self.name} does not have enough chips to bet {amount}.")
        self.chips -= amount
        return amount  # Return the amount bet for adding to the pot
    
__all__ = ["Player"]