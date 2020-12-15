# UT-Aux-mapping ![github CI](https://github.com/umd-lhcb/UT-Aux-mapping/workflows/CI/badge.svg?branch=master)

[![built with nix](https://builtwithnix.org/badge.svg)](https://builtwithnix.org)

Python script to generate various UT auxiliary mappings. So far, we have:

* COMET FPGA to DCB pin-by-pin mapping
* COMET FPGA to Path finder U.FL pin-by-pin mapping
* True backplane power mapping
* Mirror backplane power mapping


## Prerequisite
Update the submodule:
```
git submodule update --init
```

Then install the dependencies:
```
pip install -r pyUTM/requirements.txt
```


## Usage
```
python ./CometDcbMapping.py
python ./CometPFMapping.py
python ./TrueBPInnerMapping.py
python ./MirrorBPInnerMapping.py
```

All generated mapping `.csv` files are located under `output/`
