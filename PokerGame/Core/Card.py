class Card:
    def __init__(self, suit, rank):
        self.suit = suit
        self.rank = rank
    
    def __str__(self):
        # Rank: print face names (jack, queen, king, ace) or numeric value for 2-10
        r = self.rank
        if hasattr(r, "name"):
            name = r.name
            if name in ("JACK", "QUEEN", "KING", "ACE"):
                rank_str = name.lower()
            else:
                try:
                    rank_str = str(int(r))
                except Exception:
                    rank_str = name.lower()
        else:
            rank_str = str(r)

        # Suit: use enum member name (clubs, hearts, ...)
        s = self.suit
        suit_str = s.name.lower() if hasattr(s, "name") else str(s)

        return f"{rank_str} of {suit_str}"

    def __repr__(self):
        return self.__str__()

__all__ = ["Card"]