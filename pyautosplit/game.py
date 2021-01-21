import time
import shlex
from pathlib import Path
from dataclasses import dataclass, field
from typing import Any

from simpleeval import simple_eval

from .process import GameProcess


class State(dict):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__dict__ = self


@dataclass
class Split():
    name: str
    trigger: str
    time: int = None
    subsplits: list[Any] = field(default_factory=list)


class Route:
    def entry_to_split(self, splits_dict):
        splits = []
        for key, attr in splits_dict.items():
            split = self.events[key]
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
    def __init__(self, gamedata, rundata, callback_handlers):
        self.data = gamedata

        events = {name: Split(**s) for name, s in self.data["events"].items()}
        route = Route(rundata, events)
        self.callback_handlers = callback_handlers

        for cbh in self.callback_handlers:
            cbh.init(route, (self.data.get("time")))

        if "cwd" in self.data:
            cwd = Path(self.data["cwd"]).expanduser()
        else:
            cwd = None

        command = shlex.split(self.data["command"])
        command[0] = Path(command[0]).expanduser()
        self.process = GameProcess(command, cwd)

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
        def get_address(varname):
            try:
                return simple_eval(
                    self.data["variables"][varname]["address"],
                    names=self.state)
            except TypeError:
                return None

        for name, var in self.data["variables"].items():
            if var["type"] == "rsp":
                continue
            addr = get_address(name)
            try:
                self.state[name] = self.process.read_int(addr)
            except TypeError:
                pass

    def hook(self):
        self.process.cont()
        try:
            while True:
                self.handle_breakpoints()
                self.update_data()
                for cbh in self.callback_handlers:
                    cbh.tick(self.state)
                time.sleep(1 / int(self.data["frequency"]))
        except BaseException:
            pass
