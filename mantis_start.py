import argparse
import importlib

from Mantis.InjectionManager.default import DefaultInjectionManager


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Run Mantis on the host machine based on the configuration file provided')

    parser.add_argument('host', type=str,
                        help='local/global IP address of the host')

    parser.add_argument('conf_file', type=str,
                        help='Path to the configuration file (e.g., confs.ftp_hackback_rshell)')
    
    
    # Parse the arguments
    args = parser.parse_args()

    conf = importlib.import_module(args.conf_file)

    
    inj_manager = DefaultInjectionManager(
        conf.TRIGGER_EVENTS,
        args.host,
    )
    
    inj_manager.spawn_decoys(conf.DECOYS)

