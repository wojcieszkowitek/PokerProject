# managing connections
from fastapi import WebSocket, FastAPI

class connectionManager:
    def __init__(self):
        # Dictionary of rooms 
        # {roomName: {playerID: WebSocket}}
        self.rooms: dict[str, dict[str, WebSocket]] = {}
        
    async def connect(self, room: str, playerID: str, websocket: WebSocket):
        # handshake
        await websocket.accept()
        
        # if table doesn't exist create it
        if room not in self.rooms:
            self.rooms[room] = {}
        self.rooms[room][playerID] = websocket
        
        # print info for debugging
        print(f"player {playerID} joined room {room}")
            
    def disconnect(self, room: str, playerID: str):
        # remove player from room
        if room in self.rooms and playerID in self.rooms[room]:
            del self.rooms[room][playerID]
            print(f"player {playerID} left room {room}")
            
            if not self.rooms[room]:
                del self.rooms[room]
                print(f"table {room} closed")
                
    async def broadcast_to_room(self, room: str, message: str):
        if room in self.rooms:
            for playerID, websocket in self.rooms[room].items():
                await websocket.send_text(message)
                
    async def send_private_message(self, room: str, playerID: str, message: str):
        if room in self.rooms and playerID in self.rooms[room]:
            await self.rooms[room][playerID].send_text(message)
            
    async def send_private_JSON(self, room: str, playerID: str, message: dict):
        if room in self.rooms and playerID in self.rooms[room]:
            await self.rooms[room][playerID].send_json(message)
            
    async def broadcast_JSON_to_room(self, room: str, message: dict):
        if room in self.rooms:
            for playerID, websocket in self.rooms[room].items():
                await websocket.send_json(message)
            
manager = connectionManager()