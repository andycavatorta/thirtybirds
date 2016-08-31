from __future__ import with_statement
import commands
import json
import netifaces
import socket
import struct
import threading
import time
import zmq
import yaml
import os
import imp
import sys
import datetime
from sys import platform as _platform
HOSTNAME = socket.gethostname()
BASE_PATH = os.path.split(os.path.dirname(os.path.realpath(__file__)))[0]
CLIENT_PATH = "%s/client/" % (BASE_PATH )
DEVICES_PATH = "%s/client/devices/" % (BASE_PATH )
COMMON_PATH = "%s/common/" % (BASE_PATH )
HOST_SPECIFIC_PATH = "%s/client/devices/%s/" % (BASE_PATH, HOSTNAME)
import nerveOSC
#####################
###### PUB SUB ######
#####################
subscribernames = None
HEARTBEAT = 2.0 # seconds
condition = threading.Condition()
pubsocket = None
subs_instance = None
osc_handler = None


class PubSocket():
    def __init__(self, port):
        self.port = port
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.PUB)
        # self.socket.setsockopt(zmq.LINGER, 0)
        self.socket.bind("tcp://*:%s" % port)
    def send(self, topic, msg):
        self.socket.send_string("%s %s" % (topic, msg))
 

class Subscription():
    def __init__(self, hostname):
        self.hostname = hostname
        self.ip = None
        self.localPort = None
        self.remotePort = None
        self.lastHeartbeat = 0.0
        self.connected = False
    def setHeartbeat(self):
        self.lastHeartbeat = time.time()
    def getLastHeartbeat(self, lastHeartbeat):
        return self.lastHeartbeat
    def testConnection(self):
        hb = self.lastHeartbeat + ( 2 * HEARTBEAT) > time.time() #if heartbeat is two beats stale
        if self.connected and not hb: # recently disconnected
            self.connected = False
            return False
        if not self.connected and hb: # recently connected
            self.connected = True          
            return True
        return None
    def setConnected(self, ip=None, remotePort=None):
        self.ip = ip
        self.remotePort = remotePort
        self.connected = True

class Subscriptions(threading.Thread):
    """ this class manages a zmq sub socket and code for tracking publishers' connect state using heartbeats """
    def __init__(self, condition, hostnames, role, publish_port, recvCallback, netStateCallback):
        threading.Thread.__init__(self)
        # socket details
        self.role = role
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.SUB)
        # self.socket.setsockopt(zmq.LINGER, 0)
        self.recvCallback = recvCallback
        # subscription tracking details
        self.subscriptions = {}
        map(self.addSubscription, hostnames)
        self.hbTimeout = 1.0
        self.publish_port = publish_port
        self.netStateCallback = netStateCallback
    def addSubscription(self, hostname):
        """ nominally registers a new subscription, does not connect a socket for them b/c it may not be connected at init """
        self.subscriptions[hostname] = Subscription(hostname)
    def connectSubscription(self, hostname, ip, port, topics_t, topic_osc=None, topics_v=None):
        """ when a publisher's ip and hostname are discovered, we can connect a subscription to it """
        if hostname not in self.subscriptions:
            with condition:
                self.subscriptions[hostname] = Subscription(hostname)
                self.socket.connect("tcp://%s:%s" % (ip, port))
                condition.notify_all()
        else:
            with condition:
                self.socket.connect("tcp://%s:%s" % (ip, port))
                condition.notify_all()
        for topic in topics_t:
            topic = topic.decode('ascii')
            self.socket.setsockopt_string(zmq.SUBSCRIBE, topic)
        if topics_v is not None:
            topics_v = topics_v.decode('ascii')
            self.socket.setsockopt_string(zmq.SUBSCRIBE, topics_v)
        if topic_osc is not None:
            topic_osc = topic_osc.decode('ascii')
            self.socket.setsockopt_string(zmq.SUBSCRIBE, topic_osc)
        self.subscriptions[hostname].setConnected(ip, self.publish_port)
        self.netStateCallback(hostname, True, self.role, port)


    def disconnectSubscription(self, hostname):
        self.netStateCallback(hostname, False, self.role, self.publish_port)
    def printSubscriptions(self):
        pubsocket.send("DASHBOARD", self.subscriptions)
    def getSubscriptions(self):
        return self.subscriptions
    def recordHeartbeat(self, hostname):
        # print repr(self.subscriptions), hostname
        print 'hearbeat',(hostname)
        self.subscriptions[hostname].setHeartbeat()
    def run(self):
        while True:
            msg_str = self.socket.recv()
            #print msg_str
            topic, msg = msg_str.split(' ', 1)
            if topic == "__heartbeat__":
                self.recordHeartbeat(msg)
            elif topic == "DASHBOARD":
                print topic, msg
            else:
                self.recvCallback(topic, msg)
            

class CheckHeartbeats(threading.Thread):
    """ this class manages a zmq sub socket and code for tracking publishers' connect state using heartbeats """
    def __init__(self, condition, subscriptions_instance, role, publish_port):
        threading.Thread.__init__(self)
        self.subscriptions_instance = subscriptions_instance
        self.role = role
        self.pubPort = publish_port
    def run(self):
        with condition:
            condition.wait()
        while True:
            subs = self.subscriptions_instance.getSubscriptions().iteritems()
            if self.pubPort == 10002:
                global subs_instance
                subs_instance = self.subscriptions_instance
            for hostname, subscriber in subs:#self.subscriptions_instance.getSubscriptions().iteritems():
                stat = subscriber.testConnection()
                if stat is True:
                    self.subscriptions_instance.netStateCallback(hostname, True, self.role, self.pubPort)
                    if self.pubPort == 10002:
                        pubsocket.send("DASHBOARD", "server connected")
                    else:
                        pubsocket.send("DASHBOARD", "dashboard connected")
                        if ROLE == 'client':
                            if subs_instance is not None:
                                subs_instance.printSubscriptions()
                    
                if stat == False:
                    self.subscriptions_instance.netStateCallback(hostname, False, self.role, self.pubPort)
                    if self.pubPort == 10002:
                        pubsocket.send("DASHBOARD", "server disconnected")
            time.sleep(HEARTBEAT)

def sendHeartbeats(pubsocket, heartbeatMsg):
    while True:
        pubsocket.send("__heartbeat__", heartbeatMsg)
        # pubsocket.send("DASHBOARD", heartbeatMsg)
        time.sleep(HEARTBEAT/2)

def init(subscribernames,localName, role, publish_port, recvCallback,netStateCallback):
    #pubsocket = PubSocket(publish_port, localName)
    #pubsocket.start()
    print 'starting pubsub...'
    global pubsocket
    pubsocket = PubSocket(publish_port)
    subscriptions = Subscriptions(condition, subscribernames, role, publish_port, recvCallback, netStateCallback)
    subscriptions.daemon = True
    subscriptions.start()
    checkheartbeats = CheckHeartbeats(condition, subscriptions, role, publish_port)
    checkheartbeats.daemon = True
    checkheartbeats.start()


    t1 = threading.Thread(target=sendHeartbeats, args=(pubsocket, localName))
    t1.daemon = True
    t1.start()

    return {
        "publish":pubsocket.send, # topic, msg
        "subscribe":subscriptions.connectSubscription, # hostname, ip, port, topics_t
        "getSubscriptions":subscriptions.getSubscriptions,
        "printSubscriptions":subscriptions.printSubscriptions
    }

#####################
##### DISCOVERY #####
#####################

def getLocalIP():
    if _platform == "darwin":
        interfaceName = "en0"
    else:
        interfaceName = "wlan0"
    netifaces.ifaddresses(interfaceName)
    return netifaces.ifaddresses(interfaceName)[2][0]['addr']

#####################
##### RESPONDER #####
#####################

class Responder(threading.Thread):
    def __init__(self, pubPort, listener_grp, listener_port, response_port, localIP, callback):
        threading.Thread.__init__(self)
        self.pubPort = pubPort
        self.listener_port = listener_port
        self.response_port = response_port
        self.localIP = localIP
        self.callback = callback
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_LINGER, struct.pack('ii', 1, 0))
        self.sock.bind((listener_grp, listener_port))
        self.mreq = struct.pack("4sl", socket.inet_aton(listener_grp), socket.INADDR_ANY)
        self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, self.mreq)
        self.IpTiming = {}
    def response(self, remoteIP, msg_json): # response sends the local IP to the remote device
        print "discovery Responder 1"
        if self.IpTiming.has_key(remoteIP):
            if self.IpTiming[remoteIP] + 6 > time.time():
                return
        else:
            self.IpTiming[remoteIP] = time.time()
        print "discovery Responder 2"
        context = zmq.Context()
        print "discovery Responder 3"
        socket = context.socket(zmq.PAIR)
        print "discovery Responder 4"
        socket.connect("tcp://%s:%s" % (remoteIP,self.response_port))
        print "discovery Responder 5"
        socket.send(msg_json)
        print "discovery Responder 6"
        socket.close()
        print "discovery Responder 7"
    def run(self):
        while True:
                msg_json = self.sock.recv(1024)
                msg_d = json.loads(msg_json)
                print "Event: Device Discovered:",msg_json
                remoteIP = msg_d["ip"]
                resp_d = self.callback(msg_d, self.pubPort)
                if ROLE == "server":
                    resp_json = json.dumps( {"ip":self.localIP,"hostname":"**SERVER**"})
                elif ROLE == "dashboard":
                    resp_json = json.dumps( {"ip":self.localIP,"hostname":"**DASHBOARD**"})
                else:
                    resp_json = json.dumps( {"ip":self.localIP,"hostname":socket.gethostname()})
                #print "resp_json=", resp_json
                self.response(remoteIP,resp_json)
            #except Exception as e:
            #    print "Exception in dynamicDiscovery.server.Discovery: %s" % (repr(e))

def init_responder(pubPort, listener_grp, listener_port, response_port, callback):
    print "listening for multicast on port" , listener_port, "in multicast group", listener_grp
    global responder
    responder = Responder(
        pubPort,
        listener_grp,
        listener_port, 
        response_port, 
        getLocalIP(), 
        callback
    )
    responder.daemon = True
    responder.start()

##################
##### CALLER #####
##################

class CallerSend(threading.Thread):
    def __init__(self, localHostname, localIP, mcast_grp, mcast_port):
        #print "-----", localHostname, localIP, mcast_grp, mcast_port
        threading.Thread.__init__(self)
        self.mcast_grp = mcast_grp
        self.mcast_port = mcast_port
        self.mcast_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.mcast_sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 32)
        # self.mcast_sock.setsockopt(socket.SOL_SOCKET, socket.SO_LINGER, struct.pack('ii', 1, 0))
        self.msg_d = {"ip":localIP,"hostname":localHostname}
        self.msg_json = json.dumps(self.msg_d)
        self.mcast_msg = self.msg_json
        self.serverFound_b = False
    def setServerFound(self,b):
        self.serverFound_b = b
    def run(self):
        while True:
            if not self.serverFound_b:
                print "calling to",self.mcast_grp, self.mcast_port
                self.mcast_sock.sendto(self.mcast_msg, (self.mcast_grp, self.mcast_port))
            time.sleep(5)

class CallerRecv(threading.Thread):
    def __init__(self, hostname, pubPort, recv_port, callback, callerSend, id_num):
        threading.Thread.__init__(self)
        self.id_num = id_num
        self.hostname = hostname
        self.pubPort = pubPort
        self.callback = callback
        self.callerSend = callerSend
        self.listen_context = zmq.Context()
        self.listen_sock = self.listen_context.socket(zmq.PAIR)
        # self.listen_sock.setsockopt(zmq.LINGER, 0)
        self.listen_sock.bind("tcp://*:%d" % recv_port)
        print "CallerRecv listening on port %d" % (recv_port)
    def run(self):
        #print "CallerRecv run"
        print "discovery CallerRecv 1"
        msg_json = self.listen_sock.recv()
        #print ">>>>>>>>>>", msg_json
        print "discovery CallerRecv 2"
        msg_d = yaml.safe_load(msg_json)
        print ">>>>>>>>>>>>>> %s" % (msg_d)
        print "discovery CallerRecv 3"
        self.callback(msg_d,self.pubPort,msg_d['hostname'],self.id_num)
        # to do: test the connection
        print "discovery CallerRecv 4"
        self.callerSend.setServerFound(True)
        print "discovery CallerRecv 5"
        if self.pubPort == 10002:
            pubsocket.send("DASHBOARD", "server connected")
        else:
            pubsocket.send("DASHBOARD", "dashboard connected")

def init_caller(hostname, pubPort, mcast_grp, mcast_port, recv_port, callback, id_num):
    print "calling port" , mcast_port, "in multicast group", mcast_grp
    if id_num == 0:
        global callerSend
        callerSend = CallerSend(socket.gethostname(), getLocalIP(), mcast_grp, mcast_port)
        callerRecv = CallerRecv(hostname, pubPort, recv_port, callback, callerSend, 0)
        callerRecv.daemon = True
        callerRecv.start()
        callerSend.daemon = True
        callerSend.start()
        return callerSend
    else:
        global callerSend2
        callerSend2 = CallerSend(socket.gethostname(), getLocalIP(), mcast_grp, mcast_port)
        callerRecv2 = CallerRecv(hostname, pubPort, recv_port, callback, callerSend2, 1)
        callerRecv2.daemon = True
        callerRecv2.start()
        callerSend2.daemon = True
        callerSend2.start()
        return callerSend2

#####################
#### GLOBAL INIT ####
#####################

def init_networking(
        subscribernames, 
        hostname, 
        role, 
        pubPort, 
        pubPort2, 
        mcastGroup, 
        mcastPort, 
        mcastPort2, 
        rspnsPort, 
        rspnsPort2, 
        oschandler=None
    ):
    global pubsub_api
    global ROLE
    ROLE = role
    global osc_handler
    osc_handler = oschandler

    if role == "dashboard":
        pubsub_api = init(subscribernames, hostname, role, pubPort2, recvCallback, netStateCallback)
    else:
        pubsub_api = init(subscribernames, hostname, role, pubPort, recvCallback,netStateCallback)

    if role == "client":
        global pubsub_api2
        pubsub_api2 = init(subscribernames, hostname, role, pubPort2, recvCallback, netStateCallback)

        global callerSend
        callerSend = init_caller(hostname, pubPort, mcastGroup, mcastPort, rspnsPort, serverFoundCallback, 0)

        global callerSend2
        callerSend2 = init_caller(hostname, pubPort2, mcastGroup, mcastPort2, rspnsPort2, serverFoundCallback, 1)
    else:
        if role == "dashboard":
            rspnsPort = rspnsPort2
            mcastPort = mcastPort2
            pubPort = pubPort2
        global responder
        responder = init_responder(pubPort, mcastGroup, mcastPort, rspnsPort, handleSubscriberFound)

    while threading.active_count() > 0:
        time.sleep(0.1)


def recvCallback(topic, msg):
    print "recvCallback", repr(topic), repr(msg)
    if ROLE == "client":
        osc_handler(nerveOSC.parse(msg))

def netStateCallback(hostname, connected, role, pubPort):
    print "netStateCallback", hostname, connected, pubPort
    if role == "client":
        if pubPort == 10002:
            callerSend.setServerFound(connected)
        else:
            callerSend2.setServerFound(connected)

def serverFoundCallback(msg,pubPort,hostname, id_num):
    if id_num == 0:
        SPECIFIC_PATH =  "%s/client/devices/%s" % (BASE_PATH,socket.gethostname())
        instruments = imp.load_source('mapping', '%s/mapping.py'%(SPECIFIC_PATH))
        for instrument in instruments.instruments:
            instrumentName = "%s%s" % (socket.gethostname(),instrument)
            print 'DENTRO: ', instrumentName
            pubsub_api["subscribe"](msg["hostname"],msg["ip"],pubPort, ("__heartbeat__", hostname),instrumentName)
    else:
        pubsub_api2["subscribe"](msg["hostname"],msg["ip"],pubPort, ("__heartbeat__", hostname), None, "DASHBOARD")

def handleSubscriberFound(msg, pubPort):
    print "@@@@@@@@@@@@@@@@@@",pubPort
    if pubPort == 10002:
        print '>>>>>>>>>>>>>>>>>> SERVER'
        pubsub_api["subscribe"](msg["hostname"],msg["ip"],pubPort, ("__heartbeat__"))
    else:
        print '>>>>>>>>>>>>>>>>>> DASHBOARD'
        pubsub_api["subscribe"](msg["hostname"],msg["ip"],pubPort, ("__heartbeat__"), None, "DASHBOARD")


