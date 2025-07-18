This page explains how to install Krux from a test (beta), pre-built release.

### Warning
Keep in mind that these are unsigned binaries.

### Download
Download experimental compiled firmware at [test (beta) repository](https://github.com/odudex/krux_binaries) or the Mobile Android app `apk` at [KruxMobileApp](https://github.com/selfcustody/KruxMobileApp).

#### Mobile - Android
The [Krux Mobile Android app](../../faq.md#what-is-krux-mobile-android-app) is designed for learning about Krux and Bitcoin air-gapped transactions. Due to the numerous potential vulnerabilities inherent in smartphones, such as the lack of control over the operating system, libraries, and hardware peripherals, the Krux app should NOT be used to manage wallets containing savings or important keys and mnemonics. For secure management of your keys, a dedicated device is recommended.

#### Compiled firmware for Kendryte K210 devices
#### M5StickV
To Flash M5StickV run the following.

##### Linux
```bash
./ktool-linux -B goE -b 1500000 maixpy_m5stickv/kboot.kfpkg
```

##### Mac
```bash
./ktool-mac -B goE -b 1500000 maixpy_m5stickv/kboot.kfpkg
```

##### Windows
```pwsh
.\ktool-win.exe -B goE -b 1500000 maixpy_m5stickv\kboot.kfpkg
```

#### Sipeed Maix Amigo
To Flash Maix Amigo run the following.

##### Linux
```bash
./ktool-linux -B goE -b 1500000 maixpy_amigo/kboot.kfpkg
```

##### Mac
```bash
./ktool-mac -B goE -b 1500000 maixpy_amigo/kboot.kfpkg
```

##### Windows
```pwsh
.\ktool-win.exe -B goE -b 1500000 maixpy_amigo\kboot.kfpkg
```

----8<----
amigo-more-info-faq.en.txt
----8<----

#### Sipeed Maix Bit
To Flash Maix Bit run the following.

##### Linux
```bash
./ktool-linux -B goE -b 1500000 maixpy_bit/kboot.kfpkg
```

##### Mac
```bash
./ktool-mac -B goE -b 1500000 maixpy_bit/kboot.kfpkg
```

##### Windows
```pwsh
.\ktool-win.exe -B goE -b 1500000 maixpy_bit\kboot.kfpkg
```

#### Sipeed Maix Cube
To Flash Maix Cube run the following.

##### Linux
```bash
./ktool-linux -B goE -b 1500000 maixpy_cube/kboot.kfpkg
```

##### Mac
```bash
./ktool-mac -B goE -b 1500000 maixpy_cube/kboot.kfpkg
```

##### Windows
```pwsh
.\ktool-win.exe -B goE -b 1500000 maixpy_cube\kboot.kfpkg
```

#### Sipeed Maix Dock
To Flash Maix Dock you need to pass the `-B dan` parameter.

##### Linux
```bash
./ktool-linux -B dan -b 1500000 maixpy_dock/kboot.kfpkg
```

##### Mac
```bash
./ktool-mac -B dan -b 1500000 maixpy_dock/kboot.kfpkg
```

##### Windows
```pwsh
.\ktool-win.exe -B dan -b 1500000 maixpy_dock\kboot.kfpkg
```

#### Aimotion Yahboom k210 module
To Flash Yahboom k210 module you'll have to manually specify the port.

##### Linux
See the correct port using `ls /dev/ttyUSB*`, in the example below we use `/dev/ttyUSB0`:
```bash
./ktool-linux -B goE -b 1500000 -p /dev/ttyUSB0 maixpy_yahboom/kboot.kfpkg
```

##### Mac
See the correct port using the command line: `ls /dev/cu.usbserial*`, in the example below we use `/dev/cu.usbserial-10`:
```bash
./ktool-mac -B goE -b 1500000 -p /dev/cu.usbserial-10 maixpy_yahboom/kboot.kfpkg
```

##### Windows
See the correct port at **Device Manager -> Ports (COM & LPT)**, in the example below we use `COM6`:
```pwsh
.\ktool-win.exe -B goE -b 1500000 -p COM6 maixpy_yahboom\kboot.kfpkg
```

#### Hiwonder WonderMV Vision Recognition Module
To Flash WonderMV you need to pass the `-B dan` parameter.

##### Linux
```bash
./ktool-linux -B dan -b 1500000 maixpy_wonder_mv/kboot.kfpkg
```

##### Mac
```bash
./ktool-mac -B dan -b 1500000 maixpy_wonder_mv/kboot.kfpkg
```

##### Windows
```pwsh
.\ktool-win.exe -B dan -b 1500000 maixpy_wonder_mv\kboot.kfpkg
```
