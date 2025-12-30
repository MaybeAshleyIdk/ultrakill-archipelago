<!--
  Copyright (c) 2025 MaybeAshleyIdk
  SPDX-License-Identifier: CC-BY-SA-4.0
-->

# ULTRAKILL Archipelago Client Mod #

<!-- This stays commented out until the project root README actually contains the user setup guide.
> [!IMPORTANT]
> **This is developer documentation!**  
> If you are a user that just wants to install the mod, then refer to [the project root README file](../README.md).
-->

The client mod is written as a [BepInEx] plugin.
Basic knowledge about how BepInEx plugins work and how they are installed is required.

[BepInEx]: <https://docs.bepinex.dev/> "Welcome to BepinEx Docs! | BepInEx Docs"

## Development Setup ##

The following things need to be installed:

* [Python] (at least version 3.12)
* [The .NET SDK]
* [ULTRAKILL]
* An editor/IDE that supports C# and .NET.  
  Popular choices:
  * [Visual Studio] (bundles the .NET SDK)
  * [Visual Studio Code] / [VSCodium]

The build the mod, the main assembly from [UKPluginConfigurator] and a handful of ULTRAKILL assemblies are required.  
These assemblies are automatically gathered by the script [`setup.py`](./setup.py) and copied to the directory `libs`.  
The first step after installing all required software is to execute this script.

For the ULTRAKILL assemblies, the script will try to automatically detect the ULTRAKILL game directory to copy
the assemblies from.  
The script does that by checking some common paths that the Steam library could be located at.  
In case the directory that the script finds is incorrect, it is possible to manually enter a custom one.  
The directory also needs to be manually entered in case the script couldn't find it automatically.

[Python]: <https://www.python.org/downloads/> "Download Python | Python.org"
[The .NET SDK]: <https://dotnet.microsoft.com/en-us/download> "Download .NET (Linux, macOS, and Windows) | .NET"
[ULTRAKILL]: <https://store.steampowered.com/app/1229490/ULTRAKILL/> "ULTRAKILL on Steam"
[Visual Studio]: <https://visualstudio.microsoft.com/> "Visual Studio: IDE and Code Editor for Software Development"
[Visual Studio Code]: <https://code.visualstudio.com/download> "Download Visual Studio Code - Mac, Linux, Windows"
[VSCodium]: <https://vscodium.com/> "VSCodium - Open Source Binaries of VSCode"
[UKPluginConfigurator]: <https://github.com/eternalUnion/UKPluginConfigurator> "eternalUnion/UKPluginConfigurator"

## Building ##

To build the mod assemblies and the Thunderstore package, execute the MSBuild target `Build`.  
On the command line:

```sh
dotnet build
# or
msbuild
```

The package will be placed into the directory `thunderstore/packages`.

For release builds, execute `Build` with the configuration `Release`:

```sh
dotnet build --configuration Release
# or
msbuild -property Configuration=Release
```

## Updating the ULTRAKILL target version ##

> [!NOTE]
> This process has not actually been done yet. It is currently purely theoretical.  
> The next ULTRAKILL update is planned to release ["very early next year"][ultrakill_fraud_dev_update] (2026), so we'll
> see if these steps hold up in practice soon.
>
> [ultrakill_fraud_dev_update]: <https://store.steampowered.com/news/app/1229490/view/526488194423718484> "ULTRAKILL - Fraud Development Update - Steam News"

1. Start ULTRAKILL with BepInEx installed and the console enabled to check which version of Unity ULTRAKILL now uses
   and update it in [`UltrakillArchipelago.csproj`](./UltrakillArchipelago.csproj) if it changed

2. Execute the script `setup.py` with the argument `update-ultrakill` to copy the new assemblies from
   the ULTRAKILL game directory to the `libs` directory:

   ```sh
   ./setup.py update-ultrakill
   ```

3. After the script is done, it will print a table of the copied assembly files and their SHA-256 checksums.  
   Copy the checksums and update the ones that changed in `UltrakillArchipelago.csproj`

4. Update the comment in `UltrakillArchipelago.csproj` with the new patch number, optional update title
   (e.g.: "The ULTRA_REVAMP Update", "The FULL ARSENAL Update", …) and the URL to the update's SteamDB patch page

5. Fix any build errors and test if the mod still works as intended

## Updating UKPluginConfigurator ##

> [!NOTE]
> This process has not actually been done yet. It is currently purely theoretical.  
> We'll see if these steps hold up in practice once a new UKPluginConfigurator version is released.

1. Update the version of UKPluginConfigurator in `UltrakillArchipelago.csproj`
2. Execute the script `setup.py` with the argument `update-plugin-configurator`
3. After the script is done, it will print the new assembly's SHA-256 checksum.
   Copy it and update it in `UltrakillArchipelago.csproj`
4. Fix any build errors and test if the mod still works as intended
