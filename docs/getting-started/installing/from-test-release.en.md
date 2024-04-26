This page explains how to install Krux from a test (beta), pre-built release.

### Warning
Keep in mind that these are unsigned binaries.

### Download
Download experimental compiled firmware or the Android app `apk`: [Krux binaries](https://github.com/odudex/krux_binaries)

#### Android
Krux Android app is intended for learning about Krux and Bitcoin airgapped transactions. Vulnerabilities inherent to Android phones such as the OS, other apps and wireless / CDMA / GSM / Bluetooth connectivity make using any phone insecure. Krux app should NOT be used to manage savings or important keys and mnemonics. For that, a dedicated device is recommended.

#### M5StickV
##### Linux
To Flash M5stickV run:
```bash
./ktool-linux -B goE -b 1500000 maixpy_m5stickv/kboot.kfpkg
```

##### Windows
Replace './ktool-linux' for 'ktool-win.exe' and / for \ in commands:
```pwsh
./ktool-win.exe -B goE -b 1500000 maixpy_m5stickv\kboot.kfpkg
```

#### Sipeed Maix Amigo
##### Linux
To Flash Maix Amigo run:
```bash
./ktool-linux -B goE -b 1500000 maixpy_amigo/kboot.kfpkg
```

##### Windows
Replace './ktool-linux' for 'ktool-win.exe' and / for \ in commands:
```pwsh
./ktool-win.exe -B goE -b 1500000 maixpy_amigo\kboot.kfpkg
```

----8<----
amigo-more-info-faq.en.txt
----8<----

#### Sipeed Maix Bit
##### Linux
To Flash Maix Bit run:
```bash
./ktool-linux -B goE -b 1500000 maixpy_bit/kboot.kfpkg
```

##### Windows
Replace './ktool-linux' for 'ktool-win.exe' and / for \ in commands:
```pwsh
./ktool-win.exe -B goE -b 1500000 maixpy_bit\kboot.kfpkg
```

#### Sipeed Maix Dock
##### Linux
To Flash Maix Dock run:
```bash
./ktool-linux -B dan -b 1500000 maixpy_dock/kboot.kfpkg
```

##### Windows
Replace './ktool-linux' for 'ktool-win.exe' and / for \ in commands:
```pwsh
./ktool-win.exe -B dan -b 1500000 maixpy_dock\kboot.kfpkg
```

#### Aimotion Yahboom k210 module
##### Linux
To Flash Yahboom k210 module you'll have to manually specify the port, on this example `/dev/ttyUSB0`:
```bash
./ktool-linux -B goE -b 1500000 -p /dev/ttyUSB0 yahboom/kboot.kfpkg
```






