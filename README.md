# NESP-Lib – New Era Syringe Pump Library for Python

This project aims to offer a clean high-level interface to the New Era syringe pumps by New Era Pump
Systems.

These pumps are also distributed under different names, like Aladdin by World Precision Instruments
(WPI) and LA by Landgraf Laborsysteme.

## Features

- Object-oriented design
- Documented public elements via type hints and docstrings
- Signaling errors via exceptions
- Blocking and non-blocking running
- Sending heartbeat messages automatically

## Installing

```
pip install NESP-Lib
```

## Importing

``` python
import nesp_lib
```

## Examples

### Opening and Closing a Port

#### Manual Closing

``` python
from nesp_lib import Port

# Constructs and opens the port to which the pump is connected.
port = Port('COM1')

# Do something here while the port is open.
...

# Closes the port.
port.close()
```

#### Automatic Closing

``` python
from nesp_lib import Port

# Constructs, opens and automatically closes the port to which the pump is connected.
with Port('COM1') as port :
    # Do something here while the port is open.
    ...
```

### Configuring a Pump

``` python
from nesp_lib import Pump, PumpingDirection

# Constructs the pump connected to the port.
pump = Pump(port)

# Sets the syringe diameter of the pump in units of millimeters.
pump.syringe_diameter = 30.0

# Sets the pumping direction of the pump.
pump.pumping_direction = PumpingDirection.INFUSE

# Sets the pumping volume of the pump in units of milliliters.
pump.pumping_volume = 1.0

# Sets the pumping rate of the pump in units of milliliters per minute.
pump.pumping_rate = 20.0
```

### Identifying a Pump

``` python
# Prints the model number of the pump (e.g. "1000" for NE-1000).
print(pump.model_number)

# Prints the firmware version of the pump (e.g. "(3, 928)" for 3.928).
print(pump.firmware_version)
```

### Running a Pump

#### Blocking

Blocking running waits while the pump is running.

``` python
# Runs the pump considering the direction, volume, and rate set.
pump.run()
```

#### Non-blocking

Non-blocking running returns immediately after starting the running.

``` python
# Starts running the pump considering the direction, volume, and rate set.
pump.run(False)

# Waits while the pump is running.
pump.wait_while_running()

# Starts running the pump considering the direction, volume, and rate set.
pump.run(False)

# Waits while the pump is running.
while pump.running :
    # Do something here while the pump is running.
    ...

# Starts running the pump considering the direction, volume, and rate set.
pump.run(False)

# Do something here while the pump is running.
...

# Stops the pump.
pump.stop()
```