#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: Leonardo La Rocca
"""

import melopero_RV_3028 as mp
import datetime
import time


def main():
    # First initialize and create the rtc device
    rtc = mp.RV_3028()
    # Set the device to use the 24hour format (default) instead of the 12 hour format
    rtc.set_12h_format(False)

    # Then set the date and time.
    # retrieve the datetime from the library datetime
    current_datetime = datetime.datetime.now()

    # set the date and time for the device
    rtc.set_time(current_datetime.hour, current_datetime.minute, current_datetime.second)
    rtc.set_date(current_datetime.weekday(), current_datetime.day, current_datetime.month, current_datetime.year % 2000)

    # print datetime to make sure everything works
    print(rtc.get_datetime())

    # print datetime every 10 seconds (for 10 times)
    for i in range(10):
        time.sleep(10)
        print(rtc.get_datetime())


if __name__ == "__main__":
    main()
