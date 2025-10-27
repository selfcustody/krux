# Updating the built-in font
Krux uses a [custom fork](https://github.com/bachan/terminus-font-vietnamese) of the [Terminus](http://terminus-font.sourceforge.net/) font for its glyphs that includes Vietnamese characters, the Bitcoin currency symbol (₿) and custom icons.

To rebuild the font for all devices, run:
```python
poetry run python bdftokff.py True
```

If the `True` argument was passed, the Python script will automatically overwrite the contents of the `font_device.h` file in each of the projects `../MaixPy/projects/*/compile/overrides/components/micropython/port/src/omv/img/include/font_device.h`, otherwise the script will produce 3 files: `m5stickv_font_device.h`, `amigo_font_device.h` and `bit_dock_yahboom_font_device.h`. Use these files to manually replace the contents of the `font_device.h` file in each of your projects.

# How it works
Krux uses bitmap fonts that are custom-built for each device it runs on. The format that the firmware expects fonts to be in is a custom format referred to as "krux font format," or `.kff`. 

## Format Spec
Krux font format is a sparse bitmap font format that is intended to minimize the amount of memory used to store a subset of unicode glyphs. In this format, all glyphs are encoded as a 2-byte header integer containing their unicode codepoint followed by a fixed-size array of bytes describing how to draw the glyph. These glyphs are stored contiguously in a one-dimensional byte array sorted by codepoint. The header of this array is a 2-byte integer containing the total number of glyphs in the file. At runtime, each glyph is looked up using binary search.

## Converting to kff
To create a `.kff` file, you first need to find a font in `.bdf` format. You can edit and generate a `.bdf` file using [FontForge](https://fontforge.org)

From there, you can run the `bdftohex.py` script which converts the bdf file to an intermediary `.hex` format mapping each character's unicode codepoint to a series of hex digits describing how to draw it.

From there, you can run the `hexfill.py` script which takes in a `.hex` file and font width and height and post-processes the file to fill in any gaps in the codepoint sequence, adding zero'd lines for missing glyphs. If the specified font size is larger than the hex for a glyph, leading zero padding will be added to the glyph to make it the right size, and if the hex for a glyph is larger than the font size it will be zero'd out.

The `hexmerge.py` script takes a list of `.hex` font files and merges them into one combined `.hex` file sorted by unicode codepoint. If multiple files refer to the same character, the earliest non-zero glyph will be used.

Finally, the `hextokff.py` script takes a `.hex` font file and font width and height and converts it into the 1D sparse bitmap array format that Krux needs. Importantly, this script scans the `i18n/translations` folder and builds the set of unique codepoints used across all translations to drastically reduce the number of glyphs stored.
