import websockets
import asyncio
import json

no_players = int(input("podaj liczbe graczy: "))
connected_websockets = {}
uri = "ws://127.0.0.1:8000/ws/10"
test_token = "1234"
headers = {
    "token": test_token
}

async def connect_client(clientID: str, uri: str):
    async with websockets.connect(uri=uri, additional_headers=headers) as websocket:
        print(f"{clientID} just connected to {uri}")
        connected_websockets[clientID] = websocket

        try:
            while(True):
                message = await websocket.recv()
                message = parse_to_json(message)
                # if not message:
                #     print("couldn't parse to json")
                #     continue

        except websockets.exceptions.ConnectionClosed:
            print(f"player {clientID} disconnected :<")

        finally:
            if clientID in connected_websockets:
                del connected_websockets[clientID]


def parse_to_json(string: str):
    try:
        string = json.loads(string)
        return string
    except Exception as e:
        return None
    
async def main():
    tasks = []
    for i in range(no_players):
        task = asyncio.create_task(connect_client(str(i+1), uri=uri))
        tasks.append(task)

    # start all tasks
    await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main())