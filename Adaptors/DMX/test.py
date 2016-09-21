
import time

import threading

from main import init as dmx_init

dmx = dmx_init(universe=0,frame_size=40)

while True:
    for val in range(255):
        print "value=", val
        for ch in range (40):
            dmx.set(10, val)
        #dmx.set(8, 0)
        time.sleep(0.01)
