# Requirements
https://github.com/sipeed/MaixPy/blob/master/build.md#install-dependencies
https://github.com/sipeed/MaixPy/blob/master/build.md#download-toolchain

# Building
We use a custom build of the `maixpy_m5stickv` firmware.

```bash
cd MaixPy/projects/maixpy_m5stickv
python3 project.py clean && python3 project.py distclean
python3 project.py menuconfig
python3 project.py build
```

If everything worked, a custom build of the firmware should be available at `./build/maixpy.bin`

# Installing
First, plug in the device via its USB-C port, then locate it with:

```bash
ls -lha /dev/tty* | grep usb
```

Once the device path is found, for example `/dev/tty.usbserial-123`, run the following
to install the firmware you built in the previous step:

```bash
python3 project.py -B goE -p /dev/tty.usbserial-123 -b 1500000 -S flash
```