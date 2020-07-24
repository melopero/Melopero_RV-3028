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
    print(rtc.get_time())
    time.sleep(3)
    print(rtc.get_time())

if __name__ == "__main__":
    main()