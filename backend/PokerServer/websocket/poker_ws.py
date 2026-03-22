# websocket endpoint
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from PokerServer.websocket.manager import manager

router = APIRouter()

@router.websocket("/ws/{table_ID}/{playerID}")
async def connect_to_table(websocket: WebSocket, table_ID: str, playerID: str):
    #connection logic
    await manager.connect(table_ID, playerID, websocket)
    
    try:
        while(True):
            data = await websocket.receive_json()
            if data["action"] == "test":
                await manager.send_private_JSON(table_ID, playerID, {"action": "test", "message": "test message"})
            
    except WebSocketDisconnect:
        manager.disconnect(table_ID, websocket)
        await manager.broadcast_to_room(table_ID, "player left")