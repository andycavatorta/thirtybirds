#########################################
######## IMPORTS, PATHS, GLOBALS ########
#########################################

import info
import json
import socket
import struct
import threading
import time
import zmq

def callerSend(start_stop):
    logger("info","Thirtybirds.Network.discovery:callerSend","global reference called before initialized",None)

#####################
##### RESPONDER #####
#####################

class Responder(threading.Thread):
    def __init__(self, listener_grp, listener_port, response_port, localIP, callback, logger):
        threading.Thread.__init__(self)
        self.listener_port = listener_port
        self.response_port = response_port
        self.localIP = localIP
        self.callback = callback
        self.logger = logger
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((listener_grp, listener_port))
        self.mreq = struct.pack("4sl", socket.inet_aton(listener_grp), socket.INADDR_ANY)
        self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, self.mreq)
        self.IpTiming = {}
        self.logger("trace","Thirtybirds.Network.discovery:Responder.__init__","Responder started",None)
    def response(self, remoteIP, msg_json): # response sends the local IP to the remote device
        if self.IpTiming.has_key(remoteIP):
            if self.IpTiming[remoteIP] + 6 > time.time():
                return
        else:
            self.IpTiming[remoteIP] = time.time()
        context = zmq.Context()
        socket = context.socket(zmq.PAIR)
        socket.connect("tcp://%s:%s" % (remoteIP,self.response_port))
        socket.send(msg_json)
        socket.close()
    def run(self):
        while True:
                msg_json = self.sock.recv(1024)
                self.logger("trace","Thirtybirds.Network.discovery:Responder.run","Device Discovered:%s" % (msg_json),None)
                msg_d = json.loads(msg_json)
                remoteIP = msg_d["ip"]
                resp_d = self.callback(msg_d)
                resp_json = json.dumps( {"ip":self.localIP,"hostname":socket.gethostname()})
                self.response(remoteIP,resp_json)

def init_responder(listener_grp, listener_port, response_port, callback):
    print "listening for multicast on port" , listener_port, "in multicast group", listener_grp
    responder = Responder(
        listener_grp,
        listener_port, 
        response_port, 
        info.getLocalIp(), 
        callback
    )
    responder.start()


##################
##### CALLER #####
##################

class CallerSend(threading.Thread):
    def __init__(self, localHostname, localIP, mcast_grp, mcast_port, logger):
        threading.Thread.__init__(self)
        self.mcast_grp = mcast_grp
        self.mcast_port = mcast_port
        self.logger = logger
        self.mcast_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.mcast_sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 32)
        self.msg_d = {"ip":localIP,"hostname":localHostname}
        self.msg_json = json.dumps(self.msg_d)
        self.mcast_msg = self.msg_json
        self.active = True
        self.logger("trace","Thirtybirds.Network.discovery:CallerSend.__init__","CallerSend started",None)
    def set_active(self,val):
        self.logger("trace","Thirtybirds.Network.discovery:CallerSend.set_active",val,None)
        self.active = val
    def run(self):
        while True:
            if self.active == True:
                self.logger("trace","Thirtybirds.Network.discovery:CallerSend.run","calling to %s:%d" % (self.mcast_grp, self.mcast_port),None)                
                self.mcast_sock.sendto(self.mcast_msg, (self.mcast_grp, self.mcast_port))
            time.sleep(5)

class CallerRecv(threading.Thread):
    def __init__(self, recv_port, callback, callerSend, logger):
        threading.Thread.__init__(self)
        self.callback = callback
        self.callerSend = callerSend
        self.logger = logger
        self.listen_context = zmq.Context()
        self.listen_sock = self.listen_context.socket(zmq.PAIR)
        self.listen_sock.bind("tcp://*:%d" % recv_port)
        self.msg = ""
        self.server_ip = ""
        self.logger("trace","Thirtybirds.Network.discovery:CallerRecv.__init__","CallerRecv listening on port %d" % (recv_port),None)
    def run(self):
        while True:
            msg_json = self.listen_sock.recv()
            msg_d = json.loads(msg_json)
            print msg_json
            if self.callback:
                self.callback(msg_d)
            self.callerSend.set_active("stop")

###################
##### WRAPPER #####
###################

class Discovery():
    def __init__(
            self,
            role,
            multicastGroup,
            multicastPort, 
            responsePort,
            status_callback,
            logger
        ):
        self.role = role
        self.multicastGroup = multicastGroup
        self.multicastPort = multicastPort
        self.responsePort = responsePort
        self.status_callback = status_callback
        self.logger = logger
        self.server_ip = ""
        self.status = "" 

        if self.role == "caller":
            self.callerSend = CallerSend(
                info.getHostName(), 
                info.getLocalIp(), 
                multicastGroup, 
                multicastPort, 
                logger
            )
            self.callerRecv = CallerRecv(
                responsePort, 
                self.status_callback, 
                self.callerSend, 
                logger
            )
            self.callerRecv.start()
            self.callerSend.start()

        if self.role == "responder":
            self.responder = Responder(
                self.multicastGroup,
                self.multicastPort, 
                self.responsePort, 
                info.getLocalIp(), 
                self.status_callback, 
                logger
            )
            self.responder.start()

        logger("trace","Thirtybirds.Network.discovery:Discovery","initialized as %s" % (self.role),None)

    def begin(self):
        self.callerSend.set_active(True)

    def end(self):
        self.callerSend.set_active(False)

    def get_status(self):
        return self.status

    def get_server_ip(self):
        return self.server_ip

def init(
        role,
        multicastGroup,
        multicastPort, 
        responsePort,
        status_callback,
        logger
    ):
    return Discovery(
        role,
        multicastGroup,
        multicastPort, 
        responsePort,
        status_callback,
        logger
    )
