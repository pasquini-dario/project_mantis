import socket
import threading
from ..utils.logger import logger
from ..InjectionManager import UNDETERMINED, IS_CURIOUS, IS_MALICIOUS, IS_LLM_ATTACKER

MAX_THREADS = 2 ** 6

class DecoyService:

    source_name = ''
    
    def __init__(
        self,
        port,
        host="0.0.0.0",
        name='decoy',
        hparams={}
    ):
        self.port = port
        self.host = host
        self.name = name
        self.hparams = hparams
        self.semaphore = threading.Semaphore(MAX_THREADS)

    def __call__(self, client_socket, client_address, injection_manager):
        raise NotImplementedError

    def handle_client(self, client_socket, client_address, injection_manager):
        try:
            self.__call__(client_socket, client_address, injection_manager)
        finally:
            self.semaphore.release()  # Release semaphore when done

        injection_manager.tracker.remove(*client_address)
        print(injection_manager.tracker.alive)

    def serve(self, injection_manager):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
            server_socket.bind((self.host, self.port))
            server_socket.listen()
            
            logger.info(f"{self.source_name}/{self.name} listening on {self.host}:{self.port}")
    
            while True:
                client_socket, client_address = server_socket.accept()
                self.semaphore.acquire()
                injection_manager.tracker.insert(*client_address, IS_CURIOUS, self)
                client_thread = threading.Thread(
                    target=self.handle_client,
                    args=(client_socket, client_address, injection_manager)
                )
                client_thread.start()