#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: Leonardo La Rocca
"""

import melopero_RV_3028 as mp
import datetime
import time

def main():
    rtc = mp.RV_3028()
    current_datetime = datetime.datetime.now()
    rtc.set_time(current_datetime.hour, current_datetime.minute, current_datetime.second)
    rtc.set_date(current_datetime.weekday(), current_datetime.day, current_datetime.month, current_datetime.year % 2000)
    print(rtc.get_datetime())
    for i in range(10):
        time.sleep(.99)
        print(rtc.get_datetime())

if __name__ == "__main__":
    main()