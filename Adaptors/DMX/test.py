
import time

import threading

from main import init as dmx_init

dmx = dmx_init(universe=0,frame_size=40)

while True:
    for val in range(255):
        print "value=", val
        for ch in range (40):
            if ch != 8:
                dmx.set(ch, val)
        #dmx.set(8, 0)
        time.sleep(0.02)
    for val in range(255):
        print "value=", val
        for ch in range (40):
            if ch != 8:
                dmx.set(ch, 255-val)
        #dmx.set(8, 0)
        time.sleep(0.02)