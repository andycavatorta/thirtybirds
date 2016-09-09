import info
import threading
import time
import zmq

from thirtybirds.Logs.main import ExceptionCollector

class Publisher():
    @ExceptionCollector("Thirtybirds.Network.heartbeat Publisher.__init__")
    def __init__(self, hostname, timeout =5.0):
        self.hostname = hostname
        self.timeout = timeout
        self.last_heartbeat = time.time() - (2 * self.timeout )
    @ExceptionCollector("Thirtybirds.Network.heartbeat Publisher.check_if_alive")
    def check_if_alive(self):
        return True if time.time() - self.timeout < self.last_heartbeat else False
    @ExceptionCollector("Thirtybirds.Network.heartbeat Publisher.record_heartbeat")
    def record_heartbeat(self):
        self.last_heartbeat = time.time()

class Heartbeat(threading.Thread):
    @ExceptionCollector("Thirtybirds.Network.heartbeat Heartbeat.__init__")
    def __init__(self, hostname, pubsub):
        threading.Thread.__init__(self)
        self.topic = "__heartbeat__"
        self.hostname = hostname
        self.pubsub = pubsub
        self.publishers = {}
    @ExceptionCollector("Thirtybirds.Network.heartbeat Heartbeat.subscribe")
    def subscribe(self, hostname):
        self.publishers[hostname] = Publisher(hostname)
    @ExceptionCollector("Thirtybirds.Network.heartbeat Heartbeat.check_if_alive")
    def check_if_alive(self, hostname):
        return self.publishers[hostname].check_if_alive()
    @ExceptionCollector("Thirtybirds.Network.heartbeat Heartbeat.record_heartbeat")
    def record_heartbeat(self, hostname):
        if hostname not in self.publishers:
            self.subscribe(hostname)
        self.publishers[hostname].record_heartbeat()
    @ExceptionCollector("Thirtybirds.Network.heartbeat Heartbeat.run")
    def run(self):
        while True: 
            self.pubsub.send(self.topic, self.hostname)
            time.sleep(2)

@ExceptionCollector("Thirtybirds.Network.heartbeat init")
def init(hostname, pubsub):
    hb = Heartbeat(hostname, pubsub)
    hb.start()
    return hb
