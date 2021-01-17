from .game import GV, Trigger

class CallbackHandler():
    def triggers(self):
        def flatten_splits(split):
            flat_splits = [split]
            for subsplit in split.subsplits:
                flat_splits += flatten_splits(subsplit)
            return flat_splits

        flat_splits = []
        for split in self.route.splits:
            flat_splits += flatten_splits(split)

        triggers = list({(split.trigger, split.variable, split.value) for split in flat_splits})
        return triggers

    def time_in_seconds(self):
        return self.state[GV.HOURS] * 60 * 60 + self.state[GV.MINUTES] * 60 + self.state[GV.SECONDS]

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

    def __init__(self, route):
        self.started = False
        self.route = route
        self.state = None
        self.old_state = None

    def update_time(self):
        pass

    def success(self, split):
        pass

    def checksplit(self, split):
        if split.trigger == Trigger.Value:
            return self.state[split.variable] == split.value
        #elif split.trigger == Trigger.Changed:
        return self.old_state[split.variable] != self.state[split.variable]

    def tick(self, values):
        self.state = values.copy()

        if self.old_state is None:
            self.old_state = self.state.copy()

        nextsplits = self.nextsplit()
        if nextsplits == []:
            return

        nextsplit = nextsplits[-1]
        self.update_time()
        if self.checksplit(nextsplit):
            self.started = True
            nextsplit.time = self.time_in_seconds()
            self.success(nextsplit)

        self.old_state = self.state.copy()

class ConsoleOut(CallbackHandler):
    def nextsplit_as_string(self):
        if self.nextsplit() == []:
            return ""
        return " - ".join([split.name for split in self.nextsplit()])

    def update_time(self):
        if self.started:
            print(f"\r{self.state[GV.HOURS]:02d}:{self.state[GV.MINUTES]:02d}:"\
                  f"{self.state[GV.SECONDS]:02d} - {self.nextsplit_as_string()}", end='')

    def success(self, split):
        print()
