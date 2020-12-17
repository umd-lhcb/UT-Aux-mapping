# UT-Aux-mapping [![github CI](https://github.com/umd-lhcb/UT-Aux-mapping/workflows/CI/badge.svg?branch=master)](https://github.com/umd-lhcb/UT-Aux-mapping/actions?query=workflow%3ACI)

[![built with nix](https://builtwithnix.org/badge.svg)](https://builtwithnix.org)

Python scripts to generate various UT auxiliary mappings:

* `TrueP2B2toPPPMapping.py`: cable mapping for true P2B2 -> true PPP
* `MirrorP2B2toPPPMapping.py`: cable mapping for mirror P2B2 -> mirror PPP
* `PPPDebug.py`: Print out unique netnames between P2B2 and PPP
* All other scripts are no longer actively maintained. Though some of their
  outputs are available at [`0.4.3`](https://github.com/umd-lhcb/UT-Aux-mapping/releases/tag/0.4.3).


## Usage
All dependencies of this project are specified and pinpointed by `nix`. To run
these scripts, install `nix` on you computer.

Once that is done, if your `nix` has `flake` support:
```
nix develop -c make all
```
else:
```
nix-shell --run "make all"
```
