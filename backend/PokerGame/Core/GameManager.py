from PokerGame.Core.Game import Game
from PokerGame.Core.Player import Player
from PokerGame.Core.HandChecker import HandChecker
from enum import Enum

class GameManager:
    """
    Manages the state of a game of poker.
    """
    def __init__(self, *, small_blind=10, big_blind=20):
        self.game: Game = Game(small_blind, big_blind)
        self._round: GamePhase = GamePhase.WAITING_FOR_PLAYERS
        self.turn: int = 0

    # ------------------------------------------------------------------
    # Round / phase
    # ------------------------------------------------------------------
    @property
    def players(self):
        return self.game.players
    
    @property
    def ready_players(self):
        return self.game.ready_players
    
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
                raise ValueError(f"Invalid round value: {value}.")
        else:
            raise TypeError(f"Round must be a GamePhase or int, got {type(value)}")
    
    @property
    def game_state(self) -> dict:
        state = {
            "blinds": {
                "small_blind": self.game.small_blind,
                "big_blind": self.game.big_blind
            },
            "players": [p.player_id for p in self.game.players],
            "players_in_game": [p.player_id for p in self.game.players_in_game],
            "folded_players": [p.player_id for p in self.game.folded_players],
            "current_bets": [(p.player_id, amount) for p, amount in self.game.current_bets.items()],
            "total_contributions": [(p.player_id, amount) for p, amount in self.game.total_contributions.items()],
            "all_in_players": [p.player_id for p in self.game.all_in_players],
            "side_pots": self.game.side_pots,
            "pot": self.game.pot,
            "round": self.round.value,
        }

        # Only include current_player if game is in active round
        if self.round != GamePhase.WAITING_FOR_PLAYERS and len(self.game.players_in_game) > 0:
            try:
                state["current_player"] = self.current_player.player_id
            except Exception:
                state["current_player"] = None
        else:
            state["current_player"] = None

        return state

    # ------------------------------------------------------------------
    # Player helpers
    # ------------------------------------------------------------------

    @property
    def starting_player_index(self):
        if self.round == GamePhase.WAITING_FOR_PLAYERS:
            raise RuntimeError("Cannot get starting player index: game is not in a round.")
        elif self.round == GamePhase.PRE_FLOP:
            return self.game.utg_player_index
        else:
            return self.game.small_blind_player_index

    @property
    def current_player(self):
        total = len(self.game.players_in_game)
        idx = (self.starting_player_index + self.turn) % total
        return self.game.players_in_game[idx]
    
    def get_player_by_id(self, player_id: str):
        for p in self.game.players:
            if p.player_id == player_id:
                return p
    
    # ------------------------------------------------------------------
    # Betting round state
    # ------------------------------------------------------------------

    def is_betting_round_over(self):
        """
        Returns True when all active players have either:
          - matched the highest current bet, OR
          - gone all-in (they can't bet any more regardless)

        CHANGED: the original check required every active player to have
        matched max_bet exactly.  All-in players cannot match the max if
        a larger bet came in after them, so we now skip them in the
        equality check.
        """
        active_in_round = self.game.players_in_round

        if len(active_in_round) <= 1:
            return True

        max_bet = max(self.game.current_bets.values())

        all_matched = all(
            self.game.current_bets[p] == max_bet or p in self.game.all_in_players
            for p in active_in_round
        )

        everyone_acted = self.turn >= len(self.game.players_in_game)

        return all_matched and everyone_acted

    # ------------------------------------------------------------------
    # Game lifecycle
    # ------------------------------------------------------------------

    def start_new_game(self):
        self.game.new_game()
        self.round = GamePhase.WAITING_FOR_PLAYERS
        self.start_game()

    def start_game(self):
        if self.round != GamePhase.WAITING_FOR_PLAYERS:
            raise RuntimeError("Cannot start game: not in WAITING_FOR_PLAYERS phase.")
        if len(self.game.players) < 2:
            raise RuntimeError("Cannot start game: need at least 2 players.")

        self.turn = 0
        self.next_round()

    def next_round(self):
        """
        Advances to the next phase of the game.

        CHANGED 1: If only one player remains (everyone else folded),
        we skip straight to SHOWDOWN instead of dealing more cards to
        an empty table.

        CHANGED 2: When transitioning into SHOWDOWN, game.showdown() is
        called automatically so chips are distributed without needing a
        separate manual call.
        """
        self.turn = 0
        self.game.start_new_round()

        if len(self.game.players_in_round) == 1:
            self.round = GamePhase.SHOWDOWN
            self.game.showdown()
            return

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
            self.round = GamePhase.SHOWDOWN
            self.game.showdown()

        elif self.round == GamePhase.SHOWDOWN:
            raise RuntimeError("Cannot move to next round: already in SHOWDOWN.")

    def showdown(self):
        """
        Manual showdown trigger — kept for backwards compatibility.
        next_round() now calls this automatically, but external code can
        still call it directly if needed.
        """
        if self.round != GamePhase.SHOWDOWN:
            raise RuntimeError("Cannot perform showdown: not in SHOWDOWN phase.")
        self.game.showdown()

    # ------------------------------------------------------------------
    # Players
    # ------------------------------------------------------------------

    def add_player(self, player: Player):
        self.game.add_player(player)
    
    def remove_player(self, player: Player):
        self.game.remove_player(player)
    
    def has_player(self, player: Player):
        return player in self.game.players

    # ------------------------------------------------------------------
    # Turn management
    # ------------------------------------------------------------------

    def next_turn(self):
        """
        Advances to the next player who still needs to act.

        CHANGED: also skips all-in players — they have no chips left
        to bet so there is nothing for them to do until showdown.
        """
        self.turn += 1

        while (
            self.current_player in self.game.folded_players or
            self.current_player in self.game.all_in_players
        ):
            self.turn += 1

    def play_turn(self, action: PlayerActions, *, amount: int = 0):
        """
        Executes one player action then checks if the betting round is over.

        BET   — places `amount` chips; resets turn counter so everyone
                gets a chance to respond to the new bet.
        CALL  — matches the current highest bet.  add_bet() in Game will
                automatically cap this at the player's remaining chips,
                so a player with fewer chips simply goes all-in.
        FOLD  — removes the player from the active round.

        No changes to the core logic here — the all-in cap is handled
        inside Game.add_bet(), so CALL already works correctly.
        """
        if self.round == GamePhase.WAITING_FOR_PLAYERS:
            raise RuntimeError("Cannot play turn: game is not in a round.")

        current_player = self.current_player
        
        if current_player in self.game.players_to_remove:
            self.game.fold_player(current_player)

        if action == PlayerActions.BET:
            self.game.add_bet(current_player, amount)
            self.turn = 0

        if action == PlayerActions.CALL:
            call_amount = max(self.game.current_bets.values()) - self.game.current_bets[current_player]
            self.game.add_bet(current_player, call_amount)

        if action == PlayerActions.FOLD:
            self.game.fold_player(current_player)

        if action == PlayerActions.ALL_IN:
            self.game.add_bet(current_player, current_player.chips)

        if self.is_betting_round_over():
            self.next_round()
        
        self.next_turn()


# ------------------------------------------------------------------
# Enums
# ------------------------------------------------------------------

class GamePhase(Enum):
    WAITING_FOR_PLAYERS = 0
    PRE_FLOP = 1
    FLOP = 2
    TURN = 3
    RIVER = 4
    SHOWDOWN = 5


class PlayerActions(Enum):
    BET = "BET"
    CALL = "CALL"
    FOLD = "FOLD"
    ALL_IN = "ALL_IN"