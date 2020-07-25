#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: Leonardo La Rocca
"""

import melopero_RV_3028 as mp
import time

def main():
    # First initialize and create the rtc device
    rtc = mp.RV_3028()

    # setup the rtc to use the eeprom memory (disables the automatic configuration refresh)
    rtc.use_eeprom()

    my_reg_address = 0x00
    my_data = 0x42

    # to write to ram registers you must use rtc.write_register
    # to write to eeprom you must use rtc.write_eeprom_register
    # user eeprom address space : [0x00 - 0x2A]
    # configuration eeprom address space : [0x30 - 0x37]
    rtc.write_eeprom_register(register_address=my_reg_address, value=my_data)

    print("Saved {} at address {} in eeprom".format(my_data, my_reg_address))

    # give some time to execute writing operation
    time.sleep(1)

    # to read from ram registers you must use rtc.read_register
    # to write to eeprom you must use rtc.read_eeprom_register
    # user eeprom address space : [0x00 - 0x2A]
    # configuration eeprom address space : [0x30 - 0x37]
    my_saved_data = rtc.read_eeprom_register(register_address=my_reg_address)

    print("Read {} from eeprom address {}".format(my_saved_data, my_reg_address))


if __name__ == "__main__":
    main()