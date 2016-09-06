import info
import os
import sys
import threading
import time
import traceback
import zmq

from thirtybirds.Logs.main import ExceptionCollector

class Subscription():
    @ExceptionCollector("Thirtybirds.Network.pubsub Subscription.__init__")
    def __init__(self, hostname, remote_ip, remote_port):
        self.hostname = hostname
        self.remote_ip = remote_ip
        self.remote_port = remote_port
        self.connected = False

class PubSub(threading.Thread):
    @ExceptionCollector("Thirtybirds.Network.pubsub PubSub.__init__")
    def __init__(self, publish_port, recvCallback, netStateCallback):
        threading.Thread.__init__(self)
        self.publish_port = publish_port
        self.recvCallback = recvCallback 
        self.netStateCallback = netStateCallback 
        self.hostname = info.getHostName()
        self.ip = info.getLocalIp()
        self.context = zmq.Context()
        self.pub_socket = self.context.socket(zmq.PUB)
        self.pub_socket.bind("tcp://*:%s" % publish_port)
        self.sub_socket = self.context.socket(zmq.SUB)
        self.subscriptions = {}

    @ExceptionCollector("Thirtybirds.Network.pubsub PubSub.send")
    def send(self, topic, msg):
            self.pub_socket.send_string("%s %s" % (topic, msg))

    @ExceptionCollector("Thirtybirds.Network.pubsub PubSub.connect_to_publisher")
    def connect_to_publisher(self, hostname, remote_ip, remote_port):
            if hostname not in self.subscriptions:
                self.subscriptions[hostname] = Subscription(hostname, remote_ip, remote_port)
                self.sub_socket.connect("tcp://%s:%s" % (remote_ip, remote_port))

    @ExceptionCollector("Thirtybirds.Network.pubsub PubSub.subscribe_to_topic")
    def subscribe_to_topic(self, topic):
            self.sub_socket.setsockopt(zmq.SUBSCRIBE, topic)

    @ExceptionCollector("Thirtybirds.Network.pubsub PubSub.unsubscribe_from_topic")
    def unsubscribe_from_topic(self, topic):
            topic = topic.decode('ascii')
            self.sub_socket.setsockopt(zmq.UNSUBSCRIBE, topic)

    @ExceptionCollector("Thirtybirds.Network.pubsub PubSub.run")
    def run(self):
        while True:
            incoming = self.sub_socket.recv()
            topic, msg = incoming.split(' ', 1)
            self.recvCallback(topic, msg)
                
@ExceptionCollector("Thirtybirds.Network.pubsub init")
def init(publish_port, recvCallback, netStateCallback):
    ps = PubSub(publish_port, recvCallback, netStateCallback)
    ps.start()
    return ps
