import subprocess

class AudioRouter:
    def __init__(self):
        self.current_device = None

    def route_audio(self, device_name):
        if self.current_device == device_name:
            return  # Already routed to this device

        command = f"pactl set-default-sink {device_name}"
        try:
            subprocess.run(command, shell=True, check=True)
            self.current_device = device_name
            print(f"Audio routed to {device_name}")
        except subprocess.CalledProcessError as e:
            print(f"Failed to route audio to {device_name}: {e}")
