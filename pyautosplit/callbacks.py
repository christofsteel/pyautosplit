import datetime
import time
import socket
from copy import deepcopy
from flask import Flask
from flask_sockets import Sockets
from gevent import monkey
from gevent import pywsgi
from geventwebsocket.handler import WebSocketHandler
from threading import Thread

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

    def time_in_seconds(self):
        if self.timing is None or self.timing == "":
            return time.time() - self.real_time
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
        return simple_eval(
            event.trigger,
            names={
                "state": self.state,
                "oldstate": self.old_state})

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

    def update_time(self):
        if self.timing is not None and self.timing != "":
            self.socket.send(
                f"setgametime {self.time_in_seconds()}\r\n".encode())

    def split(self, split):
        self.socket.send(b"split\r\n")


class LiveSplitOne(CallbackHandler):
    def __init__(self, port=5000):
        super().__init__()

        monkey.patch_all()

        self.app = Flask(__name__)
        self.app.config['SECRET_KEY'] = 'secret!'
        self.sockets = Sockets(self.app)
        self.ws_list = []

        @self.sockets.route('/')
        def echo_socket(ws):
            self.ws_list.append(ws)
            while not ws.closed:
                message = ws.receive()
                ws.send(message)

        self.server = pywsgi.WSGIServer(
            ('', port), self.app, handler_class=WebSocketHandler)

        self.thread = Thread(target=self._start_server, daemon=True)
        print(f"Connect LiveSplitOne to ws://localhost:{port}")
        self.thread.start()

    def init(self, *args, **kwargs):
        super().init(*args, **kwargs)

    def reset(self):
        self._send_command("reset")

    def start(self):
        self._send_command("start")

    def split(self, split):
        self._send_command("split")

    def pause(self):
        self._send_command("togglepause")

    def resume(self):
        self._send_command("togglepause")

    def _send_command(self, name):
        for ws in self.ws_list:
            if not ws.closed:
                ws.send(name)
            else:
                self.ws_list.remove(ws)

    def _start_server(self):
        self.server.start()
