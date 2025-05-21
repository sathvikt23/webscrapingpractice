import asyncio
import websockets
import json

async def listen_and_send():
    uri = "ws://localhost:8120/ws"
    async with websockets.connect(uri) as websocket:
        async def send():
            while True:
                # Send structured JSON data
                message = {
                    "username": input("Enter your username: "),
                    "content": input("Message: ")
                }
                await websocket.send(json.dumps(message))
                response = await websocket.recv()
                print(f"Server: {response}")


        async def receive():
            while True:
                response = await websocket.recv()
                print(f"Server: {response}")

        await asyncio.gather(send(), receive())

asyncio.run(listen_and_send())
