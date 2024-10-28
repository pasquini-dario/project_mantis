import socket
import random, time

from . import *
from .. import DecoyService
from ...utils.logger import logger
from ...utils import uniform_random_natural, generate_random_date

from .fake_ftp import AnonymousFTP

class TarpitFTP(AnonymousFTP):

    """ FTP tarpit """

    source_name = 'Decoy.tarpit.FTP'

    def handle_ftp_session(self, client_socket, client_address, injection_manager):
        with client_socket:
            # Send FTP banner message
            client_socket.sendall(b"220 %s\r\n" % SERVER_BANNER)

            user = None
            authenticated = False
            current_path = '/'
            client_data_connection_info = None  # To store IP and port from the PORT command

            while True:
                # Receive data from the client
                data = client_socket.recv(BUFFSIZE).decode(ENCODING).strip()
                
                if not data:
                    break

                logger.info(f"Received from {client_address}: {data}")
                
                # Handle commands
                if data.upper().startswith('USER'):
                    self.handle_user(client_socket, client_address, data, injection_manager)
                    user = data.split(' ')[1] if len(data.split(' ')) > 1 else "Unknown"
                    authenticated = user.lower() == 'anonymous'
                
                elif data.upper().startswith('PASS'):
                    authenticated = self.handle_pass(client_socket, client_address, user, data)
                
                elif data.upper() == 'PWD':
                    if authenticated:
                        self.handle_pwd(client_socket, current_path)
                    else:
                        client_socket.sendall(b"530 Not logged in\r\n")
                
                elif data.upper().startswith('LIST'):
                    if authenticated:
                        if client_data_connection_info:
                            self.handle_list(client_socket, current_path, client_data_connection_info, injection_manager)
                        else:
                            client_socket.sendall(b"425 Use PORT or PASV first.\r\n")
                    else:
                        client_socket.sendall(b"530 Not logged in\r\n")
                        
                elif data.upper().startswith('RETR'):
                    msg = b"550 File not found\r\n"
                    client_socket.sendall(msg)

                elif data.upper().startswith('CWD'):
                    if authenticated:
                        current_path = self.handle_cwd(client_socket, current_path, data)
                    else:
                        client_socket.sendall(b"530 Not logged in\r\n")
                
                elif data.upper().startswith('PORT'):
                    if authenticated:
                        client_data_connection_info = self.handle_port(client_socket, data)
                    else:
                        client_socket.sendall(b"530 Not logged in\r\n")

                elif data.upper() == 'QUIT':
                    self.handle_quit(client_socket)
                    break
                
                else:
                    client_socket.sendall(b"500 Unknown command\r\n")
            
            # Close connection after handling the session
            logger.info(f"Closing connection to {client_address}")


    def handle_user(self, client_socket, client_address, data, injection_manager):
        """Handle the USER command."""

        user = data.split(' ')[1] if len(data.split(' ')) > 1 else "Unknown"
        if user.lower() == 'anonymous':
            logger.critical(f"{user}@{client_address} into the tarpit")
            
            msg = b"230 Login Successful"
            msg, _ = injection_manager(client_address, self.source_name, self.name, msg)
            msg += b'\r\n'
            client_socket.sendall(msg)
        else:
            client_socket.sendall(b"331 Username OK, need password\r\n")

    def handle_pass(self, client_socket, client_address, user, data):
        """Handle the PASS command."""
        password = data.split(' ')[1] if len(data.split(' ')) > 1 else "Unknown"
        if user.lower() == 'anonymous':
            client_socket.sendall(b"230 Anonymous login successful\r\n")
            return True
        else:
            client_socket.sendall(b"530 Login incorrect\r\n")
            logger.info(f"Login attempt - USER: {user}, PASS: {password}")
            return False

    def handle_pwd(self, client_socket, current_path):
        """Handle the PWD command to display the current directory."""
        client_socket.sendall(f'257 "{current_path}" is the current directory\r\n'.encode(ENCODING))

    def make_fake_dir_names(self, seed):
        random.seed(seed)
        
        num_dirs = uniform_random_natural(self.hparams['EXPECTED_NUMBER_OF_DIRECTORIES'])
        dirs = random.choices(TARPIT_DIR_NAMES, k=num_dirs)
        return dirs

        
    def handle_list(self, client_socket, current_path, client_data_connection_info, injection_manager):
        """Handle the LIST command to list directory contents."""
        # Simulate infinite directory tree

        seed = hash(current_path)
        fake_dirs = self.make_fake_dir_names(seed)
        dir_listing = ''.join([f"drwxr-xr-x 1 root group 4096 {generate_random_date(seed + hash(d))} {d}\r\n" for d in fake_dirs])

        # Create a new data connection to the client using the PORT details
        client_ip, client_port = client_data_connection_info
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as data_socket:
            try:
                data_socket.connect((client_ip, client_port))
                client_socket.sendall(b"150 Here comes the directory listing\r\n")
                time.sleep(1)  # Simulate a small delay
                data_socket.sendall(dir_listing.encode(ENCODING))
                data_socket.close()
                
                msg = b"226 Directory send OK\r\n"
                msg, _ = injection_manager(client_ip, self.source_name, self.name, msg)
                msg += b'\r\n'
                client_socket.sendall(msg)
                
            except socket.error as e:
                client_socket.sendall(b"425 Can't open data connection.\r\n")
                logger.info(f"Error connecting to client for data transfer: {e}")

    def handle_cwd(self, client_socket, current_path, data):
        """Handle the CWD command to change directories."""
        new_dir = data.split(' ')[1] if len(data.split(' ')) > 1 else '/'
        if new_dir == '/':
            new_path = '/'
        else:
            new_path = current_path.rstrip('/') + '/' + new_dir
        
        client_socket.sendall(b"250 Directory successfully changed\r\n")
        return new_path

    def handle_port(self, client_socket, data):
        """Handle the PORT command and extract IP and port for data connection."""
        try:
            port_data = data.split(' ')[1].split(',')
            ip_address = '.'.join(port_data[:4])
            port_number = (int(port_data[4]) * 256) + int(port_data[5])
            client_socket.sendall(b"200 PORT command successful.\r\n")
            logger.info(f"Client data connection IP: {ip_address}, Port: {port_number}")
            return (ip_address, port_number)
        except Exception as e:
            client_socket.sendall(b"501 Syntax error in PORT command.\r\n")
            logger.info(f"Error handling PORT command: {e}")
            return None

    def handle_quit(self, client_socket):
        """Handle the QUIT command to close the session."""
        client_socket.sendall(b"221 Goodbye\r\n")