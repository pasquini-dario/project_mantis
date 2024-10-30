# Telnet protocol commands and options
IAC  = 255  # Interpret as Command
DONT = 254
DO   = 253
WONT = 252
WILL = 251

# Telnet options
OPT_ECHO              = 1
OPT_SUPPRESS_GO_AHEAD = 3


ENCODING = 'utf-8'

BANNER = b'Welcome to the Secure Shell Server\r\n'

RESPONSE_ON_CMD_MSG = b'command not found$ '