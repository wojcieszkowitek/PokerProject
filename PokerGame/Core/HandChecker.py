from collections import Counter
from enum import IntEnum
from Core.Card import Card
from typing import Iterable, Optional


class HandRank(IntEnum):
    """
    Represents poker hand strength.
    Higher value means a stronger hand.
    """
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


def filter_valid_cards(cards: Iterable["Card"]) -> list["Card"]:
    """
    Removes None values from the card collection.
    Acts as a safeguard against incomplete input.
    """
    return [c for c in cards if c is not None]


def count_ranks(cards: Iterable["Card"]) -> Counter:
    """
    Counts how many times each rank appears.
    """
    return Counter(card.rank for card in cards)


def count_suits(cards: Iterable["Card"]) -> Counter:
    """
    Counts how many times each suit appears.
    """
    return Counter(card.suit for card in cards)


def get_flush_suit(suit_counts: Counter) -> Optional[str]:
    """
    Returns the suit that appears at least 5 times (flush),
    or None if no flush is possible.
    """
    for suit, count in suit_counts.items():
        if count >= 5:
            return suit
    return None


def get_sorted_ranks(cards: Iterable["Card"], reverse: bool = True) -> list[int]:
    """
    Returns card ranks sorted.
    By default, sorted in descending order.
    """
    return sorted((card.rank for card in cards), reverse=reverse)


def get_straight_high(ranks: Iterable[int]) -> Optional[int]:
    """
    Detects a straight (5 consecutive ranks).
    Returns the highest card of the straight.

    Supports the wheel straight (A-2-3-4-5),
    treating Ace as both 14 and 1.
    """
    unique = sorted(set(ranks))  # remove duplicates

    # Handle Ace-low straight case
    if 14 in unique:
        unique.insert(0, 1)

    # Check every consecutive 5-card window
    for i in range(len(unique) - 4):
        window = unique[i:i + 5]
        if window[-1] - window[0] == 4:
            return window[-1]

    return None


def get_multiples(rank_counts: Counter):
    """
    Extracts:
    - Four of a kind
    - Three of a kind
    - Pairs

    Each returned list is sorted in descending order.
    """
    triples = sorted(
        (r for r, c in rank_counts.items() if c >= 3),
        reverse=True
    )
    pairs = sorted(
        (r for r, c in rank_counts.items() if c >= 2),
        reverse=True
    )
    quads = sorted(
        (r for r, c in rank_counts.items() if c == 4),
        reverse=True
    )
    return quads, triples, pairs


class HandChecker:
    @staticmethod
    def evaluate_hand(
        player_hand: tuple["Card", "Card"],
        community_cards: list["Card"]
    ):
        """
        Evaluates a poker hand using:
        - 2 hole cards
        - community cards

        Returns:
            (HandRank, tiebreaker_tuple)

        The tiebreaker tuple contains ranks used for
        lexicographical comparison between equal hand types.
        """

        # Combine all available cards
        cards = filter_valid_cards((*player_hand, *community_cards))

        # At least 5 cards are required to evaluate a hand
        if len(cards) < 5:
            raise ValueError("Need at least 5 cards to evaluate hand")

        # Precompute rank and suit counts
        rank_counts = count_ranks(cards)
        suit_counts = count_suits(cards)

        # Precompute sorted ranks (descending)
        sorted_ranks = get_sorted_ranks(cards)

        # Detect potential flush
        flush_suit = get_flush_suit(suit_counts)

        # Detect multiples (pairs, trips, quads)
        quads, triples, pairs = get_multiples(rank_counts)

        # ---------- Straight Flush / Royal Flush ----------
        if flush_suit:
            flush_cards = [c for c in cards if c.suit == flush_suit]
            flush_ranks = [c.rank for c in flush_cards]

            sf_high = get_straight_high(flush_ranks)

            if sf_high:
                # Royal Flush is a straight flush to Ace
                if sf_high == 14:
                    return HandRank.ROYAL_FLUSH, (14,)
                return HandRank.STRAIGHT_FLUSH, (sf_high,)

        # ---------- Four of a Kind ----------
        if quads:
            quad = quads[0]
            kicker = max(r for r in sorted_ranks if r != quad)
            return HandRank.FOUR_OF_A_KIND, (quad, kicker)

        # ---------- Full House ----------
        if triples:
            for triple in triples:
                # Find a pair different from the triple
                remaining_pairs = [p for p in pairs if p != triple]
                if remaining_pairs:
                    return HandRank.FULL_HOUSE, (triple, remaining_pairs[0])

        # ---------- Flush ----------
        if flush_suit:
            flush_ranks = sorted(
                (c.rank for c in cards if c.suit == flush_suit),
                reverse=True
            )
            return HandRank.FLUSH, tuple(flush_ranks[:5])

        # ---------- Straight ----------
        straight_high = get_straight_high(sorted_ranks)
        if straight_high:
            return HandRank.STRAIGHT, (straight_high,)

        # ---------- Three of a Kind ----------
        if triples:
            triple = triples[0]
            kickers = [r for r in sorted_ranks if r != triple][:2]
            return HandRank.THREE_OF_A_KIND, (triple, *kickers)

        # ---------- Two Pair ----------
        if len(pairs) >= 2:
            high_pair, low_pair = pairs[:2]
            kicker = max(r for r in sorted_ranks if r not in (high_pair, low_pair))
            return HandRank.TWO_PAIR, (high_pair, low_pair, kicker)

        # ---------- One Pair ----------
        if pairs:
            pair = pairs[0]
            kickers = [r for r in sorted_ranks if r != pair][:3]
            return HandRank.PAIR, (pair, *kickers)

        # ---------- High Card ----------
        return HandRank.HIGH_CARD, tuple(sorted_ranks[:5])


__all__ = ["HandChecker", "HandRank"]