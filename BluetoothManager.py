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
        # Check for paired devices and add to queue
        while True:
            command = "bluetoothctl devices Paired"
            process = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            stdout, stderr = await process.communicate()

            if process.returncode == 0:
                devices_output = stdout.decode().strip().split('\n')
                for line in devices_output:
                    if line.startswith('Device'):
                        parts = line.split(' ', 2)
                        mac = parts[1]
                        name = parts[2] if len(parts) > 2 else ""
                        await self.queue.addDevice(mac, name)

            # Check whether the current device is still connected
            try:
                snap = await self.queue.snapshot()
                current = snap.get("current")
                if current and current.get("mac"):
                    cur_mac = current.get("mac")
                    cur_name = current.get("name")
                    info_cmd = f"bluetoothctl info {cur_mac}"
                    info_proc = await asyncio.create_subprocess_shell(
                        info_cmd,
                        stdout=asyncio.subprocess.PIPE,
                        stderr=asyncio.subprocess.PIPE,
                    )

                    info_out, info_err = await info_proc.communicate()
                    if info_proc.returncode == 0:
                        out_text = info_out.decode()
                        connected = False
                        for l in out_text.splitlines():
                            if l.strip().startswith("Connected:"):
                                val = l.split(":", 1)[1].strip().lower()
                                connected = (val == "yes")
                                break

                        if not connected:
                            print(f"[bt] {cur_name} disconnected, advancing queue")
                            await self.queue.autoNext()
                    else:
                        # log and continue; bluetoothctl might momentarily fail
                        err_text = info_err.decode().strip()
                        print(f"[bt] info check failed for {cur_mac}: {err_text}")
            except Exception as e:
                print(f"[bt] error checking current device: {e}")

            await asyncio.sleep(10)  # Poll every 10 seconds