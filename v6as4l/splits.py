from dataclasses import dataclass, field
from typing import Any

from .game import GV, Trigger

@dataclass
class Split():
    name: str
    trigger: Trigger
    variable: GV
    value: int = None
    time: int = None
    subsplits: list[Any] = field(default_factory=list)

splits = {
    "gamestart": Split("Game Start", Trigger.Value, GV.STATE, 0),
    "ss1": Split("Space Station 1", Trigger.Value, GV.STATE, 3051),
    "lab": Split("Laboratory", Trigger.Value, GV.STATE, 3040),
    "ss2": Split("Space Station 2", Trigger.Value, GV.STATE, 3020),
    "im1": Split("Intermission 1", Trigger.Value, GV.STATE, 3085),
    "wz" : Split("Warp Zone", Trigger.Value, GV.STATE, 3006),
    "im2": Split("Intermission 2", Trigger.Value, GV.STATE, 3080),
    "tow": Split("Tower", Trigger.Value, GV.STATE, 3060),
    "fin": Split("Game Complete", Trigger.Value, GV.STATE, 3503),
    "secret_to_nobody": Split("Trinket - It's a Secret to Nobody", Trigger.Changed, GV.TRINKETS),
    "trench_warfare": Split("Trinket - Trench Warfare", Trigger.Changed, GV.TRINKETS),
    "worth_the_challenge":
        Split("Trinket - Young Man, It's Worth the Challenge", Trigger.Changed, GV.TRINKETS),
    "lab_maze": Split("Lab maze", Trigger.Changed, GV.TRINKETS),
    "tantalizing_trinket": Split("Trinket - The Tantalizing Trinket", Trigger.Changed, GV.TRINKETS),
    "purest_unobtainium": Split("Trinket - Purest Unobtainium", Trigger.Changed, GV.TRINKETS),
    "victoria_vitellary": Split("Trinket - Victoria/Vitellary", Trigger.Changed, GV.TRINKETS),
    "elephant": Split("Trinket - Elephant", Trigger.Changed, GV.TRINKETS),
    "one_way_room": Split("Trinket - One Way Room", Trigger.Changed, GV.TRINKETS),
    "keep_coming_back": Split("Trinket - You Just Keep Coming Back", Trigger.Changed, GV.TRINKETS),
    "clarion_call": Split("Trinket - Clarion Call", Trigger.Changed, GV.TRINKETS),
    "dtthw": Split("Trinket - Doing Things the Hard Way", Trigger.Changed, GV.TRINKETS),
    "prize_for_the_reckless":
        Split("Trinket - Prize for the Reckless", Trigger.Changed, GV.TRINKETS),
    "cave_1": Split("Trinket - Cave 1", Trigger.Changed, GV.TRINKETS),
    "cave_2": Split("Trinket - Cave 2", Trigger.Changed, GV.TRINKETS),
    "cave_3": Split("Trinket - Cave 3", Trigger.Changed, GV.TRINKETS),
    "edge_games": Split("Trinket - Edge Games", Trigger.Changed, GV.TRINKETS),
    "tower_1": Split("Trinket - Tower 1", Trigger.Changed, GV.TRINKETS),
    "tower_2": Split("Trinket - Tower 2", Trigger.Changed, GV.TRINKETS),
    "v": Split("Trinket - V", Trigger.Changed, GV.TRINKETS)
}
