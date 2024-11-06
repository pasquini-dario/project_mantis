import threading

from ..utils.logger import logger

class User:
    def __init__(self, ip, port, state):
        self.ip = ip
        self.port = port
        self.state = state

    def add_interaction(self, state):
        if state > self.state:
            self.state = state

    def __repr__(self):
        return f"[{self.state}] {self.ip}:{self.port}"
        
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
                self.alive[key] = User(ip, port, state)
            self.alive[key].add_interaction(state)

    def remove(self, ip, port):
        key = (ip, port)
        with self.lock:
            if not key in self.alive:
                logger.error(f"Trying to remove from the tracker a user not in the alive list: {key}")
                return
            user = self.alive.pop(key)
            self.previous.append(user)

        
        
        
        
        