# Melopero_RV-3028

## How to use

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

If you don't need to read/write anymore to the eeprom and want to enable the automatic configuration refresh you can call the ```use_eeprom(disable_refresh : bool)``` function again:
```python 
rtc.use_eeprom(disable_refresh = False) 
```