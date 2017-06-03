
import time
import threading

import simpledmx
dmx = simpledmx.DMXConnection("/dev/ttyUSB0")


def test_cycle(channels,values,delay):
    for value in values:
        for channel in channels:
            print channel,value
            dmx.setChannel(channel,value, True)
            time.sleep(0.01)
        time.sleep(delay)

#test_cycle([1,2,3,4,5],[0,255,0,255,0,255], 60)
