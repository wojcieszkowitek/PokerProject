from PokerGame.Core.Deck import Deck
from PokerGame.Core.Card import Card
from PokerGame.Core.Player import Player
from PokerGame.Core.HandChecker import HandChecker


class Game:
    """
    Represents a game of poker.
    """
    def __init__(self, small_blind: int = 10, big_blind: int = 20):
        self.players: list[Player] = []
        self.players_in_game: list[Player] = []
        self.folded_players: list[Player] = []
        self.players_to_remove: list[Player] = []

        self.deck: Deck = Deck()

        self.pot: int = 0
        self.current_bets: dict[Player, int] = {}

        self.total_contributions: dict[Player, int] = {}

        self.all_in_players: list[Player] = []

        self.side_pots: list[dict] = []

        self.community_cards: list[Card] = []
        self.dealer_position: int = -1
        self.small_blind: int = small_blind
        self.big_blind: int = big_blind

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def players_in_round(self) -> list[Player]:
        return [p for p in self.players_in_game if p not in self.folded_players]

    @property
    def ready_players(self) -> list[Player]:
        return [player for player in self.players if player.ready and player.chips > 0]

    @property
    def small_blind_player_index(self) -> int:
        return self.players_in_round.index(self.get_player_at_offset(1))

    @property
    def utg_player_index(self) -> int:
        if len(self.players_in_round) == 2:
            return self.players_in_round.index(self.get_player_at_offset(2))
        return self.players_in_round.index(self.get_player_at_offset(3))

    # ------------------------------------------------------------------
    # Hand evaluation
    # ------------------------------------------------------------------

    def check_hands(self) -> list[tuple[Player, tuple]]:
        return [
            (player, HandChecker.evaluate_hand(player.hand, self.community_cards))
            for player in self.players_in_round
        ]

    def get_strongest_hand(self) -> list[tuple[Player, tuple]]:
        """
        Return all players (and their evaluations) that share the best hand
        among players still active in the round.
        Multiple entries are returned on a draw.
        """
        hands = self.check_hands()
        best_eval = max(evaluation for _, evaluation in hands)
        return [(player, evaluation) for player, evaluation in hands if evaluation == best_eval]

    # ------------------------------------------------------------------
    # Pot calculation
    # ------------------------------------------------------------------

    def calculate_pots(self) -> list[dict]:
        """
        Build the list of pots from total_contributions.

        Algorithm:
          - Work through each all-in level from smallest to largest.
          - At each level, every player contributes at most `cap` chips
            to this pot.  All players who contributed are eligible to
            win it — including the short-stacked all-in player who set
            the cap.
          - Whatever is left after all caps form a final pot that only
            players who are NOT all-in (i.e. full contributors) contest.
          - If there were no all-ins at all, the entire pot is returned
            as a single pot open to everyone.

        Returns:
            list of {"amount": int, "eligible": list[Player]}
        """
        all_players = list(self.total_contributions.keys())

        # Work on a mutable copy so we can subtract chip-by-chip per level
        remaining = dict(self.total_contributions)

        pots: list[dict] = []

        # Sort all-in contribution amounts from smallest (shortest stack) upward
        all_in_levels = sorted(
            {remaining[p] for p in self.all_in_players if p in remaining}
        )

        for cap in all_in_levels:
            pot_amount = 0
            eligible: list[Player] = []

            for player in all_players:
                if remaining.get(player, 0) <= 0:
                    continue
                # This player contributes at most `cap` chips to this pot
                taken = min(remaining[player], cap)
                pot_amount += taken
                remaining[player] -= taken
                eligible.append(player)

            if pot_amount > 0:
                pots.append({"amount": pot_amount, "eligible": eligible})

            # Reduce the cap for the next level so each pot layer is relative
            # e.g. levels [50, 100] -> first pot capped at 50 each,
            # second pot capped at (100-50)=50 each from those remaining.
            # We achieve this by having already subtracted from `remaining`.

        # Any chips still left after all all-in caps form the last side pot.
        # Only players who are NOT all-in can win this (they put in the full amount).
        leftover = sum(remaining.values())
        if leftover > 0:
            eligible = [p for p in all_players if p not in self.all_in_players]
            pots.append({"amount": leftover, "eligible": eligible})

        # No all-ins: single pot, everyone eligible
        if not pots:
            pots.append({"amount": self.pot, "eligible": all_players})

        return pots

    # ------------------------------------------------------------------
    # Showdown
    # ------------------------------------------------------------------

    def showdown(self):
        """
        Distribute the pot(s) to the winner(s).

        For each pot (main + side pots):
          1. Filter eligible players to those who haven't folded.
          2. Find the best hand among them.
          3. Split that pot equally among all players who share the best hand.
        """
        self.side_pots = self.calculate_pots()

        for pot in self.side_pots:
            # Only players still in the hand can win each pot
            contenders = [p for p in pot["eligible"] if p not in self.folded_players]

            if not contenders:
                continue

            # Evaluate each contender's hand
            evaluations = {
                p: HandChecker.evaluate_hand(p.hand, self.community_cards)
                for p in contenders
            }

            best_eval = max(evaluations.values())
            winners = [p for p, ev in evaluations.items() if ev == best_eval]

            # Split the pot — integer division; remainder chips are lost (standard casino rule)
            share = pot["amount"] // len(winners)
            for winner in winners:
                winner.chips += share

    # ------------------------------------------------------------------
    # Game lifecycle
    # ------------------------------------------------------------------

    def add_player(self, player: Player):
        self.players.append(player)

    def remove_player(self, player: Player):
        self.players_to_remove.append(player)
    
    def new_game(self):
        """
        Reset all state and prepare for a new game.
        """
        self.deck = Deck()
        self.current_bets.clear()
        self.community_cards.clear()
        self.pot = 0

        self.total_contributions.clear()
        self.all_in_players.clear()
        self.side_pots.clear()
        
        for player in self.players_to_remove:
            self.players.remove(player)
        self.players_to_remove.clear()

        self.players_in_game = self.ready_players
        self.folded_players.clear()

        if len(self.players_in_round) < 2:
            raise ValueError("At least 2 players must be ready to start a new game.")

        self.current_bets = {player: 0 for player in self.players_in_round}

        self.total_contributions = {player: 0 for player in self.players_in_round}

        self.dealer_position += 1

    def start_new_round(self):
        """
        Reset per-street bets (but NOT total_contributions — those are cumulative).
        """
        self.current_bets = {player: 0 for player in self.players_in_round}

    # ------------------------------------------------------------------
    # Betting
    # ------------------------------------------------------------------

    def add_bet(self, player: Player, amount: int):
        """
        Place a bet for a player, capping at their available chips (all-in).

        Changes vs original:
          - `actual = min(amount, player.chips)` — player can never bet
            more than they have; excess is silently capped (all-in).
          - `total_contributions` is updated alongside `current_bets`.
          - If the player's chips hit 0 after the bet they are added to
            `all_in_players`.
        """
        if player not in self.players_in_round:
            raise ValueError(f"{player.name} is not active in the round.")

        actual = min(amount, player.chips)
        bet_amount = player.place_bet(actual)

        self.current_bets[player] = self.current_bets.get(player, 0) + bet_amount

        self.total_contributions[player] = self.total_contributions.get(player, 0) + bet_amount
        self.pot += bet_amount

        if player.chips == 0 and player not in self.all_in_players:
            self.all_in_players.append(player)

    # ------------------------------------------------------------------
    # Dealing
    # ------------------------------------------------------------------

    def deal_cards(self):
        if not self.players_in_round:
            raise ValueError("No active players to deal to.")
        if len(self.players_in_round) < 2:
            raise ValueError("Not enough players to deal.")

        for player in self.players_in_round:
            player.receive_cards(self.deck.draw_card(), self.deck.draw_card())

    def deal_community_cards(self, number: int):
        if number < 1 or number > 5:
            raise ValueError("Must deal between 1 and 5 community cards.")
        if len(self.community_cards) + number > 5:
            raise ValueError("Cannot exceed 5 community cards.")

        for _ in range(number):
            self.community_cards.append(self.deck.draw_card())

    def deal_blinds(self):
        if len(self.players_in_round) < 2:
            raise ValueError("Not enough players to post blinds.")

        self.add_bet(self.get_player_at_offset(1), self.small_blind)
        self.add_bet(self.get_player_at_offset(2), self.big_blind)

    # ------------------------------------------------------------------
    # Player actions
    # ------------------------------------------------------------------

    def fold_player(self, player: Player):
        if player not in self.players_in_round:
            raise ValueError(f"{player.name} is not active in the round.")
        self.folded_players.append(player)

    def get_player_at_offset(self, offset: int) -> Player:
        if not self.players_in_round:
            raise ValueError("No active players in the round.")
        return self.players_in_round[(self.dealer_position + offset) % len(self.players_in_round)]


__all__ = ["Game"]