import asyncio
import websockets
import json

async def listen_and_send():
    uri = "ws://localhost:8120/ws"
    async with websockets.connect(uri) as websocket:
        username = await asyncio.to_thread(input, "Enter your username: ")

        async def send():
            while True:
                content = await asyncio.to_thread(input, "Message: ")
                message = {
                    "username": username,
                    "content": content
                }
                await websocket.send(json.dumps(message))

        async def receive():
            while True:
                response = await websocket.recv()
                print(f"\nServer: {response}")

        await asyncio.gather(send(), receive())

asyncio.run(listen_and_send())
