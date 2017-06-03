
import time
import threading

import simpledmx
simpledmx.DMXConnection("/dev/ttyUSB0")

from main3 import init as dmx_init
dmx = dmx_init(universe=0,frame_size=40)

def test_cycle(channels,values,delay):
    for value in values:
        for channel in channels:
            print channel,value
            dmx.set(channel,value)
            time.sleep(0.01)
        time.sleep(delay)

test_cycle([1,2,3,4],[0,255,0,255,0,255], 60)
