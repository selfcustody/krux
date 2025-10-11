import pytest
from .test_home import tdata
from .. import create_ctx


def test_xor_bytes(mocker, m5stickv):
    from src.krux.pages.home_pages.mnemonic_xor import MnemonicXOR

    # bytes_0 XOR bytest_1 = result_bytes
    cases = [
        # Basic cases for single bytes
        (b"\x00", b"\x00", b"\x00"),
        (b"\x00", b"\x01", b"\x01"),
        (b"\x00", b"\x10", b"\x10"),
        (b"\x10", b"\x10", b"\x00"),
        (b"\x11", b"\x10", b"\x01"),
        (b"\x11", b"\x01", b"\x10"),
        # Case from https://github.com/Coldcard/firmware/blob/master/docs/seed-xor.md
        # A = 5DC 7DE 420 07D 635 0E1 1BF 723 58E 194 74E 001 46E 68C 2BF 22E 3FB 5A9 59B 4BF 275 59F 210 5DF
        # B = 411 46D 1FF 37D 3EB 2CD 106 01F 388 3E0 578 763 227 2E8 63E 105 620 4B0 733 1A2 3BD 61A 1D9 422
        # C = 78E 4AF 18F 644 4F0 2EC 70A 3FA 100 59B 6EB 7EE 2F5 6D1 63C 52F 573 169 219 2AC 625 6FB 69C 234
        # X = 643 71C 450 544 12E 0C0 7B3 4C6 706 7EF 4DD 08C 4BC 2B5 2BD 604 0A8 070 0B1 7B1 7ED 57E 555 3xx
        # final word between: gas [300] - lend [3FF]
        # correct final word: indoor [398]
        # We had 3C9, is between the final but isn't one from CC docs
        (
            b"\x05\xdc\x07\xde\x04\x20\x00\x7d\x06\x35\x00\xe1\x01\xbf\x07\x23\x05\x8e\x01\x94\x07\x4e\x00\x01\x04\x6e\x06\x8c\x02\xbf\x02\x2e\x03\xfb\x05\xa9\x05\x9b\x04\xbf\x02\x75\x05\x9f\x02\x10\x05\xdf",
            b"\x04\x11\x04\x6d\x01\xff\x03\x7d\x03\xeb\x02\xcd\x01\x06\x00\x1f\x03\x88\x03\xe0\x05\x78\x07\x63\x02\x27\x02\xe8\x06\x3e\x01\x05\x06\x20\x04\xb0\x07\x33\x01\xa2\x03\xbd\x06\x1a\x01\xd9\x04\x22",
            b"\x01\xcd\x03\xb3\x05\xdf\x03\x00\x05\xde\x02\x2c\x00\xb9\x07\x3c\x06\x06\x02\x74\x02\x36\x07\x62\x06\x49\x04\x64\x04\x81\x03\x2b\x05\xdb\x01\x19\x02\xa8\x05\x1d\x01\xc8\x03\x85\x03\xc9\x01\xfd",
        ),
        (
            b"\x01\xcd\x03\xb3\x05\xdf\x03\x00\x05\xde\x02\x2c\x00\xb9\x07\x3c\x06\x06\x02\x74\x02\x36\x07\x62\x06\x49\x04\x64\x04\x81\x03\x2b\x05\xdb\x01\x19\x02\xa8\x05\x1d\x01\xc8\x03\x85\x03\xc9\x01\xfd",
            b"\x07\x8e\x04\xaf\x01\x8f\x06\x44\x04\xf0\x02\xec\x07\x0a\x03\xfa\x01\x00\x05\x9b\x06\xeb\x07\xee\x02\xf5\x06\xd1\x06\x3c\x05\x2f\x05\x73\x01\x69\x02\x19\x02\xac\x06\x25\x06\xfb\x06\x9c\x02\x34",
            b"\x06\x43\x07\x1c\x04\x50\x05\x44\x01\x2e\x00\xc0\x07\xb3\x04\xc6\x07\x06\x07\xef\x04\xdd\x00\x8c\x04\xbc\x02\xb5\x02\xbd\x06\x04\x00\xa8\x00\x70\x00\xb1\x07\xb1\x07\xed\x05\x7e\x05\x55\x03\xc9",
        ),
    ]

    n = 0
    for case in cases:
        print(f"Case: {n}")
        assert MnemonicXOR._xor_bytes(case[0], case[1]) == case[2]
        n += 1


def test_fail_xor_bytes_different_lengths(mocker, m5stickv):
    from src.krux.pages.home_pages.mnemonic_xor import MnemonicXOR

    a = b"\x05\xdc\x07\xde\x04\x20\x00\x7d\x06\x35\x00\xe1\x01\xbf\x07\x23\x05\x8e\x01\x94\x07\x4e\x00\x01"
    b = b"\x04\x11\x04\x6d\x01\xff\x03\x7d\x03\xeb\x02\xcd\x01\x06\x00\x1f\x03\x88\x03\xe0\x05\x78\x07\x63\x02\x27\x02\xe8\x06\x3e\x01\x05\x06\x20\x04\xb0\x07\x33\x01\xa2\x03\xbd\x06\x1a\x01\xd9\x04\x22"

    with pytest.raises(ValueError) as exc:
        MnemonicXOR._xor_bytes(a, b)

    assert str(exc.value) == "Sequences should have same length"

    with pytest.raises(ValueError) as exc:
        MnemonicXOR._xor_bytes(b, a)

    assert str(exc.value) == "Sequences should have same length"


def test_xor_with_current_mnemonic(mocker, m5stickv, tdata):
    from embit.networks import NETWORKS
    from krux.pages.home_pages.mnemonic_xor import MnemonicXOR
    from krux.key import Key, TYPE_SINGLESIG
    from krux.wallet import Wallet

    cases = [
        # Case from https://github.com/Coldcard/firmware/blob/master/docs/seed-xor.md#12-words-xor-seed-example-using-3-parts
        (
            tdata.TEST_XOR_12_WORD_MNEMONIC_1,
            tdata.TEST_XOR_12_WORD_MNEMONIC_2,
            tdata.TEST_XOR_12_WORD_MNEMONIC_INTERMEDIARY_RESULT,
        ),
        (
            tdata.TEST_XOR_12_WORD_MNEMONIC_INTERMEDIARY_RESULT,
            tdata.TEST_XOR_12_WORD_MNEMONIC_3,
            tdata.TEST_XOR_12_WORD_MNEMONIC_RESULT,
        ),
        # Case from https://github.com/Coldcard/firmware/blob/master/docs/seed-xor.md#24-words-xor-seed-example-using-3-parts
        (
            tdata.TEST_XOR_24_WORD_MNEMONIC_1,
            tdata.TEST_XOR_24_WORD_MNEMONIC_2,
            tdata.TEST_XOR_24_WORD_MNEMONIC_INTERMEDIARY_RESULT,
        ),
        (
            tdata.TEST_XOR_24_WORD_MNEMONIC_INTERMEDIARY_RESULT,
            tdata.TEST_XOR_24_WORD_MNEMONIC_3,
            tdata.TEST_XOR_24_WORD_MNEMONIC_RESULT,
        ),
    ]

    n = 0
    for case in cases:
        print(f"Case: {n}")
        key = Key(case[0], TYPE_SINGLESIG, NETWORKS["test"])
        wallet = Wallet(key)
        ctx = create_ctx(mocker, case, wallet)
        m = MnemonicXOR(ctx)
        assert m.xor_with_current_mnemonic(case[1]) == case[2]
        n += 1


def test_fail_xor_mnemonics_different_lengths(mocker, m5stickv, tdata):
    from embit.networks import NETWORKS
    from krux.pages.home_pages.mnemonic_xor import MnemonicXOR
    from krux.key import Key, TYPE_SINGLESIG
    from krux.wallet import Wallet

    cases = [
        (tdata.TEST_XOR_12_WORD_MNEMONIC_1, tdata.TEST_XOR_24_WORD_MNEMONIC_1),
        (tdata.TEST_XOR_12_WORD_MNEMONIC_2, tdata.TEST_XOR_24_WORD_MNEMONIC_2),
        (tdata.TEST_XOR_12_WORD_MNEMONIC_3, tdata.TEST_XOR_24_WORD_MNEMONIC_3),
        (
            tdata.TEST_XOR_12_WORD_MNEMONIC_INTERMEDIARY_RESULT,
            tdata.TEST_XOR_24_WORD_MNEMONIC_INTERMEDIARY_RESULT,
        ),
        (
            tdata.TEST_XOR_12_WORD_MNEMONIC_RESULT,
            tdata.TEST_XOR_24_WORD_MNEMONIC_RESULT,
        ),
    ]

    for case in cases:
        with pytest.raises(ValueError) as exc:
            key = Key(case[0], TYPE_SINGLESIG, NETWORKS["test"])
            wallet = Wallet(key)
            ctx = create_ctx(mocker, case, wallet)
            m = MnemonicXOR(ctx)
            m.xor_with_current_mnemonic(case[1])

            assert str(exc.value) == "Mnemonics should have same length"


def test_menu_load_and_back(mocker, m5stickv, tdata):
    from embit.networks import NETWORKS
    from krux.pages.home_pages.mnemonic_xor import MnemonicXOR
    from krux.key import Key, TYPE_SINGLESIG
    from krux.wallet import Wallet
    from krux.input import BUTTON_ENTER, BUTTON_PAGE, BUTTON_PAGE_PREV

    cases = [
        (
            BUTTON_PAGE_PREV,  # Move to Back
            BUTTON_ENTER,  # Press Back
        ),
        (
            BUTTON_ENTER,  # Press "Via camera"
            BUTTON_PAGE_PREV,  # Move to Back
            BUTTON_ENTER,  # Press Back
            BUTTON_PAGE_PREV,  # Move to "Back"
            BUTTON_ENTER,  # Press "Back"
        ),
        (
            BUTTON_PAGE,  # Move to "Via manual input"
            BUTTON_ENTER,  # Press "Via manual input"
            BUTTON_PAGE_PREV,  # Move to Back
            BUTTON_ENTER,  # Press Back
            *([BUTTON_PAGE_PREV] * 2),  # Move to "Back"
            BUTTON_ENTER,  # Press "Back"
        ),
        (
            *([BUTTON_PAGE] * 2),  # Move to "Via storage"
            BUTTON_ENTER,  # Press "Via storage
            BUTTON_PAGE_PREV,  # Move to Back
            BUTTON_ENTER,  # Press Back
            BUTTON_PAGE,  # Move to "Back"
            BUTTON_ENTER,  # Press "Back"
        ),
    ]

    n = 0
    for case in cases:
        print(f"Case {n}")
        key = Key(tdata.TEST_XOR_12_WORD_MNEMONIC_1, TYPE_SINGLESIG, NETWORKS["test"])
        wallet = Wallet(key)
        ctx = create_ctx(mocker, case, wallet)
        m = MnemonicXOR(ctx)
        m.load()

        assert ctx.wallet.key.fingerprint.hex() == "a70e2c26"
        assert ctx.input.wait_for_button.call_count == len(case)
        n += 1


def test_menu_load_qrcode_and_back(mocker, amigo, tdata):
    from embit.networks import NETWORKS
    from krux.pages.home_pages.mnemonic_xor import MnemonicXOR
    from krux.key import Key, TYPE_SINGLESIG
    from krux.wallet import Wallet
    from krux.input import BUTTON_ENTER, BUTTON_PAGE, BUTTON_PAGE_PREV
    from krux.qr import FORMAT_NONE
    from krux.pages.qr_capture import QRCodeCapture

    cases = [
        # Not accept the part
        (
            BUTTON_ENTER,  # Press "Via camera"
            BUTTON_ENTER,  # QRCode
            BUTTON_PAGE_PREV,  # Move to "No"
            BUTTON_ENTER,  # Press "No"
            BUTTON_PAGE_PREV,  # Move to Back
            BUTTON_ENTER,  # Press Back
            BUTTON_PAGE_PREV,  # Move to Back
            BUTTON_ENTER,  # Press Back
        ),
        # Load the part, but not accept the fingerprint
        (
            BUTTON_ENTER,  # Press "Via camera"
            BUTTON_ENTER,  # QRCode
            BUTTON_ENTER,  # Press "Yes"
            BUTTON_PAGE_PREV,  # Move to "No"
            BUTTON_ENTER,  # Press "No"
            BUTTON_PAGE_PREV,  # Move to back
            BUTTON_ENTER,  # Press back
            BUTTON_PAGE_PREV,  # Move to back
            BUTTON_ENTER,  # Press back
        ),
    ]

    n = 0

    for case in cases:
        print(f"Case {n}")
        key = Key(tdata.TEST_XOR_12_WORD_MNEMONIC_1, TYPE_SINGLESIG, NETWORKS["test"])
        wallet = Wallet(key)
        ctx = create_ctx(mocker, case, wallet)

        mocker.patch.object(
            QRCodeCapture,
            "qr_capture_loop",
            new=lambda self: (tdata.TEST_XOR_12_WORD_MNEMONIC_2, FORMAT_NONE),
        )

        m = MnemonicXOR(ctx)
        m.load()

        assert ctx.wallet.key.fingerprint.hex() == "a70e2c26"
        assert ctx.input.wait_for_button.call_count == len(case)
        n += 1


def test_load_from_qrcode(mocker, amigo, tdata):
    from embit.networks import NETWORKS
    from krux.pages.home_pages.mnemonic_xor import MnemonicXOR
    from krux.key import Key, TYPE_SINGLESIG
    from krux.wallet import Wallet
    from krux.input import BUTTON_ENTER, BUTTON_PAGE_PREV
    from krux.qr import FORMAT_NONE
    from krux.pages.qr_capture import QRCodeCapture

    cases = [
        # Case from https://github.com/Coldcard/firmware/blob/master/docs/seed-xor.md#12-words-xor-seed-example-using-3-parts
        # Via camera, QRCode, XOR 12, 1st XOR 2nd shares
        (
            [
                BUTTON_ENTER,  # Press "Via camera"
                BUTTON_ENTER,  # QRCode
                BUTTON_ENTER,  # Press "Yes" to accept part words
                BUTTON_ENTER,  # Press "Yes" to Proceed after see fingerprints
                BUTTON_ENTER,  # Press "Yes" to accept XORed words
            ],
            (
                tdata.TEST_XOR_12_WORD_MNEMONIC_1,
                tdata.TEST_XOR_12_WORD_MNEMONIC_2,
                tdata.TEST_XOR_12_WORD_MNEMONIC_INTERMEDIARY_RESULT,
            ),
            ("a70e2c26", "d9987b75"),
        ),
        # Via camera, QRCode, XOR 12, (1st XOR 2nd) XOR 3rd shares
        (
            [
                BUTTON_ENTER,  # Press "Via camera"
                BUTTON_ENTER,  # QRCode
                BUTTON_ENTER,  # Press "Yes" to accept part words
                BUTTON_ENTER,  # Press "Yes" to Proceed after see fingerprints
                BUTTON_ENTER,  # Press "Yes" to accept XORed words
            ],
            (
                tdata.TEST_XOR_12_WORD_MNEMONIC_INTERMEDIARY_RESULT,
                tdata.TEST_XOR_12_WORD_MNEMONIC_3,
                tdata.TEST_XOR_12_WORD_MNEMONIC_RESULT,
            ),
            ("d9987b75", "60259e7d"),
        ),
        # Case from https://github.com/Coldcard/firmware/blob/master/docs/seed-xor.md#24-words-xor-seed-example-using-3-parts
        # Via camera, QRCode, XOR 24, 1st XOR 2nd
        (
            [
                BUTTON_ENTER,  # Press "Via camera"
                BUTTON_ENTER,  # QRCode
                BUTTON_ENTER,  # Press "Yes" to accept part words
                BUTTON_ENTER,  # Press "Yes" to Proceed after see fingerprints
                BUTTON_ENTER,  # Press "Yes" to accept XORed words
            ],
            (
                tdata.TEST_XOR_24_WORD_MNEMONIC_1,
                tdata.TEST_XOR_24_WORD_MNEMONIC_2,
                tdata.TEST_XOR_24_WORD_MNEMONIC_INTERMEDIARY_RESULT,
            ),
            ("e51c20a3", "0849dc5e"),
        ),
        # Via camera, QRCode, XOR 24, (1st XOR 2nd) XOR 3rd
        (
            [
                BUTTON_ENTER,  # Press "Via camera"
                BUTTON_ENTER,  # QRCode
                BUTTON_ENTER,  # Press "Yes" to accept part words
                BUTTON_ENTER,  # Press "Yes" to Proceed after see fingerprints
                BUTTON_ENTER,  # Press "Yes" to accept XORed words
            ],
            (
                tdata.TEST_XOR_24_WORD_MNEMONIC_INTERMEDIARY_RESULT,
                tdata.TEST_XOR_24_WORD_MNEMONIC_3,
                tdata.TEST_XOR_24_WORD_MNEMONIC_RESULT,
            ),
            ("0849dc5e", "e335e9c4"),
        ),
    ]

    n = 0

    for case in cases:
        print(f"Case {n}")
        key = Key(case[1][0], TYPE_SINGLESIG, NETWORKS["test"])
        wallet = Wallet(key)
        ctx = create_ctx(mocker, case[0], wallet)

        assert ctx.wallet.key.mnemonic == case[1][0]
        assert ctx.wallet.key.fingerprint.hex() == case[2][0]

        mocker.patch.object(
            QRCodeCapture,
            "qr_capture_loop",
            new=lambda self: (case[1][1], FORMAT_NONE),
        )

        m = MnemonicXOR(ctx)
        m.load()

        assert ctx.wallet.key.mnemonic == case[1][2]
        assert ctx.wallet.key.fingerprint.hex() == case[2][1]
        assert ctx.input.wait_for_button.call_count == len(case[0])
        n += 1


def test_load_from_qrcode_with_hide_mnemonic(mocker, amigo, tdata):
    from embit.networks import NETWORKS
    from krux.pages.home_pages.mnemonic_xor import MnemonicXOR
    from krux.key import Key, TYPE_SINGLESIG
    from krux.wallet import Wallet
    from krux.input import BUTTON_ENTER
    from krux.qr import FORMAT_NONE
    from krux.pages.qr_capture import QRCodeCapture
    from krux.krux_settings import Settings

    cases = [
        # Case from https://github.com/Coldcard/firmware/blob/master/docs/seed-xor.md#12-words-xor-seed-example-using-3-parts
        # Via camera, QRCode, XOR 12, 1st XOR 2nd shares
        (
            [
                BUTTON_ENTER,  # Press "Via camera"
                BUTTON_ENTER,  # QRCode
                BUTTON_ENTER,  # Press "Yes" to accept part words
                BUTTON_ENTER,  # Press "Yes" to Proceed after see fingerprints
                BUTTON_ENTER,  # Press "Yes" to accept XORed words
            ],
            (
                tdata.TEST_XOR_12_WORD_MNEMONIC_1,
                tdata.TEST_XOR_12_WORD_MNEMONIC_2,
                tdata.TEST_XOR_12_WORD_MNEMONIC_INTERMEDIARY_RESULT,
            ),
            ("a70e2c26", "d9987b75"),
        ),
        # Via camera, QRCode, XOR 12, (1st XOR 2nd) XOR 3rd shares
        (
            [
                BUTTON_ENTER,  # Press "Via camera"
                BUTTON_ENTER,  # QRCode
                BUTTON_ENTER,  # Press "Yes" to accept part words
                BUTTON_ENTER,  # Press "Yes" to Proceed after see fingerprints
                BUTTON_ENTER,  # Press "Yes" to accept XORed words
            ],
            (
                tdata.TEST_XOR_12_WORD_MNEMONIC_INTERMEDIARY_RESULT,
                tdata.TEST_XOR_12_WORD_MNEMONIC_3,
                tdata.TEST_XOR_12_WORD_MNEMONIC_RESULT,
            ),
            ("d9987b75", "60259e7d"),
        ),
        # Case from https://github.com/Coldcard/firmware/blob/master/docs/seed-xor.md#24-words-xor-seed-example-using-3-parts
        # Via camera, QRCode, XOR 24, 1st XOR 2nd
        (
            [
                BUTTON_ENTER,  # Press "Via camera"
                BUTTON_ENTER,  # QRCode
                BUTTON_ENTER,  # Press "Yes" to accept part words
                BUTTON_ENTER,  # Press "Yes" to Proceed after see fingerprints
                BUTTON_ENTER,  # Press "Yes" to accept XORed words
            ],
            (
                tdata.TEST_XOR_24_WORD_MNEMONIC_1,
                tdata.TEST_XOR_24_WORD_MNEMONIC_2,
                tdata.TEST_XOR_24_WORD_MNEMONIC_INTERMEDIARY_RESULT,
            ),
            ("e51c20a3", "0849dc5e"),
        ),
        # Via camera, QRCode, XOR 24, (1st XOR 2nd) XOR 3rd
        (
            [
                BUTTON_ENTER,  # Press "Via camera"
                BUTTON_ENTER,  # QRCode
                BUTTON_ENTER,  # Press "Yes" to accept part words
                BUTTON_ENTER,  # Press "Yes" to Proceed after see fingerprints
                BUTTON_ENTER,  # Press "Yes" to accept XORed words
            ],
            (
                tdata.TEST_XOR_24_WORD_MNEMONIC_INTERMEDIARY_RESULT,
                tdata.TEST_XOR_24_WORD_MNEMONIC_3,
                tdata.TEST_XOR_24_WORD_MNEMONIC_RESULT,
            ),
            ("0849dc5e", "e335e9c4"),
        ),
    ]

    n = 0

    for case in cases:
        print(f"Case {n}")
        Settings().security.hide_mnemonic = True
        key = Key(case[1][0], TYPE_SINGLESIG, NETWORKS["test"])
        wallet = Wallet(key)
        ctx = create_ctx(mocker, case[0], wallet)

        assert ctx.wallet.key.mnemonic == case[1][0]
        assert ctx.wallet.key.fingerprint.hex() == case[2][0]

        mocker.patch.object(
            QRCodeCapture,
            "qr_capture_loop",
            new=lambda self: (case[1][1], FORMAT_NONE),
        )

        m = MnemonicXOR(ctx)
        m.load()

        assert ctx.wallet.key.mnemonic == case[1][2]
        assert ctx.wallet.key.fingerprint.hex() == case[2][1]
        assert ctx.input.wait_for_button.call_count == len(case[0])
        n += 1


def test_export_from_words(mocker, amigo, tdata):
    from embit.networks import NETWORKS
    from krux.pages.home_pages.mnemonic_xor import MnemonicXOR
    from krux.key import Key, TYPE_SINGLESIG
    from krux.wallet import Wallet
    from krux.input import BUTTON_ENTER, BUTTON_PAGE, BUTTON_PAGE_PREV
    from krux.qr import FORMAT_NONE

    cases = [
        # Case from https://github.com/Coldcard/firmware/blob/master/docs/seed-xor.md#12-words-xor-seed-example-using-3-parts
        # Via manual input/words, QRCode, XOR 12, 1st XOR 2nd shares
        (
            [
                BUTTON_PAGE,  # Move to "Via Manual Input"
                BUTTON_ENTER,  # Press "Via Manual Input"
                BUTTON_ENTER,  # Words
                BUTTON_ENTER,  # Press "Yes" for "Enter each word of your BIP39 mnemonic"
                *([BUTTON_ENTER] * 12),  # Accept each word
                BUTTON_ENTER,  # Done "Yes"
                BUTTON_ENTER,  # Press "Yes" to accept part words
                BUTTON_ENTER,  # Press "Yes" to Proceed after see fingerprints
                BUTTON_ENTER,  # Press "Yes" to accept XORed words
            ],
            (
                tdata.TEST_XOR_12_WORD_MNEMONIC_1,
                tdata.TEST_XOR_12_WORD_MNEMONIC_2,
                tdata.TEST_XOR_12_WORD_MNEMONIC_INTERMEDIARY_RESULT,
            ),
            ("a70e2c26", "d9987b75"),
        ),
        # Via manual input/words, QRCode, XOR 12, (1st XOR 2nd) XOR 3rd shares
        (
            [
                BUTTON_PAGE,  # Move to "Via Manual Input"
                BUTTON_ENTER,  # Press "Via Manual Input"
                BUTTON_ENTER,  # Words
                BUTTON_ENTER,  # Press "Yes" for "Enter each word of your BIP39 mnemonic"
                *([BUTTON_ENTER] * 12),  # Accept each word
                BUTTON_ENTER,  # Done "Yes"
                BUTTON_ENTER,  # Press "Yes" to accept part words
                BUTTON_ENTER,  # Press "Yes" to Proceed after see fingerprints
                BUTTON_ENTER,  # Press "Yes" to accept XORed words
            ],
            (
                tdata.TEST_XOR_12_WORD_MNEMONIC_INTERMEDIARY_RESULT,
                tdata.TEST_XOR_12_WORD_MNEMONIC_3,
                tdata.TEST_XOR_12_WORD_MNEMONIC_RESULT,
            ),
            ("d9987b75", "60259e7d"),
        ),
        # Case from https://github.com/Coldcard/firmware/blob/master/docs/seed-xor.md#24-words-xor-seed-example-using-3-parts
        # Via manual input/words, QRCode, XOR 24, 1st XOR 2nd shares
        (
            [
                BUTTON_PAGE,  # Move to "Via Manual Input"
                BUTTON_ENTER,  # Press "Via Manual Input"
                BUTTON_ENTER,  # Words
                BUTTON_ENTER,  # Press "Yes" for "Enter each word of your BIP39 mnemonic"
                *([BUTTON_ENTER] * 12),  # Accept each word
                BUTTON_PAGE_PREV,  # Move to "No" (we do not finished)
                BUTTON_ENTER,  # Press "No",
                *([BUTTON_ENTER] * 12),  # Accept each word
                BUTTON_ENTER,  # Press "Yes" to accept part words
                BUTTON_ENTER,  # Press "Yes" to Proceed after see fingerprints
                BUTTON_ENTER,  # Press "Yes" to accept XORed words
            ],
            (
                tdata.TEST_XOR_24_WORD_MNEMONIC_1,
                tdata.TEST_XOR_24_WORD_MNEMONIC_2,
                tdata.TEST_XOR_24_WORD_MNEMONIC_INTERMEDIARY_RESULT,
            ),
            ("e51c20a3", "0849dc5e"),
        ),
        # Via manual input/words, QRCode, XOR 24, (1st XOR 2nd) XOR 3rd shares
        (
            [
                BUTTON_PAGE,  # Move to "Via Manual Input"
                BUTTON_ENTER,  # Press "Via Manual Input"
                BUTTON_ENTER,  # Words
                BUTTON_ENTER,  # Press "Yes" for "Enter each word of your BIP39 mnemonic"
                *([BUTTON_ENTER] * 12),  # Accept each word
                BUTTON_PAGE_PREV,  # Move to "No" (we do not finished)
                BUTTON_ENTER,  # Press "No",
                *([BUTTON_ENTER] * 12),  # Accept each word
                BUTTON_ENTER,  # Press "Yes" to accept part words
                BUTTON_ENTER,  # Press "Yes" to Proceed after see fingerprints
                BUTTON_ENTER,  # Press "Yes" to accept XORed words
            ],
            (
                tdata.TEST_XOR_24_WORD_MNEMONIC_INTERMEDIARY_RESULT,
                tdata.TEST_XOR_24_WORD_MNEMONIC_3,
                tdata.TEST_XOR_24_WORD_MNEMONIC_RESULT,
            ),
            ("0849dc5e", "e335e9c4"),
        ),
    ]

    n = 0
    for case in cases:
        print(f"Case {n}")
        key = Key(case[1][0], TYPE_SINGLESIG, NETWORKS["test"])
        wallet = Wallet(key)
        ctx = create_ctx(mocker, case[0], wallet)

        assert ctx.wallet.key.mnemonic == case[1][0]
        assert ctx.wallet.key.fingerprint.hex() == case[2][0]
        words = case[1][1].split(" ")

        m = MnemonicXOR(ctx)
        mocker.patch.object(m, "capture_from_keypad", side_effect=words)
        mocker.spy(m, "xor_with_current_mnemonic")
        m.load()

        m.xor_with_current_mnemonic.assert_called_once_with(case[1][1])
        assert ctx.wallet.key.mnemonic == case[1][2]
        assert ctx.wallet.key.fingerprint.hex() == case[2][1]
        assert ctx.input.wait_for_button.call_count == len(case[0])
        n += 1


def test_export_xor_to_same_mnemonic_from_qrcode(mocker, amigo, tdata):
    from embit.networks import NETWORKS
    from krux.pages.home_pages.mnemonic_xor import MnemonicXOR
    from krux.key import Key, TYPE_SINGLESIG
    from krux.wallet import Wallet
    from krux.input import BUTTON_ENTER, BUTTON_PAGE
    from krux.qr import FORMAT_NONE
    from krux.pages.qr_capture import QRCodeCapture

    BTN_SEQUENCE = [
        BUTTON_ENTER,  # Press "Via camera"
        BUTTON_ENTER,  # QRCode
        BUTTON_ENTER,  # Press "Yes" to accept part words (will raise error)
        *([BUTTON_PAGE] * 5),  # Move to back
        BUTTON_ENTER,  # Press back
        *([BUTTON_PAGE] * 3),  # Move to back
        BUTTON_ENTER,  # Press back
    ]

    key = Key(tdata.TEST_XOR_12_WORD_MNEMONIC_1, TYPE_SINGLESIG, NETWORKS["test"])
    wallet = Wallet(key)
    ctx = create_ctx(mocker, BTN_SEQUENCE, wallet)

    assert ctx.wallet.key.mnemonic == tdata.TEST_XOR_12_WORD_MNEMONIC_1
    assert ctx.wallet.key.fingerprint.hex() == "a70e2c26"

    mocker.spy(ctx.display, "draw_centered_text")
    mocker.patch.object(
        QRCodeCapture,
        "qr_capture_loop",
        new=lambda self: (tdata.SIGNING_MNEMONIC, FORMAT_NONE),
    )

    m = MnemonicXOR(ctx)
    m.load()
    ctx.display.draw_centered_text.assert_has_calls(
        [mocker.call("Error:\nValueError('Low entropy mnemonic')", 248)],
        any_order=True,
    )


def test_export_xor_to_inverted_mnemonic_from_qrcode(mocker, amigo, tdata):
    from embit.networks import NETWORKS
    from krux.pages.home_pages.mnemonic_xor import MnemonicXOR
    from krux.key import Key, TYPE_SINGLESIG
    from krux.wallet import Wallet
    from krux.input import BUTTON_ENTER, BUTTON_PAGE, BUTTON_PAGE_PREV
    from krux.qr import FORMAT_NONE
    from krux.pages.qr_capture import QRCodeCapture

    ZOO = "zoo zoo zoo zoo zoo zoo zoo zoo zoo zoo zoo wrong"
    BTN_SEQUENCE = [
        BUTTON_ENTER,  # Press "Via camera"
        BUTTON_ENTER,  # QRCodeCapture
        BUTTON_ENTER,  # Press "Yes" to accept part words (will raise error)
        *([BUTTON_PAGE] * 5),  # Move to back
        BUTTON_ENTER,  # Press back
        *([BUTTON_PAGE] * 3),  # Move to back
        BUTTON_ENTER,  # Press back
    ]

    key = Key(tdata.TEST_XOR_12_WORD_MNEMONIC_1, TYPE_SINGLESIG, NETWORKS["test"])
    wallet = Wallet(key)
    ctx = create_ctx(mocker, BTN_SEQUENCE, wallet)

    assert ctx.wallet.key.mnemonic == tdata.TEST_XOR_12_WORD_MNEMONIC_1
    assert ctx.wallet.key.fingerprint.hex() == "a70e2c26"

    mocker.spy(ctx.display, "draw_centered_text")
    mocker.patch.object(
        QRCodeCapture,
        "qr_capture_loop",
        new=lambda self: (ZOO, FORMAT_NONE),
    )

    m = MnemonicXOR(ctx)
    m.load()
    ctx.display.draw_centered_text.assert_has_calls(
        [mocker.call("Error:\nValueError('Low entropy mnemonic')", 248)],
        any_order=True,
    )


def test_export_xor_low_entropy_mnemonic_from_qrcode(mocker, amigo, tdata):
    from embit.networks import NETWORKS
    from krux.pages.home_pages.mnemonic_xor import MnemonicXOR
    from krux.key import Key, TYPE_SINGLESIG
    from krux.wallet import Wallet
    from krux.input import BUTTON_ENTER, BUTTON_PAGE, BUTTON_PAGE_PREV
    from krux.qr import FORMAT_NONE
    from krux.pages.qr_capture import QRCodeCapture

    DANGEROUS = (
        "dutch aerobic know utility deer toilet siege breeze evolve sniff bike wrap"
    )
    BTN_SEQUENCE = [
        BUTTON_ENTER,  # Press "Via camera"
        BUTTON_ENTER,  # QRCodeCapture
        BUTTON_ENTER,  # Press "Yes" to accept part words (will raise error)
        *([BUTTON_PAGE] * 5),  # Move to back
        BUTTON_ENTER,  # Press back
        *([BUTTON_PAGE] * 3),  # Move to back
        BUTTON_ENTER,  # Press back
    ]

    key = Key(tdata.TEST_XOR_12_WORD_MNEMONIC_1, TYPE_SINGLESIG, NETWORKS["test"])
    wallet = Wallet(key)
    ctx = create_ctx(mocker, BTN_SEQUENCE, wallet)

    assert ctx.wallet.key.mnemonic == tdata.TEST_XOR_12_WORD_MNEMONIC_1
    assert ctx.wallet.key.fingerprint.hex() == "a70e2c26"

    mocker.spy(ctx.display, "draw_centered_text")
    mocker.patch.object(
        QRCodeCapture,
        "qr_capture_loop",
        new=lambda self: (DANGEROUS, FORMAT_NONE),
    )

    m = MnemonicXOR(ctx)
    m.load()
    ctx.display.draw_centered_text.assert_has_calls(
        [mocker.call("Error:\nValueError('Low entropy mnemonic')", 248)],
        any_order=True,
    )
