import info
import threading
import time
import zmq

class Publisher():
    def __init__(self, hostname, timeout =5.0):
        self.hostname = hostname
        self.timeout = timeout
        self.last_heartbeat = time.time() - (2 * self.timeout )
    def check_if_alive(self):
        return True if time.time() - self.timeout < self.last_heartbeat else False
    def record_heartbeat(self):
        self.last_heartbeat = time.time()

class Heartbeat(threading.Thread):
    def __init__(self, pubsub, logger):
        threading.Thread.__init__(self)
        self.topic = "__heartbeat__"
        self.hostname = info.getHostName()
        self.pubsub = pubsub
        self.publishers = {}
    def subscribe(self, hostname):
        self.publishers[hostname] = Publisher(hostname)
    def check_if_alive(self, hostname):
        return self.publishers[hostname].check_if_alive()
    def record_heartbeat(self, hostname):
        if hostname not in self.publishers:
            self.subscribe(hostname)
        self.publishers[hostname].record_heartbeat()
    def run(self):
        while True: 
            self.pubsub.send(self.topic, self.hostname)
            time.sleep(2)

def init(pubsub, logger):
    hb = Heartbeat(pubsub, logger)
    hb.start()
    return hb
