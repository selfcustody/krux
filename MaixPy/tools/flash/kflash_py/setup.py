#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import (division, print_function)

from setuptools import setup, find_packages

setup(
    name='kflash',
    py_modules=['kflash'],
    version='0.8.3',
    description=(
        'Kendryte UART ISP Utility - programming code to k210'
    ),
    long_description=open('README.rst').read(),
    long_description_content_type='text/x-rst',
    author='https://github.com/kendryte/kflash.py/graphs/contributors',
    author_email='auto@canaan-creative.com',
    maintainer='Huang Rui',
    maintainer_email='vowstar@gmail.com',
    license='MIT License',
    packages=find_packages(),
    platforms=["all"],
    url='https://github.com/kendryte/kflash.py',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Operating System :: OS Independent',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Environment :: Console',
        'Natural Language :: English',
        'Programming Language :: Python',
        'Programming Language :: Python :: Implementation',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Topic :: Software Development :: Embedded Systems'
    ],
    install_requires=[
        'pyserial>=3.4',
        'pyelftools>=0.25',
        'enum34>=1.1.6',
    ],
    entry_points={
        'console_scripts': [
            'kflash = kflash:main',
        ]
    },
)
