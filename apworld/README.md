<!--
  Copyright (c) 2025 MaybeAshleyIdk
  SPDX-License-Identifier: CC-BY-SA-4.0
-->

# ULTRAKILL Archipelago APWorld #

<!-- This stays commented out until the project root README actually contains the user setup guide.
> [!IMPORTANT]
> **This is developer documentation!**  
> If you are a user that just wants to install the APWorld, then refer to [the project root README file](../README.md).
-->

## Development Setup ##

The only thing required to build the APWorld is [Python] version **3.12** or above.  
Note that the Python version required for the build is separate from the APWorld code. Archipelago's minimum supported
Python version is **3.11.9** or above.

Building an APWorld and running the unit tests can only be done with the Archipelago source code.
(see [the APWorld Specification] and [the Archipelago Unit Testing API])  
These processes are automated with the script [`build.py`](./build.py).  
It is a custom task runner that accepts "targets" to build.
(execute the script with the option `--help` for more information)

Executing the build script without any arguments will build the APWorld
(which will be placed into the directory `output`) and run the test suite.  
Before these two steps are done, the script will download the Archipelago source code and create
a [virtual Python environment] for it. (these steps are cached for subsequent builds)  
For a first time setup, it may be beneficial to skip the test suite. This can be achieved by building
the target `archipelago_virtual_environment`.

Since APWorld Python code must use absolute imports for Archipelago's APIs
(see [the section "Caveats" in the APWorld Specification]), editors and IDEs will not be able to resolve these
imports.  
Additionally, Archipelago has many dependencies, which are all installed in the virtual environment.  
To enable your editor or IDE to resolve the imports, you must activate the virtual environment located at
`.build/archipelago-<version>/venv` and add the path `.build/archipelago-<version>/source` to the [Python path].  
Note that this must *only* be configured in your editor/IDE for the APWorld Python files. The build script should *not*
be executed with the virtual environment.

[Python]: <https://www.python.org/downloads/> "Download Python | Python.org"
[the APWorld Specification]: <https://github.com/ArchipelagoMW/Archipelago/blob/main/docs/apworld%20specification.md> "Archipelago/docs/apworld specification.md at main · ArchipelagoMW/Archipelago"
[the section "Caveats" in the APWorld Specification]: <https://github.com/ArchipelagoMW/Archipelago/blob/main/docs/apworld%20specification.md#caveats> "Archipelago/docs/apworld specification.md at main · ArchipelagoMW/Archipelago"
[the Archipelago Unit Testing API]: <https://github.com/ArchipelagoMW/Archipelago/blob/main/docs/tests.md> "Archipelago/docs/tests.md at main · ArchipelagoMW/Archipelago"
[virtual Python environment]: <https://docs.python.org/3/library/venv.html> "venv — Creation of virtual environments &#8212; Python 3 documentation"
[Python path]: <https://docs.python.org/3/library/sys_path_init.html> "The initialization of the sys.path module search path &#8212; Python 3 documentation"

### PyCharm ###

The recommended IDE is [PyCharm](https://www.jetbrains.com/pycharm/).

To activate the virtual environment and change the Python path, open the settings and navigate to
**Python » Interpreter.**

Click **Add Interpreter » Add Local Interpreter… » Select existing** and in the **Python path** field, select
the virtual environment created by the build script (`<project_root>/apworld/.build/archipelago-<version>/venv`) and
then click the **OK** button.  
PyCharm will now use the virtual environment for the project, which means that it has access to
Archipelago's *dependencies*, but not to Archipelago's APIs itself.

Still on the **Python » Interpreter** tab, click the **Python Interpreter** dropdown box and select **Show All…**.  
The previously added interpreter should be preselected. Click the **Show Interpreter Paths** button.
(the rightmost icon in the top row that looks like a directory tree structure)  
Click the **Add** button (the `+` icon), select the Archipelago source directory downloaded by the build script
(`<project_root>/apworld/.build/archipelago-<version>/source`) and click all **OK** buttons until you have exited
the settings.

If PyCharm still shows that it cannot find Archipelago's modules, then navigate to the Archipelago source directory in
PyCharm, right click it and select **Mark Directory As » Sources Root.**

## Updating the Archipelago target version ##

> [!NOTE]
> This process has not actually been done yet. It is currently purely theoretical.  
> We'll see if these steps hold up in practice once a new Archipelago version is released.

In the build script (`build.py`), update the constants `ARCHIPELAGO_VERSION` and
`ARCHIPELAGO_SOURCE_ARCHIVE_SHA256_CHECKSUM` to the desired Archipelago version and to the SHA-256 checksum of
the new Archipelago source code archive (`.tar.gz`) corresponding to the new target version respectively.

The quickest way to get the SHA-256 checksum of the new archive is to first only update the version and then to build
the target `archipelago_source_archive`.  
The build script will download the Archipelago source code archive and then print a warning that the checksum of
the downloaded archive is not what is expected.  
This warning will contain the SHA-256 checksum of the new archive (labeled as "actual").

After updating both constants, fix any build errors, (newly) failing unit tests and test if the APWorld still works as
intended.
