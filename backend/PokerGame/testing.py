from Core.GameManager import GameManager, GamePhase, PlayerActions
from Core.Player import Player
from pprint import pprint
import os

gm = GameManager(small_blind=5, big_blind=10)

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
    }
]

for player in players:
    p = Player(player["name"], player["player_id"], player["chips"])
    gm.add_player(p)

gm.start_new_game()
gm.start_game()

current_round = None

while(True):
    if gm.round == GamePhase.SHOWDOWN:
        gm.start_new_game()
        gm.start_game()
    
    if current_round != gm.round:
        print(f"-------------------------- {gm.round} --------------------------")
    
    current_round = gm.round
    
    while(True):
        print(str(gm.current_player))
        print("pot: ", gm.game.pot)
        
        print("community: ", end="")
        for card in gm.game.community_cards:
            print(str(card) + ", ", end="")
        print("")

        action = input("action: ")
        
        os.system('cls' if os.name == 'nt' else 'clear')
    
        if action == "bet":
            amount = int(input("amount: "))
            gm.play_turn(PlayerActions.BET, amount=amount)
            break
        elif action == "call":
            gm.play_turn(PlayerActions.CALL)
            break
        elif action == "fold":
            gm.play_turn(PlayerActions.FOLD)
            break
        elif action == "checkhands": 
            if len(gm.game.community_cards) >= 3:
                print("Hands:")
                for player, hand in gm.game.check_hands():
                    print(f"{player.player_id}: {hand}")
        elif action == "checkstrong":
            if len(gm.game.community_cards) >= 3:
                print("Strongest Hands:")
                for hand in gm.game.get_strongest_hand():
                    pprint(f"{hand[0].player_id}: {hand[1]}")
        elif action == "checkbets":
            print("current bets:")
            prettyJson = pprint(gm.game.current_bets)
            print(prettyJson)