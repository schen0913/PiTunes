import asyncio
import json
import websockets

#Listens for incoming websocket connections
async def ws_broadcast(queue):
    async for websocket in websockets.serve(lambda ws: client(ws, queue), "0.0.0.0", 8765):
        pass

#Sends snapshot to client every second as a json string
async def client(ws, queue):
    while True:
        snap = await queue.snapshot()
        await ws.send(json.dumps(snap))
        await asyncio.sleep(1)