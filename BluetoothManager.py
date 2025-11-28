import asyncio
import subprocess
import re

class BluetoothManager:
    def __init__(self, queue, router):
        self.queue = queue
        self.router = router
        self.connected_device = None

    async def connectDevice(self, mac):
        if self.connected_device == mac:
            return  # Already connected to this device

        command = f"bluetoothctl connect {mac}"
        process = await asyncio.create_subprocess_shell(
            command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        stdout, stderr = await process.communicate()

        if process.returncode == 0:
            self.connected_device = mac
            print(f"Connected to Bluetooth device {mac}")
        else:
            print(f"Failed to connect to {mac}: {stderr.decode().strip()}")

    async def pollLoop(self):
        while True:
            # Check for available devices and add to queue
            command = "hcitool scan"
            process = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            stdout, stderr = await process.communicate()

            if process.returncode == 0:
                devices_output = stdout.decode().strip().split('\n')
                enqueueNewDevices(devices_output)
                
            # Check whether the current device is still connected
            try:
                await testConnection()
            except Exception as e:
                print(f"[bt] error checking current device: {e}")

            await asyncio.sleep(10)  # Poll every 10 seconds

    async def enqueueNewDevices(devices):
        for line in devices:
            if not line.startswith('Scanning'):
                parts = re.split(' |\t|\n', line, 2)
                mac = parts[1]
                name = parts[2] if len(parts) > 2 else ""
                info_cmd = f"bluetoothctl info {mac}"
                info_proc = await asyncio.create_subprocess_shell(
                    info_cmd,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                )

                info_out, info_err = await info_proc.communicate()
                if info_proc.returncode == 0:
                    out_text = info_out.decode()
                    paired = False
                    for l in out_text.splitlines():
                        if l.strip().startswith("Paired:"):
                            val = l.split(":", 1)[1].strip().lower()
                            connected = (val == "yes")
                            break

                    if paired:
                        await self.queue.addDevice(mac, name)

    async def testConnection():
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