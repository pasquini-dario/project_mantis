import sys
import time
import argparse
import importlib

from Mantis.InjectionManager.default import DefaultInjectionManager
from Mantis.utils import get_local_ip, get_public_ip
from Mantis.utils.logger import logger
from Mantis.InjectionManager.interface import InterfaceClientRPC
from Mantis.utils.Paper import forward_proxy


def main(args, with_forward=False):
	conf = importlib.import_module(args.conf_file)
	
	local_ip = get_local_ip()
	public_ip = get_public_ip()

	if with_forward:
		if not args.ports:
			print("No ports to forward provided.")
			sys.exit(1)
		forward_proxy.forward_multiple_ports(local_ip, args.destination_ip, args.ports)

	if hasattr(conf, 'IP_partial_block'):
		IP_partial_block = conf.IP_partial_block
	else:
		IP_partial_block = False

	inj_manager = DefaultInjectionManager(
		conf.TRIGGER_EVENTS,
		local_ip,
		public_ip,
		IP_partial_block=IP_partial_block,
	)
	
	inj_manager.spawn_decoys(conf.DECOYS)

	if args.run_rpc_interface:
		ic = InterfaceClientRPC(inj_manager)
		ic()

	try:
		print("Mantis is running. Press Ctrl-C to exit.")
		while True:
			time.sleep(1)
	except KeyboardInterrupt:
		logger.info("KeyboardInterrupt caught — cleaning up")
		inj_manager.cleanup()
	


if __name__ == '__main__':

	parser = argparse.ArgumentParser(description='Run Mantis on the host machine based on the configuration file provided')

	parser.add_argument('conf_file', type=str,
						help='Path to the configuration file (e.g., confs.ftp_hackback_rshell)')
	parser.add_argument(
		'--run_rpc_interface',
		action='store_true',
		help="Run RPC server for external clients"
	)
	
	args = parser.parse_args()
	main(args, with_forward=False)