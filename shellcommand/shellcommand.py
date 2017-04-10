# shellcommand.py - 
# Create and manage shell processes 
# m.a.w. - 7/26/2011

import os, shlex, subprocess, sys

KILL = "/usr/bin/kill -s SIGUSR1"

# Conveience function to kill all seagull processes.  

def KillAllSeagulls(verbose=0):

    commandString = """ ps -eaf | grep seagull | grep -v "LOAD" | awk '{print $2}' """
    cmd = ShellCommand(commandString)
    cmd.wait()

    # Get what the command execution wrote on Stdout and Stderr
    out = []
    out.append(cmd.getStdout())
    out.append(cmd.getStderr())
    commandOutputList = out[0].rstrip().split('\n')

    for item in commandOutputList:
        kill = ShellCommand(KILL + " " + item)
        kill.wait()
        if (verbose):
            print (kill.getStdout()).rstrip("\n")

class ShellException(Exception):
    pass

############################################################################
# ShellCommand - Process creation, output/input control, and manaagement   #
#                                                                          #
############################################################################

class ShellCommand:
    
    def __init__(self,commandstr,INTERACT=1):

        #args = shlex.split(commandstr);
        self.m_origcmd = commandstr
        args = commandstr
        # Attempt to run the command, and raise an exception when necessary.
        # If successful, store pid and filehandles for output

        try:
            if (INTERACT):
                self.m_prochandle = subprocess.Popen(args, -1, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
            else:
                self.m_prochandle = subprocess.Popen(args, -1, shell=True)

        except OSError, ValueError:
            raise ShellException

        self.m_pid = self.m_prochandle.pid
        print("Process id of Segagull ",self.m_pid)
        self.m_stdoutFP = self.m_prochandle.stdout
        self.m_stderrFP = self.m_prochandle.stderr
        self.m_output = []

        # if the process is still running, this value is undefined.
        # If it has already exited at this point, then it is valid.
        # To be safe, we should use poll() first, and then return the result.

        self.m_exitstatus = self.m_prochandle.returncode

    def getPid(self):
        return self.m_pid

    def kill(self):
        self.m_prochandle.terminate()

    def killHard(self):
        self.m_prochandle.kill()

    def wait(self):
        self.m_prochandle.wait()
        self.m_exitstatus = self.m_prochandle.returncode
        return(self.m_exitstatus)

    def getStdout(self):
        if (not self.m_output):
            self.m_output = self.m_prochandle.communicate()        
        return (self.m_output[0])

    def getStderr(self):
        if (not self.m_output):
            self.m_output = self.m_prochandle.communicate()        
        return (self.m_output[1])

    def send(self,indata):
        self.m_prochandle.communicate(indata)
    
    def getExitStatus(self):
        self.m_prochandle.poll()
        self.m_exitstatus = self.m_prochandle.returncode
        return(self.m_exitstatus)
        
    def getCmdline(self):
        return(self.m_origcmd)
