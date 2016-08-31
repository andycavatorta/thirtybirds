import netifaces
import urllib2
import socket

def getLocalIp():
    ifaces = netifaces.interfaces()
    for iface in ifaces:
        try:
            ip = netifaces.ifaddresses(iface)[netifaces.AF_INET][0]['addr']
            if ip[0:3] != "127":
                return ip
        except Exception as e:
            print 'network %s not available...' % (iface)
    return False

def getGlobalIp():
    try:
        return urllib2.urlopen("http://icanhazip.com").read().strip()
    except Exception as e:
        return False

def getHostName():
    try:
        return socket.gethostname()
    except Exception as e:
        return False

def getOnlineStatus():
    r = getGlobalIp()
    return False if r==False else True