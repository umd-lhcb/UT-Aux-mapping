# UT-Aux-mapping [![github CI](https://github.com/umd-lhcb/UT-Aux-mapping/workflows/CI/badge.svg?branch=master)](https://github.com/umd-lhcb/UT-Aux-mapping/actions?query=workflow%3ACI)

[![built with nix](https://builtwithnix.org/badge.svg)](https://builtwithnix.org)

Python scripts to generate various UT auxiliary mappings:

* `P2B2toPPPMapping.py`: cable mapping for true/mirror P2B2 -> true/mirror PPP
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

## PPP correspondence

- `A-BOT-IP-MIRROR  <-> C-TOP-IP-MIRROR` (`a_mirror_ppp_ip <-> c_mirror_ppp_ip`)
- `A-TOP-MAG-MIRROR <-> C-BOT-MAG-MIRROR` (`a_mirror_ppp_mag <-> c_mirror_ppp_mag`)
- `A-TOP-IP-TRUE    <-> C-BOT-IP-TRUE` (`a_true_ppp_ip <-> c_true_ppp_ip`)
- `A-BOT-MAG-TRUE   <-> C-TOP-MAG-TRUE` (`a_true_ppp_mag <-> c_true_ppp_mag`)
