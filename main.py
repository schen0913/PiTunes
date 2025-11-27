import asyncio
from DeviceQueue import DeviceQueue
from web_api import createAPI
from ws_server import ws_broadcast
from AudioRouter import AudioRouter
from BluetoothManager import BluetoothManager

async def main():
    queue = DeviceQueue()
    router = AudioRouter()
    bt = BluetoothManager(queue, router)

    #Background tasks
    asyncio.create_task(bt.pollLoopTBD())
    asyncio.create_task(ws_broadcast(queue))

    #Start Quart API
    PiTunes = createAPI(queue)
    await PiTunes.run_task(host="0.0.0.0", port=5000)

if __name__ == "__main__":
    asyncio.run(main())
