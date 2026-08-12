#!/usr/bin/env python3

import argparse
import configparser
from pathlib import Path
from SCAPI import Soundcore
import sys
import asyncio

if sys.platform == "win32":
    CONFIG_PATH = Path.home() / "AppData" / "Roaming" / "SoundCoreAPI" / "config.ini"
else:
    CONFIG_PATH = Path.home() / ".config" / "SoundCoreAPI" / "config.ini"

def setup_config():
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)

    mac = input("Bluetooth MAC address: ").strip()
    channel = input("RFCOMM channel [10]: ").strip() or "10"

    config = configparser.ConfigParser()
    config["Soundcore"] = {
        "mac": mac,
        "channel": channel
    }

    with open(CONFIG_PATH, "w") as f:
        config.write(f)

    return mac, int(channel)

def load_config():
    if not CONFIG_PATH.exists():
        return setup_config()

    config = configparser.ConfigParser()
    config.read(CONFIG_PATH)

    mac = config["Soundcore"]["mac"]
    channel = config.getint("Soundcore", "channel")

    return mac, channel

parser = argparse.ArgumentParser()
parser.add_argument(
    "mode",
    nargs="?",
    type=str.lower,
    choices=["anc", "normal", "transparency"]
)

parser.add_argument(
    "--config",
    action="store_true",
    help="Change Bluetooth configuration"
)
parser.add_argument(
    '--verbose',
    '-v',
    action="store_true",
    help="Run app in verbose mode"
)
parser.add_argument(
    '--getmac',
    action="store_true",
    help="Returns your currently connected device's MAC address"
)
args = parser.parse_args()

if args.config:
    mac, channel = setup_config()
else:
    mac, channel = load_config()

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
            # Run bluetoothctl asynchronously without blocking the event loop
            proc = await asyncio.create_subprocess_exec(
                "bluetoothctl", "devices", "Connected",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, _ = await proc.communicate()
            output = stdout.decode("utf-8")

            for line in output.splitlines():
                parts = line.strip().split(" ", 2)
                # Output format: "Device XX:XX:XX:XX:XX:XX Soundcore Motion+"
                if len(parts) == 3 and parts[0] == "Device":
                    mac, name = parts[1], parts[2]
                    if "soundcore" in name.lower():
                        return mac.upper()
        except FileNotFoundError:
            print("Error: bluetoothctl is not installed on this Linux system.")
        except Exception as e:
            print(f"Linux Bluetooth query failed: {e}")

    return None

if args.getmac:
    print(asyncio.run(get_currently_connected_device()))
    exit()

soundcore = Soundcore(mac, channel, args.verbose)

if soundcore.connect() and args.mode:
    soundcore.switchMode(args.mode)

soundcore.close()