from .Card import Card
from .CardData import Suit, Rank

class Deck:
    def __init__(self, shuffle: bool = True):
        self.cards = []
        self.reset()  # Initialize the deck with a full set of cards
        
        if shuffle:
            self.shuffle()
    
    def shuffle(self):
        """Shuffles the deck of cards in place."""
        import random
        random.shuffle(self.cards)

    def draw_card(self):
        """Deals (removes and returns) the top card from the deck."""
        if len(self.cards) <= 0:
            raise ValueError("Not enough cards in the deck to deal")
        
        return self.cards.pop(0)  # Remove and return the top card
    
    def deal_multiple(self, count: int):
        """Deals multiple cards from the top of the deck."""
        if count > len(self.cards):
            raise ValueError(f"Not enough cards in the deck to deal {count} cards")
        
        dealt_cards = self.cards[:count]  # Get the top 'count' cards
        self.cards = self.cards[count:]  # Remove the dealt cards from the deck
        return dealt_cards
    
    def reset(self):
        if len(self.cards) < 0:
            self.cards = []  # Clear the deck if it has negative length (shouldn't happen, but just in case)
        
        """Resets the deck to a full, ordered set of 52 cards."""
        self.cards = [Card(suit, rank) for suit in Suit for rank in Rank]
        
    def __len__(self):
        return len(self.cards)
    
    def __str__(self):
        return f"Deck of {len(self.cards)} cards"

    def __iter__(self):
        """Return an iterator over the cards so `for card in deck` works."""
        return iter(self.cards)

    def __getitem__(self, index):
        """Allow indexing/slicing: `deck[0]`, `deck[1:5]`."""
        return self.cards[index]