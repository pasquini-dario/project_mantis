import random
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

from .. import DecoyService
from ...utils.logger import logger
from . import SERVER_BANNER, SQL_INJECTION_STRINGS, SQL_ERROR_STR
from ...InjectionManager.utils import make_text_invisible_terminal


def check_for_string(s, targets):
    for target in targets:
        if target in s:
            return True
    return False
    
class CustomHTTPRequestHandler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def send_custom_response(self, code=200, content=b""):
        """Helper to send HTTP response with custom headers and content"""

        content += b"\n"
        # Write the status line and headers

        self.wfile.write(f"HTTP/1.1 {code} OK\r\n".encode())
        self.wfile.write(f"Server: {self.server.banner}\r\n".encode())
        
        self.send_header("Content-Type", "text/html")
        self.send_header("Content-Length", str(len(content)))
        self.send_header("Connection", "close")
        self.end_headers()
        
        self.wfile.write(content)
        self.wfile.flush()  # Ensure content is sent

    def generate_index_page(self):
        """Generate the HTML content for the index (login form) page"""
        content = SQL_ERROR_STR + b"""
            
            <h2>Login</h2>
            <form action="/login" method="GET">
                Username: <input name="username"><br><br>
                Password: <input name="password" type="password"><br><br>
                <input type="submit" value="Login">
            </form>
        """
        
        return content

    def generate_login_response(self, username, password):
        """Generate the HTML response after form submission"""

        client_address = self.client_address

        if check_for_string(username, SQL_INJECTION_STRINGS) or check_for_string(password, SQL_INJECTION_STRINGS):
            response_content = f"""Welcome! Login successful. """.encode()
            response_content, _ = self.server.injection_manager(client_address, self.server.source_name, self.server.name, response_content)
        else:
            response_content = f"""Login Failed. Try again.""".encode()
        
        return response_content

    def do_HEAD(self):
        """Handle HEAD request by sending headers only"""
        self.send_custom_response()

    def do_POST(self):
        """Handle HEAD request by sending headers only"""
        self.send_custom_response()

    def do_OPTIONS(self):
        """Handle HEAD request by sending headers only"""
        self.send_custom_response()

    def do_GET(self):
        """Handle GET requests for different routes"""
        parsed_path = urlparse(self.path)

        client_ip, client_port = self.client_address
        logger.info(f"{client_ip} {client_port} connected to the decoy")
        
        if parsed_path.path == "/":
            # Serve the index page with login form
            content = self.generate_index_page()
            self.send_custom_response(content=content)
        
        elif parsed_path.path == "/login":
            # Parse query parameters
            
            query_params = parse_qs(parsed_path.query)
            username = query_params.get("username", [""])[0]
            password = query_params.get("password", [""])[0]

            logger.info(f"{client_ip} {client_port} login attempt: {username} {password}")
            
            # Serve the login response page
            content = self.generate_login_response(username, password)
            self.send_custom_response(content=content)
        
        else:
            # Serve a 404 page for any other path
            self.send_custom_response(code=404, content=b"<h1>404 Not Found</h1>")

class CustomHTTPServer(HTTPServer):
    
    def __init__(
        self,
        server_address,
        RequestHandlerClass,
        injection_manager,
        name,
        source_name,
        banner,
    ):
        super().__init__(server_address, RequestHandlerClass)
        self.injection_manager = injection_manager
        self.name = name
        self.source_name = source_name
        self.banner = banner


class WebFakeDB_sqlinj(DecoyService):

    source_name = "Decoy.WebAppSqlInj"
    
    def serve(self, injection_manager):
        logger.info(f"{self.name} listening on {self.host}:{self.port}")

        banner = SERVER_BANNER
        if 'BANNER_INJECTION_POOL' in self.hparams:
            payload = random.choice(self.hparams['BANNER_INJECTION_POOL'])
            payload = make_text_invisible_terminal(payload)
            banner += payload

        self.banner = banner
        
        
        httpd = CustomHTTPServer((self.host, self.port), CustomHTTPRequestHandler, injection_manager, self.name, self.source_name, banner)
        httpd.serve_forever()
