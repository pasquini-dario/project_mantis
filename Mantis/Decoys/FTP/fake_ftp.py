import socket

from . import *
from .. import DecoyService
from ...utils.logger import logger

class AnonymousFTP(DecoyService):

    """Decoy FTP with Anonymous credentials enabled"""

    source_name = 'Decoy.FTP'
    
    def __call__(self, injection_manager):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
            server_socket.bind((self.host, self.port))
            server_socket.listen(5)
            
            logger.info(f"{self.source_name} listening on {self.host}:{self.port}")

            while True:
                try:
                    client_socket, client_address = server_socket.accept()
                    logger.info(f"Connection from {client_address}")                
                    self.handle_ftp_session(client_socket, client_address, injection_manager)
                except Exception as ex:
                    logger.error(f"{type(self)} raised exception {ex} and died.")
                    logger.info(f"{type(self)} restarting...")
                

    def handle_ftp_session(self, client_socket, client_address, injection_manager):
        with client_socket:
            # Send FTP banner message
            client_socket.sendall(b"220 %s\r\n" % SERVER_BANNER)

            user = None
            password = None

            while True:
                data = client_socket.recv(BUFFSIZE).decode(ENCODING).strip()
                
                if not data:
                    break

                logger.info(f"Received from {client_address}: {data}")
                
                if data.upper().startswith('USER'):                    
                    user = data.split(' ')[1] if len(data.split(' ')) > 1 else "Unknown"

                    logger.info(f"{user}@{client_address} into the decoy")
                    
                    if user.lower() == 'anonymous':
                        
                        msg = b"230 Login Successful"
                        msg, to_kill = injection_manager(client_address, self.source_name, self.name, msg)
                        msg += b'\r\n'
                        client_socket.sendall(msg)

                        if to_kill:
                            logger.info("Self-kill")
                            client_socket.close()
                            break
                    else:
                        client_socket.sendall(b"331 Username OK, need password\r\n")
                        
                elif data.upper().startswith('PASS'):
                    password = data.split(' ')[1] if len(data.split(' ')) > 1 else "Unknown"
                    
                    if user.lower() == 'anonymous':
                        # No password needed for anonymous login
                        client_socket.sendall(b"230 Anonymous login successful\r\n")
                    else:
                        client_socket.sendall(b"530 Login incorrect\r\n")
                    
                    logger.info(f"Login attempt - USER: {user}, PASS: {password}")
                    
                    if user.lower() != 'anonymous':
                        break
                else:
                    client_socket.sendall(b"500 Unknown command\r\n")
            
            logger.info(f"Closing connection to {client_address}")