from Core.GameManager import GameManager
from Core.Player import Player

gm = GameManager()

players = [
    {
        "name": "Player 1",
        "player_id": "player1",
        "chips": 100,
    },
    {
        "name": "Player 2",
        "player_id": "player2",
        "chips": 100,
    },
    {
        "name": "Player 3",
        "player_id": "player3",
        "chips": 100,
    },
    {
        "name": "Player 4",
        "player_id": "player4",
        "chips": 100,
    }
]

for player in players:
    p = Player(player["name"], player["player_id"], player["chips"])
    gm.add_player(p)

gm.start_new_game()
gm.start_game()

print(gm.game.get_player_at_offset(gm.turn).name)
