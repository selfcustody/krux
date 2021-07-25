#!/bin/sh
set -e

if [ "$1" == "build" ]; then
    mkdir -p MaixPy/projects/maixpy_m5stickv/build
    docker build . -t krux-firmware
    docker cp $(docker create krux-firmware):/src/MaixPy/projects/maixpy_m5stickv/build/maixpy.bin MaixPy/projects/maixpy_m5stickv/build/maixpy.bin
fi

if [ "$1" == "flash" ]; then
    cd MaixPy/projects/maixpy_m5stickv
    python3 project.py -B goE -p "$2" -b 1500000 -S flash
fi