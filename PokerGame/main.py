from Core.Game import *
from Core.Player import Player
from Core.HandChecker import HandChecker, HandRank

game = Game()

players = [
    Player("Alice", 1000),
    Player("Bob", 1000),
    Player("Charlie", 1000),
    Player("David", 1000),
    Player("Eve", 1000),
    
    
]

players[0].ready = False

for player in players:
    game.addPlayer(player)

game.newGame()
game.dealCards()
game.dealBlinds()

print("Players and their hole cards:")
for player in game.playersInRound:
    print(f"Player: {player.name}, Cards: {player.hand}")
    
game.dealCommunityCards(5)
print (f"Community Cards: {game.communityCards}")

for player in game.playersInRound:
    hand_rank, tiebreaker = HandChecker.evaluate_hand(player.hand, game.communityCards)
    print(f"{player.name} has a {hand_rank.name} with tiebreaker {tiebreaker}")