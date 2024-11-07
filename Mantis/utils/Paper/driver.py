import pexpect
import os
import tempfile
import os

from . import CONFS, FLAGS, PWNED_FLAG, AttackerGotPwned, AttackerSolvedCTF
from .. import find_string_in_directory

# to prevent hints/autocompletion in interactive sessions which can break the driver interaction
os.environ['TERM'] = 'dumb'

class Executer:

    def __init__(self, confs=CONFS):
        self.current_process = None
        self.current_root = None
        
        self.confs = confs
        self.cwd = tempfile.TemporaryDirectory()

    def is_tag_present(self, tag, out):
        """ Check if a tag is either in the output of a command or in the attacker's filesystem. """ 
        if tag and (tag in out or find_string_in_directory(self.cwd.name, tag)):
            return True
        else:
            return False

    def checks_for_tags(self, out):
        """ Checks if either the attacker has been pwned by a reverse shell or solved the CTF """
        if self.is_tag_present(PWNED_FLAG, out):
            raise AttackerGotPwned

        for tag in FLAGS.values():
            if self.is_tag_present(tag, out):
                raise AttackerSolvedCTF

    def check_current_process(self):
        if self.current_process is not None and self.current_process.isalive():
            return self.current_process 
        else:
            return None

    def pick_timeout(self, root):
        root_cmd = root.split(' ')[0]
        timeout = self.confs['timeout_per_tool'].get(root_cmd, self.confs['interaction_time_out_multi_step'])
        return timeout

    def _execute_root_cmd(self, cmd):
        timeout = self.pick_timeout(cmd)
        process = pexpect.spawn(cmd, timeout=timeout, cwd=self.cwd.name)
        return process

    def _read_process_output(self, process):
        is_dead = False
        try:
            if process:
                output = process.expect(pexpect.TIMEOUT)
            else:
                is_dead = True
        except pexpect.EOF:
            print("---->Process has Exited")
            is_dead = True
        
        output = process.before.decode('utf-8')
        process = None if is_dead else process  
        
        return output, process

    def reset(self):
        print("Reset")
        self.current_root = None
        if self.current_process:
            self.current_process.close()
        self.current_process = None     
        
        
    def __call__(self, cmd):

        process = self.check_current_process()

        try:
            if process is None:
                print(f"--->Running {cmd} on fresh bash")
                    
                process = self._execute_root_cmd(cmd)
                self.current_root = cmd
            else:
                # cmd must be an input for a previous command or special tag
                ## send input on stdin and wait for an answer 

                # wait for previous stuff to go in
                _output, _ = self._read_process_output(process)
                
                print(f"--->```{cmd}``` as input to {self.current_root}")
                process.send(cmd+'\n')
                    
        except pexpect.exceptions.ExceptionPexpect:
            process = None
            root = cmd.split(' ')[0]
            _output = f'[Command ```{root}``` not installed. Try something else.]'
        else:
            _output, process = self._read_process_output(process)
        
        if process is None or not process.isalive():
            self.current_root = None
            process = None        
    
        output = _output

        self.checks_for_tags(output)

        if output is None:
            output = '[No output returned]'
             
        self.current_process = process

        if self.current_root:
            output += f"\n\n[Remember, you are still in an interactive session opened with the command ```{self.current_root}```]"

        return output