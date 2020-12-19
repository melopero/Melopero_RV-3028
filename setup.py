#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: Leonardo La Rocca
"""
from setuptools import setup

setup(
    name='melopero_RV-3028',
    version='0.1.1',
    packages=['melopero_RV_3028'],
    url='https://github.com/melopero/Melopero_RV-3028',
    license='MIT',
    author='Leonardo La Rocca',
    author_email='info@melopero.com',
    description='A module to easily access the RV-3028 rtc features.',
    install_requires=["smbus2>=0.4"]
)
