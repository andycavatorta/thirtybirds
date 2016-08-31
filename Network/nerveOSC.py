"""
nerveOSC messages

format:


device/path/../path/verb {pitch:{},timbre:{},dynamics:{}}

if device is undefined, path starts with /


"""
import json
import socket

def parse(nerveOSC_str):
	path_str, params_j = nerveOSC_str.split(" ", 1)
	path_l = path_str.split("/")
	return {
		"host":path_l[0],
		"path":path_str,
		"innerpath":"/"+"/".join(path_l[1:]),
		"params": json.loads(params_j)
	}


def assemble(device_str, path_str, payload_str):
	"""
	path_str is formatted without or trailing leading slash
	"""
	return "%s%s %s" % (device_str, path_str, payload_str)
