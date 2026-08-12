import socket

mac = "34:09:C9:2F:1A:98"

s = socket.socket(
    socket.AF_BLUETOOTH,
    socket.SOCK_STREAM,
    socket.BTPROTO_RFCOMM,
)

print("fd:", s.fileno())

s.connect((mac, 10))

print("connected")
s.send(bytes.fromhex("08ee0000000681110001550000010000e5"))

input("Press Enter to disconnect...")
s.close()