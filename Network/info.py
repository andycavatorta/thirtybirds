import netifaces
import urllib2
import socket

from thirtybirds.Logs.main import ExceptionCollector

@ExceptionCollector("Thirtybirds.Network.info getLocalIp")
def getLocalIp():
    ifaces = netifaces.interfaces()
    for iface in ifaces:
        try:
            ip = netifaces.ifaddresses(iface)[netifaces.AF_INET][0]['addr']
            if ip[0:3] != "127":
                return ip
        except Exception as e:
            pass
    return False

@ExceptionCollector("Thirtybirds.Network.info getGlobalIp")
def getGlobalIp():
    try:
        return urllib2.urlopen("http://icanhazip.com").read().strip()
    except Exception as e:
        return False

@ExceptionCollector("Thirtybirds.Network.info getHostName")
def getHostName():
    try:
        return socket.gethostname()
    except Exception as e:
        return False

@ExceptionCollector("Thirtybirds.Network.info getOnlineStatus")
def getOnlineStatus():
    r = getGlobalIp()
    return False if r==False else True