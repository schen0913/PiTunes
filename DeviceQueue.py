import asyncio
from BluetoothManager import BluetoothManager

#Constant variables
SKIP_THRESHOLD = 2

class DeviceQueue:
    def __init__(self) -> None:
        self.lock = asyncio.Lock()
        self.queue = []             #list of {"mac", "name"}
        self.current = None         #{"mac", "name"} or None
        self.voters = set()

    #Return snapshot of queue state
    async def snapshot(self):
        async with self.lock:
            return {
                "current": self.current,
                "queue": list(self.queue),
                "votes": len(self.voters),
                "skip_threshold": SKIP_THRESHOLD
            }

    #Adds a device to queue only if it's new
    async def addDevice(self, mac, name):
        async with self.lock:
            if not name: 
                name = mac

            if self.current and self.current.get("mac") == mac:
                return False
            
            if any(device["mac"] == mac for device in self.queue):
                return False
            
            if not self.current:
                await BluetoothManager.connectDevice(self, mac)
                self.current = {"mac": mac, "name": name}
                print(f"[queue] set current to {name} ({mac})")
                return True
            else:
                self.queue.append({"mac":mac, "name": name})
                print(f"[queue] added {name} ({mac})")
                return True
        
    #When current device decides to end its turn
    async def endTurn(self):
        async with self.lock:
            if not self.current:
                return None
            
            ended = self.current
            self.voters.clear()

            if self.queue:
                await BluetoothManager.connectDevice(self, self.queue[0]["mac"])
                self.current = self.queue.pop(0)
                return self.current
            else:
                self.current = None
                return None
        
    #When current device disconnects or idle timeout hits
    async def autoNext(self):
        async with self.lock:
            if not self.queue:
                self.current = None
                return None
            
            self.voters.clear()
            self.current = self.queue.pop(0)
            return self.current
    
    async def voteSkip(self, voterID):
        async with self.lock:
            if not self.current:
                return False, False
            
            self.voters.add(voterID)
            
            if len(self.voters) >= SKIP_THRESHOLD:
                self.voters.clear()
                return True, True
            return True, False