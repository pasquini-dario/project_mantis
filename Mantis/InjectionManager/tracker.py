import threading
from datetime import datetime

from ..utils.logger import logger
from . import UNDETERMINED, IS_CURIOUS, IS_MALICIOUS, IS_LLM_ATTACKER, DECOY_VISIT, DECOY_ATTACK

def id2str(id):
    return {
    UNDETERMINED:'UNDETERMINED',
    IS_CURIOUS:'IS_CURIOUS',
    IS_MALICIOUS:'IS_MALICIOUS',
    IS_LLM_ATTACKER:'IS_LLM_ATTACKER',

    DECOY_VISIT:'DECOY_VISIT',
    DECOY_ATTACK:'DECOY_ATTACK', 
    }[id]

def get_timestamp():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

class User:
    def __init__(self, ip):
        self.ip = ip

        self.state = UNDETERMINED
        self.events = []

    def add_interaction(self, state, event):
        self.events.append(event)
        if state > self.state:
            self.state = state

    def __repr__(self):
        return f"[{self.state}] {self.ip}"

    def to_entry(self):
        entry = {
                'ip' : self.ip,
                'state' : id2str(self.state),
                'events' : [event.to_entry() for event in self.events],
        }
        return entry

        

class Event:
    def __init__(self, type, port, source, **kargs):
        self.port = port
        self.source = source
        self.type = type
        self.timestamp = get_timestamp()
        self.kargs = kargs

    def to_entry(self):
        entry = {
                'port' : self.port,
                'type' : id2str(self.type),
                'source' : self.source,
                'timestamp' : self.timestamp,
        }
        entry.update(self.kargs)
        return entry

class Tracker:
    def __init__(self):
        self.users = {}
        self.previous = []
        self.trigger_events_history = []

        self.lock = threading.Lock()

    def insert(self, ip, port, state, event):
        key = ip
        with self.lock:
            if not key in self.users:
                user = User(ip)
                self.users[key] = user
            else:
                user = self.users[key]
            user.add_interaction(state, event)
        return user

    def remove(self, ip, port):
        ...

    def add_trigger_event(self, ip, port, source, keyword, armed_payload):
        event = Event(
            DECOY_ATTACK,
            port,
            source,
            keyword=keyword,
            armed_payload=armed_payload
        )
        user = self.insert(ip, port, IS_MALICIOUS, event)

    def add_decoy_visit(self, ip, port, source, **kargs):
        event = Event(DECOY_VISIT, port, source, **kargs)
        user = self.insert(ip, port, IS_CURIOUS, event)


    
        
        