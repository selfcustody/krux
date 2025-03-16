# The MIT License (MIT)

# Copyright (c) 2021-2024 Krux contributors

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
from .krux_settings import Settings

SATS_PER_BTC = 100000000
BTC_SATS_LEN = "8"
THOUSANDS_SEPARATOR = " "


def format_btc(amount):
    """Formats a BTC value according to the locale and
    the International Bureau of Weights and Measures,
    while still using the idea behind the Satcomma standard
    """

    btc_without_decimal = amount // SATS_PER_BTC
    btc_decimal_only = amount % SATS_PER_BTC
    btc_decimal_8char = ("{:0>" + BTC_SATS_LEN + "}").format(btc_decimal_only)

    return (
        generate_thousands_separator(btc_without_decimal)
        + render_decimal_separator()
        + btc_decimal_8char[:2]
        + THOUSANDS_SEPARATOR
        + btc_decimal_8char[2:5]
        + THOUSANDS_SEPARATOR
        + btc_decimal_8char[5:]
    )


def render_decimal_separator():
    """Return decimal separator depending on locale"""
    decimal_separator = ","
    if Settings().i18n.locale == "en-US":
        decimal_separator = "."

    return decimal_separator


def replace_decimal_separator(text):
    """Replace decimal separator in text depending on locale"""
    return text.replace(".", render_decimal_separator())


def generate_thousands_separator(number_without_decimal):
    """Generate thousands separator in number_without_decimal"""
    return "{:,}".format(number_without_decimal).replace(",", THOUSANDS_SEPARATOR)


def format_address(address, length=4):
    """Format addresses by adding spaces after each length"""
    return " ".join(address[i : i + length] for i in range(0, len(address), length))
