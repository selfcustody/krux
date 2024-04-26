## Krux Compatible Devices
<img src="../img/krux-devices.jpg">

### Comparative Table

| Device | M5stickV | Maix Amigo | Maix Dock | Maix Bit | Yahboom k210 module |
| ------------- | ------------- | ------------- | ------------- | ------------- | ------------- |
| Price avg. | US$50 | US$55 | US$35 | US$35 | US$60 |
| Screen size / resolution | 1.14" / 135*240 | 3.5" / 320*480 | 2.4" / 240*320 | 2.4" / 240*320 | 2" / 240*320 |
| Touchscreen  | :x: | Capacitive | :x: | :x: | Capacitive |
| Camera  | OV7740 | OV7740 rear<br>GC0328 front | GC0328 | OV2640 or<br>OV5642 | OV2640 <!-- or<br>GC2145 --> |
| Battery  | 200mAh | 520mAh | :x: | :x: | :x: |
| Requirements | None | None | [Rotary encoder](https://duckduckgo.com/?q=ky-040)<br> [3D printed case](https://github.com/selfcustody/DockEncoderCase)<br> Soldering<br>Assembly | Buttons<br> [3D printed case](https://github.com/selfcustody/MaixBitCase)<br> Soldering<br>Assembly | None |
| Warnings  | [:material-information:{ title="M5stickV and USB-C" }](#m5stickv-info) | [:material-information:{ title="Maix Amigo screens" }](#amigo-info) | [:material-information:{ title="Maix Dock and soldered pin" }](#dock-info) | Camera has<br> lens distortion | Micro USB |

<i style="font-size: 85%">:material-information:{id="m5stickv-info"}:
----8<----
m5stickv-usb-c.en.txt
----8<----
</i>

<i style="font-size: 85%">:material-information:{id="amigo-info"}:
----8<----
amigo-more-info-faq.en.txt:2
----8<----
</i>

<i style="font-size: 85%">:material-information:{id="dock-info"}:
Some stores ship the Maix Dock with soldered pin connectors that do not fit into the [3D printed case](https://github.com/selfcustody/DockEncoderCase)
</i>

<i style="font-size: 85%">**All devices feature Kendryte K210 chip:**
28nm process, dual-core RISC-V 64bit @400MHz, 8 MB high-speed SRAM, DVP camera and MCU LCD interface, AES Accelerator, SHA256 Accelerator, FFT Accelerator.
</i>

### M5StickV
<img src="../img/maixpy_m5stickv/logo-125.png" align="right" width="75">

Below is a list of some distributors where you can find this device:

- [M5Stack](https://shop.m5stack.com/products/stickv)
- [Mouser](https://www.mouser.com/c/?q=m5stickv)
- [Digi-Key](https://www.digikey.com/en/products/detail/m5stack-technology-co-ltd/K027/10492135)
- [Elektromaker](https://www.electromaker.io/shop/product/m5stickv-k210-ai-camera-without-wifi)
- [Lee's Electronic](https://leeselectronic.com/en/product/169940-m5stick-ai-camera-kendryte-k210-risc-v-core-no-wifi.html)
- [AliExpress](https://www.aliexpress.com/w/wholesale-m5stickv.html)
- [ABRA](https://abra-electronics.com/sensors/cameras/m5stickv-k210-ai-camera-ideal-for-machine-vision.html)
- [Adafruit](https://www.adafruit.com/product/4321)
- [Cytron](https://www.cytron.io/c-development-tools/c-fpga/p-m5stickv-k210-ai-camera-without-wifi)

<div style="clear: both"></div>

### Maix Amigo
<img src="../img/maixpy_amigo/logo-150.png" align="right">

Below is a list of some distributors where you can find this device:

- [AliExpress](https://www.aliexpress.com/w/wholesale-sipeed-amigo.html)
- [Seeed Studio](https://www.seeedstudio.com/Sipeed-Maix-Amigo-p-4689.html)
- [Digi-Key](https://www.digikey.com/en/products/detail/seeed-technology-co-ltd/102110463/13168813)
- [Mouser](https://www.mouser.com/c/?q=sipeed)
- [Electromaker](https://www.electromaker.io/shop/search/sipeed)

<div style="clear: both"></div>

### Yahboom k210 module
<img src="../img/maixpy_yahboom/logo-156.png" align="right" width="116">

Below is a list of some distributors where you can find this device:

- [AliExpress](https://www.aliexpress.com/w/wholesale-yahboom-k210-module.html)
- [Amazon](https://www.amazon.com/s?k=Yahboom+k210+module)
- [Yahboom Store](https://category.yahboom.net/collections/mb-module/products/k210-module)
- [ETC HK Shop](https://www.etchkshop.com/products/k210-module-ai-camera)

<div style="clear: both"></div>

### Maix Dock and Maix Bit
<img src="../img/maixpy_dock/logo-151.png" align="right" width="144">

For the DIYers, the Maix Dock and Maix Bit are also supported but will require sourcing the parts individually and building the device yourself.

Below are example implementations with instructions on how to recreate them:

- [https://github.com/selfcustody/DockEncoderCase](https://github.com/selfcustody/DockEncoderCase)
- [https://github.com/selfcustody/MaixBitCase](https://github.com/selfcustody/MaixBitCase)

Below is a list of some distributors where you can find these devices:

- [Mouser](https://www.mouser.com/c/?q=sipeed)
- [Electromaker](https://www.electromaker.io/shop/search/sipeed)
- [Digi-Key](https://www.digikey.com.br/en/products/filter/embedded-mcu-dsp-evaluation-boards/786?s=N4IgTCBcDaIM4EsAOBTFATEBdAvkA)
- [AliExpress](https://www.aliexpress.com/w/wholesale-sipeed-maix.html)
- [Amazon](https://www.amazon.com/s?k=sipeed+k210)

<div style="clear: both"></div>

## Other Parts
### USB-C Charge Cable
This will be included with the M5StickV and Maix Amigo that you purchase from one of the distributors above. It will be necessary to power and charge the device and to initially flash the firmware.

### (Optional) MicroSD Card
----8<----
sd-card-info-faq.en.txt
----8<----
The size of the SD card isn't important; anything over a few megabytes will be plenty.

### (Optional) Thermal Printer
Krux has the capability to print all QR codes it generates, including those for mnemonics, xpubs, wallet backups, and signed PSBTs, using a locally-connected thermal printer via its serial port.

Many thermal printers may be compatible, but currently, the Goojprt QR203 (easily found on AliExpress) has the best support. The [Adafruit printer starter pack](https://www.adafruit.com/product/600) can also be a convenient option to get started, as it includes all the necessary components for printing (except the conversion cable). To ensure proper functionality, enable the printer driver in the [Krux settings](./getting-started/settings.md/#thermal), set the Tx pin and baud rate value to either 19200 or 9600, as explained in this [Adafruit printer tutorial](https://learn.adafruit.com/mini-thermal-receipt-printer/first-test). You will need to connect the device's Tx to the printer's Rx and ground. The printer requires a dedicated power supply, typically with an output of 5 to 9V and capable of supplying at least 2A. For more information, [see this discussion](https://github.com/selfcustody/krux/discussions/312).

### (Optional) Conversion Cable for Thermal Printer
To connect the printer to the device, you will need a [conversion cable](https://store-usa.arduino.cc/products/grove-4-pin-male-to-grove-4-pin-cable-5-pcs)with a 4-pin female Grove connector on one end (to connect to the device) and 4-pin male jumpers on the other end (to connect to the printer). For a more reliable connection, it is recommended to cut and solder the wires of your custom cables instead of using jumpers.