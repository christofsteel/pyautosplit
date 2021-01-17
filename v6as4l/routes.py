from .splits import splits

class Route:
    def entry_to_split(self, entry):
        if isinstance(entry, tuple):
            split = splits[entry[0]]
            children = [self.entry_to_split(child) for child in entry[1]]
            split.subsplits = children
            return split
        return splits[entry]

    def __init__(self, route_as_list):
        self.splits = [self.entry_to_split(entry) for entry in route_as_list]

glitchless100perc = [
    "gamestart",
    ("ss1", ["secret_to_nobody", "trench_warfare"]),
    ("lab", ["worth_the_challenge", "lab_maze", "tantalizing_trinket", "purest_unobtainium"]),
    ("ss2", [
        "victoria_vitellary",
        "elephant",
        "one_way_room",
        "keep_coming_back",
        "clarion_call",
        "dtthw",
        "prize_for_the_reckless"
    ]),
    "im1",
    ("wz", ["cave_1", "cave_2", "cave_3", "edge_games"]),
    "im2",
    ("tow", ["tower_1", "tower_2"]),
    ("fin", ["v"])
]
