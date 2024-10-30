import socket
import sys

from . import *
from .. import DecoyService
from ...utils.logger import logger

def perform_negotiation(conn):
    # Negotiate Telnet options to make the honeypot appear more legitimate
    conn.sendall(bytes([IAC, WILL, OPT_ECHO]))
    conn.sendall(bytes([IAC, WILL, OPT_SUPPRESS_GO_AHEAD]))
    conn.sendall(bytes([IAC, DO, OPT_SUPPRESS_GO_AHEAD]))

def read_line(conn, echo=False):
    line = b''
    while True:
        data = recv_telnet(conn)
        if not data:
            break
        if data == b'\n':
            break
        elif data == b'\r':
            continue
        else:
            line += data
            if echo:
                conn.sendall(data)
    return line.decode(ENCODING, errors='ignore').strip()

def recv_telnet(conn):
    data = conn.recv(1)
    if not data:
        return data
    if data[0] == IAC:
        # Handle Telnet command sequences
        command = conn.recv(1)
        if not command:
            return b''
        if command[0] in (DO, DONT, WILL, WONT):
            option = conn.recv(1)
            respond_to_negotiation(conn, command[0], option[0])
            return b''
        else:
            # Other Telnet commands can be ignored for simplicity
            return b''
    else:
        return data

def respond_to_negotiation(conn, command, option):
    # Simplistically respond to Telnet negotiations by refusing all options
    if command in (DO, DONT, WILL, WONT):
        conn.sendall(bytes([IAC, WONT, option]))

class AnyPasswordFakeTelnet(DecoyService):

    source_name = 'Decoy.Telent'

    def __call__(self, injection_manager):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
            server_socket.bind((self.host, self.port))
            server_socket.listen()
            
            logger.info(f"{self.source_name} listening on {self.host}:{self.port}")
            
            while True:
                client_conn, client_addr = server_socket.accept()
                logger.info(f"Connection from {client_addr}")    
                self.handle_client(client_conn, client_addr, injection_manager)
             
    def handle_client(self, conn, addr, injection_manager):
        with conn:
            username = ''
            password = ''
            try:
                perform_negotiation(conn)
                # Send welcome header
                conn.sendall(BANNER)
                # Handle login prompt
                conn.sendall(b'login: ')
                while not username:
                    username = read_line(conn)
    
                conn.sendall(b'Password: ')
                password = read_line(conn, echo=False)
                # Log the credentials
                logger.info(f'Login attempt from {addr}: username="{username}", password="{password}"')

                # injection on login
                msg = b'\r230 Login successful.'
                msg, to_kill = injection_manager(addr, self.source_name, self.name, msg)
                msg += b'\r\n'
                conn.sendall(msg)

                msg = b'$ '
                conn.sendall(msg)

                if to_kill:
                    logger.info("Self-kill")
                    conn.close()
                    sys.exit(0)
                
                while True:
                    command = read_line(conn)
                    if not command:
                        break
                    logger.info(f'Command from {addr}: {command}')

                    
                    # injection on cmd submit
                    msg = RESPONSE_ON_CMD_MSG
                    msg, _ = injection_manager(addr, self.source_name, self.name+'.submit_cmd', msg)
                    msg += b'\r\n'
                    conn.sendall(msg)
                    
            except Exception as e:
                logger.error(f'Error handling client {addr}: {e}')