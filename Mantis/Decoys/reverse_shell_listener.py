import socket

from . import DecoyService
from ..utils.logger import logger

COMMAND = 'pwd'
BUFFERSIZE = 1024

class ReverseShellListenerTest(DecoyService):

    """ Simple listener for reverse shell. Used for testing. """

    source_name = "reverse_shell_listener"
    
    def __call__(self, conn, addr, injection_manager):

        logger.info(f"{addr} connected.")

        logger.info(f"Sending {COMMAND} to {addr}.")
        conn.sendall(COMMAND.encode())
        
        client_response = conn.recv(BUFFERSIZE).decode()  
        
        logger.critical(f"{addr} responded: {client_response}")
        logger.critical(f'{addr} PWNED! Reverse shell open on {addr}')