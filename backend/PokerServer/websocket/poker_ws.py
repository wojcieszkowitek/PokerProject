# websocket endpoint
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

router = APIRouter()

# testowy socket
@router.websocket("/ws/test")
async def websocket_test_endpoint(websocket: WebSocket):
    # 1. Akceptujemy połączenie (Handshake)
    await websocket.accept()
    
    # 2. Wysyłamy powitanie zaraz po połączeniu
    await websocket.send_text("Siema! Połączono z serwerem pokera.")
    
    try:
        # 3. Pętla, która utrzymuje socket przy życiu
        while True:
            # Czekamy na wiadomość od klienta
            data = await websocket.receive_text()
            
            # Wyświetlamy to, co napisał klient, w konsoli serwera
            print(f"Klient napisał: {data}")
            
            # Odsyłamy potwierdzenie do klienta
            await websocket.send_text(f"Otrzymałem Twoją wiadomość: {data}")
            
    except WebSocketDisconnect:
        print("Klient się rozłączył")