import info
import threading
import time
import zmq


class Subscription():
    def __init__(self, hostname, remote_ip, remote_port):
        self.hostname = hostname
        self.remote_ip = remote_ip
        self.remote_port = remote_port
        self.connected = False

class PubSub(threading.Thread):
    def __init__(self, publish_port, recvCallback, netStateCallback, logger):
        threading.Thread.__init__(self)
        self.publish_port = publish_port
        self.recvCallback = recvCallback 
        self.netStateCallback = netStateCallback 
        self.logger = logger
        self.hostname = info.getHostName()
        self.ip = info.getLocalIp()
        self.context = zmq.Context()
        self.pub_socket = self.context.socket(zmq.PUB)
        self.pub_socket.bind("tcp://*:%s" % publish_port)
        self.sub_socket = self.context.socket(zmq.SUB)
        self.subscriptions = {}

    def send(self, topic, msg):
        self.pub_socket.send_string("%s %s" % (topic, msg))

    def connect_to_publisher(self, hostname, remote_ip, remote_port):
        if hostname not in self.subscriptions:
            self.subscriptions[hostname] = Subscription(hostname, remote_ip, remote_port)
            self.sub_socket.connect("tcp://%s:%s" % (remote_ip, remote_port))

    def subscribe_to_topic(self, topic):
        #topic = topic.decode('ascii')
        #print "subscribe_to_topic", topic
        self.sub_socket.setsockopt(zmq.SUBSCRIBE, topic)

    def unsubscribe_from_topic(self, topic):
        topic = topic.decode('ascii')
        self.sub_socket.setsockopt(zmq.UNSUBSCRIBE, topic)

    def run(self):
        while True:
            incoming = self.sub_socket.recv()
            #print incoming
            topic, msg = incoming.split(' ', 1)
            self.recvCallback(topic, msg)
                
def init(publish_port, recvCallback, netStateCallback, logger):
    ps = PubSub(publish_port, recvCallback, netStateCallback, logger)
    ps.start()
    return ps
