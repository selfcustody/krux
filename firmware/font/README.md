# Updating the built-in font
By default, Krux uses the [Terminus](http://terminus-font.sourceforge.net/) font for the majority of glyphs, falling back to the [Fairfax](http://www.kreativekorp.com/software/fonts/fairfax.shtml) font for missing glyphs.

To change this font, you first need to find a unicode font in `.bdf` format.

The font must be baked into the firmware as a 1D bitmap array where each character is represented by a hex byte sequence. To generate this array, you must first convert from `.bdf` to `.hex` format using the `bdftohex.py` script. This intermediate hex format maps each character's unicode codepoint to a series of hex digits describing how to draw it. 

The `hexfill.py` script takes in a `.hex` file and font width and height and post-processes the file to fill in any gaps in the codepoint sequence, adding zero'd lines for missing glyphs. If the specified font size is larger than the hex for a glyph, leading zero padding will be added to the glyph to make it the right size, and if the hex for a glyph is larger than the font size it will be zero'd out.

The `hexmerge.py` script takes a list of `.hex` font files and merges them into one combined `.hex` file, where an earlier glyph will take precedence over a later one if it's not zero'd out.

The `hextodkz.py` script takes a `.hex` font file and font width and height and converts it into the 1D bitmap array format that Krux needs.

For example, to recreate the font in Krux:
```
poetry run python bdftohex.py Fairfax.bdf > Fairfax.hex
poetry run python bdftohex.py ter-u14n.bdf > ter-u14n.hex

poetry run python hexfill.py Fairfax.hex 8 14 > Fairfax.hex
poetry run python hexfill.py ter-u14n.hex 8 14 > ter-u14n.hex
poetry run python hexfill.py btc.hex 8 14 > btc.hex

poetry run python hexmerge.py btc.hex ter-u14n.hex Fairfax.hex > all.hex

poetry run python hextodkz.py all.hex 8 14 > all.dkz
```

Once you have this array in the `all.dkz` file, find the project you want to use the new font under `firmware/MaixPy/projects`, open its `overrides/components/micropython/port/src/omv/img/font.c` file and replace the array contents in the `unicode` variable with this new array and rebuild the firmware.