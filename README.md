PyAutoSplit
===========

This is a python based autosplitting tool for speedrunning. Currently only Linux is supported, but adding Windows support should be possible, when I come around to do it. In theory MacOS and other Unix systems work, but this is completely untested.

## Why was this done?

While LiveSplit does work inside wine, the autosplit component does not work on linux machines. In addition to this, it is not possible to create breakpoints and read values in CPU registers with the autosplit component of LiveSplit. PyAutoSplit can do that. This is especially useful in a game like VVVVVV (2.2 and below), where all relevant information are on the stack, and therefore at nonstatic locations in memory. 

Current strategies involve scanning the processes memory for specific values, to guess the location of information like gamestate etc. Unfortunately this is rather error prone. With PyAutoSplit one can set a breakpoint at the (static) instruction where the game object is created, and read the cpu registers to get an exact location of the game object.

## Installation

The program can be installed via pip

```
pip install --user git+https://github.com/christofsteel/pyautosplit.git
```

## Usage

First you should start LiveSplit, and start the LiveSplit server component. After that you can launch PyAutoSplit with

```
pyautosplit routefile.json
```

## Configuration

To use PyAutoSplit for a game, you have to have it installed and two files. One specific for the game you are playing and one specific for your route. In this repository, there is an example for the game VVVVVV and a route for glitchless 100%.

### Game file

A game file is a json file with the following fields:

  * `name`, the name of the game
  * `command`, the launch command to run the game
  * `cwd`, the working directory of the command (optional)
  * `frequency`, how many times a second should the memory be read
  * `time`, how does one calculate the ingame time in seconds (optional). If not present, realtime will be used.
  * `variables`, variables, that can be used to define other components (see below)
  * `events`, events, that can trigger splits, resets etc. (see also below)


#### Variables

A variable in the `variables` field can be either a the state of the stack pointer at a specific instruction (`rsp`), the state of the base pointer at a specific instruction (`rbp`) or an integer value at an address in memory (`memory`). Addresses of variables can use the values of variables, that were defined prior, and the stack and base pointer can define an offset to be added to the value.

```
"game_object": {
    "type": "rsp",
    "address": "0x416da8",
    "offset": "0xe20"
}
```

This defines the variable `game_object` to be the value of the stack pointer at instruction `0x416da8` incremented by `0xe20`.

```
"frames": {
    "type": "memory",
    "address": "game_object + 0xa8"
}
```

This defines the variable `frames` to be the value in memory at address `game_object + 0xa8`. The variable `game_object` must be defined prior.

#### Events

An event in the `events` field is a json object with the fields `name` and `trigger`, bound to an identifier.

```
"gamestart": {
    "name": "Game Start",
    "trigger": "state.gamestate == 0"
}
```

This defines the event `gamestart` with the name `Game Start` to be triggered, if the variable `gamestate` is equal to `0` at the current state.

Events can access variables of the current state by prefixing them with `state.`. They also can access variables of the state juste before the current state by prefixing them with `oldstate.`. This is useful to track changes in the state.

```
"secret_to_nobody": {
    "name": "Trinket - It's a Secret to Nobody",
    "trigger": "state.trinkets != oldstate.trinkets"
}
```

This triggers if the variables `trinkets` changes.

### Route file

A route file defines the route for your speedrun. It is also a json file with the following fields:

 * `name`, the name of your attemtet category
 * `gamefile`, the location of the respective json file for the game
 * `start`, the event to start the timer
 * `reset`, the event to reset the timer
 * `route`, this defines the triggers for the actual route (see below)

The field `route` containes the splits. Each split is itself a json object, that can contain subsplits.

```
'first_level': {},
'second_level': {
  'mid_boss' : {}
}
```
In this example the first split is triggered when the event `first_level` happens. The next split would be the first subsplit of `second_level`, namely `mid_boss`, the next split would be `second_level` itself.

The names of the splits reference events as defined in the game file.
