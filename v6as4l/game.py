import subprocess
import signal
import time
import os.path
from enum import Enum

import ptrace.debugger

class Trigger(Enum):
    Value = 1
    Changed = 2

class GV(Enum):
    FRAMES = 1
    SECONDS = 2
    MINUTES = 3
    HOURS = 4
    TRINKETS = 5
    STATE = 6

class Game():
    GAME_OBJECT_CREATION = 0x416da8
    GAME_OBJECT_STACK_OFFSET = 0xe20
    OFFSETS = { GV.FRAMES: 0xa8,
                GV.SECONDS: 0xac,
                GV.MINUTES: 0xb0,
                GV.HOURS: 0xb4,
                GV.TRINKETS: 0x3d0,
                GV.STATE: 0x60 }

    def __init__(self, executable):
        self.process = subprocess.Popen(
            [executable],
            stdout=subprocess.DEVNULL,
            cwd=os.path.join(os.path.dirname(executable), "..")
        )
        self.debugger = ptrace.debugger.PtraceDebugger()
        self.dprocess = self.debugger.addProcess(self.process.pid, False)
        self.game_object_creation_breakpoint = self.dprocess.createBreakpoint(
            self.GAME_OBJECT_CREATION
        )
        self.pointers = {}

    def get_pointers(self):
        self.game_object_creation_breakpoint.desinstall(True)
        stack_pointer = self.dprocess.getStackPointer()
        game_object_pointer = stack_pointer + self.GAME_OBJECT_STACK_OFFSET
        self.pointers = {k: game_object_pointer + v for k, v in self.OFFSETS.items()}
        self.dprocess.cont()

    def hook(self, callback_handler):
        self.dprocess.cont()
        self.dprocess.waitSignals(signal.SIGTRAP)
        self.get_pointers()

        while self.process.poll() is None:
            values = { k: int.from_bytes(self.dprocess.readBytes(pointer, 4), 'little')
                            for k, pointer in self.pointers.items() }
            callback_handler.tick(values)
            time.sleep(0.34)
