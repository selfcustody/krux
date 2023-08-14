This page explains how to install Krux from an test, pre-built release.

### Warning

Keep in mind that these are unsigned binaries

### Download
Download experimental compiled firmware or Android app: [Krux binaries](https://github.com/odudex/krux_binaries)

#### Android

Krux Android app is intended for learning about Krux and Bitcoin air-gapped transactions. Vulnerabilities inherent in Android phones such as the OS, other apps and wireless connectivity make using any phone insecure. Krux app should NOT be used to manage savings or important keys and mnemonics. For that, a dedicated device is recommended.

#### M5StickV

##### Linux

To Flash M5stickV run:

```bash
./ktool-linux -B goE -b 1500000 maixpy_m5stickv/kboot.kfpkg
```

##### Windows

Replace './ktool-linux' for 'ktool-win.exe' and / for \ in commands. Ex:

```pwsh
./ktool-win.exe -B goE -b 1500000 maixpy_m5stickv\kboot.kfpkg
```

#### Sipeed Amigo TFT

##### Linux
To Flash Maix Amigo run:

```bash
./ktool-linux -B goE -b 1500000 maixpy_amigo_tft/kboot.kfpkg
```

##### Windows

Replace './ktool-linux' for 'ktool-win.exe' and / for \ in commands. Ex:

```pwsh
./ktool-win.exe -B goE -b 1500000 maixpy_amigo_ips\kboot.kfpkg
```

#### Sipeed Amigo IPS

##### Linux

If your Amigo got flipped character position on keypads and switched Yes/No questions try the IPS version:

```bash
./ktool-linux -B goE -b 1500000 maixpy_amigo_ips/kboot.kfpkg
```

##### Windows

Replace './ktool-linux' for 'ktool-win.exe' and / for \ in commands. Ex:

```pwsh
./ktool-win.exe -B goE -b 1500000 maixpy_amigo_tft\kboot.kfpkg
```

#### Sipeed Bit

##### Linux

To Flash Maix Dock run:

```bash
./ktool-linux -B goE -b 1500000 maixpy_bit/kboot.kfpkg
```

##### Windows

Replace './ktool-linux' for 'ktool-win.exe' and / for \ in commands. Ex:

```pwsh
./ktool-win.exe -B goE -b 1500000 maixpy_bit\kboot.kfpkg
```

#### Sipeed Dock

##### Linux

To Flash Maix Dock run:

```bash
./ktool-linux -B goE -b 1500000 maixpy_dock/kboot.kfpkg
```

##### Windows

Replace './ktool-linux' for 'ktool-win.exe' and / for \ in commands. Ex:

```pwsh
./ktool-win.exe -B goE -b 1500000 maixpy_dock\kboot.kfpkg
```

#### Aimotion Yahboom

##### Linux

To Flash Yahboom Aimotion you'll have to manually specify the port, on this example /dev/ttyUSB0:

```bash
./ktool-linux -B goE -b 1500000 -p /dev/ttyUSB0 yahboom/kboot.kfpkg
```






