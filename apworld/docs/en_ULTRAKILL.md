<!--
  Copyright (c) 2025 MaybeAshleyIdk
  SPDX-License-Identifier: CC-BY-SA-4.0
-->

# ULTRAKILL #

## Where is the options page? ##

The [player options page for this game](../player-options) contains all the options you need to configure and export
a config file.

## What does randomization do to this game? ##

The player's starting weapon and the order in which missions (or entire layers) are unlocked is randomized.
Every other weapon and mission/layer is unlocked by finding them as items in the multiworld.

Additionally, the starting mission and which abilities the player starts with (weapon alternative/secondary fire, dash,
wall jumps, slide, slam) can also be randomized. (for a slightly more in-depth overview, see
the section [**Which items can be in another player's world?**](#which-items-can-be-in-another-players-world))

### Locations ("Checks") ###

* Collecting soul orbs
* Completing mission challenges
* Completing missions with a P-rank
* Killing a type of enemy for the first time
* Catching fish in `5-S: I ONLY SAY MORNING`
* Cleaning the rooms in `7-S: HELL BATH NO FURY`
* Winning at chess in the Developer Museum
* Winning the rocket race in the Developer Museum

## What is the goal of ULTRAKILL when randomized? ##

The goal is to complete a mission that was chosen in the YAML.  
This goal mission is unlocked after completing a certain number of other missions. Secret missions and
the Prime Sanctums also count towards unlocking the goal, however the Prime Sanctums are not considered in logic unless
chosen as the goal mission.

The game can be played on any difficulty.

## Which items can be in another player's world? ##

* Individual missions or entire layers (depending on YAML options)
* Weapons
* Arms (Feedbacker, Knuckleblaster & Whiplash)
* Weapon alternates ("Slab" Revolver, Impact Hammer & Sawblade Launcher)
* Weapon's alternative/secondary fire
* Stamina bars (dashes)
* Wall jumps
* Slide
* Slam
* Skull keys
* Limbo switches
* Violence switches
* Filler items
* Traps

<!-- TODO: list filler items once they're better defined -->
<!-- TODO: list traps once they're better defined -->

## What does another world's item look like in ULTRAKILL? ##

Only the shop will display icons/names of other world's items.  
All other locations (e.g.: secret orbs, switches, …) will look the same as in vanilla ULTRAKILL.

## When the player receives an item, what happens? ##

A notification in the bottom right corner will appear for a few seconds that shows what item the player received.

The pause menu also lists a handful of the most recently received items.

Weapons and abilities that are received are immediately unlocked if the player is currently in a mission.  
Temporary powerups (some of the filler items and the traps) are queued one after another.

> **NOTE:** There is a known bug where receiving a weapon while in a mission will switch off of
> the currently held weapon to no weapon at all.  
> Simply select any weapon again through the number keys or the scroll wheel when that happens.

## Console Commands ##

The client mod adds the following console commands:

* `connect <address:port> <slot> <password>` — Connect to an Archipelago server
* `disconnect` — Disconnect from the currently connected Archipelago server
* `say <message>` — Send messages or commands to the currently connected Archipelago server

The console can be opened by pressing `F8` in the game.
