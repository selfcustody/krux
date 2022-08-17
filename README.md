[![codecov](https://codecov.io/gh/selfcustody/krux/branch/main/graph/badge.svg?token=XU80PT6Q9V)](https://codecov.io/gh/selfcustody/krux)
[![calver](https://img.shields.io/badge/calver-YY.0M.MICRO-22bfda.svg)](https://calver.org)

<p align="center">
<img src="https://selfcustody.github.io/krux/img/maixpy_m5stickv/logo-125.png">
<img src="https://selfcustody.github.io/krux/img/maixpy_amigo_tft/logo-125.png">
</p>

Krux is open-source firmware that enables anyone to build their own Bitcoin signing device via off-the-shelf parts. It runs on Kendryte K210 devices such as the [M5StickV](https://docs.m5stack.com/en/core/m5stickv) and [Maix Amigo](https://www.seeedstudio.com/Sipeed-Maix-Amigo-p-4689.html), converting them into airgapped devices that can sign transactions for multisignature and single-key wallets.

---
## Disclaimer
**WARNING**: *This software has not yet been audited by a third party. Use at your own risk!*

---

# Getting Started
Instructions for building and running Krux can now be found on our GitHub Pages site:

https://selfcustody.github.io/krux/

The instructions below are intended for developers who wish to contribute to the project.

# Development
## Fetch the code
Run the following:
```bash
git clone --recurse-submodules https://github.com/selfcustody/krux
```
This will pull down the Krux source code as well as the code for all its dependencies and put them inside a new `krux` folder.

Note: When you wish to pull down updates to this repo, you should run the following:
```bash
git pull origin main && git submodule update --init --recursive
```
This will make sure that all submodules (and their submodules, etc.) are pulled down and updated.

## Install krux and dev tools
The krux code is a Python package that should be installed with [Poetry](https://python-poetry.org/).
```bash
poetry install
```

This will also install all development tools so that you can run tests, run pylint, format code with [black](https://github.com/psf/black), etc.

Note that you can run `poetry install` after making a change to the krux code if you wish to test a change in the [interpreter](#use-the-python-interpreter-repl).

## Format code
```bash
poetry run black ./src && poetry run black ./tests
```

## Run pylint
```bash
poetry run pylint ./src
```

## Run tests
```bash
poetry run pytest --cache-clear --cov src/krux --cov-report html ./tests
```
This will run all tests and generate a coverage report you can browse to locally in your browser at `file:///path/to/krux/htmlcov/index.html`.

For more verbose test output (e.g., to see the output of print statements), run:

```bash
poetry run pytest --cache-clear --cov src/krux --cov-report html --show-capture all --capture tee-sys -r A ./tests
```

## Use the Python interpreter (REPL)
This can be useful for testing a change to the krux code without having to run a full build and flash:
```bash
poetry run python
```
```
Python 3.9.1
Type "help", "copyright", "credits" or "license" for more information.
>>> from krux.key import Key
>>> Key("olympic term tissue route sense program under choose bean emerge velvet absurd", False).xpub()
'tpubDCDuqu5HtBX2aD7wxvnHcj1DgFN1UVgzLkA1Ms4Va4P7TpJ3jDknkPLwWT2SqrKXNNAtJBCPcbJ8Tcpm6nLxgFapCZyhKgqwcEGv1BVpD7s'
>>>
```

## Run the simulator
This can be useful for testing a change to the krux code without having to run a full build and flash, visual regression testing,
generating screenshots, or even just trying out Krux before purchasing a device.
```bash
cd simulator && poetry run python simulator.py --device maixpy_amigo_tfts
```
```bash
cd simulator && poetry run python simulator.py --device maixpy_m5stickv
```

## Live debug a device
If you've made a fresh build and flashed it to your device, you can connect to the device over serial connection with:
```bash
screen /dev/tty.usbserial-device-name 115200
```

If you see a `Resource is busy` message, make sure to shut down the Vagrant box and try again:
```bash
vagrant halt
```

If successful, the device should restart and you should see:
```bash
K210 bootloader by LoBo v.1.4.1

* Find applications in MAIN parameters
0: '       firmware', @ 0x00080000, size=XXX, app_size=XXX, App ok, ACTIVE
* Loading app from flash at 0x00080000 (XXX B)
* Starting at 0x80000000 ...


[MAIXPY] Pll0:freq:XXX
[MAIXPY] Pll1:freq:XXX
[MAIXPY] Pll2:freq:XXX
[MAIXPY] cpu:freq:XXX
[MAIXPY] kpu:freq:XXX
[MAIXPY] Flash:0xef:0x17
[MaixPy] gc heap=0x8029f430-0x8036f430(851968)
init i2c:2 freq:XXX
[MAIXPY]: find ov7740
[MAIXPY]: find ov sensor
```

From here, you can use the device as normal and, if you added any print statements to the code, they should appear whenever your code is reached.

You can also drop into a live Python REPL at any point by issuing an interrupt with Ctrl-C:

```bash
Traceback (most recent call last):
  File "boot.py", line 38, in <module>
  File "krux/pages/__init__.py", line 192, in run
  File "krux/pages/__init__.py", line 207, in run_loop
  File "krux/input.py", line 27, in wait_for_button
KeyboardInterrupt:
MicroPython; Sipeed_M1 with kendryte-k210
Type "help()" for more information.
>>>
>>>
```

## Run mkdocs
```bash
poetry run mkdocs serve
```

# Inspired by these similar projects
- https://github.com/SeedSigner/seedsigner for Raspberry Pi (Zero)
- https://github.com/diybitcoinhardware/f469-disco for the F469-Discovery board

# Powered by
- [embit](https://embit.rocks/), a Bitcoin library for Python 3 and Micropython
- [MaixPy](https://github.com/sipeed/MaixPy), MicroPython for K210 RISC-V
- [MicroPython](https://github.com/micropython/micropython), a lean and efficient Python implementation for microcontrollers and constrained systems
- [Kboot](https://github.com/loboris/Kboot) and [ktool](https://github.com/loboris/ktool)

# Contributing
Issues and pull requests welcome! Let's make this as good as it can be.

Before opening a pull request for a new feature, please first start a [new discussion](https://github.com/selfcustody/krux/discussions) if the feature is large, is a proposal, or is in need of fleshing out before it can be turned into issue(s) for work. If the pull request you're opening already has an associated issue, please reference it when making your pull request and briefly explain how your PR resolves it. Ideally, each PR should be focused on resolving one issue (exceptions can be made if the work is related or tightly coupled).

**Please note**: When adding a new feature, please checkout and branch off of the `develop` branch. When making a PR, please also make sure to explicitly target `develop`; `main` is the default branch on GitHub because we want it to be easy for users (who aren't necessarily devs) to download and install Krux from source.

# Support
For technical support installing or using Krux, you can join our [#krux:matrix.org](https://matrix.to/#/#krux:matrix.org) server or [Telegram chat](https://t.me/SC_Krux). Make sure to also check out the [DIYbitcoin chat](https://t.me/diybitcoin) on Telegram, a broader community of tinkerers, builders, hackers, etc.

We do not use GitHub issues for support requests, only for bug reports and feature requests. 

You can also post a question in our [Discussions](https://github.com/selfcustody/krux/discussions) forum here on GitHub.
