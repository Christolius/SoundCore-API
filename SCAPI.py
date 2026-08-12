import socket
import threading

MODE_PACKETS = {
    "transparency": "08ee0000000681110001550000010000e5",
    "normal": "08ee0000000681110002550000010000e6",
    "anc": "08ee0000000681110000550000010000e4",
}

class Soundcore:
    def __init__(self, mac, channel, verbose):
        self.client = None
        self.mac = mac
        self.port = channel
        self.__lck = threading.Lock()
        self.v = verbose

    def connect(self):
        try:
            self.client = socket.socket(
                socket.AF_BLUETOOTH,
                socket.SOCK_STREAM,
                socket.BTPROTO_RFCOMM
            )
            self.client.connect((self.mac, self.port))
            if self.v: print(f"Connected to {self.mac} on port {self.port}")
            return True
        except OSError as e:
            if self.v: print(
                f"Failed to connect to {self.mac} on port {self.port} "
                f"[ERROR]: {e}"
            )

            if self.client:
                self.client.close()

            self.client = None
            return False

    def switchMode(self, mode):
        if mode.lower() not in MODE_PACKETS:
            return False
        self.send(MODE_PACKETS[mode.lower()])
        if self.v: print(f"Switched to mode {mode}")

    def send(self, data):
        with self.__lck:
            if self.client is None:
                return False

            try:
                self.client.sendall(bytes.fromhex(data))
                return True

            except OSError:
                try:
                    self.client.close()
                except OSError:
                    pass

                self.client = None
                return False

    def close(self):
        with self.__lck:
            if self.client is None:
                return

            try:
                self.client.close()
            except OSError:
                pass

            self.client = None

        if self.v: print("Disconnected")
