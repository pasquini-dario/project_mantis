import http.server
import socketserver

from . import DecoyService
from ..utils.logger import logger

class CustomHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        self.response_content = kwargs.pop('response_content') 
        self.injection_manager = kwargs.pop('injection_manager')
        super().__init__(*args, **kwargs)

    def do_GET(self):
        client_ip, client_port = self.client_address

        response_content = self.injection_manager.set_target_ip(client_ip, self.response_content)
        
        # Respond to all GET requests with the same content
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(response_content.encode())

class CarrierPayloadReverseShellHTTP(DecoyService):

    source_name = 'HTTP_carrier'

    """ A simple HTTP server that serves a single content. Used to carry the reverse shell payload for hack-back. """ 

    def __call__(self, injection_manager):
        handler = lambda *args, **kwargs: CustomHandler(*args, response_content=self.hparams['response_content'], injection_manager=injection_manager, **kwargs)
        with socketserver.TCPServer((self.host, self.port), handler) as httpd:
            logger.info(f"{self.source_name} listening on {self.host}:{self.port}")
            httpd.serve_forever()