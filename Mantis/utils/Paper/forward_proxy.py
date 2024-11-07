import socket
import select
import time
import multiprocessing

from . import BUFFER_SIZE, DELAY

class Forward:
    def __init__(self):
        self.forward = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def start(self, host, port):
        try:
            self.forward.connect((host, port))
            return self.forward
        except Exception as e:
            print(e)
            return False

class ForwardProxy:
    """ Forward proxy used to simulate the deployment of Mantis on a remote machine. Used to test HackTheBox CTFs in the paper. """
    
    input_list = []
    channel = {}

    def __init__(
        self,
        host,
        destination_ip,
        port,
    ):
        """
            host: ip address where to listen with the proxy
            destination_ip: ip address where to send proxied messages
            port: which port to listen on
            resped: messages manipulator actor
            logger: logger class
        """
        self.s = None

        self.host = host
        self.port = port
        self.destination_ip = destination_ip

        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind((host, port))
        self.server.listen(200)


    def __call__(self):
        self.input_list.append(self.server)
        while True:
            time.sleep(DELAY)
            ss = select.select
            inputready, outputready, exceptready = ss(self.input_list, [], [])
            for self.s in inputready:
                if self.s == self.server:
                    self.on_accept()
                    break

                self.data = self.s.recv(BUFFER_SIZE)

                if len(self.data) == 0:
                    self.on_close()
                    break
                else:
                    self.on_recv()

    def on_accept(self):
        forward = Forward().start(self.destination_ip, self.port)
        clientsock, clientaddr = self.server.accept()
        if forward:
            self.input_list.append(clientsock)
            self.input_list.append(forward)
            self.channel[clientsock] = forward
            self.channel[forward] = clientsock
        else:
            print("Can't establish connection with remote server.", end=' ')
            print("Closing connection with client side", clientaddr)
            clientsock.close()

    def on_close(self):
        print(self.port, self.s.getpeername(), "has disconnected")
        # remove objects from input_list
        self.input_list.remove(self.s)
        self.input_list.remove(self.channel[self.s])
        out = self.channel[self.s]
        # close the connection with client
        self.channel[out].close()  # equivalent to do self.s.close()
        # close the connection with remote server
        self.channel[self.s].close()
        # delete both objects from channel dict
        del self.channel[out]
        del self.channel[self.s]

    def on_recv(self):
        data = self.data
        address, port = self.channel[self.s].getsockname()

        self.channel[self.s].send(data)

def forward_multiple_ports(host, destination_ip, ports):
    servers = {}
    for port in ports:
        print(f"Server listening on {host}-->{destination_ip} on {port}")
        server = ForwardProxy(
            host,
            destination_ip,
            port,
        )
        s = multiprocessing.Process(target=server)
        s.start()
        servers[port] = s
    
    return servers

