import argparse
import sys

from mantis_start import main

if __name__ == '__main__':

	parser = argparse.ArgumentParser(description='Run Mantis on the host machine based on the configuration file provided and run a forward proxy on the given ports (to simulate the deployment of Mantis on a remote machine in tests).')

	parser.add_argument('conf_file', type=str,
						help='Path to the configuration file (e.g., confs.ftp_hackback_rshell)')

	parser.add_argument('destination_ip', type=str,
						help='Where to redirect the traffic.')

	parser.add_argument(
		'--ports',
		type=int,
		nargs='+',  # "+" means one or more arguments
		help='List of port numbers separated by spaces (e.g., --ports 8080 8081 8082)'
	)

	parser.add_argument(
		'--run_rpc_interface',
		action='store_true',
		help="Run RPC server for external clients"
	)
	
	# Parse the arguments
	args = parser.parse_args()
	main(args, with_forward=True)
