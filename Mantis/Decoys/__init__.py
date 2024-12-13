import socket
import threading
from itertools import count

from ..utils.logger import logger
from ..InjectionManager import UNDETERMINED, IS_CURIOUS, IS_MALICIOUS, IS_LLM_ATTACKER

MAX_THREADS = 2 ** 6

class DecoyService:

    source_name = 'base_class'
    
    def __init__(
        self,
        port,
        host="0.0.0.0",
        name='decoy',
        number_allowed_interactions=None,
        hparams={},
    ):
        self.port = port
        self.host = host
        self.name = name
        self.hparams = hparams
        self.semaphore = threading.Semaphore(MAX_THREADS)
        self.number_allowed_interactions = number_allowed_interactions

    def __call__(self, client_socket, client_address, injection_manager):
        raise NotImplementedError

    def handle_client(self, client_socket, client_address, injection_manager):
        try:
            self.__call__(client_socket, client_address, injection_manager)
        except BrokenPipeError:
            logger.warning(f"{self.source_name}/{self.name} likely a port scanning is happening.")
        finally:
            self.semaphore.release()  # Release semaphore when done

        injection_manager.tracker.remove(*client_address)

    def __repr__(self):
        return f'{self.source_name}'

    def serve(self, injection_manager):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
            server_socket.bind((self.host, self.port))
            server_socket.listen()
            
            logger.info(f"{self.source_name}/{self.name} listening on {self.host}:{self.port}")
    
            if self.number_allowed_interactions == None:
                loop = count()
            else:
                loop = range(self.number_allowed_interactions)

            for _ in loop:
                client_socket, client_address = server_socket.accept()
                self.semaphore.acquire()
                injection_manager.tracker.insert(*client_address, IS_CURIOUS, self.source_name)
                client_thread = threading.Thread(
                    target=self.handle_client,
                    args=(client_socket, client_address, injection_manager)
                )
                client_thread.start()

            logger.info(f"{self.source_name}/{self.name} stop listening on {self.host}:{self.port} due reaching number allowed interactions")
