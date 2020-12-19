#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: Leonardo La Rocca
"""

from smbus2 import SMBus


class RV_3028():
    # i2c address
    RV_3028_ADDRESS = 0b1010010

    # control and status
    STATUS_REGISTER_ADDRESS = 0x0E

    CONTROL1_REGISTER_ADDRESS = 0x0F
    CONTROL2_REGISTER_ADDRESS = 0x10

    # register addresses
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

    TIMER_VALUE_0_ADDRESS = 0x0A
    TIMER_VALUE_1_ADDRESS = 0x0B

    TIMER_STATUS_0_ADDRESS = 0x0C
    TIMER_STATUS_1_ADDRESS = 0x0D

    TIMER_FREQ_4096Hz = 0
    '''period 244.14 microseconds'''
    TIMER_FREQ_64Hz = 1
    '''period 15.625 milliseconds '''
    TIMER_FREQ_1Hz = 2
    '''period 1 second'''
    TIMER_FREQ_1_60Hz = 3
    '''period 60 seconds'''

    USER_RAM1_ADDRESS = 0x1F
    USER_RAM2_ADDRESS = 0x20

    EEPROM_ADDRESS_ADDRESS = 0x25
    EEPROM_DATA_ADDRESS = 0x26
    EEPROM_COMMAND_ADDRESS = 0x27

    UNIX_TIME_ADDRESS = 0x1B

    def __init__(self, i2c_addr=RV_3028_ADDRESS, i2c_bus=1):
        self.i2c_address = i2c_addr
        self.i2c_bus = i2c_bus

    def read_register(self, reg_address: int) -> int:
        with SMBus(self.i2c_bus) as bus:
            return bus.read_byte_data(self.i2c_address, reg_address)

    def read_registers(self, start_reg_address: int, amount: int) -> list:
        with SMBus(self.i2c_bus) as bus:
            return bus.read_i2c_block_data(self.i2c_address, start_reg_address, amount)

    def write_register(self, reg_address: int, value: int) -> None:
        with SMBus(self.i2c_bus) as bus:
            bus.write_byte_data(self.i2c_address, reg_address, value)

    def and_or_register(self, reg_address: int, and_flag: int, or_flag: int) -> None:
        regval = self.read_register(reg_address)
        regval &= and_flag
        regval |= or_flag
        self.write_register(reg_address, regval)

    def _bcd_to_dec(self, bcd: int) -> int:
        """
        :param bcd: 8 bit value expressed in binary coded decimal
        :return: the value converted in decimal format
        """
        return (bcd // 0x10 * 10) + (bcd % 0x10)

    def _dec_to_bcd(self, dec: int) -> int:
        """
        :param dec: 8 bit value expressed in decimal
        :return: the value converted in binary coded decimal format
        """
        return ((dec // 10) << 4) ^ (dec % 10)

    def is_using_12h_mode(self) -> bool:
        return bool(self.read_register(RV_3028.CONTROL2_REGISTER_ADDRESS) & 0x02)

    def set_12h_format(self, enable_12h_format=True) -> None:
        and_val = 0xFF if enable_12h_format else ~ 0x02
        or_val = 0x02 if enable_12h_format else 0
        self.and_or_register(RV_3028.CONTROL2_REGISTER_ADDRESS, and_val, or_val)

    def get_time(self) -> dict:
        """
        :return: a dictionary containing the current time (seconds : minutes : hours)
        """
        keys = ['s', 'm', 'h']
        values = [self._bcd_to_dec(bcd_byte) for bcd_byte in self.read_registers(RV_3028.SECONDS_REGISTER_ADDRESS, 2)]
        # reading hour
        hour_bcd = self.read_register(RV_3028.HOURS_REGISTER_ADDRESS)
        if self.is_using_12h_mode():
            # ampm hour value
            values.append(self._bcd_to_dec(hour_bcd & 0x1F))
            # period
            keys.append('period')
            values.append('pm' if hour_bcd & 0x20 else 'am')
        else:
            values.append(self._bcd_to_dec(hour_bcd))

        return dict(zip(keys, values))

    def set_time(self, hours: int, minutes: int, seconds: int = -1) -> None:
        """
        :param hours: must be an integer in range 0-23
        :param minutes: must be an integer in range 0-59
        :param seconds: must be an integer in range 0-59
        :return:
        """
        hours_bcd = self._dec_to_bcd(hours)
        if self.is_using_12h_mode():
            self.set_12h_format(False)
            self.write_register(RV_3028.HOURS_REGISTER_ADDRESS, hours_bcd)
            self.set_12h_format(True)
        else:
            self.write_register(RV_3028.HOURS_REGISTER_ADDRESS, hours_bcd)

        minutes_bcd = self._dec_to_bcd(minutes)
        self.write_register(RV_3028.MINUTES_REGISTER_ADDRESS, minutes_bcd)

        if seconds > -1:
            seconds_bcd = self._dec_to_bcd(seconds)
            self.write_register(RV_3028.SECONDS_REGISTER_ADDRESS, seconds_bcd)

    def get_date(self) -> dict:
        """
        :return: a dictionary containing the current date (weekday : date : month : year)
        """
        dec_bytes = [self._bcd_to_dec(bcd_byte) for bcd_byte in
                     self.read_registers(RV_3028.WEEKDAY_REGISTER_ADDRESS, 4)]
        return dict(zip(['weekday', 'date', 'month', 'year'], dec_bytes))

    def set_date(self, weekday: int, date: int, month: int, year: int) -> None:
        """
        :param weekday: must be an integer in range 0-6
        :param date: must be an integer in range 1-31
        :param month: must be an integer in range 1-12
        :param year: must be an integer in range 0-99
        :return:
        """
        self.write_register(RV_3028.WEEKDAY_REGISTER_ADDRESS, self._dec_to_bcd(weekday))
        self.write_register(RV_3028.DATE_REGISTER_ADDRESS, self._dec_to_bcd(date))
        self.write_register(RV_3028.MONTH_REGISTER_ADDRESS, self._dec_to_bcd(month))
        self.write_register(RV_3028.YEAR_REGISTER_ADDRESS, self._dec_to_bcd(year))

    def get_datetime(self) -> dict:
        """
        :return: a Dictionary containing the current date and time
        """
        datetime = self.get_time()
        datetime.update(self.get_date())
        return datetime

    def set_minute_alarm(self, minute: int, enable=True) -> None:
        """
        :param minute: the minute the alarm will trigger
        :param enable: if false disables the alarm
        :return:
        """
        bcd_minute = self._dec_to_bcd(minute) | ((not enable) << 7)
        self.write_register(RV_3028.MINUTES_ALARM_REGISTER_ADDRESS, bcd_minute)

    def set_hour_alarm_24h_format(self, hour: int, enable=True) -> None:
        """
        Sets the hour for the alarm in 24h format, set the device to use the 24h format before setting the
        alarm with this function.

        :param hour: the hour expressed in 24 hour format
        :param enable: if false disables the alarm
        :return:
        """
        bcd_hour = self._dec_to_bcd(hour) | ((not enable) << 7)
        self.write_register(RV_3028.HOURS_ALARM_REGISTER_ADDRESS, bcd_hour)

    def set_hour_alarm_12h_format(self, hour: int, pm: bool, enable=True):
        """
        Sets the hour for the alarm in 12h format, set the device to use the 12h format before setting the
        alarm with this function.

        :param hour: the hour expressed in 12 hour format
        :param pm: the period
        :param enable: if false disables the alarm
        :return:
        """
        bcd_hour = self._dec_to_bcd(hour) | (pm << 5) | ((not enable) << 7)
        self.write_register(RV_3028.HOURS_ALARM_REGISTER_ADDRESS, bcd_hour)

    def set_date_alarm(self, date: int, enable=True) -> None:
        """
        Sets the date for the alarm. The weekday for the alarm (if set) will be overwritten and not used anymore.

        :param date: the date expressed as an integer in range 1 to 31
        :param enable: if false disables the alarm
        :return:
        """
        # set the WADA bit to 1 for date alarm
        self.and_or_register(RV_3028.CONTROL2_REGISTER_ADDRESS, 0xFF, 0x20)
        bcd_date = self._dec_to_bcd(date) | ((not enable) << 7)
        self.write_register(RV_3028.WEEKDAY_DATE_ALARM_REGISTER_ADDRESS, bcd_date)

    def set_weekday_alarm(self, weekday: int, enable=True) -> None:
        """
        Sets the weekday for the alarm. The date for the alarm (if set) will be overwritten and not used anymore.

        :param weekday: the weekday expressed as an integer in range 0 to 6
        :param enable:
        :return:
        """
        # set the WADA bit to 0 for weekday alarm
        self.and_or_register(RV_3028.CONTROL2_REGISTER_ADDRESS, ~0x20, 0)
        bcd_weekday = self._dec_to_bcd(weekday) | ((not enable) << 7)
        self.write_register(RV_3028.WEEKDAY_DATE_ALARM_REGISTER_ADDRESS, bcd_weekday)

    def enable_alarm(self, enable: bool, generate_interrupt: bool) -> None:
        """
        Enables/Disables the alarm.

        :param enable: if False disables/resets all alarm settings.
        :param generate_interrupt: if True the alarm will trigger an interrupt on the INT pin.
        :return:
        """
        # TODO: replace if else statements with bit operations

        # reset AF bit in STATUS reg
        self.and_or_register(RV_3028.STATUS_REGISTER_ADDRESS, ~0x04, 0)
        if enable:
            if generate_interrupt:
                # enable AIE bit in CONTROL 2 reg
                self.and_or_register(RV_3028.CONTROL2_REGISTER_ADDRESS, 0xFF, 0x08)
            else:
                # disable AIE bit in CONTROL 2 reg
                self.and_or_register(RV_3028.CONTROL2_REGISTER_ADDRESS, ~0x08, 0)
        else:
            # disable AIE bit in CONTROL 2 reg
            self.and_or_register(RV_3028.CONTROL2_REGISTER_ADDRESS, ~0x08, 0)
            # disable all alarm flags
            self.set_minute_alarm(0, False)
            self.set_hour_alarm_24h_format(0, False)
            self.set_date_alarm(0, False)

    def set_timer(self, ticks: int, frequency: int) -> None:
        """
        Sets the timer parameters.

        :param ticks: the amount of ticks to countdown
        :param frequency: the frequency of the ticks. Must be one of TIMER_FREQ_X
        :return:
        """
        value_lsb = ticks & 0xFF
        value_msb = (ticks >> 8) & 0xFF
        self.write_register(RV_3028.TIMER_VALUE_0_ADDRESS, value_lsb)
        self.write_register(RV_3028.TIMER_VALUE_1_ADDRESS, value_msb)
        self.and_or_register(RV_3028.CONTROL1_REGISTER_ADDRESS, 0x3F << 2 | frequency, frequency)

    def enable_timer(self, enable: bool, repeat: bool, generate_interrupt: bool) -> None:
        """
        Enables/Disables the timer. The timer settings must be set before calling this function.

        :param enable: if true starts the timer
        :param repeat: if true the timer will repeat on end
        :param generate_interrupt: if true an interrupt will be triggered on the INT pin when the timer ends
        :return:
        """
        # TODO: replace if else statements with bit operations
        if not enable:
            # disable TE bit to disable the timer
            self.and_or_register(RV_3028.CONTROL1_REGISTER_ADDRESS, 0xFB, 0)
            # disable TIE bit to disable the timer interrupt
            self.and_or_register(RV_3028.CONTROL2_REGISTER_ADDRESS, 0xEF, 0)

        # reset the TF bit
        self.and_or_register(RV_3028.STATUS_REGISTER_ADDRESS, 0xF7, 0)
        # enable/disable TRPT
        if repeat:
            self.and_or_register(RV_3028.CONTROL1_REGISTER_ADDRESS, 0xFF, 0x80)
        else:
            self.and_or_register(RV_3028.CONTROL1_REGISTER_ADDRESS, 0x7F, 0)

        if enable:
            # enable/disable interrupt
            if generate_interrupt:
                self.and_or_register(RV_3028.CONTROL2_REGISTER_ADDRESS, 0xFF, 0x10)
            else:
                self.and_or_register(RV_3028.CONTROL2_REGISTER_ADDRESS, 0xEF, 0)
            # start timer
            self.and_or_register(RV_3028.CONTROL1_REGISTER_ADDRESS, 0xFF, 0x04)

    def get_timer_status(self) -> int:
        """
        When the timer is running (enabled), this function returns the remaining countdown ticks.
        When the timer is not running (disabled), this function returns the last updated ticks value.

        :return: an int representing the remaining ticks of the timer or the last ticks set.
        """
        values = self.read_registers(RV_3028.TIMER_STATUS_0_ADDRESS, 2)
        return values[1] << 8 | values[0]

    def set_periodic_time_update(self, second_period=True):
        """
        Sets the periodic time update settings.

        :param second_period: if True the periodic time update triggers every second. If False it triggers every minute.
        :return:
        """
        if second_period:
            self.and_or_register(RV_3028.CONTROL1_REGISTER_ADDRESS, 0xEF, 0)
        else:
            self.and_or_register(RV_3028.CONTROL1_REGISTER_ADDRESS, 0xFF, 0x10)

    def enable_periodic_time_update_interrupt(self, generate_interrupt=True):
        """

        :param generate_interrupt:
        :return:
        """
        # TODO: replace if else statements with bit operations
        if generate_interrupt:
            self.and_or_register(RV_3028.CONTROL2_REGISTER_ADDRESS, 0xFF, 0x20)
        else:
            self.and_or_register(RV_3028.CONTROL2_REGISTER_ADDRESS, 0xDF, 0)

    def clear_interrupt_flags(self, clear_timer_flag=True, clear_alarm_flag=True, clear_periodic_time_update_flag=True):
        """
        Clears the timer and alarm interrupt flags in the status register.

        :param clear_timer_flag:
        :param clear_alarm_flag:
        :param clear_periodic_time_update_flag:
        :return:
        """
        mask = 0xFF
        mask &= 0xF7 if clear_timer_flag else 0xFF
        mask &= 0xFB if clear_alarm_flag else 0xFF
        mask &= 0xEF if clear_periodic_time_update_flag else 0xFF
        self.and_or_register(RV_3028.STATUS_REGISTER_ADDRESS, mask, 0)

    #def set_interrupt_mask(self, event_interrupt: bool, alarm_interrupt: bool, periodic_countdown_interrupt: bool,
    #                       periodic_time_update_interrupt: bool) -> None:
    #    pass
    #    # TODO: implement interrupt mask

    def get_unix_time(self) -> int:
        """
        UNIX Time counter is a 32-bit counter. The counter will roll-over to 00000000h when reaching FFFFFFFFh.

        :return:
        """
        time_bytes = self.read_registers(RV_3028.UNIX_TIME_ADDRESS, 4)
        return time_bytes[3] << 24 | time_bytes[2] << 16 | time_bytes[1] << 8 | time_bytes[0]

    def use_eeprom(self, disable_refresh=True) -> None:
        """
        Sets up the device to read/write from/to the eeprom memory. The automatic refresh function has to be disabled.

        :param disable_refresh: disables/enables the automatic refresh function
        :return:
        """
        # TODO: replace if else statement with bit operations
        if disable_refresh:
            self.and_or_register(RV_3028.CONTROL1_REGISTER_ADDRESS, 0xFF, 0x08)
            self.write_register(RV_3028.EEPROM_COMMAND_ADDRESS, 0)
        else:
            self.and_or_register(RV_3028.CONTROL1_REGISTER_ADDRESS, 0xF7, 0)

    def read_eeprom_register(self, register_address: int) -> int:
        """
        Reads an eeprom register and returns its content.
        user eeprom address space : [0x00 - 0x2A]
        configuration eeprom address space : [0x30 - 0x37]

        :param register_address: the register value
        :return:
        """
        self.write_register(RV_3028.EEPROM_ADDRESS_ADDRESS, register_address)
        while self.is_eeprom_busy():
            continue
        # read a register -> eeprom data = 0x22
        self.write_register(RV_3028.EEPROM_COMMAND_ADDRESS, 0x22)
        return self.read_register(RV_3028.EEPROM_DATA_ADDRESS)

    def write_eeprom_register(self, register_address: int, value: int) -> None:
        """
        Writes value to the eeprom register at address register_address.
        user eeprom address space : [0x00 - 0x2A]
        configuration eeprom address space : [0x30 - 0x37]

        :param register_address: the address of the eeprom register
        :param value: the value to write
        :return:
        """
        self.write_register(RV_3028.EEPROM_ADDRESS_ADDRESS, register_address)
        self.write_register(RV_3028.EEPROM_DATA_ADDRESS, value)
        while self.is_eeprom_busy():
            continue
        # write to a register in eeprom = 0x21
        self.write_register(RV_3028.EEPROM_COMMAND_ADDRESS, 0x21)

    def is_eeprom_busy(self) -> bool:
        return bool(self.read_register(RV_3028.STATUS_REGISTER_ADDRESS) & 0x80)
