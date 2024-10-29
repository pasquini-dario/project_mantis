<p align="center">
 <img height="150" src="assets/logo.png"> 
</p>

# Project Mantis:  *Hacking Back the AI-Hacker*
## Prompt Injection as a Defense Against LLM-driven Cyberattacks

🔨 We are currently populating this repository. 🪚

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
Running Mantis with ```confs/ftp_hackback_rshell.py``` will spawn an FTP decoy server with anonymous credentials that aims to trick the attacking LLM-agent into opening a reverse shell via (invisible) prompt injections. When triggered, it spawns a reverse shell listener on the specified port for testing (this configuration is not intended for production).

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

## White paper
TODO
