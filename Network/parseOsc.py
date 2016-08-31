"""
This library parses nerve osc messages in the format

/M-Audio_Oxygen_88/note_on {"amplitude": "57", "channel": "1", "pitch": "{'midi': 55, 'cents': 0, '12tet': 'G3', 'octave': 3, 'pitch': 'G', 'freq': 195.998}"}

It currently only supports paths in the format /device/command

It will probably have to be ammended for more complex paths

"""

import json

def parse(osc):
    path, params_j = osc.split(" ", 1)
    path_l = path.split("/")
    device = path_l[1]
    command = path_l[-1]
    params = json.loads(params_j)
    return [device, command, params, params_j]
    
    #print repr(params)




