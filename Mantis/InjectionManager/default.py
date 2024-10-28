import re, random, copy
import threading

from . import  ENCODING, KILL_PROCESS, KEEP_ALIVE
from ..utils.logger import logger

class DefaultInjectionManager:
    def __init__(
		self,
        trigger_events,
        target,
	):
        self.target = target
        self.trigger_events = trigger_events
        self.decoy_procs = {}


    def spawn_service(self, port, service_class, kargs):
        kargs['port'] = port
        logger.info(f"Starting {service_class.__name__} listening on {port}")
        server = service_class(**kargs)
        # Use threading.Thread instead of multiprocessing.Process
        s = threading.Thread(target=server, args=[self])
        s.start()
        self.decoy_procs[port] = s  # Update the dictionary name accordingly

    def spawn_decoys(self, decoy_settings):
        for port, (service_class, kargs) in decoy_settings.items():
            self.spawn_service(port, service_class, kargs)

    def make_armed_payload(self, trigger_pool, payload_pool):
        trigger = random.choice(trigger_pool)
        payload = random.choice(payload_pool)
        payload = payload.format(TARGET=self.target)
        
        return trigger % payload
           
    def __call__(self, attacker_ip, source, keyword, msg_raw):

        try:
            msg = msg_raw.decode(ENCODING)
        except UnicodeDecodeError:
            return None, KEEP_ALIVE

        fun, kargs_fun, trigger_pool, payload_pool, to_spawn, is_to_kill = self.trigger_events[keyword]

        for port, (service_class, kargs) in to_spawn:
            self.spawn_service(port, service_class, kargs)

        armed_payload = self.make_armed_payload(trigger_pool, payload_pool)

        logger.critical(f"Trigger event [{keyword}] issued by [{attacker_ip}] via [{source}]. Payload injected: [{armed_payload}]")
        
        new_msg = fun(msg, keyword, armed_payload, **kargs_fun)
        new_msg = new_msg.encode()
        
        return new_msg, is_to_kill
