"""
Color conversions between 24-bit-rgb888 and 16-bit-rgb565
"""

from binascii import unhexlify
import sys


def rgb24_to_rgb16(rgb, big=False):
    """
    convert 3 bytes of rgb888 into 2 bytes of rgb565
    default to little-endian, so rgb565 becomes gbrg3553
    """
    assert isinstance(rgb, bytes) and len(rgb) == 3

    # 5 significant bits of red shifted to far left
    red = (rgb[0] >> 3) << 11

    # 6 significant bits of green shifted to middle
    green = (rgb[1] >> 2) << 5

    # 5 significant bits of blue on the right
    blue = rgb[2] >> 3

    return int(red + green + blue).to_bytes(2, "big" if big else "little")


def rgb16_to_rgb24(rgb, big=False):
    """
    convert 2 bytes of rgb565 into 3 bytes of rgb888
    default from little-endian, so rgb565 becomes gbrg3553
    """

    def maxv(number_of_bits):
        return (2**number_of_bits) - 1

    assert isinstance(rgb, bytes) and len(rgb) == 2

    rgb_int = int.from_bytes(rgb, "big" if big else "little")

    # left 5 bits of red multiplied to fill 8 bit space
    red = round((rgb_int >> 11) * maxv(8) / maxv(5))

    # middle 6 bits of green multiplied to fill 8 bit space
    green = round(((rgb_int & maxv(11)) >> 5) * maxv(8) / maxv(6))

    # right 5 bits of blue multiplied to fill 8 bit space
    blue = round((rgb_int & maxv(5)) * maxv(8) / maxv(5))

    return b"".join([x.to_bytes(1, "big") for x in [red, green, blue]])


def convert_color(*args):
    """Detect if the input is RGB888 or RGB565 and converts to the other."""
    if len(args) == 1:
        arg = args[0]
        rgb = (
            unhexlify(arg[2:])
            if arg[:2] == "0x"
            else (int(arg) % 65536).to_bytes(2, "big")
        )
    else:
        rgb = bytes([int(x) % 256 for x in args])

    if len(rgb) == 2:
        return rgb16_to_rgb24(rgb)
    if len(rgb) == 3:
        return rgb24_to_rgb16(rgb)
    return None


def main():
    """Main function for script execution."""
    if len(sys.argv) <= 1:
        print(f"Syntax: {sys.argv[0]} integer-bytes or 0x<hex-color>")
        sys.exit(1)

    try:
        result = convert_color(*sys.argv[1:])
        print("0x" + result.hex())
    except (ValueError, TypeError) as error:  # Catch specific exceptions
        print("Error:", error)
        sys.exit(1)


if __name__ == "__main__":
    main()
