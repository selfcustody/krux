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
# pylint: skip-file
import os

# avoids importing from flash VSF
os.chdir("/")

VERSION = "1.0"
NAME = "Nostr"

from krux.pages import Menu, MENU_CONTINUE, MENU_EXIT, LETTERS, DIGITS, ESC_KEY
from krux.pages.login import Login, DIGITS_HEX
from krux.pages.home_pages.home import Home
from krux.krux_settings import t, Settings
from krux.display import (
    STATUS_BAR_HEIGHT,
    FONT_HEIGHT,
    BOTTOM_PROMPT_LINE,
    DEFAULT_PADDING,
    FONT_WIDTH,
)
from krux.themes import theme
from krux.kboard import kboard
from krux.key import Key, TYPE_SINGLESIG
from krux.wallet import Wallet
from krux.settings import MAIN_TXT, ELLIPSIS
from embit import bech32, bip32, bip39
from embit.ec import PrivateKey
from embit.networks import NETWORKS
from binascii import hexlify, unhexlify
import ujson as json
import hashlib
import time
import gc


NSEC_SIZE = 63
HEX_SIZE = 64

NSEC = "nsec"
PRIV_HEX = "priv-hex"
NPUB = "npub"
PUB_HEX = "pub-hex"
HEX = "hex"
MNEMONIC = "mnemonic"
NIP06_PATH = "m/44h/1237h/0h/0/0"

FILE_SUFFIX = "-nostr"
FILE_EXTENSION = ".txt"


# -------------------


# https://github.com/nostr-protocol/nips
class NostrEvent:

    # https://github.com/nostr-protocol/nips/blob/master/01.md
    # {
    #     "id": <32-bytes lowercase hex-encoded sha256 of the serialized event data>,
    #     "pubkey": <32-bytes lowercase hex-encoded public key of the event creator>,
    #     "created_at": <unix timestamp in seconds>,
    #     "kind": <integer between 0 and 65535>,
    #     "tags": [
    #         [<arbitrary string>...],
    #         // ...
    #     ],
    #     "content": <arbitrary string>,
    #     "sig": <64-bytes lowercase hex of the signature of the sha256 hash of the serialized event data, which is the same as the "id" field>
    # }

    # Kind types
    KIND_REGULAR = "regular"
    KIND_REPLACEABLE = "replaceable"
    KIND_EPHEMERAL = "ephemeral"
    KIND_ADDRESSABLE = "addressable"
    UNKNOWN = "unknown"

    # event mandatory attributes
    PUBKEY = "pubkey"
    CREATED_AT = "created_at"
    KIND = "kind"
    TAGS = "tags"
    CONTENT = "content"
    ID = "id"

    KIND_DESC = {
        0: "User Metadata",
        1: "Short Text Note",
        2: "Recommend Relay (deprecated)",
        3: "Follows",
        4: "Encrypted Direct Messages",
        5: "Event Deletion Request",
        6: "Repost",
        7: "Reaction",
        8: "Badge Award",
        9: "Chat Message",
        10: "Group Chat Threaded Reply (deprecated)",
        11: "Thread",
        12: "Group Thread Reply (deprecated)",
        13: "Seal",
        14: "Direct Message",
        15: "File Message",
        16: "Generic Repost",
        17: "Reaction to a website",
        20: "Picture",
        21: "Video Event",
        22: "Short-form Portrait Video Event",
        30: "internal reference",
        31: "external web reference",
        32: "hardcopy reference",
        33: "prompt reference",
        40: "Channel Creation",
        41: "Channel Metadata",
        42: "Channel Message",
        43: "Channel Hide Message",
        44: "Channel Mute User",
        62: "Request to Vanish",
        64: "Chess (PGN)",
        443: "KeyPackage",
        444: "Welcome Message",
        445: "Group Event",
        818: "Merge Requests",
        1018: "Poll Response",
        1021: "Bid",
        1022: "Bid confirmation",
        1040: "OpenTimestamps",
        1059: "Gift Wrap",
        1063: "File Metadata",
        1068: "Poll",
        1111: "Comment",
        1222: "Voice Message",
        1244: "Voice Message Comment",
        1311: "Live Chat Message",
        1337: "Code Snippet",
        1617: "Patches",
        1621: "Issues",
        1622: "Git Replies (deprecated)",
        "1630-1633": "Status",
        1971: "Problem Tracker",
        1984: "Reporting",
        1985: "Label",
        1986: "Relay reviews",
        1987: "AI Embeddings / Vector lists",
        2003: "Torrent",
        2004: "Torrent Comment",
        2022: "Coinjoin Pool",
        4550: "Community Post Approval",
        "5000-5999": "Job Request",
        "6000-6999": "Job Result",
        7000: "Job Feedback",
        7374: "Reserved Cashu Wallet Tokens",
        7375: "Cashu Wallet Tokens",
        7376: "Cashu Wallet History",
        7516: "Geocache log",
        7517: "Geocache proof of find",
        "9000-9030": "Group Control Events",
        9041: "Zap Goal",
        9321: "Nutzap",
        9467: "Tidal login",
        9734: "Zap Request",
        9735: "Zap",
        9802: "Highlights",
        10000: "Mute list",
        10001: "Pin list",
        10002: "Relay List Metadata",
        10003: "Bookmark list",
        10004: "Communities list",
        10005: "Public chats list",
        10006: "Blocked relays list",
        10007: "Search relays list",
        10009: "User groups",
        10012: "Favorite relays list",
        10013: "Private event relay list",
        10015: "Interests list",
        10019: "Nutzap Mint Recommendation",
        10020: "Media follows",
        10030: "User emoji list",
        10050: "Relay list to receive DMs",
        10051: "KeyPackage Relays List",
        10063: "User server list",
        10096: "File storage server list (deprecated)",
        10166: "Relay Monitor Announcement",
        10312: "Room Presence",
        10377: "Proxy Announcement",
        11111: "Transport Method Announcement",
        13194: "Wallet Info",
        17375: "Cashu Wallet Event",
        21000: "Lightning Pub RPC",
        22242: "Client Authentication",
        23194: "Wallet Request",
        23195: "Wallet Response",
        24133: "Nostr Connect",
        24242: "Blobs stored on mediaservers",
        27235: "HTTP Auth",
        30000: "Follow sets",
        30001: "Generic lists (deprecated)",
        30002: "Relay sets",
        30003: "Bookmark sets",
        30004: "Curation sets",
        30005: "Video sets",
        30007: "Kind mute sets",
        30008: "Profile Badges",
        30009: "Badge Definition",
        30015: "Interest sets",
        30017: "Create or update a stall",
        30018: "Create or update a product",
        30019: "Marketplace UI/UX",
        30020: "Product sold as an auction",
        30023: "Long-form Content",
        30024: "Draft Long-form Content",
        30030: "Emoji sets",
        30040: "Curated Publication Index",
        30041: "Curated Publication Content",
        30063: "Release artifact sets",
        30078: "Application-specific Data",
        30166: "Relay Discovery",
        30267: "App curation sets",
        30311: "Live Event",
        30312: "Interactive Room",
        30313: "Conference Event",
        30315: "User Statuses",
        30388: "Slide Set",
        30402: "Classified Listing",
        30403: "Draft Classified Listing",
        30617: "Repository announcements",
        30618: "Repository state announcements",
        30818: "Wiki article",
        30819: "Redirects",
        31234: "Draft Event",
        31388: "Link Set",
        31890: "Feed",
        31922: "Date-Based Calendar Event",
        31923: "Time-Based Calendar Event",
        31924: "Calendar",
        31925: "Calendar Event RSVP",
        31989: "Handler recommendation",
        31990: "Handler information",
        32267: "Software Application",
        34550: "Community Definition",
        37516: "Geocache listing",
        38172: "Cashu Mint Announcement",
        38173: "Fedimint Announcement",
        38383: "Peer-to-peer Order events",
        "39000-9": "Group metadata events",
        39089: "Starter packs",
        39092: "Media starter packs",
        39701: "Web bookmarks",
    }

    # May have different meanings depending on the kind number
    TAGS_DESC = {
        "a": "coordinates to an event",
        "A": "root address",
        "d": "identifier",
        "e": "event id (hex)",
        "E": "root event id",
        "f": "currency code",
        "g": "geohash",
        "h": "group id",
        "i": "external identity",
        "I": "root external identity",
        "k": "kind",
        "K": "root scope",
        "l": "label, label namespace, language name",
        "L": "label namespace",
        "m": "MIME type",
        "p": "pubkey (hex)",
        "P": "pubkey (hex)",
        "q": "event id (hex)",
        "r": "url / relay url",
        "s": "status",
        "t": "hashtag",
        "u": "url",
        "x": "hash",
        "y": "platform",
        "z": "order number",
        "-": "protected",
        "alt": "summary",
        "amount": "millisatoshis, stringified",
        "bolt11": "bolt11 invoice",
        "challenge": "challenge string",
        "client": "name, address",
        "clone": "git clone URL",
        "content-warning": "reason",
        "delegation": "pubkey, conditions, delegation token",
        "dep": "Required dependency",
        "description": "description",
        "emoji": "shortcode, image URL",
        "encrypted": "--",
        "extension": "File extension",
        "expiration": "unix timestamp (string)",
        "file": "full path (string)",
        "goal": "event id (hex)",
        "HEAD": "ref: refs/heads/<branch-name>",
        "image": "image URL",
        "imeta": "inline metadata",
        "license": "License of the shared content",
        "lnurl": "bech32 encoded lnurl",
        "location": "location string",
        "name": "name",
        "nonce": "random",
        "preimage": "hash of bolt11 invoice",
        "price": "price",
        "proxy": "external ID",
        "published_at": "unix timestamp (string)",
        "relay": "relay url",
        "relays": "relay list",
        "repo": "Reference to the origin repository",
        "runtime": "Runtime or environment specification",
        "server": "file storage server url",
        "subject": "subject",
        "summary": "summary",
        "thumb": "badge thumbnail",
        "title": "title",
        "tracker": "torrent tracker URL",
        "web": "webpage URL",
        "zap": "pubkey (hex), relay URL",
    }

    @classmethod
    def get_kind_type(cls, n: int):
        """The type of the kind"""
        if n < 0 or n > 65535:
            raise ValueError("Kind number must be greater than 0 and lower than 65535!")
        if 1000 <= n < 10000 or 4 <= n < 45 or n in (1, 2):
            return cls.KIND_REGULAR
        if 10000 <= n < 20000 or n in (0, 3):
            return cls.KIND_REPLACEABLE
        if 20000 <= n < 30000:
            return cls.KIND_EPHEMERAL
        if 30000 <= n < 40000:
            return cls.KIND_ADDRESSABLE
        return cls.UNKNOWN

    @classmethod
    def get_kind_desc(cls, n: int):
        """The meaning of the event"""
        try:
            return cls.KIND_DESC[n]
        except:
            if 1630 >= n <= 1633:
                return cls.KIND_DESC["1630-1633"]
            if 5000 >= n <= 5999:
                return cls.KIND_DESC["5000-5999"]
            if 6000 >= n <= 6999:
                return cls.KIND_DESC["6000-6999"]
            if 9000 >= n <= 9030:
                return cls.KIND_DESC["9000-9030"]
            if 39000 >= n <= 39009:
                return cls.KIND_DESC["39000-9"]

        return cls.UNKNOWN

    @classmethod
    def get_tag(cls, txt: str):
        """The meaning of the tag (may vary depending on the kind)"""
        try:
            return cls.TAGS_DESC[txt]
        except:
            return cls.UNKNOWN

    @classmethod
    def parse_event(cls, txt: str):
        """
        Parse a JSON-encoded event string and validate required attributes
        Returns the parsed dict if valid or raise Error
        """
        json_content = json.loads(txt)
        expected_attrs = {
            cls.PUBKEY,
            cls.CREATED_AT,
            cls.KIND,
            cls.TAGS,
            cls.CONTENT,
            cls.ID,
        }

        missing = expected_attrs - set(json_content.keys())
        if missing:
            raise ValueError("Missing expected attributes: %s." % ", ".join(missing))

        return json_content

    @classmethod
    def serialize_event(cls, event_dict: dict):
        """UTF-8 JSON-serialized string as defined in NIP-01"""
        data = [
            0,
            event_dict[cls.PUBKEY],
            event_dict[cls.CREATED_AT],
            event_dict[cls.KIND],
            event_dict[cls.TAGS],
            event_dict[cls.CONTENT],
        ]
        return json.dumps(data).replace(", ", ",").replace(": ", ":")

    @classmethod
    def validate_id(cls, event_dict: dict, serialized_event: str):
        """Validates informed id with calculated one"""
        if event_dict[cls.ID] != cls._calculate_id(serialized_event):
            raise ValueError("Attribute id do not match calculated.")
        return True

    @staticmethod
    def _calculate_id(serialized_event: str):
        """Calculates the id field of the event"""
        return hexlify(hashlib.sha256(serialized_event.encode()).digest()).decode()

    @staticmethod
    def sign_event(root, serialized_event: str):
        """Sign a serialized_event"""
        return str(
            root.schnorr_sign(hashlib.sha256(serialized_event.encode()).digest())
        )


# -------------------


class NostrKey:
    """Store and convert Nostr keys"""

    def __init__(self):
        self.set()

    def set(self, key="", value=None):
        """Set key type and its value"""
        self.key = key
        self.value = value

    def load_nsec(self, nsec: str):
        """Load a key in nsec format"""
        if len(nsec) != NSEC_SIZE:
            raise ValueError("NSEC key must be %d chars!" % NSEC_SIZE)
        _, hrp, _ = bech32.bech32_decode(nsec)
        if hrp != NSEC:
            raise ValueError("Not an nsec key!")
        self.set(NSEC, nsec)

    def load_hex(self, hex: str):
        """Load a key in hex format"""
        if len(hex) != HEX_SIZE:
            raise ValueError("Hex key must be %d chars!" % HEX_SIZE)
        # try decoding
        unhexlify(hex)
        self.set(HEX, hex)

    def load_mnemonic(self, mnemonic: str):
        """Load a mnemonic, will assume it is valid"""
        self.set(MNEMONIC, mnemonic)

    def is_loaded(self):
        """If a key was loaded"""
        return self.key != ""

    def is_mnemonic(self):
        """If loaded key is mnemonic"""
        return self.key == MNEMONIC

    @staticmethod
    def _encode_bech32(data: bytes, version: str):
        """Encode bytes into a bech32 string with given version"""
        converted_data = bech32.convertbits(data, 8, 5)
        return bech32.bech32_encode(bech32.Encoding.BECH32, version, converted_data)

    @staticmethod
    def _decode_bech32(bech: str):
        """Decode a bech32 string returning bytes"""
        _, _, data = bech32.bech32_decode(bech)
        if not data:
            raise ValueError("Invalid bech32 data")
        raw = bech32.convertbits(data, 5, 8, False)
        return bytes(raw)

    def _mnemonic_to_nip06_key(self):
        root = bip32.HDKey.from_seed(bip39.mnemonic_to_seed(self.value))
        return root.derive(NIP06_PATH)

    def get_private_key(self):
        if self.is_mnemonic():
            return self._mnemonic_to_nip06_key()
        hex_key = self.value if self.key == HEX else self.get_hex()
        return PrivateKey(unhexlify(hex_key))

    def _get_pub_xonly(self):
        return self.get_private_key().get_public_key().xonly()

    def get_hex(self):
        """Return key in hex format"""
        if self.key == HEX:
            return self.value
        if self.key == NSEC:
            return hexlify(NostrKey._decode_bech32(self.value)).decode()
        # is mnemonic
        nostr_root = self._mnemonic_to_nip06_key()
        return hexlify(nostr_root.secret).decode()

    def get_nsec(self):
        """Return key in nsec format"""
        if self.key == NSEC:
            return self.value
        if self.key == HEX:
            return NostrKey._encode_bech32(unhexlify(self.value), NSEC)
        # is mnemonic
        nostr_root = self._mnemonic_to_nip06_key()
        return NostrKey._encode_bech32(nostr_root.secret, NSEC)

    def get_pub_hex(self):
        """Return pubkey in hex format"""
        if self.key in (HEX, NSEC):
            pub_bytes = self._get_pub_xonly()
            return hexlify(pub_bytes).decode()
        # is mnemonic
        nostr_root = self._mnemonic_to_nip06_key()
        return hexlify(nostr_root.xonly()).decode()

    def get_npub(self):
        """Return pubkey in npub format"""
        if self.key in (HEX, NSEC):
            pub_bytes = self._get_pub_xonly()
            return NostrKey._encode_bech32(pub_bytes, NPUB)
        # is mnemonic
        nostr_root = self._mnemonic_to_nip06_key()
        return NostrKey._encode_bech32(nostr_root.xonly(), NPUB)


# -------------------


class KMenu(Menu):
    """Customizes the page's menu"""

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
        if offset is None:
            self.menu_offset = STATUS_BAR_HEIGHT
        else:
            # Always disable status bar if menu has non standard offset
            self.disable_statusbar = True
            self.menu_offset = offset if offset >= 0 else DEFAULT_PADDING

    def new_draw_wallet_indicator(self):
        """Customize the top bar"""
        text = NAME
        if nostrKey.is_loaded():
            if nostrKey.is_mnemonic():
                text = Key.extract_fingerprint(nostrKey.value)
            else:
                text = nostrKey.value[:9] + ELLIPSIS

        if not kboard.is_m5stickv:
            self.ctx.display.draw_hcentered_text(
                text,
                STATUS_BAR_HEIGHT - FONT_HEIGHT - 1,
                theme.highlight_color,
                theme.info_bg_color,
            )
        else:
            self.ctx.display.draw_string(
                24,
                STATUS_BAR_HEIGHT - FONT_HEIGHT - 1,
                text,
                theme.highlight_color,
                theme.info_bg_color,
            )

    def new_draw_network_indicator(self):
        """Don't draw testnet"""

    Menu.draw_wallet_indicator = new_draw_wallet_indicator
    Menu.draw_network_indicator = new_draw_network_indicator


# -------------------


class Klogin(Login):
    """Page to load a Nostr the Key"""

    def __init__(self, ctx):
        super().__init__(ctx)
        shtn_reboot_label = t("Shutdown") if kboard.has_battery else t("Reboot")
        self.menu = KMenu(
            ctx,
            [
                (t("Load Mnemonic"), self.load_key),
                (t("New Mnemonic"), self.new_key),
                (t("Load nsec or hex"), self.load_nsec),
                (t("About"), self.about),
                (shtn_reboot_label, self.shutdown),
            ],
            back_label=None,
        )

    def _load_wallet_key(self, mnemonic):
        nostrKey.load_mnemonic(mnemonic)
        self.ctx.wallet = Wallet(Key(mnemonic, TYPE_SINGLESIG, NETWORKS[MAIN_TXT]))

        return MENU_EXIT

    def load_nsec(self):
        """Load nsec or hex menu item"""

        submenu = Menu(
            self.ctx,
            [
                (t("QR Code"), self._load_nostr_priv_cam),
                (t("Via Manual Input"), self._pre_load_nostr_priv_manual),
                (
                    t("Load from SD card"),
                    None if not self.has_sd_card() else self._load_nostr_priv_sd,
                ),
            ],
        )
        index, status = submenu.run_loop()
        if index == len(submenu.menu) - 1:
            return MENU_CONTINUE
        return status

    def _pre_load_nostr_priv_manual(self):
        submenu = Menu(
            self.ctx,
            [
                (NSEC, lambda ver=NSEC: self._load_nostr_priv_manual(ver)),
                (HEX, lambda ver=HEX: self._load_nostr_priv_manual(ver)),
            ],
        )
        index, status = submenu.run_loop()
        if index == len(submenu.menu) - 1:
            return MENU_CONTINUE
        return status

    def _load_nostr_priv_cam(self):
        from krux.pages.qr_capture import QRCodeCapture

        error_msg = t("Failed to load")
        qr_capture = QRCodeCapture(self.ctx)
        data, _ = qr_capture.qr_capture_loop()
        if data is None:
            self.flash_error(error_msg)
            return MENU_CONTINUE

        try:
            data = data.decode() if not isinstance(data, str) else data
        except:
            self.flash_error(error_msg)
            return MENU_CONTINUE

        return self._load_nostr_priv_key(data)

    def _load_nostr_priv_manual(self, version):
        title = t("Private Key")

        data = ""
        if version == NSEC:
            data = NSEC

        while True:
            if version == NSEC:
                data = self.capture_from_keypad(
                    title, [LETTERS, DIGITS], starting_buffer=data
                )
            else:
                data = self.capture_from_keypad(
                    title, [DIGITS_HEX], starting_buffer=data
                )

            if data == ESC_KEY:
                return MENU_CONTINUE

            if self._load_nostr_priv_key(data) == MENU_EXIT:
                return MENU_EXIT

    def _load_nostr_priv_sd(self):
        from krux.pages.utils import Utils

        # Prompt user for file
        filename, _ = Utils(self.ctx).load_file(prompt=False, only_get_filename=True)

        if not filename:
            return MENU_CONTINUE

        from krux.sd_card import SDHandler

        data = ""
        try:
            with SDHandler() as sd:
                data = sd.read(filename)

            data = data.replace("\r\n", "").replace("\n", "")
        except:
            self.flash_error(t("Failed to load"))
            return MENU_CONTINUE

        return self._load_nostr_priv_key(data)

    def _load_nostr_priv_key(self, data: str):
        data = data.lower()

        self.ctx.display.clear()
        self.ctx.display.draw_hcentered_text(
            t("Private Key") + ":\n\n" + data, max_lines=10, highlight_prefix=":"
        )
        if not self.prompt(
            t("Proceed?"),
            BOTTOM_PROMPT_LINE,
        ):
            return MENU_CONTINUE

        if data.startswith(NSEC):
            nostrKey.load_nsec(data)
        else:
            nostrKey.load_hex(data)

        return MENU_EXIT

    # NIP-06 and NIP-19
    # mnemonic and nsec/npub
    def about(self):
        """Handler for the 'about' menu item"""

        self.ctx.display.clear()
        self.ctx.display.draw_centered_text(
            "Kapp %s\n%s: %s\n\n" % (NAME, t("Version"), VERSION)
            + t("Load or create a key to sign events. Works with NIP-06 and NIP-19.")
        )
        self.ctx.input.wait_for_button()
        return MENU_CONTINUE


# -------------------


class Khome(Home):
    """The page after loading the Key"""

    def __init__(self, ctx):
        super().__init__(ctx)

        shtn_reboot_label = t("Shutdown") if kboard.has_battery else t("Reboot")
        self.menu = KMenu(
            ctx,
            [
                (
                    t("Backup Mnemonic"),
                    (
                        self.backup_mnemonic
                        if not Settings().security.hide_mnemonic
                        and nostrKey.is_mnemonic()
                        else None
                    ),
                ),
                (t("Nostr Keys"), self.nostr_keys),
                (t("Sign Event"), self.sign_event),
                (shtn_reboot_label, self.shutdown),
            ],
            back_label=None,
        )

    def sign_event(self):
        """Handler for Sign Event menu item"""
        from krux.pages.home_pages.sign_message_ui import SignMessage

        sing_message = SignMessage(self.ctx)
        data, qr_format, message_filename = sing_message._load_message()

        self.ctx.display.clear()
        self.ctx.display.draw_centered_text(t("Processing…"))

        # memory management
        del sing_message
        gc.collect()

        if data is None:
            self.flash_error(t("Failed to load"))
            return MENU_CONTINUE

        # SD
        if message_filename:
            data = data.decode()

        pe = NostrEvent.parse_event(data)
        se = NostrEvent.serialize_event(pe)
        NostrEvent.validate_id(pe, se)

        submenu = Menu(
            self.ctx,
            [
                (t("Review Again"), lambda: None),
                (t("Sign to QR code"), lambda: None),
                (
                    t("Sign to SD card"),
                    None if not self.has_sd_card() else lambda: None,
                ),
            ],
            back_status=lambda: None,
        )
        index = 0

        while index == 0:  # Review Again
            self._show_event(pe)
            index, _ = submenu.run_loop()

        if index == submenu.back_index:  # Back
            return MENU_CONTINUE

        self.ctx.display.clear()
        self.ctx.display.draw_centered_text(t("Signing…"))

        # memory management
        del pe
        del submenu
        gc.collect()

        signed_event = NostrEvent.sign_event(nostrKey.get_private_key(), se)

        if index == 1:  # Sign to QR code
            from krux.pages.utils import Utils

            utils = Utils(self.ctx)

            while True:
                self.display_qr_codes(signed_event, qr_format)
                utils.print_standard_qr(
                    signed_event, qr_format, t("Signed Event"), width=45
                )
                self.ctx.display.clear()
                if self.prompt(t("Done?"), self.ctx.display.height() // 2):
                    return MENU_CONTINUE

        # index == 2: Sign to SD card
        from krux.sd_card import SDHandler, SIGNED_FILE_SUFFIX, SIGNATURE_FILE_EXTENSION
        from krux.pages.file_operations import SaveFile

        save_page = SaveFile(self.ctx)
        message_filename = save_page.set_filename(
            message_filename,
            "QRCode",
            SIGNED_FILE_SUFFIX,
            SIGNATURE_FILE_EXTENSION,
        )

        if message_filename and message_filename != ESC_KEY:
            try:
                with SDHandler() as sd:
                    sd.write(message_filename, signed_event)
                    self.flash_text(
                        t("Saved to SD card:") + "\n\n%s" % message_filename,
                        highlight_prefix=":",
                    )
                    return MENU_CONTINUE
            except OSError:
                self.flash_error(t("SD card not detected."))

        return MENU_CONTINUE

    def _show_event(self, pe: dict):
        created = time.localtime(pe[NostrEvent.CREATED_AT])
        kind = pe[NostrEvent.KIND]
        unique_tags = {item[0] for item in pe[NostrEvent.TAGS]}
        txt = t("Created:")
        txt += " %s-%02d-%02d %02d:%02d" % created[:5]
        txt += "\n\n"

        txt += t("Kind:")
        txt += " %d %s {%s}" % (
            kind,
            NostrEvent.get_kind_desc(kind),
            NostrEvent.get_kind_type(kind),
        )
        txt += "\n\n"

        txt += t("Tags:")
        if unique_tags:
            txt += " " + ", ".join(
                "'%s' %s" % (tag, NostrEvent.get_tag(tag)) for tag in unique_tags
            )
            txt += "\n\n"
        txt += " | ".join(", ".join(sublist) for sublist in pe[NostrEvent.TAGS])
        txt += "\n\n"

        txt += t("Content:")
        txt += " %s" % pe[NostrEvent.CONTENT]

        offset_x = (
            DEFAULT_PADDING
            if not kboard.is_m5stickv
            else (self.ctx.display.width() % FONT_WIDTH) // 2
        )

        startpos = endpos = 0
        txt_size = len(txt)
        prefixes = [t("Created:"), t("Kind:"), t("Tags:"), t("Content:")]
        while True:
            lines, endpos = self.ctx.display.to_lines_endpos(txt[startpos:])
            self.ctx.display.clear()
            for i, line in enumerate(lines):
                self.ctx.display.draw_string(
                    offset_x,
                    (i * (FONT_HEIGHT)),
                    line,
                )
                if any(line.startswith(p) for p in prefixes):
                    prefixes.pop(0)
                    prefix_index = line.find(":")
                    if prefix_index > -1:
                        self.ctx.display.draw_string(
                            offset_x,
                            (i * (FONT_HEIGHT)),
                            line[: prefix_index + 1],
                            theme.highlight_color,
                        )
            startpos += endpos
            self.ctx.input.wait_for_fastnav_button()
            if startpos >= txt_size:
                break

    def nostr_keys(self):
        """Handler for Nostr Keys menu item"""
        submenu = Menu(
            self.ctx,
            [
                (
                    t("Private Key"),
                    lambda: self.show_key_formats([NSEC, PRIV_HEX]),
                ),
                (t("Public Key"), lambda: self.show_key_formats([NPUB, PUB_HEX])),
            ],
        )
        index, status = submenu.run_loop()
        if index == len(submenu.menu) - 1:
            return MENU_CONTINUE
        return status

    def show_key_formats(self, versions):
        """Create menu to select Nostr keys in text or QR"""

        def _nostr_key_text(version):
            def _save_nostr_to_sd(version):
                from krux.pages.file_operations import SaveFile

                save_page = SaveFile(self.ctx)
                title = version + FILE_SUFFIX
                save_page.save_file(
                    self._get_nostr_key(version),
                    title,
                    title,
                    title + ":",
                    FILE_EXTENSION,
                    save_as_binary=False,
                )

            nostr_text_menu_items = [
                (
                    t("Save to SD card"),
                    (
                        None
                        if not self.has_sd_card()
                        else lambda ver=version: _save_nostr_to_sd(ver)
                    ),
                ),
            ]
            full_nostr_key = (
                self._get_nostr_title(version)
                + ":\n\n"
                + str(self._get_nostr_key(version))
            )
            menu_offset = 5 + len(self.ctx.display.to_lines(full_nostr_key))
            menu_offset *= FONT_HEIGHT
            nostr_key_menu = Menu(self.ctx, nostr_text_menu_items, offset=menu_offset)
            self.ctx.display.clear()
            self.ctx.display.draw_hcentered_text(
                full_nostr_key,
                offset_y=FONT_HEIGHT,
                info_box=True,
                highlight_prefix=":",
            )
            nostr_key_menu.run_loop()

        def _nostr_key_qr(version):
            title = self._get_nostr_title(version)
            nostr_key = str(self._get_nostr_key(version))
            from krux.pages.qr_view import SeedQRView

            seed_qr_view = SeedQRView(self.ctx, data=nostr_key, title=title)
            seed_qr_view.display_qr(allow_export=True, transcript_tools=False)

        pub_key_menu_items = []
        for version in versions:
            title = version if version not in (PRIV_HEX, PUB_HEX) else HEX
            pub_key_menu_items.append(
                (title + " - " + t("Text"), lambda ver=version: _nostr_key_text(ver))
            )
            pub_key_menu_items.append(
                (title + " - " + t("QR Code"), lambda ver=version: _nostr_key_qr(ver))
            )
        pub_key_menu = Menu(self.ctx, pub_key_menu_items)
        while True:
            _, status = pub_key_menu.run_loop()
            if status == MENU_EXIT:
                break

        return MENU_CONTINUE

    def _get_nostr_title(self, version):
        if version == NPUB:
            return "Public Key npub"
        if version == PUB_HEX:
            return "Public Key hex"
        if version == NSEC:
            return "Private Key nsec"
        return "Private Key hex"

    def _get_nostr_key(self, version):
        if version == NPUB:
            return nostrKey.get_npub()
        if version == NSEC:
            return nostrKey.get_nsec()
        if version == PRIV_HEX:
            return nostrKey.get_hex()
        return nostrKey.get_pub_hex()


# -------------------


def run(ctx):
    """Runs this kapp"""

    Klogin(ctx).run()

    if nostrKey.is_loaded():
        Khome(ctx).run()


nostrKey = NostrKey()

# use try / catch and threat exceptions to avoid error?
# Could not execute nostr
