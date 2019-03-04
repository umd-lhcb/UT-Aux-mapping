# COMET-DCB-Mapping [![Build status](https://travis-ci.com/umd-lhcb/COMET-DCB-mapping.svg?master)](https://travis-ci.com/umd-lhcb)
Python script to generate COMET FPGA to DCB pin-by-pin mapping.


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
python ./MappingGen.py
```

All generated mapping `.csv` files are located under `output/`
