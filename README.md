# MEROSS_DEVICE

## Installation

```
update add https://raw.githubusercontent.com/DeGriesche/MEROSS_DEVICE/master/controls_meross_device.txt
update check meross_device
update all meross_device
```

Rename  `_config.ini` to `config.ini` at `fhem/FHEM/meross/` and fill properties.

## Python dependencies

```
pip install fhem 
pip install meross_iot
pip install python-daemon
```