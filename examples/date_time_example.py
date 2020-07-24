#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: Leonardo La Rocca
"""

import melopero_RV_3028 as mp


def main():
    rtc = mp.RV_3028()
    print(rtc.get_time())

if __name__ == "__main__":
    main()