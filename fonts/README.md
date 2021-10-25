# Updating the built-in font
By default, Krux uses the [Terminus](http://terminus-font.sourceforge.net/) font.

To change this font, you first need to find a unicode font in `.bdf` format, with characters that are 8x14px.

The font must be baked into the firmware as a 1D bitmap array where each character is represented by 14 hex bytes in sequence. To generate this array, you must first convert from `.bdf` to `.hex` format using the [`bdfimplode`](https://www.carta.tech/man-pages/man1/bdfimplode.1.html) utility from the [`unifont`](https://unifoundry.com/unifont/) project. This intermediate hex format maps each character's unicode codepoint to a series of hex digits describing how to draw it. The `generate_dkz.py` script in this directory is then used to convert this into the array format that Krux needs.

Once you have this array, open `MaixPy/components/micropython/port/src/omv/img/font.c` and replace the array contents in the `unicode` variable with this new array and rebuild the firmware.