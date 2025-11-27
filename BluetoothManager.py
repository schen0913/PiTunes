import asyncio
import subprocess

class BluetoothManager:
    def __init__(self, queue, router):
        self.queue = queue
        self.router = router
        self.connected_device = None

    async def connect_device(self, device_address):
        if self.connected_device == device_address:
            return  # Already connected to this device

        command = f"bluetoothctl connect {device_address}"
        process = await asyncio.create_subprocess_shell(
            command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        stdout, stderr = await process.communicate()

        if process.returncode == 0:
            self.connected_device = device_address
            print(f"Connected to Bluetooth device {device_address}")
        else:
            print(f"Failed to connect to {device_address}: {stderr.decode().strip()}")

    async def pollLoop(self):
        # Check `bluetoothctl paired-devices` to find devices and add to queue
        