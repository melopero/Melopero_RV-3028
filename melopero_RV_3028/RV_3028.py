#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: Leonardo La Rocca
"""

from smbus2 import SMBusWrapper

class RV_3028():

    #i2c address
    RV_3028_ADDRESS = 0b1010010

    #control and status
    STATUS_REGISTER_ADDRESS = 0x0E

    CONTROL1_REGISTER_ADDRESS = 0x0F
    CONTROL2_REGISTER_ADDRESS = 0x10

    #register addresses
    SECONDS_REGISTER_ADDRESS = 0x00
    MINUTES_REGISTER_ADDRESS = 0x01
    HOURS_REGISTER_ADDRESS = 0x02
    WEEKDAY_REGISTER_ADDRESS = 0x03
    DATE_REGISTER_ADDRESS = 0x04
    MONTH_REGISTER_ADDRESS = 0x05
    YEAR_REGISTER_ADDRESS = 0x06

    MINUTES_ALARM_REGISTER_ADDRESS = 0x07
    HOURS_ALARM_REGISTER_ADDRESS = 0x08
    WEEKDAY_DATE_ALARM_REGISTER_ADDRESS = 0x09

    def __init__(self, i2c_addr=RV_3028_ADDRESS, i2c_bus=1):
        self.i2c_address = i2c_addr
        self.i2c_bus = i2c_bus

    def read_register(self, reg_address: int) -> int:
        with SMBusWrapper(self.i2c_bus) as bus:
            return bus.read_byte_data(self.i2c_address, reg_address)

    def read_registers(self, start_reg_address : int, amount : int) -> list:
        with SMBusWrapper(self.i2c_bus) as bus:
            return bus.read_i2c_block_data(self.i2c_address, start_reg_address, amount)

    def write_register(self, reg_address: int, value: int) -> None:
        with SMBusWrapper(self.i2c_bus) as bus:
            bus.write_byte_data(self.i2c_address, reg_address, value)

    def and_or_register(self, reg_address : int, and_flag : int, or_flag : int) -> None:
        regval = self.read_register(reg_address)
        regval &= and_flag
        regval |= or_flag
        self.write_register(reg_address, regval)

    def _bcd_to_dec(self, bcd : int) -> int:
        '''
        :param bcd: 8 bit value expressed in binary coded decimal
        :return: the value converted in decimal format
        '''
        return (bcd / 0x10 * 10) + (bcd % 0x10)

    def _dec_to_bcd(self, dec : int) -> int:
        '''
        :param dec: 8 bit value expressed in decimal
        :return: the value converted in binary coded decimal format
        '''
        return ((dec / 10) << 4) ^ (dec % 10)

    def is_using_12h_mode(self) -> bool:
        return bool(self.read_register(RV_3028.CONTROL2_REGISTER_ADDRESS) & 0x02)

    def set_12h_format(self, enable_12h_format = True) -> None:
        and_val = 0xFF if enable_12h_format else ~ 0x02
        or_val = 0x02 if enable_12h_format else 0
        self.and_or_register(RV_3028.CONTROL2_REGISTER_ADDRESS, and_val, or_val)

    def get_time(self) -> dict:
        '''
        :return: a dictionary containing the current time (seconds : minutes : hours)
        '''
        keys = ['s', 'm', 'h']
        values = [self._bcd_to_dec(bcd_byte) for bcd_byte in self.read_registers(RV_3028.SECONDS_REGISTER_ADDRESS, 2)]
        #reading hour
        hour_bcd = self.read_register(RV_3028.HOURS_REGISTER_ADDRESS)
        if self.is_using_12h_mode():
            # ampm hour value
            values.append(self._bcd_to_dec(hour_bcd & 0x1F))
            # period
            keys.append('period')
            values.append('pm' if hour_bcd & 0x20 else 'am')
        else :
            values.append(self._bcd_to_dec(hour_bcd))

        return dict(zip(keys, values))

    def get_date(self) -> dict:
        '''
        :return: a dictionary containing the current date (weekday : date : month : year)
        '''
        dec_bytes = [self._bcd_to_dec(bcd_byte) for bcd_byte in self.read_registers(RV_3028.WEEKDAY_REGISTER_ADDRESS, 4)]
        return dict(zip['weekday', 'date', 'month', 'year'], dec_bytes)

    def get_datetime(self) -> dict:
        '''
        :return: a Dictionary containing the current date and time
        '''
        datetime = self.get_time()
        datetime.update(self.get_date())
        return datetime
    
    def set_minute_alarm(self, minute : int, enable = True) -> None:
        '''
        :param minute: the minute the alarm will trigger
        :param enable: if false disables the alarm
        :return:
        '''
        bcd_minute = self._dec_to_bcd(minute) | ((not enable) << 7)
        self.write_register(RV_3028.MINUTES_ALARM_REGISTER_ADDRESS, bcd_minute)
    
    def set_hour_alarm_24h_format(self, hour : int, enable = True) -> None:
        '''
        Sets the hour for the alarm in 24h format, set the device to use the 24h format before setting the
        alarm with this function.
        :param hour: the hour expressed in 24 hour format
        :param enable: if false disables the alarm
        :return:
        '''
        bcd_hour = self._dec_to_bcd(hour) | ((not enable) << 7)
        self.write_register(RV_3028.HOURS_ALARM_REGISTER_ADDRESS, bcd_hour)

    def set_hour_alarm_12h_format(self, hour : int, pm : bool, enable = True):
        '''
        Sets the hour for the alarm in 12h format, set the device to use the 12h format before setting the
        alarm with this function.
        :param hour: the hour expressed in 12 hour format
        :param pm: the period
        :param enable: if false disables the alarm
        :return:
        '''
        bcd_hour = self._dec_to_bcd(hour) | (pm << 5) | ((not enable) << 7)
        self.write_register(RV_3028.HOURS_ALARM_REGISTER_ADDRESS, bcd_hour)

    def set_date_alarm(self, date : int, enable = True) -> None:
        '''
        Sets the date for the alarm. The weekday for the alarm (if set) will be overwritten and not used anymore.
        :param date: the date expressed as an integer in range 1 to 31
        :param enable: if false disables the alarm
        :return:
        '''
        #set the WADA bit to 1 for date alarm
        self.and_or_register(RV_3028.CONTROL2_REGISTER_ADDRESS, 0xFF, 0x20)
        bcd_date = self._dec_to_bcd(date) | ((not enable) << 7)
        self.write_register(RV_3028.WEEKDAY_DATE_ALARM_REGISTER_ADDRESS, bcd_date)

    def set_weekday_alarm(self, weekday : int, enable = True) -> None:
        '''
        Sets the weekday for the alarm. The date for the alarm (if set) will be overwritten and not used anymore.
        :param weekday: the weekday expressed as an integer in range 0 to 6
        :param enable:
        :return:
        '''
        #set the WADA bit to 0 for weekday alarm
        self.and_or_register(RV_3028.CONTROL2_REGISTER_ADDRESS, ~0x20, 0)
        bcd_weekday = self._dec_to_bcd(weekday) | ((not enable) << 7)
        self.write_register(RV_3028.WEEKDAY_DATE_ALARM_REGISTER_ADDRESS, bcd_weekday)

    def set_alarm(self, enable : bool, generate_interrupt : bool) -> None:
        '''
        Enables/Disables the alarm.
        :param enable: if False disables/resets all alarm settings.
        :param generate_interrupt: if True the alarm will trigger an interrupt on the INT pin.
        :return:
        '''
        # reset AF bit in STATUS reg
        self.and_or_register(RV_3028.STATUS_REGISTER_ADDRESS, ~0x04, 0)
        if enable:
            if generate_interrupt:
                #enable AIE bit in CONTROL 2 reg
                self.and_or_register(RV_3028.CONTROL2_REGISTER_ADDRESS, 0xFF, 0x08)
        else:
            #disable AIE bit in CONTROL 2 reg
            self.and_or_register(RV_3028.CONTROL2_REGISTER_ADDRESS, ~0x08, 0)
            #disable all alarm flags
            self.set_minute_alarm(0, False)
            self.set_hour_alarm_24h_format(0, False)
            self.set_date_alarm(0, False)
