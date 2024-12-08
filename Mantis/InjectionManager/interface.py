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
			self.get_events_history,
			"get_events_history"
		)
		self.server.register_function(
			self.get_alive,
			"get_alive"
		)
		self.server.register_function(
			self.get_trigger_events_history,
			"get_trigger_events_history"
		)

	def get_events_history(self):
		return self.tracker.trigger_events_history

	def get_alive(self):
		return [user.to_entry() for user in self.tracker.alive.values()]

	def get_trigger_events_history(self):
		return [te.to_entry() for te in self.tracker.trigger_events_history]

	def __call__(self):
		print(f"Running RPC server for interface on {self.address}:{self.port}")
		self.server.serve_forever()