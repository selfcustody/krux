# Updating the built-in font
Krux uses the [Terminus](http://terminus-font.sourceforge.net/) font for the majority of glyphs, falling back to other fonts for missing glyphs.

To change this font, you first need to find a unicode font in `.bdf` format.

The font must be baked into the firmware as a 1D bitmap array where each character is represented by a hex byte sequence. To generate this array, you must first convert from `.bdf` to `.hex` format using the `bdftohex.py` script. This intermediate hex format maps each character's unicode codepoint to a series of hex digits describing how to draw it. 

The `hexfill.py` script takes in a `.hex` file and font width and height and post-processes the file to fill in any gaps in the codepoint sequence, adding zero'd lines for missing glyphs. If the specified font size is larger than the hex for a glyph, leading zero padding will be added to the glyph to make it the right size, and if the hex for a glyph is larger than the font size it will be zero'd out.

The `hexmerge.py` script takes a list of `.hex` font files and merges them into one combined `.hex` file, where an **earlier glyph will take precedence over a later one** if it's not zero'd out.

The `hextokf.py` script takes a `.hex` font file and font width and height and converts it into the 1D sparse bitmap array format that Krux needs.

A `bdftokf.sh` bash script has been added to simplify this workflow, invoking the aforementioned scripts as needed to compile one kf file given a list of fonts.

For example, to recreate the font in Krux on the M5StickV, Amigo, and Bit:
```
./bdftokf.sh ter-u14n,btc-14 8 14 > m5stickv.kf
./bdftokf.sh ter-u24n,btc-24 12 24 > amigo.kf
./bdftokf.sh ter-u16n,btc-16 8 16 > bit.kf
```

Once you have this array in the `*.kf` file, find the project you want to use the new font under `firmware/MaixPy/projects`, open its `overrides/components/micropython/port/src/omv/img/font.c` file and replace the array contents in the `unicode` variable with this new array and rebuild the firmware.
