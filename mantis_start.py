import argparse
import importlib

from Mantis.InjectionManager.default import DefaultInjectionManager
from Mantis.utils import get_local_ip, get_public_ip
from Mantis.InjectionManager.interface import InterfaceClientRPC

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Run Mantis on the host machine based on the configuration file provided')

    parser.add_argument('conf_file', type=str,
                        help='Path to the configuration file (e.g., confs.ftp_hackback_rshell)')

    parser.add_argument(
        '--run_rpc_interface',
        action='store_true',
        help="Run RPC server for external clients"
    )
    
    
    # Parse the arguments
    args = parser.parse_args()

    conf = importlib.import_module(args.conf_file)

    local_ip = get_local_ip()
    public_ip = get_public_ip()

    inj_manager = DefaultInjectionManager(
        conf.TRIGGER_EVENTS,
        local_ip,
        public_ip
    )
    
    inj_manager.spawn_decoys(conf.DECOYS)

    if args.run_rpc_interface:
        ic = InterfaceClientRPC(inj_manager)
        ic()