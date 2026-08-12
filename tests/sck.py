import bluetooth
import socket
import time

MAC = None

for addr, name in bluetooth.discover_devices(lookup_names=True):
    if name and "soundcore" in name.lower():
        MAC = addr
        break

if not MAC:
    raise RuntimeError("soundcore device not found")

s = None
port = None

try:
    sock = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM)
    sock.connect((MAC, 10))
    s = sock
    port = 10
except OSError:
    sock.close()

if not s:
    raise RuntimeError("No RFCOMM channel found")

def send(data):
    s.sendall(bytes.fromhex(data))

print("connected", MAC, "channel", port)
print("Switching to Transparency Mode in 5s...")
time.sleep(5)

send("08ee0000000681110001550000010000e5")

print("Switched to Transparency Mode.")
print("Disconnecting in 10s...")

time.sleep(10)
s.close()

