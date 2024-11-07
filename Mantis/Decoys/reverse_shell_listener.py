import socket

from . import DecoyService
from ..utils.logger import logger

FLAG_REVERSE_SHELL = "8a49317e060e23bb86f9225ca581e0a9"
COMMAND = f"echo '{FLAG_REVERSE_SHELL}' > PWNED.txt\n"

class ReverseShellListenerTest(DecoyService):

    """ Simple listener for reverse shell. Used for testing. It writes a flag on the attacker's machine to validate the opening of the shell. """

    source_name = "reverse_shell_listener"
    
    def __call__(self, conn, addr, injection_manager):

        logger.info(f"{addr} connected.")

        logger.critical(f'{addr} PWNED! Reverse shell open on {addr}')
        
        logger.info(f"Sending {COMMAND} to {addr}.")
        conn.sendall(COMMAND.encode())

        conn.close()
                
