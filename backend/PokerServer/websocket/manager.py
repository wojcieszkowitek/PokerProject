# managing connections
from fastapi import WebSocket
from PokerGame.Core import GameManager, Player
from typing import Dict, List, Optional, Union

class ConnectionManager:
    def __init__(self):
        # Dictionary of rooms 
        # {roomName: {playerID: WebSocket}}
        self.rooms: Dict[str, Dict[str, WebSocket]] = {}
        
        # Dictionary of games
        # {roomName: GameManager}
        self.games: Dict[str, GameManager] = {}
        
    async def connect(self, room: str, playerID: str, websocket: WebSocket) -> None:
        # if table doesn't exist create it
        if room not in self.rooms:
            self.rooms[room] = {}
        self.rooms[room][playerID] = websocket
                
        # create the game instance
        if room not in self.games:
            self.games[room] = GameManager()
            
    def disconnect(self, room: str, playerID: str) -> None:
        # remove player from room
        if room in self.rooms and playerID in self.rooms[room]:
            del self.rooms[room][playerID]
            print(f"player {playerID} left room {room}")
            
            if not self.rooms[room]:
                del self.rooms[room]
                del self.games[room]
                print(f"table {room} closed")
            
    async def send_private_JSON(self, room: str, playerID: str, message: Dict[str, Union[str, int, float]]) -> None:
        if room in self.rooms and playerID in self.rooms[room]:
            await self.rooms[room][playerID].send_json(message)
            
    async def broadcast_JSON_to_room(self, room: str, message: Dict[str, Union[str, int, float]]) -> None:
        if room in self.rooms:
            for playerID, websocket in self.rooms[room].items():
                await websocket.send_json(message)
        else:
            raise Exception(f"room {room} does not exist")
    def get_gameManager_from_playerID(self, playerID: str) -> Optional[GameManager]:
        for room, players in self.rooms.items():
            if playerID in players:
                return self.games[room]
        
        return None

# create connection manager for importing            
manager = ConnectionManager()