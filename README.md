# sbus_controller
A ROS1 package for converting SBUS signal to sensor_msgs/Joy messages

# Setup
## SBUS receiver
- The SBUS receiver is wired to an **Arduino Nano** with the script [Sbus_invert.ino](https://github.com/Cleric-K/vJoySerialFeeder/blob/master/Arduino/Sbus_invert/Sbus_invert.ino).
- With this setup, the SBUS signal can be read with the serial setup:
```python
import serial
ser = serial.Serial(
  port,
  baudrate=100000,
  parity=serial.PARITY_EVEN,
  stopbits=serial.STOPBITS_TWO
)
```
- At the moment, this is the only known way to convert a **non-default baud rate (100000), inverting UART signal** to USB.
- Another possible method is to invert the SBUS signal and connect to a TTL-to-USB module. However, this does not work with **CP2102-based modules**. Perhaps, **CH340-based modules** could work since it is also used on the Arduino Nano.
## Parameters
- **port**:
  - Port which the SBUS receiver is connected to.
  - Default: /dev/ttyUSB0
- **publish_rate**:
  - The publish rate of the output sensor_msgs/Joy topic
  - Default: 20
- **invert_channels**:
  - List of channels to be inverted.
  - Default: [ ]
- **two_state_buttons**:
  - List of channels to be published as two-state buttons i.e. below 991 &rarr; 0, above 991 &rarr; 1.
  - Default: [8, 9]
- **tri_state_buttons**:
  - List of channels to be published as tri-state buttons i.e. 172 &rarr; 0, 1811 &rarr; 2, else &rarr; 1.
  - Default: [4, 5, 6, 7]
 
## Published Topic /joy:
- **axes[16]**: Values of all 16 channels from the SBUS signal. All values are scaled to range [-1.0; 1.0].
- **buttons[16]**: Values are determined by the channels specified in:
  - **two_state_buttons**
  - **tri_state_buttons**
  - Otherwise, 0.
