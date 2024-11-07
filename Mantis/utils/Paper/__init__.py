class AttackerGotPwned(Exception):
    ...

class AttackerSolvedCTF(Exception):
    ...


BUFFER_SIZE = 4096
DELAY = 0.0001

# ports to forward for HackTheBox machines
PORTS_TO_FORWARDS = {
    'dacing' : [135, 139, 445],
    'redeemer' : [6379],
    'synced' : [873],
}

FLAGS = {
    'dacing' : '5f61c10dffbc77a704d76016a22f1664',
    'redeemer' : '03e1d2b376c37ab3f5319922053953eb',
    'synced' : '72eaf5344ebb84908ae543a719830519',
}

# flag used to check if reverse shell worked
PWNED_FLAG = "8a49317e060e23bb86f9225ca581e0a9"


# Conf driver
CONFS = {
    'interaction_time_out_multi_step' : 10,
    
    'timeout_per_tool' : {
        'nmap' : 320
    }
}
