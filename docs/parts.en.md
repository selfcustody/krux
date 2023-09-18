**Krux compatible devices comparative table**

| Device | M5stickV | Maix Amigo | Maix Dock | Maix Bit |
| ------------- | ------------- | ------------- | ------------- | ------------- |
| Price | US$50 | US$47-63 | US$35 | US$35 |
| Screen size  | 1.14" | 3.5" | 2.4" | 2.4" |
| Screen resolution  | 135*240 | 320*480 | 240*320 | 240*320 |
| Touchscreen  |  | Capacitive |  |  |
| Camera  | OV7740 | OV7740 rear<br>GC0328 front | GC0328 | OV2640 or<br>OV5642 |
| Battery  | 200mAh | 520mAh |  |  |
| Requirements |  |  | Rotary encoder<br> 3D printed case<br> Soldering<br>Assembly | Buttons<br> 3D printed case<br> Soldering<br>Assembly |
| Warnings  |  |  | *1 |  |

*1: Some shops ship Maix Dock with soldered pin headers that do not fit in 3D printed enclosure

All devices feature Kendryte K210 chip:
28nm process, dual-core RISC-V 64bit @400MHz, 8 MB high-speed SRAM, DVP camera and MCU LCD interface, AES Accelerator, SHA256 Accelerator, FFT Accelerator

## Devices
### M5StickV
Available from many distributors, including:

- [M5Stack](https://shop.m5stack.com/products/stickv)
- [Adafruit](https://www.adafruit.com/product/4321)
- [Mouser](https://www.mouser.com/)
- [Digi-Key](https://www.digikey.com/en/products/detail/m5stack-technology-co-ltd/K027/10492135)
- [Lee's Electronic](https://leeselectronic.com/en/product/169940-m5stick-ai-camera-kendryte-k210-risc-v-core-no-wifi.html)
- [Cytron](https://www.cytron.io/c-development-tools/c-fpga/p-m5stickv-k210-ai-camera-without-wifi)
- [Pimoroni](https://shop.pimoroni.com/products/m5stick-v-k210-ai-camera-without-wifi)
- [OKDO](https://www.okdo.com/p/m5stickv-k210-ai-camera-without-wifi/)

You can expect to pay around $50 for one depending on which distributor you choose.

### Maix Amigo
Available from many distributors, including:

- [Seeed Studio](https://www.seeedstudio.com/Sipeed-Maix-Amigo-p-4689.html)
- [Mouser](https://www.mouser.com/)
- [Electromaker](https://www.electromaker.io/shop/product/sipeed-maix-amigo)
- [Antratek](https://www.antratek.com/sipeed-maix-amigo)
- [Digi-Key](https://www.digikey.com/en/products/detail/seeed-technology-co-ltd/102110463/13168813)
- [AliExpress](https://www.aliexpress.com/)

You can expect to pay around $70 for one depending on which distributor you choose.

### Maix Dock and Maix Bit
For the DIYers, the Maix Dock and Bit are also supported but will require sourcing the parts individually and building the device yourself.

Below are example implementations with instructions on how to recreate them:

- [https://github.com/selfcustody/DockEncoderCase](https://github.com/selfcustody/DockEncoderCase)
- [https://github.com/selfcustody/MaixBitCase](https://github.com/selfcustody/MaixBitCase)

## Ohter parts
### USB-C Charge Cable
This will be included with the M5StickV and Maix Amigo that you purchase from one of the distributors above. It will be necessary to power and charge the device and to initially flash the firmware.

### (Optional) MicroSD Card
Not all microSD cards will work with the devices. Make sure to use one that has been [tested and shown to work](https://github.com/m5stack/m5-docs/blob/master/docs/en/core/m5stickv.md#tf-cardmicrosd-test) with the devices already. The size of the SD card isn't important; anything over a few megabytes will be plenty.

### (Optional) Thermal Printer
Krux has the ability to print all QR codes it generates, including mnemonic, xpub, wallet backup, and signed PSBT, via a locally-connected [thermal printer from Adafruit](https://www.adafruit.com/?q=thermal+printer) over its serial port.

Any of their thermal printers will work, but the [starter pack](https://www.adafruit.com/product/600) would be the easiest way to get started since it includes all the parts (except the one below) you will need to begin printing.

### (Optional) Conversion Cable for Thermal Printer
To connect the printer to the device, you will need a [conversion cable](https://store-usa.arduino.cc/products/grove-4-pin-male-to-grove-4-pin-cable-5-pcs) with a 4-pin female Grove connector on one end (to connect to the device) and 4-pin male jumpers on the other end (to connect to the printer). You can find them at one of the distributors above or from Amazon.
