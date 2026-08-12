import configparser
from pathlib import Path
import sys
import bluetooth
import socket
import threading
import time
import subprocess
import asyncio

from SCAPI import Soundcore

async def get_currently_connected_device():
    if sys.platform == "win32":        
        from winrt.windows.devices.bluetooth import BluetoothDevice
        from winrt.windows.devices.enumeration import DeviceInformation
        devices = await DeviceInformation.find_all_async()
        
        for info in devices:
            device = await BluetoothDevice.from_id_async(info.id)
    
            if device is None:
                continue
    
            if device.connection_status != 1:
                continue
    
            if "soundcore" not in device.name.lower():
                continue
    
            mac = ":".join(
                f"{(device.bluetooth_address >> (8 * i)) & 0xff:02X}"
                for i in reversed(range(6))
            )
    
            return mac
        return None
    elif sys.platform == "linux":
        try:
            proc = await asyncio.create_subprocess_exec(
                "bluetoothctl", "devices", "Connected",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, _ = await proc.communicate()
            output = stdout.decode("utf-8")

            for line in output.splitlines():
                parts = line.strip().split(" ", 2)
                if len(parts) == 3 and parts[0] == "Device":
                    mac, name = parts[1], parts[2]
                    if "soundcore" in name.lower():
                        return mac.upper()
        except FileNotFoundError:
            print("Error: bluetoothctl is not installed on this Linux system.")
        except Exception as e:
            print(f"Linux Bluetooth query failed: {e}")

    return None

def get_config_path() -> Path:
    if sys.platform == "win32":
        base_dir = Path.home() / "AppData" / "Roaming" / "SoundCoreAPI"
    else:
        base_dir = Path.home() / ".config" / "SoundCoreAPI"

    base_dir.mkdir(parents=True, exist_ok=True)
    return base_dir / "config.ini"

def setup(config_file: Path) -> configparser.ConfigParser:
    config = configparser.ConfigParser()

    config["DEFAULT"] = {
        "port": "8765",
        "channel": "10",
        "device_mac": ""
    }

    with open(config_file, "w") as f:
        config.write(f)

    print(f"[+] Config created at: {config_file}")
    return config

def load_config() -> configparser.ConfigParser:
    config_file = get_config_path()

    if not config_file.exists():
        return setup(config_file)

    config = configparser.ConfigParser()
    config.read(config_file)

    return config

config = load_config()

channel = config.getint("DEFAULT", "channel", fallback=10)
host = "127.0.0.1"
port = config.getint("DEFAULT", "port", fallback=8765)
device_mac = config.get("DEFAULT", "device_mac", fallback=None)

MODE_PACKETS = {
    "transparency": "08ee0000000681110001550000010000e5",
    "normal": "08ee0000000681110002550000010000e6",
    "anc": "08ee0000000681110000550000010000e4",
}

bt_socket = None
bt_lock = threading.Lock()

def bluetooth_worker():
    global bt_socket
    global device_mac

    while True:
        with bt_lock:
            connected = bt_socket is not None

        if connected:
            time.sleep(1)
            continue

        if not device_mac:
            print("Searching for connected soundcore device...")
            output = subprocess.check_output(
                ["bluetoothctl", "devices", "Connected"],
                text=True
            )

            for line in output.splitlines():
                _, mac, name = line.split(" ", 2)

                if "soundcore" in name.lower():
                    device_mac = mac
                    break

        if not device_mac:
            time.sleep(2)
            continue

        try:
            print(f"Connecting to {device_mac}...")

            connected_socket = None
            s = None

            try:
                s = bs = socket.socket(
                    socket.AF_BLUETOOTH,
                    socket.SOCK_STREAM,
                    socket.BTPROTO_RFCOMM,
                )
                s.connect((device_mac, 10))

                connected_socket = s

            except OSError as e:
                print(f"Channel {c}: {e}")

                if s is not None:
                    try:
                        s.close()
                    except OSError:
                        pass

            if connected_socket is None:
                print("Could not connect to any RFCOMM channel")
                time.sleep(2)
                continue

            with bt_lock:
                bt_socket = connected_socket

            print(
                f"Connected to {device_mac} "
                f"RFCOMM channel 10"
            )

        except OSError as e:
            print(f"Bluetooth connection failed: {e}")
            time.sleep(2)

def send_packet(data):
    global bt_socket

    with bt_lock:
        if bt_socket is None:
            return False

        try:
            bt_socket.send(bytes.fromhex(data))
            return True

        except OSError:
            try:
                bt_socket.close()
            except OSError:
                pass

            bt_socket = None
            return False

def handle_client(client):
    try:
        while True:
            data = client.recv(1024)

            if not data:
                break

            command = data.decode().strip()

            if command.startswith("MODE "):
                mode = command[5:].lower()

                if mode not in MODE_PACKETS:
                    client.sendall(b"ERROR\n")
                    continue

                if send_packet(MODE_PACKETS[mode]):
                    client.sendall(b"OK\n")
                else:
                    client.sendall(b"DISCONNECTED\n")

            elif command == "STATUS":
                with bt_lock:
                    connected = bt_socket is not None

                client.sendall(
                    b"CONNECTED\n" if connected else b"DISCONNECTED\n"
                )

            else:
                client.sendall(b"UNKNOWN_COMMAND\n")

    finally:
        client.close()

def server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((host, port))
    server_socket.listen()

    print(f"Daemon listening on {host}:{port}")

    while True:
        client, _ = server_socket.accept()

        threading.Thread(
            target=handle_client,
            args=(client,),
            daemon=True,
        ).start()

threading.Thread(
    target=bluetooth_worker,
    daemon=True,
).start()

server()