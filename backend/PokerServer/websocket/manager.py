from fastapi import WebSocket
from PokerGame.Core import GameManager
from typing import Dict, Optional, Union

class ConnectionManager:
    def __init__(self):
        # Dictionary of rooms
        # {roomName: {'players': {playerID: WebSocket}, 'gameManager': GameManager}}
        self.rooms: Dict[str, Dict[str, Union[Dict[str, WebSocket], GameManager]]] = {}

    async def connect(self, room: str, playerID: str, websocket: WebSocket) -> None:
        if room not in self.rooms:
            self.rooms[room] = {'players': {}, 'gameManager': GameManager()}
        self.rooms[room]['players'][playerID] = websocket
        print(f"player {playerID} joined room {room}")

    def disconnect(self, room: str, playerID: str) -> None:
        if room in self.rooms and playerID in self.rooms[room]['players']:
            del self.rooms[room]['players'][playerID]
            print(f"player {playerID} left room {room}")
            if not self.rooms[room]['players']:
                del self.rooms[room]
                print(f"table {room} closed")

    async def send_private_JSON(self, room: str, playerID: str, message: Dict[str, Union[str, int, float]]) -> None:
        if room in self.rooms and playerID in self.rooms[room]['players']:
            try:
                await self.rooms[room]['players'][playerID].send_json(message)
            except Exception:
                # Socket is dead — clean it up silently
                self.disconnect(room, playerID)

    async def broadcast_JSON_to_room(self, room: str, message: Dict[str, Union[str, int, float]]) -> None:
        if room not in self.rooms:
            raise Exception(f"room {room} does not exist")

        dead = []
        
        for playerID, websocket in list(self.rooms[room]['players'].items()):
            try:
                await websocket.send_json(message)
            except Exception:
                dead.append(playerID)

        for playerID in dead:
            self.disconnect(room, playerID)

    def get_gameManager_from_playerID(self, playerID: str) -> Optional[GameManager]:
        for room_data in self.rooms.values():
            players_dict = room_data['players']
            if playerID in players_dict:
                return room_data['gameManager']
        return None

# create connection manager for importing
manager = ConnectionManager()