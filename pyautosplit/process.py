import subprocess
import sys
from signal import SIGTRAP
from typing import Dict, Optional

import ptrace.debugger
from ptrace.debugger.process_error import ProcessError


class GameProcess:
    def __init__(self, command, cwd, env: Optional[Dict[str, str]] = None):
        self.process = subprocess.Popen(command,
                                        stdout=subprocess.DEVNULL,
                                        cwd=cwd,
                                        env=env)

        self.debugger = ptrace.debugger.PtraceDebugger()
        self.dprocess = self.debugger.addProcess(self.process.pid, False)
        self.breakpoints = {}

    def insert_breakpoint(self, addr):
        self.breakpoints[addr] = self.dprocess.createBreakpoint(addr)

    def check_breakpoint_hit(self):
        event = self.debugger._wait_event_pid(self.process.pid, False)
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
