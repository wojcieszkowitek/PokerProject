# managing connections
from fastapi import WebSocket
from PokerGame.Core import GameManager, Player
from typing import Dict, Optional, Union

class ConnectionManager:
    def __init__(self):
        # Dictionary of rooms
        # {roomName: {playerID: WebSocket}}
        self.rooms: Dict[str, Dict[str, WebSocket]] = {}
        # Dictionary of games
        # {roomName: GameManager}
        self.games: Dict[str, GameManager] = {}

    async def connect(self, room: str, playerID: str, websocket: WebSocket) -> None:
        if room not in self.rooms:
            self.rooms[room] = {}
        self.rooms[room][playerID] = websocket
        if room not in self.games:
            self.games[room] = GameManager()

    def disconnect(self, room: str, playerID: str) -> None:
        if room in self.rooms and playerID in self.rooms[room]:
            del self.rooms[room][playerID]
            print(f"player {playerID} left room {room}")
            if not self.rooms[room]:
                del self.rooms[room]
                del self.games[room]
                print(f"table {room} closed")

    async def send_private_JSON(self, room: str, playerID: str, message: Dict[str, Union[str, int, float]]) -> None:
        if room in self.rooms and playerID in self.rooms[room]:
            try:
                await self.rooms[room][playerID].send_json(message)
            except Exception:
                # Socket is dead — clean it up silently
                self.disconnect(room, playerID)

    async def broadcast_JSON_to_room(self, room: str, message: Dict[str, Union[str, int, float]]) -> None:
        if room not in self.rooms:
            raise Exception(f"room {room} does not exist")

        dead = []
        # FIX 1: list() creates a snapshot of the dict so that concurrent
        # coroutines adding new players don't cause "dictionary changed size
        # during iteration" RuntimeError
        for playerID, websocket in list(self.rooms[room].items()):
            try:
                await websocket.send_json(message)
            except Exception:
                # FIX 2: catch dead sockets per-player instead of letting one
                # crashed connection abort the entire broadcast
                dead.append(playerID)

        for playerID in dead:
            self.disconnect(room, playerID)

    def get_gameManager_from_playerID(self, playerID: str) -> Optional[GameManager]:
        for room, players in self.rooms.items():
            if playerID in players:
                return self.games[room]
        return None


# create connection manager for importing
manager = ConnectionManager()