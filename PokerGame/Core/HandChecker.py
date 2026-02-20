from collections import Counter
from enum import IntEnum
from .Card import Card

class HandRank(IntEnum):
    HIGH_CARD = 1
    PAIR = 2
    TWO_PAIR = 3
    THREE_OF_A_KIND = 4
    STRAIGHT = 5
    FLUSH = 6
    FULL_HOUSE = 7
    FOUR_OF_A_KIND = 8
    STRAIGHT_FLUSH = 9
    ROYAL_FLUSH = 10

# TODO: refactor the whole functon making it more modular and easier to read, maybe even split into multiple functions for each hand type

class HandChecker:
    @staticmethod
    def evaluate_hand(player_hand: tuple[Card, Card], community_cards: list[Card]):
        # Filter out None values
        cards = [card for card in list(player_hand) + list(community_cards) if card is not None]
        if len(cards) < 5:
            raise ValueError("Need at least 5 cards to evaluate hand")

        ranks = [card.rank for card in cards]
        suits = [card.suit for card in cards]

        rank_counts = Counter(ranks)
        suit_counts = Counter(suits)

        sorted_ranks_desc = sorted(ranks, reverse=True)

        # --- Flush ---
        flush_suit = None
        for suit, count in suit_counts.items():
            if count >= 5:
                flush_suit = suit
                break

        flush_cards = []
        if flush_suit:
            flush_cards = sorted(
                [card.rank for card in cards if card.suit == flush_suit],
                reverse=True
            )

        # --- Straight ---
        def get_straight_high(ranks_list):
            unique = sorted(set(ranks_list))
            if 14 in unique:
                unique.insert(0, 1)  # Ace as 1

            for i in range(len(unique) - 4):
                window = unique[i:i+5]
                if window[4] - window[0] == 4:
                    return window[4]  # highest card in straight
            return None

        straight_high = get_straight_high(ranks)

        # --- Straight Flush ---
        straight_flush_high = None
        if flush_suit:
            flush_ranks = [card.rank for card in cards if card.suit == flush_suit]
            straight_flush_high = get_straight_high(flush_ranks)

            if straight_flush_high == 14:
                return (
                    HandRank.ROYAL_FLUSH,
                    [14]
                )

            if straight_flush_high:
                return (
                    HandRank.STRAIGHT_FLUSH,
                    [straight_flush_high]
                )

        # --- Four of a Kind ---
        for rank, count in rank_counts.items():
            if count == 4:
                kickers = sorted([r for r in ranks if r != rank], reverse=True)
                return (
                    HandRank.FOUR_OF_A_KIND,
                    [rank] + kickers[:1]
                )

        # --- Full House ---
        triples = sorted([r for r, c in rank_counts.items() if c >= 3], reverse=True)
        pairs = sorted([r for r, c in rank_counts.items() if c >= 2], reverse=True)

        if triples:
            for triple in triples:
                remaining_pairs = [p for p in pairs if p != triple]
                if remaining_pairs:
                    return (
                        HandRank.FULL_HOUSE,
                        [triple, remaining_pairs[0]]
                    )

        # --- Flush ---
        if flush_suit:
            return (
                HandRank.FLUSH,
                flush_cards[:5]
            )

        # --- Straight ---
        if straight_high:
            return (
                HandRank.STRAIGHT,
                [straight_high]
            )

        # --- Three of a Kind ---
        if triples:
            triple = triples[0]
            kickers = sorted([r for r in ranks if r != triple], reverse=True)
            return (
                HandRank.THREE_OF_A_KIND,
                [triple] + kickers[:2]
            )

        # --- Two Pair ---
        if len(pairs) >= 2:
            high_pair, low_pair = pairs[:2]
            kicker = max([r for r in ranks if r not in (high_pair, low_pair)])
            return (
                HandRank.TWO_PAIR,
                [high_pair, low_pair, kicker]
            )

        # --- One Pair ---
        if pairs:
            pair = pairs[0]
            kickers = sorted([r for r in ranks if r != pair], reverse=True)
            return (
                HandRank.PAIR,
                [pair] + kickers[:3]
            )

        # --- High Card ---
        return (
            HandRank.HIGH_CARD,
            sorted_ranks_desc[:5]
        )
        
__all__ = ["HandChecker", "HandRank"]