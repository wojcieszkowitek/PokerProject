from PokerServer.websocket.manager import manager
from PokerGame.Core import GameManager, PlayerActions, GamePhase, Player

games = manager.games

async def handle_action(room: str, playerID: str, action: PlayerActions, amount: int = None):
    player = games[room].current_player

    if player.player_id != playerID:
        await manager.send_private_JSON(room, playerID, {"error": "Not your turn"})
        raise RuntimeError("Not your turn")

    # Execute action
    if action == PlayerActions.BET:
        games[room].play_turn(action, amount=amount)
    else:
        games[room].play_turn(action)

    # Broadcast event
    event_data = {
        "event": action.name.lower(),
        "playerID": player.player_id
    }

    if amount is not None:
        event_data["amount"] = amount

    await manager.broadcast_JSON_to_room(room, event_data)

    await broadcast_game_state(room)
    await ask_to_play_turn(room)

# Wrapper functions (API stays clean)

async def bet(room: str, amount: int, playerID: str):
    await handle_action(room, playerID, PlayerActions.BET, amount)

async def fold(room: str, playerID: str):
    await handle_action(room, playerID, PlayerActions.FOLD)

async def call(room: str, playerID: str):
    await handle_action(room, playerID, PlayerActions.CALL)
    
async def all_in(room: str, playerID: str):
    await handle_action(room, playerID, PlayerActions.ALL_IN)
    
async def player_joined_room(room: str, playerID: str):
    print(f"game phase: {games[room].round}, {len(games[room].ready_players)} players ready")
    print(f"player {playerID} joined room {room}")
    
    await manager.broadcast_JSON_to_room(room, {"event": "player joined", "playerID": playerID})
    await broadcast_game_state_to_player(room, playerID)
    
    # add player to game manager
    games[room].add_player(Player(playerID, playerID, 1000))
    
    
    if games[room].round == GamePhase.WAITING_FOR_PLAYERS and len(games[room].ready_players) >= 2:
        print(f"starting game: {room}")
        games[room].start_new_game()
        
        await manager.broadcast_JSON_to_room(room, {"event": "game started"})
        await ask_to_play_turn(room)

async def player_disconected(room: str, playerID: str):
    await manager.broadcast_JSON_to_room(room, {"event": "player left", "playerID": playerID})
    
async def ask_to_play_turn(room: str):
    playerID = games[room].current_player.player_id
    await manager.broadcast_JSON_to_room(room, {"event": "turn", "playerID": playerID})

async def broadcast_game_state(room: str):
    await manager.broadcast_JSON_to_room(room, games[room].game_state)
    
async def broadcast_game_state_to_player(room: str, playerID: str):
    await manager.send_private_JSON(room, playerID, games[room].game_state)

async def send_player_state(room: str, playerID: str):
    await manager.send_private_JSON(room, playerID, games[room].get_player_by_id(playerID).player_state)