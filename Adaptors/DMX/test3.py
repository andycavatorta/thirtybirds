"""
1 pump
4 pump
5 
6
7
9


"""

import time
import threading

import simpledmx

"""
dmx = simpledmx.DMXConnection("/dev/serial/by-id/usb-ENTTEC_DMX_USB_PRO_EN211488-if00-port0")
while True:
    dmx.setChannel(1, 255, True)
    time.sleep(60)
    dmx.setChannel(1, 0, True)
    time.sleep(60)

"""

from main import init as dmx_init
dmx = dmx_init(universe=0,frame_size=40)

dmx.set(1, 255)
time.sleep(60)

"""
while True:
    dmx.set(1, 255)
    time.sleep(60)
    dmx.set(1, 0)
    time.sleep(60)
"""