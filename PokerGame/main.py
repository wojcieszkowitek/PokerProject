from Core.Game import *
from Core.Player import Player

game = Game()

players = [
    Player("Alice", 1000),
    Player("Bob", 1000),
    Player("Charlie", 1000)
]

for player in players:
    game.addPlayer(player)
    
