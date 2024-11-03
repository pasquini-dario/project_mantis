import re, random, copy
import threading

from . import  ENCODING, KILL_PROCESS, KEEP_ALIVE
from ..utils import get_local_ip, get_public_ip, is_private_ip
from ..utils.logger import logger

class DefaultInjectionManager:
    def __init__(
		self,
        trigger_events,
        host_local_ip,
        host_public_ip,
	):
        self.trigger_events = trigger_events
        self.host_local_ip = host_local_ip
        self.host_public_ip = host_public_ip
        self.decoy_ths = {}


    def set_target_ip(self, attacker_ip, payload):
        # set target ip based on if the attacker is local or external
        if is_private_ip(attacker_ip):
            payload = payload.format(TARGET=self.host_local_ip)
        else:
            payload = payload.format(TARGET=self.host_public_ip)
        return payload    
    
    def spawn_service(self, port, service_class, kargs):
        if port in self.decoy_ths:
            return
        kargs['port'] = port
        logger.info(f"Starting {service_class.__name__} listening on {port}")
        server = service_class(**kargs)
        s = threading.Thread(target=server.serve, args=[self])
        s.start()
        self.decoy_ths[port] = s

    def spawn_decoys(self, decoy_settings):
        for port, (service_class, kargs) in decoy_settings.items():
            self.spawn_service(port, service_class, kargs)

    def make_armed_payload(self, trigger_pool, payload_pool):
        trigger = random.choice(trigger_pool)
        payload = random.choice(payload_pool)
        
        return trigger % payload

           
    def __call__(self, attacker_ip, source, keyword, msg_raw):

        if not keyword in self.trigger_events:
            logger.critical(f"Trigger event [{keyword}] issued by [{attacker_ip}] via [{source}]. But no event registered for [{keyword}]!")
            return msg_raw, False

        self.hook_decoy_vulnerability_exploitation(attacker_ip, source, keyword)
        
        try:
            msg = msg_raw.decode(ENCODING)
        except UnicodeDecodeError:
            return None, KEEP_ALIVE

        fun, kargs_fun, trigger_pool, payload_pool, to_spawn, is_to_kill = self.trigger_events[keyword]

        for port, (service_class, kargs) in to_spawn:
            self.spawn_service(port, service_class, kargs)

        armed_payload = self.make_armed_payload(trigger_pool, payload_pool)
        armed_payload = self.set_target_ip(attacker_ip, armed_payload)

        logger.critical(f"Trigger event [{keyword}] issued by [{attacker_ip}] via [{source}]. Payload injected: [{armed_payload}]")
        
        new_msg = fun(msg, keyword, armed_payload, **kargs_fun)
        new_msg = new_msg.encode()
        
        return new_msg, is_to_kill


    def hook_decoy_vulnerability_exploitation(self, attacker_ip, source, keyword):
        """ Hook function for trigger event. E.g., you can use it to send an allert email. """
        ...
