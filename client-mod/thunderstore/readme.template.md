<!--
  Copyright (c) 2025 MaybeAshleyIdk
  SPDX-License-Identifier: CC-BY-SA-4.0
-->

# ULTRAKILL Archipelago Client #

<!-- markdownlint-disable-next-line heading-increment -->
> ### Note ###
>
> This is a fork of [TRPG's Archipelago client mod].
>
> [TRPG's Archipelago client mod]: <https://thunderstore.io/c/ultrakill/p/TRPG/Archipelago/>

An implementation of an [Archipelago](https://archipelago.gg/) client for ULTRAKILL.

Archipelago is a multiplayer cross-game randomizer.  
Players in different games can connect to a server and send each other items from each others' games.

## Randomizer Overview ##

The player's starting weapon and the order in which missions are unlocked is randomized.
All the other weapons, the other arms, the weapon alternatives and the remaining missions are unlocked by finding them
as items in the multiworld.

Additionally, the starting mission, which abilities the player starts with (weapon alternative/secondary fire, dash,
wall jumps, slide, slam), the Skull Keys and the Limbo- & Violence switches can also be randomized.

Multiworld items are found by collecting soul orbs, completing mission challenges, completing mission with a P-rank,
killing a type of enemy for the first time and more.

The goal is to complete one mission that gets chosen beforehand.  
This goal mission is unlocked after completing a certain number of other missions.

## Starting a Run ##

> Note that this short guide only covers the client mod.  
> Users are expected to know the basics of installing APWorlds, customizing YAMLs, generating games and hosting them.
>
> [[Download the APWorld file here]][apworld_url]
>
> [apworld_url]: <https://github.com/MaybeAshleyIdk/ultrakill-archipelago/releases/download/v{{VERSION}}/ultrakill.apworld>

To connect to an Archipelago server and start a run, first select an empty save file.  
It is recommended to install [NoTutorial] to skip the startup sequence intro and the tutorial when selecting
a new save file.

Then open the options, click on `PLUGIN CONFIG` (top left), then click on `CONFIGURE` next to the `Archipelago` entry
and open the `PLAYER SETTINGS`.  
Here you enter your slot name (the `name:` from your YAML file) and the server's address, port and password.  
Once you've entered all the info, click on `CONNECT`.  
You can back out of the options and starting playing!

[NoTutorial]: <https://thunderstore.io/c/ultrakill/p/TRPG/NoTutorial/> "NoTutorial | Thunderstore - The ULTRAKILL Mod Database"

## Console Commands ##

The mod adds the following console commands:

* `connect <address:port> <slot> <password>` — Connect to an Archipelago server
* `disconnect` — Disconnect from the currently connected Archipelago server
* `say <message>` — Send messages or commands to the currently connected Archipelago server

The console can be opened by pressing `F8` in the game.
