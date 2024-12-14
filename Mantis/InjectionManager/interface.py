from xmlrpc.server import SimpleXMLRPCServer

from . import ADDRESS_SERVER_RPC_INTERFACE, PORT_SERVER_RPC_INTERFACE

class InterfaceClientRPC:
	def __init__(self, injection_manager, address=ADDRESS_SERVER_RPC_INTERFACE, port=PORT_SERVER_RPC_INTERFACE):
		self.injection_manager = injection_manager
		self.tracker = self.injection_manager.tracker

		self.address = address
		self.port = port

		self.server = SimpleXMLRPCServer(
			(self.address, self.port)
		)

		# register funs
		self.server.register_function(
			self.get_interactions,
			"get_interactions"
		)
		

	def get_interactions(self):
		return [user.to_entry() for user in self.tracker.users.values()]


	def __call__(self):
		print(f"Running RPC server for interface on {self.address}:{self.port}")
		self.server.serve_forever()