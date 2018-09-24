import asyncio
import websockets


async def client():
    async with websockets.connect('ws://localhost:8765') as websocket:
        while True:
            for i in range(200):
                await websocket.send(str(i*5))
                print(i*5)
                await asyncio.sleep(0.1)
            for i in range(200, 0, -1):
                await websocket.send(str(i*5))
                print(i*5)
                await asyncio.sleep(0.1)

loop = asyncio.get_event_loop()
loop.run_until_complete(client())
