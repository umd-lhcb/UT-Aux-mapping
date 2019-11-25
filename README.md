# UT-Aux-mapping [![Build status](https://travis-ci.com/umd-lhcb/UT-Aux-mapping.svg?master)](https://travis-ci.com/umd-lhcb/UT-Aux-mapping)
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
