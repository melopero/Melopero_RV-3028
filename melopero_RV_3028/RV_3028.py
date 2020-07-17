#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: Leonardo La Rocca
"""

from smbus2 import SMBusWrapper


class RV_3028():

    def __init__(self, i2c_addr=0b1010010, i2c_bus=1):
        self.i2c_address = i2c_addr
        self.i2c_bus = i2c_bus

    def read_register(self, reg_address: int):
        with SMBusWrapper(self.i2c_bus) as bus:
            return bus.read_byte_data(self.i2c_address, reg_address)

    def write_register(self, reg_address: int, value: int):
        with SMBusWrapper(self.i2c_bus) as bus
            bus.write_byte_data(self.i2c_address, reg_address, value)
