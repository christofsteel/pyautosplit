import os
import subprocess
import sys
from signal import SIGTRAP

import ptrace.debugger
from ptrace.debugger.process_error import ProcessError


class GameProcess:
    def __init__(self, command, cwd, env=os.environ.copy(), exe=None):
        self.process = subprocess.Popen(command,
                                        stdout=subprocess.DEVNULL,
                                        cwd=cwd,
                                        env=env)

        self.debugger = ptrace.debugger.PtraceDebugger()

        if exe is None:
            self.dprocess = self.debugger.addProcess(self.process.pid, False)
        else:
            # If an executable is set we're listening for that specific pid
            # instead of our own child. This is useful for programs that
            # spawn own subchilds we can't track normally. This needs
            # elevated user rights which will be provided by a wrapper binary.
            pids = 0
            while pids == 0:
                # Wine is heavy, wait for our process to show up
                try:
                    pids = subprocess.check_output(
                        ["pgrep", "--count", "--exact", exe], text=True)
                except subprocess.CalledProcessError:
                    # pgrep throws 1 if count is 0
                    pass
            pids = subprocess.check_output(
                ["pgrep", "--exact", exe], text=True).split()
            self.dprocess = self.debugger.addProcess(int(pids[0]), False)
        self.breakpoints = {}

    def insert_breakpoint(self, addr):
        self.breakpoints[addr] = self.dprocess.createBreakpoint(addr)

    def check_breakpoint_hit(self):
        event = self.debugger._wait_event_pid(self.dprocess.pid, False)
        return event is not None and event.signum == SIGTRAP

    def delete_breakpoint(self, addr):
        self.breakpoints[addr].desinstall(True)

    def get_instruction_pointer(self):
        return self.dprocess.getInstrPointer()

    def get_stack_pointer(self):
        return self.dprocess.getStackPointer()

    def get_base_pointer(self):
        return self.dprocess.getFramePointer()

    def cont(self):
        self.dprocess.cont()

    def read_mem(self, addr, length=4, signed=False, byteorder=sys.byteorder):
        try:
            return int.from_bytes(self.dprocess.readBytes(addr, length),
                                  byteorder=byteorder, signed=signed)
        except ProcessError:
            return None

    def read_bool(self, addr):
        try:
            return self.dprocess.readBytes(addr, 1) == b'\01'
        except ProcessError:
            return None
