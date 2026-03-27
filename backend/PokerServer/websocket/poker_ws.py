# websocket endpoint
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from PokerServer.websocket.manager import manager
from PokerServer.websocket.tokens import tokenManager
import PokerServer.websocket.events as events

router = APIRouter()

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

    # handshake
    await websocket.accept()
    
    # connection logic, create player etc
    await manager.connect(table_ID, user_ID, websocket)
    
    await events.player_joined_room(table_ID, user_ID)
    
    try:
        while(True):
            try: 
                data: dict = await websocket.receive_json()
                print("recived json from client: ", user_ID, "at", table_ID)
            except Exception:
                await manager.send_private_JSON(table_ID, user_ID, {"error": "invalid json"})
                continue
            
            if not data.get("action"):
                await manager.send_private_JSON(table_ID, user_ID, {"error": "action has to be specified"})
                continue
            
            elif data["action"] == "bet":
                try:
                    await events.bet(table_ID, amount=data["amount"], playerID=user_ID)
                except RuntimeError:
                    print("wrong turn")
                    continue
                    
            elif data["action"] == "call":
                try:
                    await events.call(table_ID, user_ID)
                except RuntimeError:
                    print("wrong turn")
                    continue
                    
            elif data["action"] == "fold":
                try:
                    await events.fold(table_ID, user_ID)
                except RuntimeError:
                    print("wrong turn")
                    continue
            
            elif data["action"] == "get state":
                await events.send_player_state(table_ID, user_ID)
                continue

            else:
                await manager.send_private_JSON(table_ID, user_ID, {"error": "invalid action"})
                continue
                        
    except WebSocketDisconnect:
        manager.disconnect(table_ID, user_ID)
        await events.player_disconected(table_ID, user_ID)