# SoundCore API

SoundCore API is an unofficial Python API for interacting with SoundCore Bluetooth services on desktop.

## Disclaimer

This is an unofficial API. I am not affiliated with or endorsed by SoundCore in any way.

## Supported Devices

Currently, this API only supports the SoundCore R50i NC, as it is the only SoundCore device I own.

If you have another SoundCore device and would like to help add support for it, feel free to DM me on Discord.

### Why doesn't this app support all SoundCore devices?

SoundCore encrypts or obfuscates the data sent between the app and the device. The encryption or obfuscation method are different between devices, so each device requires its own implementation.

## Requirements

* Python 3
* Bluetooth adapter

## Usage

Run the application with:

```bash
python app.py
```

On the first run, the application will ask for your device's Bluetooth MAC address and RFCOMM channel. These settings will be saved for future use.

### Switch Modes

```bash
python app.py anc
python app.py normal
python app.py transparency
```

Mode names are case-insensitive.

### Configuration

To change the saved Bluetooth configuration:

```bash
python app.py --config
```

### Verbose Mode

To enable verbose output:

```bash
python app.py --verbose
```

or:

```bash
python app.py -v
```

### Help

```bash
python app.py --help
```

```text
usage: app.py [-h] [--config] [--verbose] [{anc,normal,transparency}]

positional arguments:
  {anc,normal,transparency}

options:
  -h, --help            show this help message and exit
  --config              Change Bluetooth configuration
  --verbose, -v         Run app in verbose mode
```

## Finding Your Device Information

### Finding the MAC Address

To find the MAC address of your device, you can use `app.py` by running:

```bash
python app.py --getmac
```

It will output something like this:

```text
1A:2B:3C:4D:5E:6F
```

This is your device's MAC address.

If that method doesn't work, you can try the following methods.

### Linux

Run this command in your terminal:

```bash
bluetoothctl devices Connected
```

You should get output similar to this:

```text
Device 1A:2B:3C:4D:5E:6F soundcore R50i NC
```

The MAC address is the `1A:2B:3C:4D:5E:6F` part.

### Windows

If the first method doesn't work on Windows, please report the issue to me through Discord DMs so I can help fix the app.

### Finding the RFCOMM Channel

Finding the correct RFCOMM channel is a little more difficult.

The RFCOMM channel is required for communicating with your device. Connecting to a random channel will not work.

You could try brute-forcing all available channels (`1-30`) to find the correct one. However, the method I used was to capture the Bluetooth communication between the SoundCore mobile app and the device.

1. Enable **Bluetooth HCI snoop logging** in your phone's Developer Options.
2. Connect your SoundCore device to your phone.
3. Open the SoundCore mobile app.
4. Change a setting on your device, such as switching the ANC mode.
5. Retrieve the Bluetooth HCI snoop log using ADB.
6. Open the HCI snoop log in [Wireshark](https://www.wireshark.org/).
7. Find the RFCOMM traffic generated when changing the setting.
8. Inspect the RFCOMM packets and find the channel being used.
9. Use that channel when configuring the API.
