from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from PokerServer.websocket.manager import manager
from PokerServer.websocket.tokens import tokenManager
import PokerServer.websocket.events as events

router = APIRouter()

async def _handle_action(table_ID: str, user_ID: str, data: dict) -> None:
    action = data.get("action")

    if not action:
        await manager.send_private_JSON(table_ID, user_ID, {"error": "action has to be specified"})
        return

    if action == "get state":
        await events.send_player_state(table_ID, user_ID)
        return

    action_handlers = {
        "bet":    lambda: events.bet(table_ID, amount=data.get("amount"), playerID=user_ID),
        "call":   lambda: events.call(table_ID, user_ID),
        "fold":   lambda: events.fold(table_ID, user_ID),
        "all in": lambda: events.all_in(table_ID, user_ID),
    }

    handler = action_handlers.get(action)
    if not handler:
        await manager.send_private_JSON(table_ID, user_ID, {"error": "invalid action"})
        return

    try:
        await handler()
    except RuntimeError:
        print(f"wrong turn: player {user_ID} at {table_ID}")
    except ValueError:
        await manager.send_private_JSON(table_ID, user_ID, {"error": "invalid amount"})


@router.websocket("/ws/{table_ID}")
async def connect_to_table(websocket: WebSocket, table_ID: str):
    token = websocket.headers.get("token")
    if not token:
        await websocket.close()
        return

    user_ID = tokenManager.verifyToken(token)
    if not user_ID:
        await websocket.close()
        return

    await websocket.accept()
    await manager.connect(table_ID, user_ID, websocket)
    await events.player_joined_room(table_ID, user_ID)

    try:
        while True:
            try:
                data: dict = await websocket.receive_json()
                print(f"received json from client: {user_ID} at {table_ID}")
            except Exception:
                await manager.send_private_JSON(table_ID, user_ID, {"error": "invalid json"})
                continue

            await _handle_action(table_ID, user_ID, data)

    except WebSocketDisconnect:
        manager.disconnect(table_ID, user_ID)
        await events.player_disconected(table_ID, user_ID)