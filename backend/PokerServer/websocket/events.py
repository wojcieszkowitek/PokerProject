from typing import Optional
from PokerServer.websocket.manager import manager
from PokerGame.Core import PlayerActions, GamePhase, Player, GameManager


def get_game(room: str) -> Optional[GameManager]:
    return manager.get_game(room)


# ------------------------------------------------------------------ actions


async def handle_action(room: str, player_id: str, action: PlayerActions, amount: int = None):
    game = get_game(room)
    if not game:
        raise RuntimeError(f"game manager not found for room {room}")

    if game.current_player.player_id != player_id:
        await manager.send_private_JSON(room, player_id, {"error": "not your turn"})
        raise RuntimeError("not your turn")

    if action == PlayerActions.BET:
        game.play_turn(action, amount=amount)
    else:
        game.play_turn(action)

    event = {"event": action.name.lower(), "playerID": player_id}
    if amount is not None:
        event["amount"] = amount

    await manager.broadcast_JSON_to_room(room, event)
    await broadcast_game_state(room)
    await ask_to_play_turn(room)


async def bet(room: str, amount: int, player_id: str):
    await handle_action(room, player_id, PlayerActions.BET, amount)

async def fold(room: str, player_id: str):
    await handle_action(room, player_id, PlayerActions.FOLD)

async def call(room: str, player_id: str):
    await handle_action(room, player_id, PlayerActions.CALL)

async def all_in(room: str, player_id: str):
    await handle_action(room, player_id, PlayerActions.ALL_IN)


# ------------------------------------------------------------------ events


async def player_joined_room(room: str, player_id: str):
    game = get_game(room)
    if not game:
        raise RuntimeError(f"game manager not found for room {room}")

    await manager.broadcast_JSON_to_room(room, {"event": "player joined", "playerID": player_id})
    await broadcast_game_state_to_player(room, player_id)

    game.add_player(Player(player_id, player_id, 1000))
    print(f"player {player_id} joined room {room} | phase: {game.round} | ready: {len(game.ready_players)}")

    if game.round == GamePhase.WAITING_FOR_PLAYERS and len(game.ready_players) >= 2:
        game.start_new_game()
        await manager.broadcast_JSON_to_room(room, {"event": "game started"})
        await ask_to_play_turn(room)


async def player_disconected(room: str, player_id: str):
    game = get_game(room)
    if game:
        try:
            game.remove_player(player_id)
            print(f"removed player {player_id} from game in room {room}")
        except Exception as e:
            print(f"error removing player {player_id} from room {room}: {e}")

    await manager.broadcast_JSON_to_room(room, {"event": "player left", "playerID": player_id})


# ---------------------------------------------------------------- broadcasts


async def ask_to_play_turn(room: str):
    game = get_game(room)
    if not game:
        print(f"warning: no game manager for room {room} when asking for turn")
        return

    if not game.current_player:
        print(f"warning: no current player in room {room}")
        return

    await manager.broadcast_JSON_to_room(room, {"event": "turn", "playerID": game.current_player.player_id})


async def broadcast_game_state(room: str):
    game = get_game(room)
    if not game:
        print(f"warning: no game manager for room {room} when broadcasting state")
        return
    await manager.broadcast_JSON_to_room(room, game.game_state)


async def broadcast_game_state_to_player(room: str, player_id: str):
    game = get_game(room)
    if not game:
        print(f"warning: no game manager for room {room} when sending state to {player_id}")
        return
    await manager.send_private_JSON(room, player_id, game.game_state)


async def send_player_state(room: str, player_id: str):
    game = get_game(room)
    if not game:
        print(f"warning: no game manager for room {room} when sending player state to {player_id}")
        return

    player = game.get_player_by_id(player_id)
    if not player:
        await manager.send_private_JSON(room, player_id, {"error": "player not found"})
        return

    await manager.send_private_JSON(room, player_id, player.player_state)