from fastapi import WebSocket
from PokerGame.Core import GameManager
from typing import Dict, Optional, Union
from dataclasses import dataclass, field


@dataclass
class Room:
    game: GameManager = field(default_factory=GameManager)
    players: Dict[str, WebSocket] = field(default_factory=dict)

    def add_player(self, player_id: str, websocket: WebSocket) -> None:
        self.players[player_id] = websocket

    def remove_player(self, player_id: str) -> None:
        self.players.pop(player_id, None)

    @property
    def is_empty(self) -> bool:
        return not self.players


class ConnectionManager:
    def __init__(self):
        self.rooms: Dict[str, Room] = {}

    # ------------------------------------------------------------------ rooms

    def _get_or_create_room(self, room_id: str) -> Room:
        if room_id not in self.rooms:
            self.rooms[room_id] = Room()
        return self.rooms[room_id]

    def _close_room_if_empty(self, room_id: str) -> None:
        if room_id in self.rooms and self.rooms[room_id].is_empty:
            del self.rooms[room_id]
            print(f"table {room_id} closed")

    # --------------------------------------------------------------- players

    async def connect(self, room_id: str, player_id: str, websocket: WebSocket) -> None:
        room = self._get_or_create_room(room_id)
        room.add_player(player_id, websocket)
        print(f"player {player_id} joined room {room_id}")

    def disconnect(self, room_id: str, player_id: str) -> None:
        if room_id not in self.rooms:
            return
        self.rooms[room_id].remove_player(player_id)
        print(f"player {player_id} left room {room_id}")
        self._close_room_if_empty(room_id)

    # ---------------------------------------------------------------- sending

    async def send_private_JSON(
        self,
        room_id: str,
        player_id: str,
        message: Dict[str, Union[str, int, float]],
    ) -> None:
        room = self.rooms.get(room_id)
        if not room:
            return
        websocket = room.players.get(player_id)
        if not websocket:
            return
        try:
            await websocket.send_json(message)
        except Exception:
            self.disconnect(room_id, player_id)

    async def broadcast_JSON_to_room(
        self,
        room_id: str,
        message: Dict[str, Union[str, int, float]],
    ) -> None:
        room = self.rooms.get(room_id)
        if not room:
            raise ValueError(f"room {room_id} does not exist")

        dead: list[str] = []
        for player_id, websocket in list(room.players.items()):
            try:
                await websocket.send_json(message)
            except Exception:
                dead.append(player_id)

        for player_id in dead:
            self.disconnect(room_id, player_id)

    # --------------------------------------------------------------- lookups

    def get_game(self, room_id: str) -> Optional[GameManager]:
        room = self.rooms.get(room_id)
        return room.game if room else None

    def get_game_by_player(self, player_id: str) -> Optional[GameManager]:
        for room in self.rooms.values():
            if player_id in room.players:
                return room.game
        return None


manager = ConnectionManager()