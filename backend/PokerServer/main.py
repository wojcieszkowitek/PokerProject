from fastapi import FastAPI
from PokerServer.websocket.poker_ws import router as ws_router

app = FastAPI()

app.include_router(ws_router)