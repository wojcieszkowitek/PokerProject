from Core.Card import Card

class Player:
    def __init__(self, name: str, chips: int):
        self.name: str = name
        self.chips: int = chips
        self.hand: tuple[Card, Card] = (None, None)  # Players start with no cards in hand
        self.ready: bool = True  # Assume players are ready by default, can be used to manage player states in the game
        
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