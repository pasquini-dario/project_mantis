import argparse
import importlib
import sys

from Mantis.InjectionManager.default import DefaultInjectionManager
from Mantis.utils import get_local_ip, get_public_ip
from Mantis.utils.Paper import forward_proxy


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
    
    # Parse the arguments
    args = parser.parse_args()
    ports = args.ports

    if not ports:
        print("No ports to forward provided.")
        sys.exit(1)

    conf = importlib.import_module(args.conf_file)

    local_ip = get_local_ip()
    public_ip = get_public_ip()

    inj_manager = DefaultInjectionManager(
        conf.TRIGGER_EVENTS,
        local_ip,
        public_ip
    )

    forward_proxy.forward_multiple_ports(local_ip, args.destination_ip, ports)
    inj_manager.spawn_decoys(conf.DECOYS)

