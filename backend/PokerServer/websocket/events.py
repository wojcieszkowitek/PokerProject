from typing import Optional
from PokerServer.websocket.manager import manager
from PokerGame.Core import PlayerActions, GamePhase, Player
from backend.PokerGame.Core import GameManager

# Access GameManager instances through the manager
# games = manager.games # Removed this line

def get_game_manager(room: str) -> Optional[GameManager]:
    if room in manager.rooms:
        return manager.rooms[room]['gameManager']
    return None

async def handle_action(room: str, playerID: str, action: PlayerActions, amount: int = None):
    gameManager = get_game_manager(room)
    if not gameManager:
        # This should ideally not happen if connect() is called first
        raise RuntimeError(f"Game manager not found for room {room}")
        
    player = gameManager.current_player

    if player.player_id != playerID:
        await manager.send_private_JSON(room, playerID, {"error": "Not your turn"})
        raise RuntimeError("Not your turn")

    # Execute action
    if action == PlayerActions.BET:
        gameManager.play_turn(action, amount=amount)
    else:
        gameManager.play_turn(action)

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
    gameManager = get_game_manager(room)
    if not gameManager:
        raise RuntimeError(f"Game manager not found for room {room} when player joined")

    print(f"game phase: {gameManager.round}, {len(gameManager.ready_players)} players ready")
    print(f"player {playerID} joined room {room}")
    
    await manager.broadcast_JSON_to_room(room, {"event": "player joined", "playerID": playerID})
    await broadcast_game_state_to_player(room, playerID)
    
    # add player to game manager
    gameManager.add_player(Player(playerID, playerID, 1000))
    
    # Check if game should start only if it's still in WAITING_FOR_PLAYERS phase
    if gameManager.round == GamePhase.WAITING_FOR_PLAYERS and len(gameManager.ready_players) >= 2:
        print(f"starting game: {room}")
        gameManager.start_new_game()
        
        await manager.broadcast_JSON_to_room(room, {"event": "game started"})
        await ask_to_play_turn(room)

async def player_disconected(room: str, playerID: str):
    # It's important to also remove the player from the game manager if they disconnect
    gameManager = get_gameManager_from_playerID(room) # Use get_gameManager_from_playerID helper
    if gameManager:
        try:
            # Assuming there's a method to remove a player from the game manager
            # If not, this part might need adjustment based on GameManager's actual methods
            gameManager.remove_player(playerID)
            print(f"Removed player {playerID} from game manager in room {room}")
        except Exception as e:
            print(f"Error removing player {playerID} from game manager in room {room}: {e}")

    await manager.broadcast_JSON_to_room(room, {"event": "player left", "playerID": playerID})
    
async def ask_to_play_turn(room: str):
    gameManager = get_game_manager(room)
    if not gameManager:
        print(f"Warning: Game manager not found for room {room} when asking for turn.")
        return

    # Ensure there is a current player before accessing their ID
    if gameManager.current_player:
        playerID = gameManager.current_player.player_id
        await manager.broadcast_JSON_to_room(room, {"event": "turn", "playerID": playerID})
    else:
        print(f"No current player to ask for turn in room {room}.")

async def broadcast_game_state(room: str):
    gameManager = get_gameManager_from_playerID(room)
    if gameManager:
        await manager.broadcast_JSON_to_room(room, gameManager.game_state)
    else:
        print(f"Warning: Game manager not found for room {room} when broadcasting game state.")
    
async def broadcast_game_state_to_player(room: str, playerID: str):
    gameManager = get_gameManager_from_playerID(room)
    if gameManager:
        await manager.send_private_JSON(room, playerID, gameManager.game_state)
    else:
        print(f"Warning: Game manager not found for room {room} when broadcasting game state to player {playerID}.")

async def send_player_state(room: str, playerID: str):
    gameManager = get_gameManager_from_playerID(room)
    if gameManager:
        player = gameManager.get_player_by_id(playerID)
        if player:
            await manager.send_private_JSON(room, playerID, player.player_state)
        else:
            await manager.send_private_JSON(room, playerID, {"error": "Player not found in game"})
    else:
        print(f"Warning: Game manager not found for room {room} when sending player state to {playerID}.")

# Helper to get GameManager from room, used by player_disconected and others
def get_gameManager_from_playerID(room: str) -> Optional[GameManager]:
    if room in manager.rooms:
        return manager.rooms[room]['gameManager']
    return None
