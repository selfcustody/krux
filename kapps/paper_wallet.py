# The MIT License (MIT)
# Copyright (c) 2021-2026 Krux contributors

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
"""
paper_wallet.py - Bitcoin Paper Wallet Generator for Krux

A Kapp (Krux Application) for generating, loading, and exporting Bitcoin
paper wallets compatible with bitaddress.org format.

Overview
--------
This module provides functionality to:
- Load Bitcoin private keys (WIF format) from QR codes or SD card
- Generate styled paper wallets as SVG files
- Export wallets in multiple formats (Base64, Hex, CSV, SVG)
- Encrypt wallets using KEF (KEF Encrypted Format)
- Generate encrypted paper wallets with scannable QR codes

Classes
-------
Wallet Classes:
    ``KBaseWallet``   : Base class for all wallet types
    ``KSingleWallet`` : Represents a single WIF/address pair
    ``KBulkWallet``   : Collection of multiple ``KSingleWallet`` instances
    ``KPaperWallet``  : Styled paper wallet with SVG generation

SVG Generation:
    ``KSVG``          : Helper class for generating paper wallet and encrypted wallet SVGs

UI/UX Classes:
    ``KMenu``         : Customized menu for the paper wallet interface
    ``KLogin``        : Login page for loading wallets
    ``KHome``         : Home page for wallet operations
    ``KManager``      : Main manager coordinating login and home pages

Storage:
    ``KWalletStorage``: Handler for encrypted wallet storage

Usage
-----
As a Kapp (run from Krux device):

    from paper_wallet import run
    run(ctx)  # ctx is the Krux ``Context``

Programmatic SVG generation:

    # Create a single wallet
    wallet = KSingleWallet(wallet=(0, "L4x...bkN"))

    # Convert to paper wallet and generate SVG
    paper = KPaperWallet.from_single_wallet(wallet)
    svg_list = paper.to_svg()  # Returns list of SVG strings

    # Generate encrypted SVG
    enc_svg = KSVG()
    svg_content = enc_svg.to_encrypted_svg(
        encrypted_data="<base64_kef_data>",
        wallet_id="my_wallet",
        wallet_index=0
    )

Export Formats
--------------
Plaintext exports:
    - Base64 (.b64) : WIF encoded as Base64
    - Hex (.hex)    : WIF encoded as hexadecimal
    - CSV (.csv)    : Format: index, "address", "wif"
    - SVG (.svg)    : Styled paper wallet (bitaddress.org style)

Encrypted exports (KEF):
    - KEF (default) : Stored in Krux encrypted format (JSON)
    - Base64 (.b64) : Encrypted data as Base64
    - Hex (.hex)    : Encrypted data as hexadecimal
    - CSV (.csv)    : Format: wallet_id, format, data
    - SVG (.svg)    : Encrypted paper wallet with QR code

Paper Wallet Styles
-------------------
Unencrypted (``KSVG``):
    - Yellow/gold gradient background
    - Two sections: SHARE (public) and SECRET (private)
    - Bitcoin orange (#f7931a) color scheme
    - QR codes for both address and WIF
    - Fold line between sections

Encrypted (``KSVG.to_encrypted_svg()``):
    - Blue gradient background
    - Single QR code with encrypted KEF data
    - Krux K logo and lock icon
    - KEF FORMAT badge
    - Warning about compatible device requirement

Constants
---------
    VERSION         : Module version ("1.0")
    NAME            : Display name ("Paper Wallet")
    WIF             : Compiled regex for WIF validation

See Also
--------
    - bitaddress.org : Original paper wallet generator
"""

# pylint: disable=too-many-lines
# -------------------
import os
import re

# avoids importing from flash VSF
os.chdir("/")

from krux.display import (
    STATUS_BAR_HEIGHT,
    DEFAULT_PADDING,
    FONT_HEIGHT,
    BOTTOM_PROMPT_LINE,
)

from krux.baseconv import base_decode, base_encode
from krux.context import Context
from krux.encryption import MnemonicStorage
from krux.kboard import kboard
from krux.krux_settings import t, Settings
from krux.pages.qr_capture import QRCodeCapture
from krux.pages import Menu, MENU_CONTINUE, MENU_EXIT, MENU_SHUTDOWN
from krux.pages.encryption_ui import KEFEnvelope, OVERRIDE_LABEL
from krux.pages.login import Login
from krux.pages.home_pages.home import Home
from krux.themes import theme

# -------------------

VERSION = "1.0"
NAME = "Paper Wallet"
CSV_FILE_EXTENSION = "csv"
BASE58 = r"[1-9A-HJ-NP-Za-km-z]"
WIF = re.compile(
    r"^(?:"
    r"5(?:%s){50}"  # mainnet uncompressed
    r"|[KL](?:%s){51}"  # mainnet compressed
    r"|9(?:%s){50}"  # testnet uncompressed
    r"|c(?:%s){51}"  # testnet compressed
    r")$" % (BASE58, BASE58, BASE58, BASE58)
)


# -------------------
# Utility Functions
# -------------------


def normalize_on_load(on_load):
    """Normalize the on_load callback for KLogin.load_from method.

    Args:
        on_load: Callback function or None.

    Returns:
        The original callback if not None, otherwise a default no-op function.
    """
    if on_load is not None:
        return on_load

    def _default_on_load(*_):
        return None

    return _default_on_load


def is_wif(data):
    """Check if the given data is a valid Wallet Import Format (WIF) string.

    WIF is a Base58Check encoding of a private key used in Bitcoin.
    Supports mainnet (5, K, L prefixes) and testnet (9, c prefixes).

    Args:
        data: String to validate.

    Returns:
        True if data is a valid WIF string, False otherwise.

    Raises:
        ValueError: If data is not a string.

    Example:
        >>> is_wif("L4xHoBuqpn654roZAUKaVrzrH6wbvXhQQt68747igWSdrtU4ZbkN")
        True
        >>> is_wif("invalid")
        False
    """
    if not isinstance(data, str):
        raise ValueError("Data must be str")

    s = (data or "").strip()
    if len(s) not in (51, 52):
        return False

    return bool(WIF.match(s))


def is_base64(data):
    """Check if the given data is a valid Base64 encoded string.

    Args:
        data: String to validate.

    Returns:
        True if data is valid Base64, False otherwise.

    Raises:
        ValueError: If data is not a string.
    """
    if not isinstance(data, str):
        raise ValueError("Data must be str")

    s = (data or "").strip()
    if not s or len(s) % 4 != 0:
        return False

    return bool(re.match(r"^[A-Za-z0-9+/]+={0,2}$", s))


def is_csv(data):
    """Check if the given data appears to be CSV formatted.

    Checks if the string starts with a number followed by a comma,
    which is the expected format for paper wallet CSV exports.

    Args:
        data: String to validate.

    Returns:
        True if data appears to be CSV format, False otherwise.

    Raises:
        ValueError: If data is not a string.
    """
    if not isinstance(data, str):
        raise ValueError("Data must be str")

    s = (data or "").strip()
    if not s:
        return False

    return bool(re.match(r"^\s*\d+\s*,", s))


def is_svg(data):
    """Check if the given data appears to be SVG content.

    Args:
        data: String to validate.

    Returns:
        True if data contains an SVG tag, False otherwise.

    Raises:
        ValueError: If data is not a string.
    """
    if not isinstance(data, str):
        raise ValueError("Data must be str")

    s = (data or "").strip()
    if not s:
        return False

    return bool(re.search(r"<svg\b", s, flags=re.IGNORECASE))


def hash256(data):
    """Compute double SHA-256 hash of data.

    This is the standard Bitcoin hash function used for checksums.

    Args:
        data: Bytes to hash.

    Returns:
        Hexadecimal string of the double SHA-256 digest.
    """
    from hashlib import sha256

    return sha256(sha256(data).digest()).digest().hex()


# -------------------
# Wallet Classes
# -------------------


class KBaseWallet:
    """Base class for all Bitcoin paper wallet types.

    Provides common functionality for wallet type validation and
    data format detection. Subclasses implement specific wallet
    behaviors (single, bulk, paper).

    Attributes:
        WALLET_TYPES: Tuple of valid wallet type strings.

    Args:
        wallet_type: Type of wallet ("single", "bulk", or "paper").
    """

    WALLET_TYPES = ("single", "bulk", "paper")

    def __init__(self, wallet_type="single"):
        self._wallet_type = wallet_type

    @property
    def wallet_type(self):
        """str: The type of this wallet instance."""
        return self._wallet_type

    @wallet_type.setter
    def wallet_type(self, value):
        """Set the wallet type with validation.

        Args:
            value: Must be one of WALLET_TYPES.

        Raises:
            ValueError: If value is None, not a string, or invalid type.
        """
        if value is None:
            raise ValueError("Wallet type is None")

        if not isinstance(value, str):
            raise ValueError("Wallet type isnt str")

        if value not in KBaseWallet.WALLET_TYPES:
            raise ValueError("Invalid wallet_type: '%s'" % value)

        self._wallet_type = value

    @staticmethod
    def from_bytes(data):
        """Detect the format of wallet data.

        Analyzes the input data to determine its encoding format
        (Base64, Hex, SVG, or CSV).

        Args:
            data: Bytes or string containing wallet data.

        Returns:
            Tuple of (format_name, data_string) where format_name is
            one of "base64", "hex", "svg", or "csv".

        Raises:
            ValueError: If data is None, empty, wrong type, or unknown format.
        """
        if data is None:
            raise ValueError("Data is None")

        if isinstance(data, (bytes, bytearray)):
            s = bytes(data).decode("utf-8", errors="strict").strip()
        elif isinstance(data, str):
            s = data.strip()
        else:
            raise ValueError("Data must be bytes or str")

        if not s:
            raise ValueError("Empty data")

        # Base64 wallet
        if re.match(r"^[A-Za-z0-9+/]+={0,2}$", s) and (len(s) % 4 == 0):
            return ("base64", s)

        # hex wallet
        if re.match(r"^[0-9a-fA-F]+$", s) and (len(s) % 2 == 0):
            return ("hex", s)

        # SVG wallet (paper-only)
        if re.search(r"<svg\b", s, flags=re.IGNORECASE) or re.search(
            r"\bsvg\b", s, flags=re.IGNORECASE
        ):
            return ("svg", s)

        # CSV wallet (single, bulk or paper)
        if re.match(r"^\s*\d+\s*,", s):
            return ("csv", s)

        raise ValueError("Failed to convert")


class KSingleWallet(KBaseWallet):
    """Represents a single Bitcoin wallet with one WIF/address pair.

    Stores a single private key in WIF format and provides access to
    derived properties like public key, address, and checksum.

    Args:
        wallet: Tuple of (index, wif_string).

    Example:
        >>> w = KSingleWallet((0, "L4x...bkN"))
        >>> w.address
        '16k8TH6VDexBRteFd6VQARgvxAxzXdzTmU'
    """

    def __init__(self, wallet):
        super().__init__(wallet_type="single")
        self._wallet = wallet

    @property
    def wallet(self):
        """tuple: The raw wallet tuple (index, wif)."""
        return self._wallet

    @property
    def index(self):
        """int: The wallet index number."""
        return self.wallet[0]

    @property
    def wif(self):
        """str: The Wallet Import Format private key string."""
        return self.wallet[1]

    @property
    def checksum(self):
        """str: First 8 characters of the double SHA-256 hash of the private key.

        Used as a short identifier for the wallet.
        """
        return hash256(self.private_key.serialize())[:8]

    @property
    def private_key(self):
        """embit.ec.PrivateKey: The private key object derived from WIF."""
        from embit import ec

        return ec.PrivateKey.from_wif(self.wif)

    @property
    def public_key(self):
        """embit.ec.PublicKey: The public key derived from the private key."""
        return self.private_key.get_public_key()

    @property
    def script(self):
        """embit.script.Script: The P2PKH script for this wallet."""
        from embit import script

        return script.p2pkh(self.public_key)

    @property
    def address(self):
        """str: The Bitcoin address (P2PKH format)."""
        return self.script.address()

    def __str__(self):
        """Return a string representation of the wallet.

        Returns:
            String in format: <KSingleWallet index=N wif="..." checksum="...">
        """
        return '<KSingleWallet index=%d wif="%s" checksum="%s">' % (
            self.index,
            self.wif,
            self.checksum,
        )


class KBulkWallet(KBaseWallet):
    """Represents a collection of multiple ``KSingleWallet`` instances.

    Used when generating multiple paper wallets at once.

    Args:
        wallets: List of wallet tuples, each in (index, wif) format.

    Example:
        >>> wallets = [(0, "L4xHo..."), (1, "K3abc...")]
        >>> bulk = KBulkWallet(wallets)
        >>> len(bulk.wallets)
        2
    """

    def __init__(self, wallets):
        super().__init__(wallet_type="bulk")
        self._wallets = [KSingleWallet(wallet=w) for w in wallets]

    @property
    def wallets(self):
        """list[``KSingleWallet``]: List of single wallet instances."""
        return self._wallets

    @property
    def checksum(self):
        """str: First 8 characters of the double SHA-256 hash of each loaded
        private key concatenated.

        Used as a short identifier for the wallet.
        """
        wifs = b"".join([wallet.private_key.serialize() for wallet in self.wallets])
        return hash256(wifs)[:8]


# -------------------
# SVG Generation Classes
# -------------------
class KSVG:
    """Helper class for generating paper wallet SVG files.

    Provides methods to build SVG elements for the bitaddress.org-style
    paper wallet layout, including headers, QR codes, text sections,
    and the two-panel SHARE/SECRET design.

    The generated SVG uses a yellow/gold color scheme with Bitcoin
    orange (#f7931a) accents.

    Example:
        >>> svg = KSVG()
        >>> content = svg.xml_open() + svg.open(width=994, height=263)
        >>> content += svg.paper_wallet_defs()
        >>> # ... add more elements
        >>> content += svg.close()
    """

    def xml_open(self, version=1, encoding="UTF-8"):
        """Generate XML declaration header.

        Args:
            version: XML version number (default: 1).
            encoding: Character encoding (default: UTF-8).

        Returns:
            XML declaration string.
        """
        return '<?xml version="%d.0" encoding="%s"?>' % (version, encoding)

    def open(self, xmlns="http://www.w3.org/2000/svg", width=900, height=450):
        """Generate SVG opening tag with dimensions.

        Args:
            xmlns: XML namespace URL.
            width: SVG width in pixels.
            height: SVG height in pixels.

        Returns:
            SVG opening tag string.
        """
        return "\n".join(
            [
                '<svg xmlns="%s"' % xmlns,
                '     width="%d"' % width,
                '     height="%d"' % height,
                '     viewBox="0 0 %d %d">' % (width, height),
            ]
        )

    def box(
        self,
        x=20,
        y=20,
        width=860,
        height=410,
        rx=19,
        fill="#fff",
        stroke="#111",
        strokewidth=3,
    ):
        """Create a rounded rectangle element.

        Args:
            x: X position.
            y: Y position.
            width: Rectangle width.
            height: Rectangle height.
            rx: Corner radius.
            fill: Fill color.
            stroke: Stroke color.
            strokewidth: Stroke width.

        Returns:
            SVG rect element string.
        """
        return " ".join(
            [
                '<rect x="%d"' % x,
                'y="%d"' % y,
                'width="%d"' % width,
                'height="%d"' % height,
                'rx="%d"' % rx,
                'fill="%s"' % fill,
                'stroke="%s"' % stroke,
                'stroke-width="%s"/>' % strokewidth,
            ]
        )

    def bitcoin_logo(self, x=50, y=40, size=50):
        """Create a Bitcoin ```&#x20bf;``` symbol with circular orange background.

        Args:
            x: X position of the logo.
            y: Y position of the logo.
            size: Diameter of the circle.

        Returns:
            SVG elements for the Bitcoin logo.
        """
        cx = x + size // 2
        cy = y + size // 2
        return " ".join(
            [
                '<circle cx="%d" cy="%d" r="%d"' % (cx, cy, size // 2),
                'fill="#f7931a" stroke="#c16a00" stroke-width="2"/>',
                '<text x="%d" y="%d"' % (cx, cy + size // 5),
                'font-family="Arial, sans-serif" font-size="%d"' % (size * 7 // 10),
                'font-weight="bold" fill="#fff" text-anchor="middle">&#x20bf;</text>',
            ]
        )

    def header(
        self,
        title,
        font="monospace",
        fontsize=28,
        textcolor="#111",
        textx=110,
        texty=75,
    ):
        """Create a header text element.

        Args:
            title: Header text content.
            font: Font family.
            fontsize: Font size in pixels.
            textcolor: Text color.
            textx: X position.
            texty: Y position.

        Returns:
            SVG text element string.
        """
        return " ".join(
            [
                '<text x="%d"' % textx,
                'y="%d"' % texty,
                'font-family="%s"' % font,
                'font-size="%d"' % fontsize,
                'font-weight="bold"',
                'fill="%s">' % textcolor,
                "%s</text>" % title,
            ]
        )

    # pylint: disable=too-many-arguments
    def item(
        self,
        key,
        value,
        x=50,
        y=140,
        fontfamily="monospace",
        fontsize=13,
        fill="#111",
        width=540,
        height=45,
        rx=8,
        boxfill="#f7f7f7",
        boxstroke="#222",
        boxstrokewidth=2,
    ):
        """Create a labeled text box with key-value display.

        Renders a label (key) above a rounded rectangle containing
        the value text.

        Args:
            key: Label text displayed above the box.
            value: Content text displayed inside the box.
            x: X position.
            y: Y position.
            fontfamily: Font family for text.
            fontsize: Font size.
            fill: Text color.
            width: Box width.
            height: Box height.
            rx: Box corner radius.
            boxfill: Box background color.
            boxstroke: Box border color.
            boxstrokewidth: Box border width.

        Returns:
            SVG elements for the labeled text box.
        """
        return " ".join(
            [
                '<text x="%d"' % x,
                'y="%d"' % y,
                'font-family="%s"' % fontfamily,
                'font-size="%d"' % fontsize,
                'font-weight="bold"',
                'fill="%s">' % fill,
                key,
                "</text>",
                '<rect x="%d"' % x,
                'y="%d"' % (y + 10),
                'width="%d"' % width,
                'height="%d"' % height,
                'rx="%d"' % rx,
                'fill="%s"' % boxfill,
                'stroke="%s"' % boxstroke,
                'stroke-width="%d"/>' % boxstrokewidth,
                '<text x="%d"' % (x + 10),
                'y="%d"' % (y + 40),
                'font-family="%s"' % fontfamily,
                'font-size="%d"' % fontsize,
                'fill="%s">' % fill,
                value,
                "</text>",
            ]
        )

    def qrcode(
        self, data, x=620, y=110, size=130, module_color="#111", bg_color="#fff"
    ):
        """Generate a QR code as SVG rectangle elements.

        Creates a QR code by drawing individual module rectangles.
        Uses Krux's qrcode module which returns packed binary data.

        Args:
            data: String data to encode in the QR code.
            x: X position of the QR code.
            y: Y position of the QR code.
            size: Width and height of the QR code in pixels.
            module_color: Color of the dark modules.
            bg_color: Background color.

        Returns:
            SVG elements forming the complete QR code.
        """
        import math
        import qrcode as qr

        if isinstance(data, str):
            data = data.encode("utf-8")
        code = qr.encode(data)
        qr_size = int(math.sqrt(len(code) * 8))
        module_size = size // qr_size

        rects = []
        # Background with border
        rects.append(
            '<rect x="%d" y="%d" width="%d" height="%d" fill="%s"'
            % (x - 5, y - 5, size + 10, size + 10, bg_color)
        )
        rects.append('stroke="#ddd" stroke-width="1"/>')

        # Draw QR modules from packed binary (LSB-first)
        for row in range(qr_size):
            for col in range(qr_size):
                bit_index = row * qr_size + col
                if code[bit_index >> 3] & (1 << (bit_index % 8)):
                    rx = x + col * module_size
                    ry = y + row * module_size
                    rects.append(
                        '<rect x="%d" y="%d" width="%d" height="%d" fill="%s"/>'
                        % (rx, ry, module_size, module_size, module_color)
                    )

        return " ".join(rects)

    def paper_wallet_defs(self):
        """Generate SVG defs with yellow/gold gradient for paper wallet.

        Returns:
            SVG defs element with goldGrad linear gradient.
        """
        return " ".join(
            [
                "<defs>",
                '<linearGradient id="goldGrad" x1="0%" y1="0%" x2="0%" y2="100%">',
                '<stop offset="0%" style="stop-color:#fff9e6"/>',
                '<stop offset="100%" style="stop-color:#fff3cd"/>',
                "</linearGradient>",
                "</defs>",
            ]
        )

    def paper_wallet_background(self):
        """Generate the main card background with orange top border.

        Returns:
            SVG elements for card background and decorative top stripe.
        """
        return " ".join(
            [
                '<rect x="2" y="2" width="990" height="259" rx="5"',
                'fill="url(#goldGrad)" stroke="#d4a012" stroke-width="3"/>',
                '<rect x="2" y="2" width="990" height="8" fill="#f7931a"/>',
            ]
        )

    def share_section(self, address):
        """Generate the left SHARE section with public Bitcoin address.

        Creates the public-facing section of the paper wallet containing
        the Bitcoin address QR code and text for receiving funds.

        Args:
            address: Bitcoin address string.

        Returns:
            SVG elements for the complete SHARE section.
        """
        return " ".join(
            [
                # Section background
                '<rect x="12" y="20" width="470" height="230" rx="4"',
                'fill="#fff" stroke="#e0c068" stroke-width="1"/>',
                # Header bar
                '<rect x="12" y="20" width="470" height="32" rx="4" fill="#f7931a"/>',
                '<rect x="12" y="40" width="470" height="12" fill="#f7931a"/>',
                # Bitcoin logo
                '<circle cx="36" cy="36" r="16" fill="#fff"/>',
                '<text x="36" y="42" font-family="Arial" font-size="18"',
                'font-weight="bold" fill="#f7931a" text-anchor="middle">&#x20bf;</text>',
                # SHARE label
                '<text x="60" y="42" font-family="Arial" font-size="18"',
                'font-weight="bold" fill="#fff">SHARE</text>',
                # QR Code for address
                self.qrcode(data=address, x=24, y=62, size=145),
                # Address label
                '<text x="185" y="80" font-family="Arial" font-size="11"',
                'font-weight="bold" fill="#333">Bitcoin Address</text>',
                # Address text box
                '<rect x="185" y="90" width="285" height="105" rx="3"',
                'fill="#fffef5" stroke="#e0c068" stroke-width="1"/>',
                # Address text (wrapped)
                '<text x="195" y="115" font-family="Courier New, monospace"',
                'font-size="14" fill="#333">%s</text>' % address[:17],
                '<text x="195" y="140" font-family="Courier New, monospace"',
                'font-size="14" fill="#333">%s</text>' % address[17:],
                # Deposit instructions
                '<text x="185" y="218" font-family="Arial" font-size="9"',
                'fill="#666">DEPOSIT Bitcoin to this address.</text>',
                '<text x="185" y="232" font-family="Arial" font-size="9"',
                'fill="#666">Verify on blockchain before trusting.</text>',
            ]
        )

    def fold_line(self):
        """Generate the dashed fold line between SHARE and SECRET sections.

        Returns:
            SVG line element with dashed stroke.
        """
        return " ".join(
            [
                '<line x1="497" y1="15" x2="497" y2="255"',
                'stroke="#999" stroke-width="1" stroke-dasharray="8,4"/>',
            ]
        )

    def secret_section(self, wif):
        """Generate the right SECRET section with private key (WIF).

        Creates the private section of the paper wallet containing
        the WIF private key QR code and text. Uses darker orange
        color scheme to visually distinguish from the public section.

        Args:
            wif: Wallet Import Format private key string.

        Returns:
            SVG elements for the complete SECRET section.
        """
        return " ".join(
            [
                # Section background
                '<rect x="512" y="20" width="470" height="230" rx="4"',
                'fill="#fff" stroke="#d47800" stroke-width="1"/>',
                # Header bar (darker orange for secret)
                '<rect x="512" y="20" width="470" height="32" rx="4" fill="#e67e00"/>',
                '<rect x="512" y="40" width="470" height="12" fill="#e67e00"/>',
                # Bitcoin logo
                '<circle cx="536" cy="36" r="16" fill="#fff"/>',
                '<text x="536" y="42" font-family="Arial" font-size="18"',
                'font-weight="bold" fill="#e67e00" text-anchor="middle">&#x20bf;</text>',
                # SECRET label
                '<text x="560" y="42" font-family="Arial" font-size="18"',
                'font-weight="bold" fill="#fff">SECRET</text>',
                # QR Code for WIF
                self.qrcode(data=wif, x=524, y=62, size=145),
                # Private Key label
                '<text x="685" y="80" font-family="Arial" font-size="11"',
                'font-weight="bold" fill="#333">Private Key (WIF Format)</text>',
                # WIF text box
                '<rect x="685" y="90" width="285" height="105" rx="3"',
                'fill="#fff8f0" stroke="#d47800" stroke-width="1"/>',
                # WIF text (wrapped into 3 lines)
                '<text x="695" y="115" font-family="Courier New, monospace"',
                'font-size="13" fill="#333">%s</text>' % wif[:18],
                '<text x="695" y="138" font-family="Courier New, monospace"',
                'font-size="13" fill="#333">%s</text>' % wif[18:36],
                '<text x="695" y="161" font-family="Courier New, monospace"',
                'font-size="13" fill="#333">%s</text>' % wif[36:],
                # Warning
                '<text x="685" y="218" font-family="Arial" font-size="9"',
                'font-weight="bold" fill="#c62828">',
                "Keep this SECRET. Don't share!</text>",
                '<text x="685" y="232" font-family="Arial" font-size="9"',
                'fill="#666">Anyone with this key can spend your Bitcoin.</text>',
            ]
        )

    def paper_wallet_footer(self, wallet_index):
        """Generate the footer with wallet number and Krux branding.

        Args:
            wallet_index: Index number of this wallet.

        Returns:
            SVG text elements for the footer.
        """
        return " ".join(
            [
                '<text x="250" y="256" font-family="Arial" font-size="8"',
                'fill="#888" text-anchor="middle">',
                "Wallet #%d</text>" % wallet_index,
                '<text x="747" y="256" font-family="Arial" font-size="8"',
                'fill="#f7931a" text-anchor="middle">',
                "Generated with Krux</text>",
            ]
        )

    def close(self):
        """Generate the SVG closing tag.

        Returns:
            SVG closing tag string.
        """
        return "</svg>"

    @staticmethod
    def from_svg(svg_data):
        """Parse an SVG paper wallet and extract wallet data.

        Extracts the WIF private key and wallet index from a paper wallet
        SVG generated by this class.

        Args:
            svg_data: SVG content as string or bytes.

        Returns:
            ``KPaperWallet`` instance containing the extracted wallet(s).

        Raises:
            ValueError: If SVG data is invalid or WIF cannot be extracted.

        Example:
            >>> svg_content = open("wallet.svg").read()
            >>> wallet = KSVG.from_svg(svg_content)
            >>> print(wallet.wallets[0].wif)
        """
        if svg_data is None:
            raise ValueError("SVG data is None")

        if isinstance(svg_data, (bytes, bytearray)):
            svg_data = bytes(svg_data).decode("utf-8", errors="strict")

        if not isinstance(svg_data, str):
            raise ValueError("SVG data must be str or bytes")

        if not svg_data.strip():
            raise ValueError("SVG data is empty")

        # Extract WIF parts from SECRET section (x="695" text elements)
        # Pattern matches: <text x="695" y="115|138|161" ...>WIF_PART</text>
        wif_pattern = r'<text\s+x="695"\s+y="(?:115|138|161)"[^>]*>([^<]+)</text>'
        wif_matches = re.findall(wif_pattern, svg_data)

        if len(wif_matches) != 3:
            raise ValueError(
                "Could not extract WIF from SVG (found %d parts)" % len(wif_matches)
            )

        wif = "".join(wif_matches)

        if not is_wif(wif):
            raise ValueError("Extracted WIF is invalid: %s" % wif)

        # Extract wallet index from footer
        # Pattern matches: Wallet #N</text>
        index_pattern = r"Wallet\s+#(\d+)</text>"
        index_match = re.search(index_pattern, svg_data)

        wallet_index = 0
        if index_match:
            wallet_index = int(index_match.group(1))

        return KPaperWallet(wallets=[(wallet_index, wif)])

    # -------------------------
    # Encrypted Wallet Methods
    # -------------------------

    def lock_icon(self, x=0, y=0, size=24, color="#1565c0"):
        """Generate a padlock icon using SVG path.

        Used in encrypted wallet headers to indicate security.

        Args:
            x: X position.
            y: Y position.
            size: Icon size (scaled from 24px base).
            color: Fill color.

        Returns:
            SVG group with lock icon path.
        """
        scale = size / 24
        return " ".join(
            [
                '<g transform="translate(%d, %d) scale(%.2f)">' % (x, y, scale),
                '<path fill="%s"' % color,
                'd="M18 8h-1V6c0-2.76-2.24-5-5-5S7 3.24 7 6v2H6c-1.1 0-2 .9-2 2v10',
                "c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2V10c0-1.1-.9-2-2-2zm-6 9c-1.1",
                "0-2-.9-2-2s.9-2 2-2 2 .9 2 2-.9 2-2 2zm3.1-9H8.9V6c0-1.71",
                '1.39-3.1 3.1-3.1 1.71 0 3.1 1.39 3.1 3.1v2z"/>',
                "</g>",
            ]
        )

    def krux_logo(self, x=0, y=0, size=24, color="#fff"):
        """Generate the Krux K logo with circular background.

        Args:
            x: X position.
            y: Y position.
            size: Logo diameter.
            color: Circle background color.

        Returns:
            SVG elements for the K logo.
        """
        return " ".join(
            [
                # Circle background
                '<circle cx="%d" cy="%d" r="%d"'
                % (x + size // 2, y + size // 2, size // 2),
                'fill="%s" stroke="#0d47a1" stroke-width="1"/>' % color,
                # K letter
                '<text x="%d" y="%d"' % (x + size // 2, y + size // 2 + size // 5),
                'font-family="Arial" font-size="%d"' % (size * 6 // 10),
                'font-weight="bold" fill="#1565c0" text-anchor="middle">k</text>',
            ]
        )

    def encrypted_defs(self):
        """Generate SVG defs with blue gradient for encrypted wallet.

        Returns:
            SVG defs element with ```encGrad``` linear gradient.
        """
        return " ".join(
            [
                "<defs>",
                '<linearGradient id="encGrad" x1="0%" y1="0%" x2="0%" y2="100%">',
                '<stop offset="0%" style="stop-color:#e3f2fd"/>',
                '<stop offset="100%" style="stop-color:#bbdefb"/>',
                "</linearGradient>",
                "</defs>",
            ]
        )

    def encrypted_background(self):
        """Generate the main card background for encrypted wallet.

        Returns:
            SVG rect element with blue gradient fill.
        """
        return " ".join(
            [
                '<rect x="2" y="2" width="496" height="376" rx="8"',
                'fill="url(#encGrad)" stroke="#1565c0" stroke-width="3"/>',
            ]
        )

    def encrypted_header(self):
        """Generate the header with K logo, lock icon, title and KEF badge.

        Uses ``krux_logo()`` and ``lock_icon()`` methods.

        Returns:
            SVG elements for the complete encrypted wallet header.
        """
        return " ".join(
            [
                # Header bar
                '<rect x="2" y="2" width="496" height="50" rx="8" fill="#1565c0"/>',
                '<rect x="2" y="40" width="496" height="12" fill="#1565c0"/>',
                # Krux K logo
                self.krux_logo(x=12, y=11, size=32, color="#fff"),
                # Lock icon (next to K logo)
                self.lock_icon(x=50, y=13, size=28, color="#fff"),
                # Header text
                '<text x="88" y="35" font-family="Arial" font-size="18"',
                'font-weight="bold" fill="#fff">ENCRYPTED WALLET</text>',
                # KEF badge
                '<rect x="380" y="15" width="100" height="24" rx="12" fill="#0d47a1"/>',
                '<text x="430" y="32" font-family="Arial" font-size="11"',
                'font-weight="bold" fill="#fff" text-anchor="middle">KEF FORMAT</text>',
            ]
        )

    def encrypted_warning(self):
        """Generate the warning box about KEF encrypted format.

        Displays a prominent warning that the QR contains encrypted
        data and requires a compatible device to decrypt.

        Returns:
            SVG elements for the warning box.
        """
        return " ".join(
            [
                '<rect x="20" y="62" width="460" height="40" rx="4"',
                'fill="#fff3e0" stroke="#ff9800" stroke-width="1"/>',
                '<text x="250" y="80" font-family="Arial" font-size="10"',
                'font-weight="bold" fill="#e65100" text-anchor="middle">',
                "&#x26a0; This QR contains encrypted data (KEF)</text>",
                '<text x="250" y="94" font-family="Arial" font-size="9"',
                'fill="#666" text-anchor="middle">',
                "Scan with Krux or compatible device to decrypt</text>",
            ]
        )

    def encrypted_qr_section(self, encrypted_data, wallet_id):
        """Generate the QR code section with encrypted data and wallet ID.

        Uses the ``qrcode()`` method to render the encrypted data.

        Args:
            encrypted_data: Base64-encoded KEF encrypted data.
            wallet_id: Wallet identifier label.

        Returns:
            SVG elements for QR code container and wallet ID.
        """
        return " ".join(
            [
                # QR Code container
                '<rect x="125" y="112" width="250" height="250" rx="6"',
                'fill="#fff" stroke="#1565c0" stroke-width="2"/>',
                # QR Code (centered, large)
                self.qrcode(
                    data=encrypted_data,
                    x=145,
                    y=132,
                    size=210,
                    module_color="#1565c0",
                ),
                # Wallet ID label
                '<text x="250" y="356" font-family="Courier New" font-size="11"',
                'font-weight="bold" fill="#333" text-anchor="middle">ID: %s</text>'
                % wallet_id,
            ]
        )

    def encrypted_footer(self, wallet_index, wallet_id):
        """Generate the footer with wallet number and Krux branding.

        Args:
            wallet_index: Index number of this wallet.
            wallet_id: Wallet identifier/label for display.

        Returns:
            SVG text element for the footer.
        """
        return " ".join(
            [
                '<text x="250" y="372" font-family="Arial" font-size="9"',
                'font-weight="bold" fill="#666" text-anchor="middle">',
                "Wallet #%d | ID: %s</text>" % (wallet_index, wallet_id),
            ]
        )

    def to_encrypted_svg(self, encrypted_data, wallet_id, wallet_index=0):
        """Generate a complete encrypted paper wallet SVG.

        Assembles all encrypted wallet SVG components into a single
        SVG document string. Uses blue color scheme with single QR code.

        Args:
            encrypted_data: Base64-encoded KEF encrypted data.
            wallet_id: Wallet identifier/label for display.
            wallet_index: Index number for multiple wallets.

        Returns:
            Complete SVG document as a string.

        Example:
            >>> svg = KSVG()
            >>> content = svg.to_encrypted_svg(
            ...     encrypted_data="base64_kef_data",
            ...     wallet_id="my_wallet",
            ...     wallet_index=0
            ... )
        """
        return " ".join(
            [
                self.xml_open(),
                self.open(width=500, height=380),
                self.encrypted_defs(),
                self.encrypted_background(),
                self.encrypted_header(),
                self.encrypted_warning(),
                self.encrypted_qr_section(encrypted_data, wallet_id),
                self.encrypted_footer(wallet_index, wallet_id),
                self.close(),
            ]
        )

    def to_combined_encrypted_svg(self, encrypted_wallets):
        """Generate a combined encrypted paper wallet SVG.

        Creates one SVG document with all encrypted wallets stacked vertically.

        Args:
            encrypted_wallets: List of tuples (encrypted_data, wallet_id, wallet_index).

        Returns:
            Complete combined SVG document as a string.
        """
        wallet_height = 380
        wallet_width = 500
        total_height = wallet_height * len(encrypted_wallets)

        parts = [
            self.xml_open(),
            self.open(width=wallet_width, height=total_height),
            self.encrypted_defs(),
        ]

        for i, (encrypted_data, wallet_id, wallet_index) in enumerate(
            encrypted_wallets
        ):
            y_offset = i * wallet_height
            parts.append(
                '<g transform="translate(0, %d)" id="%s">' % (y_offset, wallet_id)
            )
            parts.append(self.encrypted_background())
            parts.append(self.encrypted_header())
            parts.append(self.encrypted_warning())
            parts.append(self.encrypted_qr_section(encrypted_data, wallet_id))
            parts.append(self.encrypted_footer(wallet_index, wallet_id))
            parts.append("</g>")

        parts.append(self.close())
        return " ".join(parts)


# -------------------
# Paper Wallet Class
# -------------------
class KPaperWallet(KBaseWallet):
    """Styled paper wallet generator for Bitcoin wallets.

    Converts ``KSingleWallet`` or ``KBulkWallet`` instances into printable
    SVG paper wallets in the bitaddress.org style, with SHARE (public)
    and SECRET (private) sections.

    Args:
        wallets: List of wallet tuples in (index, wif) format.

    Example:
        >>> paper = KPaperWallet([(0, "L4xHo...")])
        >>> svgs = paper.to_svg()
        >>> print(svgs[0])  # SVG content for wallet #0
    """

    def __init__(self, wallets):
        super().__init__(wallet_type="paper")
        self._wallets = [KSingleWallet(wallet=w) for w in wallets]
        self._svg = KSVG()

    @property
    def wallets(self):
        """list[``KSingleWallet``]: List of wallet instances."""
        return self._wallets

    def to_svg(self):
        """Generate SVG paper wallets for all wallets.

        Creates one SVG document per wallet in bitaddress.org style
        with SHARE (public address) and SECRET (private key) sections.

        Returns:
            List of SVG document strings, one per wallet.
        """
        svgs = []

        for i, wallet in enumerate(self.wallets):
            svg = " ".join(
                [
                    self._svg.xml_open(),
                    self._svg.open(width=994, height=263),
                    self._svg.paper_wallet_defs(),
                    self._svg.paper_wallet_background(),
                    self._svg.share_section(wallet.address),
                    self._svg.fold_line(),
                    self._svg.secret_section(wallet.wif),
                    self._svg.paper_wallet_footer(i),
                    self._svg.close(),
                ]
            )
            svgs.append(svg)

        return svgs

    def to_combined_svg(self):
        """Generate a single combined SVG containing all wallets.

        Creates one SVG document with all wallets stacked vertically,
        each wallet identified by its checksum. Used for bulk wallet export.

        Returns:
            Single SVG document string containing all wallets.
        """
        wallet_height = 263
        wallet_width = 994
        total_height = wallet_height * len(self.wallets)

        # Start SVG with combined dimensions
        parts = [
            self._svg.xml_open(),
            self._svg.open(width=wallet_width, height=total_height),
            self._svg.paper_wallet_defs(),
        ]

        # Add each wallet in a translated group
        for i, wallet in enumerate(self.wallets):
            y_offset = i * wallet_height
            parts.append(
                '<g transform="translate(0, %d)" id="%s">' % (y_offset, wallet.checksum)
            )
            parts.append(self._svg.paper_wallet_background())
            parts.append(self._svg.share_section(wallet.address))
            parts.append(self._svg.fold_line())
            parts.append(self._svg.secret_section(wallet.wif))
            parts.append(self._svg.paper_wallet_footer(i))
            parts.append("</g>")

        parts.append(self._svg.close())
        return " ".join(parts)

    @staticmethod
    def from_single_wallet(w):
        """Create a ``KPaperWallet`` from a single wallet.

        Args:
            w: ``KSingleWallet`` instance.

        Returns:
            ``KPaperWallet`` with one wallet.
        """
        return KPaperWallet(wallets=[w.wallet])

    @staticmethod
    def from_bulk_wallet(bulk_wallet):
        """Create a ``KPaperWallet`` from a bulk wallet.

        Args:
            bulk_wallet: ``KBulkWallet`` instance.

        Returns:
            ``KPaperWallet`` containing all wallets from the bulk wallet.
        """
        return KPaperWallet(wallets=[w.wallet for w in bulk_wallet.wallets])


# -------------------
# UI/UX Classes
# -------------------
class KMenu(Menu):
    """Custom menu for the Paper Wallet Kapp.

    Extends the base Krux ``Menu`` with Paper Wallet branding
    and custom status bar display.

    Attributes:
        TITLE: Menu title displayed in the status bar.
    """

    def __init__(
        self,
        ctx,
        menu,
        offset=None,
        disable_statusbar=False,
        back_label="Back",
        back_status=lambda: MENU_EXIT,
    ):
        super().__init__(ctx, menu, offset, disable_statusbar, back_label, back_status)
        self.disable_statusbar = False
        self._title = None
        if offset is None:
            self.menu_offset = STATUS_BAR_HEIGHT
        else:
            # Always disable status bar if menu has non standard offset
            self.disable_statusbar = True
            self.menu_offset = offset if offset >= 0 else DEFAULT_PADDING

    @property
    def title(self):
        return self._title

    @title.setter
    def title(self, value: str):
        if not KManager.WALLET or not isinstance(KManager.WALLET, KBaseWallet):
            self.title = NAME
        self.title = value

    def __str__(self):
        """Return string representation of the menu."""
        return " ".join(
            [
                '<KMenu name="%s"' % self.title,
                "disable_statusbar=%s" % str(self.disable_statusbar),
                "menu_offset=%d" % self.menu_offset,
                ">",
            ]
        )

    def new_draw_wallet_indicator(self):
        """Draw the Paper Wallet title in the status bar."""
        if not kboard.is_m5stickv:
            self.ctx.display.draw_hcentered_text(
                self.title,
                STATUS_BAR_HEIGHT - FONT_HEIGHT - 1,
                theme.highlight_color,
                theme.info_bg_color,
            )
        else:
            self.ctx.display.draw_string(
                24,
                STATUS_BAR_HEIGHT - FONT_HEIGHT - 1,
                self.title,
                theme.highlight_color,
                theme.info_bg_color,
            )

    Menu.draw_wallet_indicator = new_draw_wallet_indicator


class KWalletStorage(MnemonicStorage):
    """Storage handler for encrypted paper wallets using KEF.

    Extends ``MnemonicStorage`` to handle encrypted paper wallet data
    with Krux's KEF (Krux Encrypted Format) encryption.

    Args:
        ctx: Krux ``Context`` for display and input.
    """

    def __init__(self, ctx):
        super().__init__()
        self.ctx = ctx

    def flash_error(self, msg):
        """Display an error message and wait for user acknowledgment.

        Args:
            msg: Error message to display.
        """
        self.ctx.display.clear()
        self.ctx.display.draw_centered_text(str(msg), theme.error_color)
        self.ctx.input.wait_for_button()

    def prompt(self, text, y_offset):
        """Display a yes/no confirmation prompt.

        Args:
            text: Prompt text to display.
            y_offset: Vertical position for the text.

        Returns:
            True if user pressed Enter, False otherwise.
        """
        from krux.input import BUTTON_ENTER

        self.ctx.display.draw_hcentered_text(text, y_offset)
        return self.ctx.input.wait_for_button() == BUTTON_ENTER

    def decrypt(self, key, mnemonic_id, sd_card=False):
        """Decrypt an encrypted wallet from storage.

        Args:
            key: Decryption key.
            mnemonic_id: Wallet identifier.
            sd_card: If True, load from SD card; otherwise from flash.

        Returns:
            Decrypted wallet data as string, or None on failure.
        """
        try:
            if sd_card:
                stored_value = self.stored_sd.get(mnemonic_id)
            else:
                stored_value = self.stored.get(mnemonic_id)
        except Exception as e:
            self.flash_error(e)
            return None

        if stored_value is None:
            self.flash_error("Wallet ID '%s' not found" % mnemonic_id)
            return None

        from krux import kef

        if stored_value.get("b64_kef"):
            envelope = base_decode(stored_value["b64_kef"], 64)
            id_, version, iterations, data = kef.unwrap(envelope)
            decryptor = kef.Cipher(key, id_, iterations)
            decrypted = decryptor.decrypt(data, version)
            if decrypted:
                if isinstance(decrypted, bytes):
                    return decrypted.decode("utf-8")
                return decrypted
        else:
            iterations = stored_value.get("key_iterations")
            version = stored_value.get("version")
            mode = kef.VERSIONS[version]["mode"]
            data = base_decode(stored_value.get("data"), 64)
            decrypted = self._deprecated_decrypt(
                key, mnemonic_id, iterations, mode, data
            )
            if decrypted:
                if isinstance(decrypted, bytes):
                    return decrypted.decode("utf-8")
                return decrypted
        return None


class KManager:
    """Main coordinator for the Paper Wallet Kapp.

    Manages the application flow between login (``KLogin``) and home
    (``KHome``) screens.

    Attributes:
        WALLET: Class-level storage for the currently loaded wallet.

    Args:
        ctx: Krux ``Context`` for display, input, and settings.
    """

    WALLET = None

    def __init__(self, ctx):
        self._ctx = ctx
        self._mode_name = Settings().encryption.version
        self._storage = KWalletStorage(self.ctx)

    def start(self):
        """Start the Paper Wallet application.

        Runs the login flow first to load a wallet, then proceeds
        to the home screen for wallet operations.

        Returns:
            Menu exit status.
        """
        self.on_login()
        return self.on_home()

    @property
    def ctx(self):
        """``Context``: The Krux context instance."""
        return self._ctx

    @ctx.setter
    def ctx(self, value):
        """Set the context with validation.

        Args:
            value: Must be a valid Krux ``Context``.

        Raises:
            ValueError: If value is None or not a ``Context``.
        """
        if value is None:
            raise ValueError("Context must not be None")

        if not isinstance(value, Context):
            raise ValueError("Context should be krux based")
        self._ctx = value

    def is_logged(self):
        """Check if a valid wallet has been loaded.

        Validates that ``KManager.WALLET`` is a valid ``KBaseWallet`` instance.

        Returns:
            True if a wallet is loaded and context is valid.
        """
        return (
            self.ctx is not None
            and isinstance(self.ctx, Context)
            and KManager.WALLET is not None
            and isinstance(KManager.WALLET, KBaseWallet)
            and KManager.WALLET.wallet_type in ("single", "bulk", "paper")
        )

    def on_login(self):
        """Display the login screen for wallet loading.

        Returns:
            Menu status from the login screen.
        """
        klogin = KLogin(self.ctx)
        return klogin.login()

    def on_home(self):
        """Display the home screen for wallet operations.

        Only shows if a wallet is loaded.

        Returns:
            Menu exit status.
        """
        if self.is_logged():
            khome = KHome(self.ctx)
            return khome.home()
        return MENU_EXIT


class KLogin(Login):
    """Login screen for loading paper wallets.

    Extends Krux ``Login`` page with Paper Wallet-specific options
    to load wallets from QR codes or SD card, view information
    about the Kapp, and shutdown/reboot.

    Args:
        ctx: Krux ``Context``.
    """

    def __init__(self, ctx):
        super().__init__(ctx)

    def login(self):
        """Display the main login menu.

        Returns:
            Menu exit status.
        """
        shtn_reboot_label = t("Shutdown") if kboard.has_battery else t("Reboot")
        submenu = KMenu(
            self.ctx,
            [
                (t("Load wallet"), self.load_wallet),
                (t("About"), self.about),
                (shtn_reboot_label, self.shutdown),
            ],
            back_label=None,
        )
        submenu.title = NAME

        _, status = submenu.run_loop()
        if status == MENU_SHUTDOWN:
            return MENU_SHUTDOWN
        return MENU_EXIT

    def load_wallet(self):
        """Handler for the 'Load wallet' menu item"""
        index = self.load_method()

        if index == 0:
            return self.from_qrcode()
        if index == 1:
            return self.from_sdcard()
        return MENU_EXIT

    def about(self):
        """Handler for the 'about' menu item"""
        self.ctx.display.clear()
        self.ctx.display.draw_centered_text(
            "Kapp %s\n%s: %s\n\n" % (NAME, t("Version"), VERSION)
            + t("Load paper wallets from https://bitaddress.org")
        )
        self.ctx.input.wait_for_button()
        return MENU_CONTINUE

    def from_sdcard(self):
        """Handler for the 'SDCard' ``KMenu`` item.

        Iteratively adds wallets from SD card while user does not
        confirm they are done, allowing bulk wallet creation.
        """
        return self.load_from(on_load=self.on_load_sdcard)

    def from_qrcode(self):
        """Handler for the 'From QRCode' ``KMenu`` item. It iteratively adds
        addresses and keys while user does not break the loop."""
        return self.load_from(on_load=self.on_load_qrcode)

    def on_load_qrcode(self):
        """Load ``QRCodeCapture`` instance and show the provided data into
        a QRCode to confirm, through visualization."""
        qr = QRCodeCapture(self.ctx)

        # Capture the data
        data, _ = qr.qr_capture_loop()

        # show QRCode so user can confirm
        self.display_qr_codes(
            data=data, title=": ".join(["WIF", data]), highlight_prefix=":"
        )
        return data

    def on_load_sdcard(self):
        """Uses ``KWalletStorage`` to load and decrypt a mnemonic from SD card."""
        from krux.pages.encryption_ui import EncryptionKey

        storage = KWalletStorage(self.ctx)
        wallets_ids = storage.list_mnemonics(sd_card=True)

        if not wallets_ids:
            self.flash_error(t("No wallets found"))
            return None

        submenu = Menu(
            self.ctx,
            [(id, lambda: None) for id in wallets_ids],
        )

        index, _ = submenu.run_loop()
        if index == len(wallets_ids):
            return None

        wallet_id = wallets_ids[index]

        if not self.prompt(
            t("Decrypt %s?") % wallet_id,
            self.ctx.display.height() // 2,
        ):
            return None

        keypage = EncryptionKey(self.ctx)
        key = keypage.encryption_key()
        return storage.decrypt(key, wallet_id, sd_card=True)

    def extract_wif(self, data):
        """Extract WIF from data in various formats (WIF, Base64, CSV).
        Returns the WIF string if valid, or None on error."""
        if is_wif(data):
            return data

        if is_base64(data):
            decoded = base_decode(data, 64)
            wif = base_encode(decoded, 58)
            if is_wif(wif):
                return wif
            self.flash_error(t("Invalid WIF from Base64"))
            return None

        if is_csv(data):
            parts = data.strip().split(",")
            wif = parts[-1].strip().strip('"')
            if is_wif(wif):
                return wif
            self.flash_error(t("Invalid WIF from CSV"))
            return None

        if is_svg(data):
            self.flash_error(t("SVG import not supported"))
            return None

        self.flash_error(t("Unknown format"))
        return None

    def load_from(self, on_load=None):
        """Load some wallet from ``QRCodeCapture`` or keypad."""
        on_load = normalize_on_load(on_load)
        entries = []
        index = 0

        while True:
            wallet = [index]
            self.ctx.display.clear()
            self.ctx.display.draw_hcentered_text(t("Add one or more WIFs"))
            if not self.prompt(t("Proceed?"), BOTTOM_PROMPT_LINE):
                return MENU_CONTINUE

            data = on_load()
            if data is None:
                return MENU_CONTINUE

            if not isinstance(data, str):
                self.flash_error(t("Invalid data"))
                return MENU_CONTINUE

            wif = self.extract_wif(data)
            if wif is None:
                return MENU_CONTINUE

            wallet.append(wif)
            entries.append(tuple(wallet))

            self.ctx.display.clear()
            if self.prompt(t("Done?"), self.ctx.display.height() // 2):
                break

            index += 1

        if len(entries) == 1:
            KManager.WALLET = KSingleWallet(wallet=entries[0])
        else:
            KManager.WALLET = KBulkWallet(wallets=entries)

        return MENU_EXIT


class KHome(Home):
    """Home screen for wallet operations.

    Extends Krux ``Home`` page with Paper Wallet-specific options
    to backup the loaded wallet in various formats (Base64, Hex, CSV, SVG),
    with optional encryption support.

    The menu title displays the wallet checksum for identification.

    Args:
        ctx: Krux ``Context``.
    """

    def __init__(self, ctx):
        super().__init__(ctx)

    def home(self):
        """Display the main home menu with wallet operations.

        Returns:
            Menu exit status.
        """
        shtn_reboot_label = t("Shutdown") if kboard.has_battery else t("Reboot")
        submenu = KMenu(
            self.ctx,
            [
                (t("Backup key"), lambda: self.on_key("backup")),
                (t("Export key"), lambda: self.on_key("export")),
                (t("Sign transaction"), None),
                (t("Sign message"), None),
                (shtn_reboot_label, self.shutdown),
            ],
            back_label=None,
        )
        submenu.title = KManager.WALLET.checksum

        _, status = submenu.run_loop()
        if status == MENU_SHUTDOWN:
            return MENU_SHUTDOWN
        return MENU_EXIT

    def on_key(self, kind="backup"):
        """Display the backup or export format selection menu.

        ``Backup key`` menu item will encrypt WIF(s) on ``seeds.json`` in CSV
        format while the ``Export key`` will format the wallet with the following options:

        - Base64;
        - Hex;
        - CSV;
        - SVG.

        Each can be saved as plaintext or encrypted.

        Returns:
            Menu status.
        """

        def on_save(sd_card=False):
            """Helper to backup wallets (single or bulk) to encrypted storage."""
            if isinstance(KManager.WALLET, KSingleWallet):
                return self.backup_wallet(KManager.WALLET.wif, sd_card)

            # KBulkWallet: backup each wallet
            for wallet in KManager.WALLET.wallets:
                encrypted_data, wallet_id = self._encrypt_data(wallet.wif)

                # If user cancelled encryption, stop the loop
                if encrypted_data is None:
                    return MENU_CONTINUE

                storage = KWalletStorage(self.ctx)
                if storage.store_encrypted_kef(wallet_id, encrypted_data, sd_card):
                    self.ctx.display.clear()
                    self.ctx.display.draw_centered_text(
                        t("Encrypted wallet stored with ID:") + " " + wallet_id,
                        highlight_prefix=":",
                    )
                else:
                    self.ctx.display.clear()
                    self.ctx.display.draw_centered_text(
                        t("Failed to store wallet"), theme.error_color
                    )
                self.ctx.input.wait_for_button()

            return MENU_CONTINUE

        if kind == "backup":
            submenu = KMenu(
                self.ctx,
                [
                    (t("To SDCard"), lambda: on_save(sd_card=True)),
                    (t("To Flash"), lambda: on_save(sd_card=False)),
                    (t("Back <"), lambda: MENU_EXIT),
                ],
                back_label=None,
            )
        else:
            submenu = KMenu(
                self.ctx,
                [
                    (t("to Base64"), lambda k=kind: self.to_base_64(k)),
                    (t("to Hex"), lambda k=kind: self.to_hex(k)),
                    (t("to CSV"), lambda k=kind: self.to_csv(k)),
                    (t("to SVG"), lambda k=kind: self.to_svg(k)),
                    (t("Back <"), lambda: MENU_EXIT),
                ],
                back_label=None,
            )

        submenu.title = KManager.WALLET.checksum

        _, status = submenu.run_loop()
        if status == MENU_SHUTDOWN:
            return MENU_SHUTDOWN
        return MENU_CONTINUE

    def to_base_64(self, kind):
        """Export the wallet as Base64 encoded WIF.

        Converts the WIF from Base58 to Base64 encoding.
        For bulk wallets, exports as CSV with Base64 encoded WIFs.

        Args:
            kind: Either "backup" or "export" mode.

        Returns:
            Menu continue status.
        """
        if KManager.WALLET.wallet_type == "single":
            wif = KManager.WALLET.wif
            decoded = base_decode(wif, 58)
            encoded = base_encode(decoded, 64)
            self.save_to(
                title="Base64 private key",
                plaintext=encoded,
                kind=kind,
                display_qr=True,
            )
        else:
            # Bulk wallet: CSV format with Base64 encoded WIFs
            lines = []
            for wallet in KManager.WALLET.wallets:
                decoded = base_decode(wallet.wif, 58)
                b64_wif = base_encode(decoded, 64)
                lines.append('%d, "%s", "%s"' % (wallet.index, wallet.address, b64_wif))
            encoded = "\n".join(lines)
            self.save_to(
                title="Base64 CSV",
                plaintext=encoded,
                kind=kind,
                file_extension=".csv",
                sd_card=True,
            )
        return MENU_CONTINUE

    def to_hex(self, kind):
        """Export the wallet as hexadecimal encoded WIF.

        Converts the WIF from Base58 to hexadecimal encoding.
        For bulk wallets, exports as CSV with hex encoded WIFs.

        Args:
            kind: Either "backup" or "export" mode.

        Returns:
            Menu continue status.
        """
        from binascii import hexlify

        if KManager.WALLET.wallet_type == "single":
            decoded = base_decode(KManager.WALLET.wif, 58)
            encoded = hexlify(decoded).decode("utf-8")
            self.save_to(
                title="Hex private key",
                plaintext=encoded,
                kind=kind,
                display_qr=True,
            )
        else:
            # Bulk wallet: CSV format with hex encoded WIFs
            lines = []
            for wallet in KManager.WALLET.wallets:
                decoded = base_decode(wallet.wif, 58)
                hex_wif = hexlify(decoded).decode("utf-8")
                lines.append('%d, "%s", "%s"' % (wallet.index, wallet.address, hex_wif))
            encoded = "\n".join(lines)
            self.save_to(
                title="Hex CSV",
                plaintext=encoded,
                kind=kind,
                file_extension=".csv",
                sd_card=True,
            )
        return MENU_CONTINUE

    def to_csv(self, kind):
        """Export the wallet as CSV format.

        Generates CSV with format: index, "address", "wif"
        Supports both single and bulk wallets.

        Args:
            kind: Either "backup" or "export" mode.

        Returns:
            Menu continue status.
        """
        if KManager.WALLET.wallet_type == "single":
            encoded = '%d, "%s", "%s"' % (
                KManager.WALLET.index,
                KManager.WALLET.address,
                KManager.WALLET.wif,
            )
        else:
            encoded = "\n".join(
                '%d, "%s", "%s"' % (wallet.index, wallet.address, wallet.wif)
                for wallet in KManager.WALLET.wallets
            )

        self.save_to(
            title="CSV private key",
            plaintext=encoded,
            kind=kind,
            file_extension=".csv",
            sd_card=True,
        )
        return MENU_CONTINUE

    def to_svg(self, kind):
        """Export the wallet as SVG paper wallet(s).

        Generates bitaddress.org-style paper wallet SVG files with
        SHARE and SECRET sections.

        For single wallets: Creates one SVG file.
        For bulk wallets: Creates a single combined SVG with all wallets,
        each identified by its checksum.

        Args:
            kind: Either "backup" or "export" mode.

        Returns:
            Menu continue status.
        """
        if KManager.WALLET.wallet_type == "single":
            wallet = KPaperWallet.from_single_wallet(KManager.WALLET)
        elif KManager.WALLET.wallet_type == "bulk":
            wallet = KPaperWallet.from_bulk_wallet(KManager.WALLET)
        else:
            wallet = KManager.WALLET

        # Single wallet: original behavior
        if KManager.WALLET.wallet_type == "single":
            svg_content = wallet.to_svg()[0]
            encrypt = self.prompt(t("Encrypt?"), self.ctx.display.height() // 2)
            plaintext = wallet.wallets[0].wif if encrypt else svg_content
            self.save_to(
                title="SVG paper wallet",
                plaintext=plaintext,
                encrypt=encrypt,
                kind=kind,
                file_extension=".svg",
                sd_card=True,
            )
            return MENU_CONTINUE

        # Bulk wallet: create combined SVG
        encrypt = self.prompt(t("Encrypt all?"), self.ctx.display.height() // 2)

        if not encrypt:
            # Unencrypted: combined SVG with all wallets
            svg_content = wallet.to_combined_svg()
            self._save_bulk_svg(svg_content, kind)
        else:
            # Encrypted: encrypt each wallet and create combined encrypted SVG
            encrypted_wallets = []
            for i, w in enumerate(wallet.wallets):
                decoded = base_decode(w.wif, 58)
                b64_wif = base_encode(decoded, 64)
                encrypted_data, wallet_id = self._encrypt_data(b64_wif)

                if encrypted_data is None:
                    return MENU_CONTINUE

                b64_data = base_encode(encrypted_data, 64)
                encrypted_wallets.append((b64_data, wallet_id, i))

            enc_svg = KSVG()
            svg_content = enc_svg.to_combined_encrypted_svg(encrypted_wallets)
            self._save_bulk_svg(svg_content, kind, encrypted=True)

        return MENU_CONTINUE

    def _save_bulk_svg(self, svg_content, kind, encrypted=False):
        """Save a bulk wallet combined SVG file.

        Args:
            svg_content: The combined SVG content.
            kind: Either "backup" or "export" mode.
            encrypted: Whether the SVG is encrypted.
        """
        from krux.pages.file_operations import SaveFile

        sf = SaveFile(self.ctx)
        checksum = KManager.WALLET.checksum
        suffix = "_encrypted" if encrypted else ""

        try:
            sf.save_file(
                svg_content,
                checksum,
                filename=checksum + suffix,
                file_description=t("Bulk paper wallet"),
                file_extension=".svg",
                save_as_binary=False,
            )
            self.ctx.display.clear()
            self.ctx.display.draw_centered_text(
                t("Saved:") + " " + checksum + suffix + ".svg",
                highlight_prefix=":",
            )
            self.ctx.input.wait_for_button()
        except Exception as e:
            self.flash_error(e)

    # pylint: disable=too-many-arguments
    def save_to(
        self,
        title,
        plaintext,
        encrypt=False,
        kind="backup",
        file_extension=".txt",
        sd_card=True,
        display_qr=False,
    ):
        """Save wallet data to storage.

        Dispatches to either ``backup_wallet`` or ``export_wallet`` based
        on the kind parameter.

        Args:
            title: Display title for the data.
            plaintext: The wallet data to save.
            encrypt: Whether to encrypt the data before saving.
            kind: Either "backup" (to encrypted storage) or "export" (to file).
            file_extension: File extension for exports (.txt, .csv, .svg).
            sd_card: Whether to save to SD card (for backup).
            display_qr: Whether to display QR code before saving.

        Returns:
            Menu status.
        """
        if display_qr:
            self.display_qr_codes(
                data=plaintext,
                title=title,
            )

        on_save = getattr(self, "%s_wallet" % kind)
        if kind == "backup":
            return on_save(plaintext, sd_card=sd_card)
        if kind == "export":
            # pylint: disable=too-many-function-args
            return on_save(plaintext, file_extension, encrypt)
        return MENU_CONTINUE

    def backup_wallet(self, plaintext, sd_card=False):
        """Backup wallet to encrypted KEF storage.

        Encrypts the wallet data using KEF and stores it in flash
        or SD card storage.

        Args:
            plaintext: The wallet data to encrypt and store.
            sd_card: If True, store on SD card; otherwise store in flash.

        Returns:
            Menu continue status.
        """
        encrypted_data, wallet_id = self._encrypt_data(plaintext)

        if encrypted_data is None:
            return MENU_CONTINUE

        storage = KWalletStorage(self.ctx)
        if storage.store_encrypted_kef(wallet_id, encrypted_data, sd_card):
            self.ctx.display.clear()
            self.ctx.display.draw_centered_text(
                t("Encrypted wallet stored with ID:") + " " + wallet_id,
                highlight_prefix=":",
            )
        else:
            self.ctx.display.clear()
            self.ctx.display.draw_centered_text(
                t("Failed to store wallet"), theme.error_color
            )
        self.ctx.input.wait_for_button()
        return MENU_CONTINUE

    def export_wallet(self, plaintext, file_extension=".txt", encrypt=False):
        """Export wallet data to a file.

        Saves wallet data to a file on SD card, optionally encrypting it first.
        For SVG exports, generates an encrypted paper wallet SVG.

        Args:
            plaintext: The wallet data to export.
            file_extension: File extension (.txt, .csv, or .svg).
            encrypt: Whether to encrypt the data before saving.

        Returns:
            Menu continue status.
        """
        from krux.pages.file_operations import SaveFile

        sf = SaveFile(self.ctx)
        self.ctx.display.clear()

        if not encrypt:
            try:
                sf.save_file(
                    plaintext,
                    KManager.WALLET.checksum,
                    filename=KManager.WALLET.checksum,
                    file_description="%s WIF" % KManager.WALLET.wallet_type,
                    file_extension=file_extension,
                    save_as_binary=False,
                )
            except Exception as e:
                self.flash_error(e)
            return MENU_CONTINUE

        # Encrypted export
        try:
            if file_extension in (".txt", ".csv"):
                encrypted_data, wallet_id = self._encrypt_data(plaintext)
                if encrypted_data is None:
                    return MENU_CONTINUE
                content = base_encode(encrypted_data, 64)
            else:
                # SVG: extract wallet data and create encrypted SVG
                decoded = base_decode(plaintext, 58)
                b64_wif = base_encode(decoded, 64)
                encrypted_data, wallet_id = self._encrypt_data(b64_wif)
                if encrypted_data is None:
                    return MENU_CONTINUE
                b64_data = base_encode(encrypted_data, 64)

                enc_svg = KSVG()
                wallet_index = (
                    KManager.WALLET.index if hasattr(KManager.WALLET, "index") else 0
                )
                content = enc_svg.to_encrypted_svg(
                    encrypted_data=b64_data,
                    wallet_id=wallet_id,
                    wallet_index=wallet_index,
                )

            sf.save_file(
                content,
                wallet_id,
                filename=wallet_id + "_encrypted",
                file_description=t("Encrypted wallet"),
                file_extension=file_extension,
                save_as_binary=False,
            )
            self._show_save_success(wallet_id, file_extension)
        except Exception as e:
            self.flash_error(e)
        return MENU_CONTINUE

    def _show_save_success(self, wallet_id, extension):
        """Display save success message.

        Args:
            wallet_id: The wallet identifier.
            extension: The file extension used.
        """
        self.ctx.display.clear()
        self.ctx.display.draw_centered_text(
            t("Encrypted wallet saved:") + "\n" + wallet_id + extension,
            highlight_prefix=":",
        )
        self.ctx.input.wait_for_button()

    def _encrypt_data(self, plaintext=""):
        """Encrypt wallet data using KEF envelope.

        Uses the wallet checksum as the default label for the encrypted data.

        Args:
            plaintext: The data to encrypt (string).

        Returns:
            Tuple of (encrypted_data, wallet_id) or (None, None) on failure.
        """
        kef_envelope = KEFEnvelope(self.ctx)

        # Obfuscate the wallet type by using the checksum as label
        kef_envelope.label = KManager.WALLET.checksum
        data = plaintext.encode() if isinstance(plaintext, str) else plaintext
        encrypted_data = kef_envelope.seal_ui(
            data,
            overrides=[OVERRIDE_LABEL],
            dflt_label_affirm=True,
        )

        if encrypted_data is None:
            return None, None

        wallet_id = kef_envelope.label
        return encrypted_data, wallet_id


def run(ctx):
    """Entry point for the Paper Wallet Kapp.

    This is the main function called by Krux to start the Paper Wallet
    application. It initializes the KManager and starts the application
    flow (login -> home).

    Args:
        ctx: Krux Context

    Returns:
        Menu exit status from the application.
    """
    try:
        manager = KManager(ctx)
        manager.start()
    except Exception as e:
        print(e)
