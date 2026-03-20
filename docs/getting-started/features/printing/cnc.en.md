
----8<----
warning-printer.en.txt
----8<----


Krux engraves any QR code (SeedQR, PSBT, address, XPUB, etc.) on GRBL 1.1 CNC machines — via airgapped SD card or direct TTL serial connection.

<img src="/krux/img/maixpy_amigo/print-qr-printing-300.png" class="amigo">
<img src="/krux/img/maixpy_m5stickv/print-qr-printing-250.png" class="m5stickv">

A GRBL g-code simulation on [OpenBuilds CONTROL](https://software.openbuilds.com/):
<video width="506" controls>
  <source src="/krux/img/CompactSeedQR_CNC.mp4" type="video/mp4"></source>
</video>

<img src="/krux/img/maixpy_amigo/print-qr-file-prompt-300.png" class="amigo">
<img src="/krux/img/maixpy_m5stickv/print-qr-file-prompt-250.png" class="m5stickv">
<img src="/krux/img/maixpy_amigo/print-qr-grbl-prompt-300.png" class="amigo">
<img src="/krux/img/maixpy_m5stickv/print-qr-grbl-prompt-250.png" class="m5stickv">

After configuring the CNC printer and driver in [settings](../../settings.md/#cnc), any screen that displays a QR code will offer to `Print as QR`. Use this to Carve QR codes into wood/metal, like backups of your mnemonics, xpubs and multisig wallet output descriptor.

If the driver is configured as *FilePrinter*, the output will be GRBL g-code in a *qr.nc* file on the SD card. If the driver is configured as *GRBLPrinter*, the output will be GRBL g-code sent directly to a GRBL controller via a TTL serial connection. A tested settings is presented below:

```json
"cnc": {
    "unit": "mm",
    "part_size": 70.675,
    "flute_diameter": 3.175,
    "depth_per_pass": 1.0,
    "cut_depth": 2.0,
    "border_padding": 2.0,
    "plunge_rate":300,
    "feed_rate":650,
    "cut_method": "spiral",
    "invert": 1
}
```

<div style="clear: both"></div>

A 96×96mm QR carved into black-painted wood with 2mm drill-bit (inverted for white):

<img src="/krux/img/96x96-2mm_bit.jpg" style="width: 38%; min-width: 130px;">

A 50x50mm QR carved into black-painted wood with 2mm drill-bit (inverted for white):

<img src="/krux/img/50x50_2mm_bit.jpg" style="width: 32%; min-width: 120px;">

Laser etching is also supported. Tested settings and results:

```json
"cnc": {
  "unit": "mm",
  "part_size": 34,
  "flute_diameter": 0.2,
  "depth_per_pass": 0.01,
  "cut_depth": 0.01,
  "border_padding": 0.0,
  "plunge_rate": 150,
  "feed_rate": 300,
  "cut_method": "row",
  "invert": 0,
  "head_type": "laser",
  "head_power": 500
}
```

From left to right: 34x34mm at 50%, 21x21mm at 5%, 21x21mm at 50% power laser-etched stainless steel:

<img src="/krux/img/laser_cnc.jpg" style="width: 60%; min-width: 280px;">

----8<----
warning-printed-QR.en.txt
----8<----



