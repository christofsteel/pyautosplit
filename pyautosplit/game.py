import os
import time
import shlex
import sys
import traceback
from pathlib import Path
from dataclasses import dataclass, field
from typing import Any, List
from copy import deepcopy

from simpleeval import simple_eval

from .process import GameProcess
from ptrace.error import PtraceError


class State(dict):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__dict__ = self


@dataclass
class Split():
    name: str
    trigger: str
    time: int = None
    subsplits: List[Any] = field(default_factory=list)


class Route:
    def entry_to_split(self, splits_dict):
        splits = []
        for key, attr in splits_dict.items():
            split = deepcopy(self.events[key])
            split.subsplits = self.entry_to_split(attr)
            splits.append(split)
        return splits

    def __init__(self, rundata, events):
        self.events = events
        self.splits = self.entry_to_split(rundata["route"])
        self.resettrigger = self.events[rundata["reset"]]
        self.starttigger = self.events[rundata["start"]]
        self.name = rundata["name"]
        self.gamefile = rundata["gamefile"]


class Game:
    def __init__(self, gamedata, rundata, callback_handlers,
                 from_wrapper=False):
        self.data = gamedata

        if 'overwrites' in rundata:
            for k, v in rundata['overwrites'].items():
                self.data[k] = v

        events = {name: Split(**s) for name, s in self.data["events"].items()}
        route = Route(rundata, events)
        self.callback_handlers = callback_handlers

        for cbh in self.callback_handlers:
            cbh.init(deepcopy(route), (self.data.get("time")))

        if "cwd" in self.data:
            cwd = Path(self.data["cwd"]).expanduser()
        else:
            cwd = None

        env = os.environ.copy()
        if "env" in self.data:
            env = env | self.data["env"]

        exe = None
        if from_wrapper is True and "exe" in self.data:
            exe = self.data["exe"]

        command = shlex.split(self.data["command"])
        command[0] = Path(command[0]).expanduser()
        self.process = GameProcess(command, cwd, env=env, exe=exe)

        self.breakpoints = {}

        for name, var in self.data["variables"].items():
            if var["type"] != "rsp" and var["type"] != "rbp":
                continue
            addr = int(var["address"], 16)
            self.process.insert_breakpoint(addr)
            self.breakpoints[addr] = name

        self.state = State(
            {varname: None for varname in self.data["variables"].keys()})

    def handle_breakpoints(self):
        if self.process.check_breakpoint_hit():
            rip = self.process.get_instruction_pointer() - 1

            varname = self.breakpoints[rip]
            self.process.delete_breakpoint(rip)

            var = self.data["variables"][varname]
            if var["type"] == "rsp":
                self.state[varname] = self.process.get_stack_pointer() + \
                    int(var["offset"], 16)
            elif var["type"] == "rbp":
                self.state[varname] = self.process.get_base_pointer() + \
                    int(var["offset"], 16)
        try:
            self.process.cont()
        except BaseException:
            pass

    def update_data(self):
        def eval_address(address_string):
            try:
                return simple_eval(address_string, names=self.state)
            except TypeError:
                return None

        for name, var in self.data["variables"].items():
            if var["type"] == "rsp" or var["type"] == "rbp":
                continue
            var["_address"] = eval_address(var["address"])
            var_obj = Variable(name=name, **var)
            try:
                if var_obj.type == "bool":
                    self.state[name] = self.process.read_bool(var_obj._address)
                elif var_obj.type == "memory":
                    self.state[name] = self.process.read_mem(
                        addr=var_obj._address,
                        length=int(var_obj.length),
                        signed=var_obj.signed,
                        byteorder=var_obj.byteorder)
            except TypeError:
                pass

    def fill_mappings(self):
        mappings = self.process.dprocess.readMappings()
        self.state["process_start"] = mappings[0].start
        self.state["stack_start"] = self.process.dprocess.findStack().start
        self.state["stack_end"] = self.process.dprocess.findStack().end

    def hook(self):
        self.process.cont()

        self.fill_mappings()

        try:
            while True:
                self.handle_breakpoints()
                self.update_data()
                for cbh in self.callback_handlers:
                    cbh.tick(self.state)
                time.sleep(1 / int(self.data["frequency"]))
        except PtraceError as p:
            if p.errno != 3:
                traceback.print_exc()


@dataclass
class Variable:
    name: str
    address: str
    _address: int
    type: str = "memory"
    length: int = 4
    signed: bool = False
    byteorder: str = sys.byteorder
    comment: str = ""
