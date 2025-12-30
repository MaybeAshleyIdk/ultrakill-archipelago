<!--
  Copyright (c) 2025 MaybeAshleyIdk
  SPDX-License-Identifier: CC-BY-SA-4.0
-->

# ULTRAKILL Archipelago #

> [!NOTE]
> This is a fork of [TRPG0/ArchipelagoULTRAKILL](https://github.com/TRPG0/ArchipelagoULTRAKILL).
>
> Credit goes to the original author for the massive amount of work that went in to creating the original version.  
> The vast majority of code is still theirs and all original image assets were created by them.
>
> This fork was created to freshen up and refactor the codebase to make it more maintainable and to add personal
> features and tweaks.  
> This will result in most code being rewritten and replaced, however since I have never made a mod before, especially
> one of this scale, the original code will always live on in the form of knowledge of how its done in the first place,
> no matter how much it will be changed.
>
> Also, the original image assets will not be replaced by me since I'm about as artistic as a rock.
>
> All that to say that I'm massively thankful to the original author and also impressed for creating the original version.

<!--
[version_shield]: <https://img.shields.io/badge/version-{{CURRENT_VERSION_NAME}}-informational.svg>
[release_page]: <https://github.com/MaybeAshleyIdk/ultrakill-archipelago/releases/tag/v{{CURRENT_VERSION_NAME}}> "GitHub Release page for version {{CURRENT_VERSION_NAME}}"
[![version: {{CURRENT_VERSION_NAME}}][version_shield]][release_page]
[![Changelog](https://img.shields.io/badge/-Changelog-informational.svg)](./CHANGELOG.md "Changelog")
-->

Adds [ULTRAKILL] support to [Archipelago].

This project encompasses both the APWorld (the "logic") and the client mod.  
The development files, along with the developer documentation, are located in the directories [`apworld`](./apworld/)
and [`client-mod`](./client-mod/).

[ULTRAKILL]: <https://store.steampowered.com/app/1229490/ULTRAKILL/> "ULTRAKILL on Steam"
[Archipelago]: <https://archipelago.gg/> "Archipelago"

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

<!-- This stays commented out until the links work, i.e.: until everything is published.

## Client Mod Setup ##

> [!NOTE]
> This guide only covers the client mod setup.  
> Users are expected to know the basics of installing APWorlds, customizing YAMLs, generating games and hosting them.
>
> [[Download the APWorld file here]][apworld_url]
>
> [apworld_url]: <https://github.com/MaybeAshleyIdk/ultrakill-archipelago/releases/download/v0.1.0/ultrakill.apworld>

### Installation ###

The recommended way to install the client mod is through a mod manager like [r2modman].  
On Thunderstore, the mod's name is `ULTRArchipelago`.  
If you instead want to install the mod manually, then refer to
the section [**Manual Installation**](#manual-installation).

It is also recommended to install [NoTutorial] to skip the startup sequence intro and the tutorial when selecting
a new save file.

[r2modman]: <https://thunderstore.io/package/ebkr/r2modman/> "r2modman | Thunderstore - The Risk of Rain 2 Mod Database"
[NoTutorial]: <https://github.com/TRPG0/UK-NoTutorial> "TRPG0/UK-NoTutorial: A mod for ULTRAKILL that prevents the tutorial from loading when starting new saves."

### Starting a Run ###

To connect to an Archipelago server and start a run, first select an empty save file.  
Then open the options, click on `PLUGIN CONFIG` (top left), then click on `CONFIGURE` next to the `Archipelago` entry
and open the `PLAYER SETTINGS`.  
Here you enter your slot name (the `name:` from your YAML file) and the server's address, port and password.  
Once you've entered all the info, click on `CONNECT`.  
You can back out of the options and starting playing!

### Console Commands ###

The client mod adds the following console commands:

* `connect <address:port> <slot> <password>` — Connect to an Archipelago server
* `disconnect` — Disconnect from the currently connected Archipelago server
* `say <message>` — Send messages or commands to the currently connected Archipelago server

The console can be opened by pressing `F8` in the game.

### Manual Installation ###

1. Install [BepInEx] into ULTRAKILL, if it isn't already

2. The client mod depends on [PluginConfigurator].  
   Follow the installation instructions of it

3. [Download the Thunderstore package ZIP file] (even if you won't be using a mod manager) and extract the DLL files
   into the directory `BepInEx/plugins`.  
   The other files in the ZIP file are not necessary

[BepInEx]: <https://docs.bepinex.dev/articles/user_guide/installation/index.html> "Installing BepInEx | BepInEx Docs"
[PluginConfigurator]: <https://github.com/eternalUnion/UKPluginConfigurator> "eternalUnion/UKPluginConfigurator"
[Download the Thunderstore package ZIP file]: <https://github.com/MaybeAshleyIdk/ultrakill-archipelago/releases/download/v0.1.0/MaybeAshleyIdk-ULTRArchipelago-0.1.0.zip>

-->
