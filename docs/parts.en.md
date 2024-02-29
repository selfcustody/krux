**Krux compatible devices comparative table**

| Device | M5stickV | Maix Amigo | Maix Dock | Maix Bit | Yahboom k210 module |
| ------------- | ------------- | ------------- | ------------- | ------------- | ------------- |
| Price avg. | US$50 | US$55 | US$35 | US$35 | US$60 |
| Screen size / resolution | 1.14" / 135*240 | 3.5" / 320*480 | 2.4" / 240*320 | 2.4" / 240*320 | 2" / 240*320 |
| Touchscreen  | :x: | Capacitive | :x: | :x: | Capacitive |
| Camera  | OV7740 | OV7740 rear<br>GC0328 front | GC0328 | OV2640 or<br>OV5642 | OV2640 |
| Battery  | 200mAh | 520mAh | :x: | :x: | :x: |
| Requirements | None | None | [Rotary encoder](https://duckduckgo.com/?q=ky-040)<br> [3D printed case](https://github.com/selfcustody/DockEncoderCase)<br> Soldering<br>Assembly | Buttons<br> [3D printed case](https://github.com/selfcustody/MaixBitCase)<br> Soldering<br>Assembly | None |
| Warnings  | [:material-information:{ title="M5stickV and USB-C" }](#m5stickv-info) |  | [:material-information:{ title="Some stores ship the Maix Dock with soldered pin connectors that do not fit into the 3D printed case" }](#dock-info) |  | Micro USB |

<i style="font-size: 85%">:material-information:{id="m5stickv-info"}:
M5stickV's USB-C port lacks pull up resistors required for it to be recognized and powered by host(computer) USB-C ports. If you don't have an USB-A available, you can use a USB hub connected between your computer's USB-C and M5stick.
</i>

<i style="font-size: 85%">:material-information:{id="dock-info"}:
Some stores ship the Maix Dock with soldered pin connectors that do not fit into the [3D printed case](https://github.com/selfcustody/DockEncoderCase)
</i>

<i style="font-size: 85%">**All devices feature Kendryte K210 chip:**
28nm process, dual-core RISC-V 64bit @400MHz, 8 MB high-speed SRAM, DVP camera and MCU LCD interface, AES Accelerator, SHA256 Accelerator, FFT Accelerator.
</i>

## Devices
### M5StickV
Available from many distributors, including:

- [M5Stack](https://shop.m5stack.com/products/stickv)
- [Adafruit](https://www.adafruit.com/product/4321)
- [Mouser](https://www.mouser.com/c/?q=m5stickv)
- [Digi-Key](https://www.digikey.com/en/products/detail/m5stack-technology-co-ltd/K027/10492135)
- [Lee's Electronic](https://leeselectronic.com/en/product/169940-m5stick-ai-camera-kendryte-k210-risc-v-core-no-wifi.html)
- [Cytron](https://www.cytron.io/c-development-tools/c-fpga/p-m5stickv-k210-ai-camera-without-wifi)
- [OKDO](https://www.okdo.com/p/m5stickv-k210-ai-camera-without-wifi/)

### Maix Amigo
Available from many distributors, including:

- [Seeed Studio](https://www.seeedstudio.com/Sipeed-Maix-Amigo-p-4689.html)
- [Mouser](https://www.mouser.com/c/?q=sipeed)
- [Electromaker](https://www.electromaker.io/shop/search/sipeed)
- [Digi-Key](https://www.digikey.com/en/products/detail/seeed-technology-co-ltd/102110463/13168813)
- [AliExpress](https://www.aliexpress.com/w/wholesale-sipeed-amigo.html)
- [Amazon](https://www.amazon.com/s?k=sipeed+amigo&dc)

### Maix Dock and Maix Bit
For the DIYers, the Maix Dock and Bit are also supported but will require sourcing the parts individually and building the device yourself.

Below are example implementations with instructions on how to recreate them:

- [https://github.com/selfcustody/DockEncoderCase](https://github.com/selfcustody/DockEncoderCase)
- [https://github.com/selfcustody/MaixBitCase](https://github.com/selfcustody/MaixBitCase)

## Ohter parts
### USB-C Charge Cable
This will be included with the M5StickV and Maix Amigo that you purchase from one of the distributors above. It will be necessary to power and charge the device and to initially flash the firmware.

### (Optional) MicroSD Card
We cannot guarantee that a microSD card is compatible and will work in your device; you'll need to test it on the device to be sure, read the [FAQ](faq.md/#why-isnt-krux-detecting-my-microsd-card-or-presenting-an-error) for more info. The size of the SD card isn't important; anything over a few megabytes will be plenty.

### (Optional) Thermal Printer
Krux has the ability to print all QR codes it generates, including mnemonic, xpub, wallet backup and signed PSBT, via a locally-connected thermal printer over its serial port.

Many thermal printers may work, but the [Adafruit printer starter pack](https://www.adafruit.com/product/600) would be the easiest way to get started, as it includes all the parts needed to print (except the conversion cable). Make sure to enable the printer driver and set the baudrate value in [settings](./getting-started/settings.md/#thermal) for 19200 or 9600 as explained in this [Adafruit printer tutorial](https://learn.adafruit.com/mini-thermal-receipt-printer/first-test). You will also need to connect 2 cables, the device TX to the printer RX and ground. For more info, [see this discussion](https://github.com/selfcustody/krux/discussions/312).

### (Optional) Conversion Cable for Thermal Printer
To connect the printer to the device, you will need a [conversion cable](https://store-usa.arduino.cc/products/grove-4-pin-male-to-grove-4-pin-cable-5-pcs) with a 4-pin female Grove connector on one end (to connect to the device) and 4-pin male jumpers on the other end (to connect to the printer).
