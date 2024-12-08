import threading
from datetime import datetime

from ..utils.logger import logger
from . import UNDETERMINED, IS_CURIOUS, IS_MALICIOUS, IS_LLM_ATTACKER

def id2state(id):
    return {
    UNDETERMINED:'UNDETERMINED',
    IS_CURIOUS:'IS_CURIOUS',
    IS_MALICIOUS:'IS_MALICIOUS',
    IS_LLM_ATTACKER:'IS_LLM_ATTACKER',
    }[id]

def get_timestamp():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

class User:
    def __init__(self, ip, port, state, source):
        self.ip = ip
        self.port = port
        self.state = state
        self.source = source
        self.last_activity = get_timestamp()

    def add_interaction(self, state):
        if state > self.state:
            self.state = state

    def __repr__(self):
        return f"[{self.state}] {self.ip}:{self.port}"

    def to_entry(self):
        entry = {
                'ip' : self.ip,
                'port' : self.port,
                'state' : id2state(self.state),
                'source' : self.source,
                'time_last_activity' : self.last_activity
        }
        return entry

        
class TriggerEvent:
    def __init__(self, user, keyword, source):
        self.user = user
        self.source = source
        self.keyword = keyword
        self.time = get_timestamp()


    def to_entry(self):
        entry = {
                'ip' : self.user.ip,
                'port' : self.user.port,
                'source' : self.source,
                'keyword' : self.keyword,
                'time' : self.time,
        }
        return entry



class Tracker:
    def __init__(self):
        self.alive = {}
        self.previous = []
        self.trigger_events_history = []

        self.lock = threading.Lock()

    def insert(self, ip, port, state, source):
        key = (ip, port)
        with self.lock:
            if not key in self.alive:
                user = User(ip, port, state, source)
                self.alive[key] = user
            else:
                user = self.alive[key]
            user.add_interaction(state)
        return user

    def remove(self, ip, port):
        key = (ip, port)
        with self.lock:
            if not key in self.alive:
                logger.error(f"Trying to remove from the tracker a user not in the alive list: {key}")
                return
            user = self.alive.pop(key)
            self.previous.append(user)

    def add_trigger_event(self, ip, port, keyword, source):
        user = self.insert(ip, port, IS_MALICIOUS, source)
        trigger_event = TriggerEvent(user, keyword, source)
        with self.lock:
            self.trigger_events_history.append(trigger_event)


        
        
        
        
        