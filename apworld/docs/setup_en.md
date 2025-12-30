<!--
  Copyright (c) 2025 MaybeAshleyIdk
  SPDX-License-Identifier: CC-BY-SA-4.0
-->

# ULTRAKILL Archipelago Setup Guide #

## Client Mod Installation ##

The recommended way to install the client mod is through a mod manager like [r2modman].  
After installing it and setting up a profile, search for `ULTRArchipelago` and install it.

It is also recommended to install [NoTutorial] to skip the startup sequence intro and the tutorial when selecting
a new save file.

[r2modman]: <https://thunderstore.io/package/ebkr/r2modman/> "r2modman | Thunderstore - The Risk of Rain 2 Mod Database"
[NoTutorial]: <https://github.com/TRPG0/UK-NoTutorial> "TRPG0/UK-NoTutorial: A mod for ULTRAKILL that prevents the tutorial from loading when starting new saves."

## Configuring your YAML File ##

### What is a YAML and why do I need one? ###

An YAML file is the way that you provide your player options to Archipelago.
See the [Archipelago Setup Guide](/tutorial/Archipelago/setup/en) here on the Archipelago website to learn more.

### Where do I get a YAML? ###

You can use the [game options page for ULTRAKILL] here on the Archipelago website to generate a YAML using
a graphical interface.

[game options page for ULTRAKILL]: </games/ULTRAKILL/player-options>

## Joining a MultiWorld Game ##

To connect to an Archipelago server and start a run, first select an empty save file.  
Then open the options, click on `PLUGIN CONFIG` (top left), then click on `CONFIGURE` next to the `Archipelago` entry
and open the `PLAYER SETTINGS`.  
Here you enter your slot name (the `name:` from your YAML file) and the server's address, port and password.  
Once you've entered all the info, click on `CONNECT`.  
You can back out of the options and starting playing!

## Console Commands ##

The mod adds the following console commands:

* `connect <address:port> <slot> <password>` — Connect to an Archipelago server
* `disconnect` — Disconnect from the currently connected Archipelago server
* `say <message>` — Send messages or commands to the currently connected Archipelago server

The console can be opened by pressing `F8` in the game.
