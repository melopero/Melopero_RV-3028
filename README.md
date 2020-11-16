# Melopero_RV-3028
A library for interfacing the <b>Melopero RV-3028 Extreme Low Power RTC module breakout</b> with a Raspberry Pi.
<br> If you were looking for the Arduino library click [HERE](https://github.com/melopero/Melopero_RV-3028_Arduino_Library)

![melopero logo](images/Melopero-RV-3028-diagonal-2.jpg?raw=true)

# Pinouts

<table style="width:100%">
  <tr>
    <th>Melopero RV-3028</th>
    <th>Description</th>
  </tr>
  <tr>
    <td>3V3</td>
    <td>Input power pin. Apply 3.3V to this pin</td>
  </tr>
  <tr>
    <td>SCL</td>
    <td>I2C Serial CLock pin</td>
  </tr>
  <tr>
    <td>SDA</td>
    <td>I2C Serial DAta pin</td>
  </tr>
  <tr>
    <td>GND</td>
    <td>Ground pin</td>
  </tr>
  <tr>
    <td>EVI</td>
    <td>External Event Input(INPUT), pulled high (see schematics for more details)</td>
  </tr>
  <tr>
    <td>INT</td>
    <td>Interrupt Output, active LOW, pulled-high (see schematics for more details) </td>
  </tr>
</table>


## Getting Started
### Prerequisites
You will need:
- a python3 version, which you can get here: [download python3](https://www.python.org/downloads/)
- a Melopero RV-3028 breakout board: [buy here](https://www.melopero.com/shop/)

### Connect the sensor to the Raspberry Pi
You can find a description of the GPIO connector of the Raspberry Pi [HERE](https://www.raspberrypi.org/documentation/usage/gpio/)
<br>The RV-3028 communicates over I2C:
<table style="width:100%">
  <tr>
    <th>Melopero RV-3028</th>
    <th>Raspberry Pi</th> 
  </tr>
  <tr>
    <td>3V3</td>
    <td>3.3V</td> 
  </tr>
  <tr>
    <td>SCL</td>
    <td>SCL</td> 
  </tr>
  <tr>
    <td>SDA</td>
    <td>SDA</td> 
  </tr>
  <tr>
    <td>GND</td>
    <td>GND</td> 
  </tr>
  <tr>
    <td>INT</td>
    <td>any available GPIO</td> 
  </tr>
</table>


## Install
To install the module, open a terminal and run this command:
<br>```sudo pip3 install melopero-RV-3028```
## How to use

Importing the module and device object creation:

```python
import melopero_RV_3028 as mp

rtc = mp.RV_3028()
# Alternatively you can specify which i2c bus and address to use
rtc = mp.RV_3028(i2c_addr=RV_3028_ADDRESS, i2c_bus=1)
```

Setting the time and date:

```python
rtc.set_time(hours=14, minutes=16, seconds=42)
# hours must be an integer in range 0-23
# minutes must be an integer in range 0-59
# seconds must be an integer in range 0-59

rtc.set_date(weekday=6, date=26, month=7, year=20)
# weekday must be an integer in range 0-6
# date must be an integer in range 1-31
# month must be an integer in range 1-12
# year must be an integer in range 0-99
```

**Using invalid values may result in undefined behaviour.**

Reading the time and date:

```python
time = rtc.get_time()
# returns a dictionary containg information about the time

date = rtc.get_date()
# returns a dictionary containg information about the date

datetime = rtc.get_datetime()
# returns a dictionary containg information about the date and time
```

### Use of the alarm interrupt

Prior to entering any timer settings for the Alarm Interrupt, it is recommended to disable the alarm to prevent inadvertent interrupts on the INT pin:

```python
rtc.enable_alarm(enable = False, generate_interrupt = False) 
```

*Note: Disabling the alarm will reset your alarm settings*

You can set the interrupt settings with the following functions:

```python
rtc.set_minute_alarm(42)
rtc.set_hour_alarm(16)
rtc.set_date_alarm(24) # or rtc.set_weekday_alarm(0)
```

Any combination of alarm settings can be used. The table below describes the effect of the combined alarm settings.

|Weekday/Date Alarm   | Hour Alarm  | Minute Alarm  | Alarm Event |
| ------------------- |-------------| --------------| :------: |
| enabled             | enabled     | enabled       | When minutes, hours and weekday/date match (once per weekday/date)|
| enabled             | enabled     | disabled      | When hours and weekday/date match (once per weekday/date)          |
| enabled             | disabled    | enabled       | When minutes and weekday/date match (once per hour per weekday/date) |
| enabled             | disabled    | disabled      | When weekday/date match (once per weekday/date) 1                |
| disabled            | enabled     | enabled       | When hours and minutes match (once per day)                        |
| disabled            | enabled     | disabled      | When hours match (once per day)                                      |
| disabled            | disabled    | enabled       | When minutes match (once per hour)                               |
| disabled            | disabled    | disabled      | All disabled – Default value                                       |

Finally you can activate the alarm :

```python
rtc.enable_alarm(enable = True, generate_interrupt = True) 
```

### Use of the countdown timer

Prior to entering any timer settings for the Timer Interrupt, it is recommended to disable the timer to prevent inadvertent interrupts on the INT pin:

```python
rtc.enable_timer(enable=False, repeat=False, generate_interrupt=False)
```

You can set the timer and interrupt settings with the following functions:

```python
rtc.set_timer(ticks=5, frequency=mp.RV_3028.TIMER_FREQ_1Hz)
rtc.enable_timer(enable=True, repeat=True, generate_interrupt=True)
```

### Use of the user RAM registers

There are two free RAM bytes, which can be used for any purpose. These registers can be accessed with the following functions:

```python 
rtc.read_register(RV_3028.USER_RAM1_ADDRESS) # returns the value stored in the register at address USER_RAM1_ADDRESS (0x1F)
rtc.write_register(RV_3028.USER_RAM2_ADDRESS, 0x42) # writes 0x42 to the register at address USER_RAM2_ADDRESS (0x20)
```

*Note: these functions can be used to read and write to any register of the RAM*

### Use of the EEPROM as user memory
There are 43 Bytes of non-volatile User EEPROM, addresses from 0x00 to 0x2A. To write and read data from these registers you must call the function :

```python 
rtc.use_eeprom(disable_refresh = True) 
```

This function disables the automatic refresh of the device configuration. This happens every 24 hours if the automatic refresh is enabled. 

Then you can read and write to the EEPROM with the following functions:

```python 
rtc.read_eeprom_register(register_address = 0x10) # reads byte in eeprom at address 0x10
rtc.write_eeprom_register(register_address = 0x10, value = 0x42) # writes 0x42 in eeprom at address 0x10 
```

Reading and writing to and from the eeprom might take a bit of time. You can check if the eeprom is busy before executing another read/write operation with the ```is_eeprom_busy()``` function.

If you don't need to read/write anymore to the eeprom and want to enable the automatic configuration refresh you can call the ```use_eeprom(disable_refresh : bool)``` function again:

```python 
rtc.use_eeprom(disable_refresh = False) 
```

### Periodic Time Update

The device triggers an interrupt every second or minute. To set the periodic time update settings you can use the following functions:

```python 
rtc.set_periodic_time_update(second_period=True) # if False sets the period to one minute
rtc.enable_periodic_time_update_interrupt(generate_interrupt=True) # if False disables the hardware interrupt for the periodic time update
```

### Multiple Interrupt sources on the INT pin

There are multiple possible interrupt sources on the rtc : Alarm, Timer, Periodic time update ...

If you want only one interrupt source to generate hardware interrupts disable the other sources:

```python 
rtc.enable_alarm(enable=False, generate_interrupt=False)
rtc.enable_timer(enable=False, repeat=False, generate_interrupt=False)
rtc.enable_periodic_time_update_interrupt(generate_interrupt=False)

rtc.clear_interrupt_flags()
```
