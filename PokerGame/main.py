from Core.Game import *
from Core.Player import Player
from Core.HandChecker import HandChecker, HandRank

game = Game()

players = [
    Player("Alice", 1000),
    Player("Bob", 1000),
    Player("Charlie", 1000)
]

players[0].ready = False

for player in players:
    game.addPlayer(player)

game.newGame()
game.dealCards()
game.dealBlinds()

print("Players and their hole cards:")
for player in game.players_in_round:
    print(f"Player: {player.name}, Cards: {player.hand}")
    
game.dealCommunityCards(5)
print (f"Community Cards: {game.community_cards}")

for player in game.players_in_round:
    hand_rank, tiebreaker = HandChecker.evaluate_hand(player.hand, game.community_cards)
    print(f"{player.name} has a {hand_rank.name} with tiebreaker {tiebreaker}")
