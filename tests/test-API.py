#!/usr/bin/env python3
from SCAPI import Soundcore
import time

soundcore = Soundcore("34:09:C9:2F:1A:98")

soundcore.connect()


soundcore.send("08ee0000000681110000550000010000e4")
print("Switched to ANC")
time.sleep(3)

soundcore.send("08ee0000000681110002550000010000e6")
print("Switched to normal mode")
time.sleep(3)

soundcore.send("08ee0000000681110001550000010000e5")
print("Switched to transparency mode")

soundcore.close()