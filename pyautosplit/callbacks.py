import datetime
import time
import socket
from copy import deepcopy

import pyautogui
from simpleeval import simple_eval


class CallbackHandler():
    """
    This is the base class for all callback handlers. The `tick` method of a callback will be called at specific invervalls and be given the current state of the observed memory locations. This method then checks, if any event - like starting a run, reaching a split, etc. - is triggerd and calls the appropriate method. These methods need to be implemented in a subclass of `CallbackHandler`.
    """

    def __init__(self):
        self.started = False
        self.route = None
        self.state = None
        self.old_state = None
        self.timing = None
        self.real_time = 0
        self.pause_time = 0
        self.pause_diff = 0
        self.is_pause = False

    def time_in_seconds(self):
        if self.timing is None or self.timing == "":
            if self.is_pause:
                return self.pause_time - self.real_time
            return (time.time() - self.pause_diff) - self.real_time
        try:
            return simple_eval(self.timing, names=self.state)
        except TypeError:
            return 0

    def findnextsplit(self, startsplit):
        if startsplit.time is None:
            for split in startsplit.subsplits:
                nextsplits = self.findnextsplit(split)
                if nextsplits != []:
                    return [startsplit] + nextsplits
            return [startsplit]
        return []

    def nextsplit(self):
        for split in self.route.splits:
            nextsplit = self.findnextsplit(split)
            if nextsplit != []:
                return nextsplit
        return []

    def init(self, route, timing):
        self.route = route
        self.timing = timing

    def update_time(self):
        pass

    def split(self, split):
        pass

    def checkevent(self, event):
        return event is not None and simple_eval(
            event.trigger,
            names={
                "state": self.state,
                "oldstate": self.old_state})

    def _pause(self):
        self.pause_time = time.time()
        self.is_pause = True
        self.pause()

    def pause(self):
        pass

    def _resume(self):
        self.pause_diff += time.time() - self.pause_time
        self.is_pause = False
        self.resume()

    def resume(self):
        pass

    def start(self):
        pass

    def resetsplit(self, split):
        self.started = False
        split.time = None
        for subsplit in split.subsplits:
            self.resetsplit(subsplit)

    def reset(self):
        pass

    def tick(self, values):
        self.state = deepcopy(values)

        if self.old_state is None:
            self.old_state = deepcopy(self.state)

        if not self.started:
            if self.checkevent(self.route.starttigger):
                self.started = True
                self.real_time = time.time()
                self.start()
        else:
            nextsplits = self.nextsplit()

            if nextsplits == []:
                for split in self.route.splits:
                    self.resetsplit(split)
            elif not self.is_pause and any([self.checkevent(pause) for pause in self.route.pausetriggers]):
                self._pause()
            elif self.is_pause and any([self.checkevent(resume) for resume in self.route.resumetriggers]):
                self._resume()
            elif self.checkevent(self.route.resettrigger):
                for split in self.route.splits:
                    self.resetsplit(split)
                self.reset()
            else:
                nextsplit = nextsplits[-1]
                self.update_time()
                if self.checkevent(nextsplit):
                    nextsplit.time = self.time_in_seconds()
                    self.split(nextsplit)

        self.old_state = self.state.copy()


class ConsoleOut(CallbackHandler):
    def nextsplit_as_string(self):
        if self.nextsplit() == []:
            return ""
        return " - ".join([split.name for split in self.nextsplit()])

    def update_time(self):
        print(
            f"\r{datetime.timedelta(seconds=self.time_in_seconds())} - {self.nextsplit_as_string()}, {self.state}",
            end='')

    def split(self, split):
        print()

    def pause(self):
        super().pause()
        print("PAUSE")

    def resume(self):
        super().resume()
        print("RESUME")

    def reset(self):
        print("RESET")

    def start(self):
        print("LET'S GO")


class LiveSplitServer(CallbackHandler):

    def __init__(self, host="localhost", port=16834):
        super().__init__()
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))

    def init(self, *args, **kwargs):
        super().init(*args, **kwargs)
        if self.timing is not None and self.timing != "":
            self.socket.send(b"initgametime\r\n")

    def reset(self):
        self.socket.send(b"reset\r\n")

    def start(self):
        super().start()
        self.socket.send(b"starttimer\r\n")

    def pause(self):
        self.socket.send(b"pause\r\n")

    def resume(self):
        self.socket.send(b"resume\r\n")

    def update_time(self):
        self.socket.send(
                f"setgametime {self.time_in_seconds()}\r\n".encode())

    def split(self, split):
        self.socket.send(b"split\r\n")

class KeyBoardPress(CallbackHandler):
    def reset(self):
        pyautogui.press("backspace")

    def start(self):
        pyautogui.press("space")

    def split(self, split):
        pyautogui.press("space")

    def pause(self):
        print("unfortunately urn does not have a pause function")

    def resume(self):
        print("unfortunately urn does not have a resume function")
