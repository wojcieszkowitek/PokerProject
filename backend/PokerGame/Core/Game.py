from Core.Deck import Deck
from Core.Card import Card
from Core.Player import Player

class Game:
    """
    Represents a game of poker.
    """
    def __init__(self, small_blind: int = 10, big_blind: int = 20):
        """
        Initialize a new game of poker with the given blinds.
        
        Args:
            small_blind (int): The amount of chips for the small blind.
            big_blind (int): The amount of chips for the big blind.
        """
        self.players: list[Player] = []  # The list of all players in the game
        self.players_in_game: list[Player] = []  # Track players still active in the current round
        self.folded_players: list[Player] = []  # Track players who have folded their hand
        
        self.deck: Deck = Deck()  # The deck of cards for the game
        
        self.pot: int = 0  # The total amount of chips in the pot
        self.current_bets: dict[Player, int] = {}  # The current bets for each player
        
        self.community_cards: list[Card] = []  # The community cards on the table
        
        self.dealer_position: int = -1  # The index of the dealer in the players list
        
        self.small_blind: int = small_blind
        self.big_blind: int = big_blind

    @property
    def players_in_round(self) -> list[Player]:
        """
        Return a list of players who are still active in the current round.
        """
        return [p for p in self.players_in_game if p not in self.folded_players]
    
    @property
    def ready_players(self) -> list[Player]:
        """
        Return a list of players who are ready to play.
        """
        return [player for player in self.players if player.ready]

    @property
    def small_blind_player_index(self) -> int:
        """
        Return the player index in the players_in_round who is currently posting the small blind.
        """
        # return the index of the player who is posting the small blind (the player immediately to the left of the dealer)
        return self.players_in_round.index(self.get_player_at_offset(1))
    
    def get_player_at_offset(self, offset: int) -> Player:
        """
        Return the player at the given offset from the dealer.
        
        Args:
            offset (int): The offset from the dealer position.
        
        Returns:
            Player: The player at the given offset.
        """
        if not self.players_in_game:
            raise ValueError("No active players in the game.")
        return self.game.players_in_game[(self.dealer_position + offset) % len(self.game.players_in_game)]

    @property
    def utg_player_index(self) -> int:
        """
        Return the player index in the players_in_round of who is currently in the Under the Gun (UTG) position.
        """
        if len(self.players_in_round) == 2:
            # In a heads-up game, the dealer is also the small blind and the UTG player is the big blind
            return self.players_in_round.index(self.get_player_at_offset(2))
            
        # return the index of the player who is in the UTG position (the player immediately to the left of the big blind)
        return self.players_in_round.index(self.get_player_at_offset(3))
    
    def add_player(self, player: Player):
        """
        Add a player to the game.
        
        Args:
            player (Player): The player to add to the game.
        """
        self.players.append(player)
        
    def new_game(self):
        """
        Start a new game by resetting the deck, pot, and player states.
        """
        self.deck = Deck()  # Reset the deck for a new game
        self.current_bets.clear()
        self.community_cards.clear()
        self.pot = 0
        
        self.players_in_game = self.ready_players  # Only players who are ready can participate in the new game
        self.folded_players.clear()
        
        if len(self.players_in_round) < 2:
            raise ValueError("At least 2 players must be ready to start a new game.")
        
        self.current_bets = {player: 0 for player in self.players_in_round}  # Reset bets for all players in the round
        
        self.dealer_position += 1  # Move the dealer position to the next player for the new game
        
    def start_new_round(self):
        """
        Start a new round by resetting the current bets for all players.
        """
        self.current_bets = {player: 0 for player in self.players_in_round}  # Reset bets for all players in the new round
    
    def add_bet(self, player: Player, amount: int):
        """
        Add a bet for a player and update the pot.
        
        Args:
            player (Player): The player who is placing the bet.
            amount (int): The amount of chips to bet.
        """
        if player not in self.players_in_round:
            raise ValueError(f"{player.name} is not currently active in the round and cannot bet.")
        
        bet_amount = player.place_bet(amount)  # This will deduct the chips from the player
        
        # Update current bets and total bets for the player
        self.current_bets[player] = self.current_bets.get(player, 0) + bet_amount
        
        self.pot += bet_amount  # Add the bet to the pot
        
    def deal_cards(self):
        """
        Deal player hands.
        """
        if not self.players_in_round:
            raise ValueError("No active players in the round to deal cards to.")
        elif len(self.players_in_round) < 2:
            raise ValueError("Not enough active players in the round to deal cards.")
        
        for player in self.players_in_round:
            card1 = self.deck.draw_card()
            card2 = self.deck.draw_card()
            
            player.receive_cards(card1, card2)
            
    def deal_community_cards(self, number: int):
        """
        Deal community cards to the table.
        
        Args:
            number (int): The number of community cards to deal.
        """
        if number < 1 or number > 5:
            raise ValueError("Number of community cards must be between 1 and 5.")
        elif len(self.community_cards) + number > 5:
            raise ValueError("Cannot deal more than 5 community cards in total.")
        
        for _ in range(number):
            card = self.deck.draw_card()
            self.community_cards.append(card)
        
    def deal_blinds(self):
        """
        Handle the posting of blinds by the appropriate players.
        """
        if len(self.players_in_round) < 2:
            raise ValueError("Not enough players to post blinds.")
        
        small_blind_player = self.get_player_at_offset(1)
        big_blind_player = self.get_player_at_offset(2)
        
        self.add_bet(small_blind_player, self.small_blind)
        self.add_bet(big_blind_player, self.big_blind)
        
    def fold_player(self, player: Player):
        """
        Handle a player folding their hand.
        
        Args:
            player (Player): The player who is folding their hand.
        """
        if player not in self.players_in_round:
            raise ValueError(f"{player.name} is not currently active in the round and cannot fold.")
        
        self.folded_players.append(player)
        
    def get_player_at_offset(self, offset: int) -> Player:
        """
        Get a player at a given offset from the dealer position.
        
        Args:
            offset (int): The offset from the dealer position.
        
        Returns:
            Player: The player at the given offset.
        """
        if not self.players_in_round:
            raise ValueError("No active players in the round.")
        return self.players_in_round[(self.dealer_position + offset) % len(self.players_in_round)]
    
__all__ = ["Game"]