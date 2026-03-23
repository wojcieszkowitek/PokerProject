from Core.Card import Card

class Player:
    def __init__(self, name: str, player_id: str ,chips: int):
        self.player_id: str = player_id
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

    def __str__(self):
        stats = {
            "name": self.name,
            "player_id": self.player_id,
            "chips": self.chips,
            "hand": self.hand,
            "ready": self.ready
        }
        
        return(f"Player: {stats}")

    def __repr__(self):
        return str(self)
    
__all__ = ["Player"]