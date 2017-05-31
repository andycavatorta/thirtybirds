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

from main import init as dmx_init

dmx = dmx_init(universe=0,frame_size=40)


while True:
    dmx.set(1, 255)
    time.sleep(60)
    dmx.set(1, 0)
    time.sleep(60)
