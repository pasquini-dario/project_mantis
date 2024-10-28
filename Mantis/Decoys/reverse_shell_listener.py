import socket

from . import DecoyService
from ..utils.logger import logger

COMMAND = 'pwd'
BUFFERSIZE = 1024

class ReverseShellListenerTest(DecoyService):

    """ Simple listener for reverse shell. Used for testing. """

    source_name = "reverse_shell_listener"
    
    def __call__(self, injection_manager):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((self.host, self.port))
            s.listen(1)

            logger.info(f"{self.source_name} listening on {self.host}:{self.port}")
            
            while True:
                conn, addr = s.accept()
                with conn:
                    logger.info(f"{addr} connected.")

                    logger.info(f"Sending {COMMAND} to {addr}.")
                    conn.sendall(COMMAND.encode())
                    
                    client_response = conn.recv(BUFFERSIZE).decode()  
                    
                    logger.critical(f"{addr} responded: {client_response}")
                    logger.critical(f'{addr} PWNED! Reverse shell open on {addr}')