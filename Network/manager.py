
"""
This start file starts and manages three network services - discovery, pubsub, and heartbeat.  
Each is dependent upon the former.  






states:

discovery.caller - never connected
    start calling
discovery.caller - connected
    stop calling
    send data to callback
discovery.caller - disconnected
    start calling

events: no response
    set state to disconnected




"""


#########################################
######## IMPORTS, PATHS, GLOBALS ########
#########################################

import discovery
import threading

"""
class Manager(threading.Thread):
    def __init__(
            self, 
            role,
            discovery,
            pubsub,
            heartbeat,
            discovery_multicastGroup,
            discovery_multicastPort,
            discovery_responsePort,
            pubsub_pubPort,
            message_callback,
            status_callback,
            logger
        ):
        threading.Thread.__init__(self)
        self.role = role
        self.discovery_multicastGroup = discovery_multicastGroup
        self.discovery_multicastPort = discovery_multicastPort
        self.discovery_responsePort = discovery_responsePort
        self.pubsub_pubPort = pubsub_pubPort
        self.message_callback = message_callback
        self.status_callback = status_callback
        self.logger = logger
        self.server_ip = ""
        self.connected = False
        # initialize discovery, pubsub, heartbeat
        self.discovery = discovery.Discovery(
            "caller" if self.role == "client" else "responder",
            discovery_multicastGroup, 
            discovery_multicastPort, 
            discovery_responsePort, 
            None,
            logger
            )

        self.pubsub = pubsub.PubSub(
            self.role, 
            pubsub_pubPort, 
            self.message_callback,
            None,
            logger
            )
        self.heartbeat = heartbeat.Heartbeat(
            self.pubsub,
            None,
            logger
            )

        pubsub.add_subscribers
        pubsub.remove_subscribers

    def pubsub_callback(self, msg, host):
        print msg, host

    def run(self):
        while True:
            if self.role == "client":
                if self.heartbeat.get_status(): # if connected
                    if not self.connected: # if connected status has just changed
                        self.connected = True
                        logger("info","Thirtybirds.Network.manager:Manager","connected to server",None)
                        self.status_callback(True,self.server_ip)
                else: # if not connected
                    if self.connected: # if connected status has just changed
                        self.connected = False
                        self.server_ip = ""
                        logger("info","Thirtybirds.Network.manager:Manager","disconnected from server",None)
                        self.status_callback(False,self.server_ip)
                    # try to connect
                    
                    if self.discovery.get_status(): # if server responds to multicast discovery
                        if self.server_ip == "": # if discovery status has just changed
                            self.server_ip = self.discovery.get_server_ip() # save server ip locally
                            logger("info","Thirtybirds.Network.manager:Manager","server discovery: succeeded.  Server responded %s" % (self.server_ip),None)
                        self.pubsub.connect(self.server_ip)
                        if self.pubsub.get_status():
                            logger("info","Thirtybirds.Network.manager:Manager","pubsub start successful",None)
                            self.heartbeat.connect(self.pubsub)
                        else:
                            logger("info","Thirtybirds.Network.manager:Manager","pubsub start failed",None)
                        # start pubsub
                        # if pubsub succeeds
                            # 


                    else: # if no response
                        self.server_ip = "" # save server ip locally
                        if self.server_ip  != "": # if discovery status has just changed
                            logger("info","Thirtybirds.Network.manager:Manager","server discovery: failed." ,None)
            time.sleep(5)

            if self.role == "server":




def discovery_responder_callback():




def discovery_caller_callback():


"""

def init(
        role,
        discovery_multicastGroup,
        discovery_multicastPort,
        discovery_multicastPort2,
        discovery_responsePort,
        discovery_responsePort2,
        pubsub_pubPort,
        pubsub_pubPort2,
        message_callback,
        status_callback,
        logger
    ):

    return discovery.Discovery(
        "caller" if role == "client" else "responder",
        discovery_multicastGroup, 
        discovery_multicastPort, 
        discovery_responsePort, 
        None,
        logger
    )
