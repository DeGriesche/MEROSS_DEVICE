# MEROSS_DEVICE



## Setup

### Prerequisites

Install Python > 3.6.

Install following Python packages:
```
pip install fhem 
pip install meross_iot
pip install python-daemon
```

### Installation

```
update add https://raw.githubusercontent.com/DeGriesche/MEROSS_DEVICE/master/controls_meross_device.txt
update check meross_device
update all meross_device
```

### Configuration
Rename  `_config.ini` to `config.ini` at `fhem/FHEM/meross/` and fill properties.