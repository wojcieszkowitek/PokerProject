from Core.Game import Game
from enum import Enum
from Core.Player import Player

class GameManager:
    """
    Manages the state of a game of poker.
    """
    def __init__(self):
        """
        Initializes a new game manager.
        """
        self.game: Game = Game()
        self._round: GamePhase = GamePhase.WAITING_FOR_PLAYERS
        self.turn: int = 0
    
    @property
    def round(self):
        """
        Returns the current round of the game.
        
        The round can be one of the following:
        WAITING_FOR_PLAYERS: The game is waiting for players to join.
        PRE_FLOP: The game is in the pre-flop phase, where blinds are dealt.
        FLOP: The game is in the flop phase, where community cards are dealt.
        TURN: The game is in the turn phase, where another community card is dealt.
        RIVER: The game is in the river phase, where the final community card is dealt.
        """
        return self._round
    
    @round.setter
    def round(self, value: GamePhase | int):
        """
        Sets the current round of the game.
        
        The round can be one of the following:
        WAITING_FOR_PLAYERS: The game is waiting for players to join.
        PRE_FLOP: The game is in the pre-flop phase, where blinds are dealt.
        FLOP: The game is in the flop phase, where community cards are dealt.
        TURN: The game is in the turn phase, where another community card is dealt.
        RIVER: The game is in the river phase, where the final community card is dealt.
        
        Raises:
            ValueError: If the value is not a valid GamePhase.
        """
        if isinstance(value, GamePhase):
            self._round = value
        elif isinstance(value, int):
            try:
                self._round = GamePhase(value)
            except ValueError:
                raise ValueError(f"Invalid round value: {value}. Must be an integer corresponding to a GamePhase.")
        else:
            raise TypeError(f"Round must be set to a GamePhase enum member or an integer, got {type(value)}")
    
    @property
    def starting_player_index(self):
        """
        Returns the index of the starting player in the current round.
        """
        if self.round == GamePhase.WAITING_FOR_PLAYERS:
            raise RuntimeError("Cannot get starting player index: game is not in a round.")
        elif self.round == GamePhase.PRE_FLOP:
            return self.game.utg_player_index
        else:
            return self.game.small_blind_player_index
    
    @property
    def current_player(self):
        """
        Returns the current player in the round.
        """
        total = len(self.game.players_in_game)

        idx = (self.starting_player_index + self.turn) % total
        return self.game.players_in_game[idx]
    
    def is_betting_round_over(self):
        """
        Returns True if the betting round is over, False otherwise.
        
        The betting round is over if all players have acted and the current highest bet has been matched by all remaining players.
        """
        active_in_round = self.game.players_in_round 

        if len(active_in_round) <= 1:
            return True

        max_bet = max(self.game.current_bets.values())
        all_matched = all(self.game.current_bets[p] == max_bet for p in active_in_round)

        everyone_acted = self.turn >= len(self.game.players_in_game)

        return all_matched and everyone_acted
    
    def start_new_game(self):
        """
        Starts a new game by resetting the game state and setting the round to PRE_FLOP.
        """
        self.game.new_game()  # Reset the game state for a new game
        self.round = GamePhase.WAITING_FOR_PLAYERS  # Start with the Waiting For players
    
    def start_game(self):
        """
        Starts the game by going to pre-flop and dealing stuff out.
        """
        if self.round != GamePhase.WAITING_FOR_PLAYERS:
            raise RuntimeError("Cannot start game: game is not in WAITING_FOR_PLAYERS phase.")
        
        if len(self.game.players) < 2:
            raise RuntimeError("Cannot start game: not enough players. Must be at least 2.")

        self.turn = 0
        
        self.next_round()
        
    def next_round(self):
        """
        Moves on to the next round by dealing blind cards or dealing community cards.
        """
        self.turn = 0
        
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
    
    def add_player(self, player: Player):
        """
        Adds a player to the game.
        """
        self.game.add_player(player)
    
    def next_turn(self):
        """
        Moves on to the next turn.
        """
        self.turn += 1
        
        while self.current_player in self.game.folded_players:
            self.turn += 1
    
    def play_turn(self, action: PlayerActions, *, amount: int = 0):
        """
        Plays a turn by performing the given action.
        
        The action can be one of the following:
        BET: Places a bet of the given amount.
        CALL: Matches the current highest bet.
        FOLD: Folds the hand and forfeits the chance to win the pot.
        """
        current_player: Player = None
        
        if self.round == GamePhase.WAITING_FOR_PLAYERS:
            raise RuntimeError("Cannot play turn: game is not in a round.")
        
        current_player = self.current_player
        
        if action == PlayerActions.BET:
            self.game.add_bet(current_player, amount)
            self.turn = 0
            self.next_turn()
        if action == PlayerActions.CALL:
            self.game.add_bet(current_player, max(self.game.current_bets.values()))
            self.next_turn()
        if action == PlayerActions.FOLD:
            self.game.fold_player(current_player)
            self.next_turn()
        
        if self.is_betting_round_over():
            self.next_round()
                
class GamePhase(Enum):
    WAITING_FOR_PLAYERS = 0
    PRE_FLOP = 1
    FLOP = 2
    TURN = 3
    RIVER = 4

class PlayerActions(Enum):
    BET = "BET"
    CALL = "CALL"
    FOLD = "FOLD"