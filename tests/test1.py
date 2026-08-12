import bluetooth
import socket
import time

def main():
    MAC = None
    Socket = None

    for addr, name in bluetooth.discover_devices(lookup_names=True):
        if name and "soundcore" in name.lower():
            MAC = addr
            break

    if not MAC:
        raise RuntimeError("soundcore device not found")
    
    try:
        sock = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM)
        sock.connect((MAC, 10))
        Socket = sock
    except OSError:
        sock.close()

    def send(data):
        Socket.sendall(bytes.fromhex(data))
    
    def m():
        print(f"Connected to {bluetooth.lookup_name(MAC)[1]} ({MAC}) channel 10")
        

if __name__ == "__main__":
    main()