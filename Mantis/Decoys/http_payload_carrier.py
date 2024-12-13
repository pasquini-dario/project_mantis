import http.server
import socketserver

from . import DecoyService
from ..utils.logger import logger

class MaxRequestsExceededException(Exception):
    """Exception raised when the maximum number of requests is exceeded."""
    pass

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


class LimitedTCPServer(socketserver.TCPServer):
    def __init__(self, server_address, handler_class, max_requests):
        super().__init__(server_address, handler_class)
        self.max_requests = max_requests
        self.request_count = 0

    def get_request(self):
        if self.max_requests and self.request_count >= self.max_requests:
            logger.info("Maximum number of requests reached. Shutting down.")
            raise MaxRequestsExceededException("Max requests reached, shutting down the server.")
        else:
            self.request_count += 1
            return super().get_request()


class CarrierPayloadReverseShellHTTP(DecoyService):

    source_name = 'HTTP_carrier'

    """ A simple HTTP server that serves a single content. Used to carry the reverse shell payload for hack-back. """ 

    def serve(self, injection_manager):
        handler = lambda *args, **kwargs: CustomHandler(*args, response_content=self.hparams['response_content'], injection_manager=injection_manager, **kwargs)
        with LimitedTCPServer((self.host, self.port), handler, self.number_allowed_interactions) as httpd:
            logger.info(f"{self.source_name} listening on {self.host}:{self.port}")
            try:
                httpd.serve_forever()
            except MaxRequestsExceededException as e:
                httpd.shutdown()
                logger.info(str(e))
                return