import pytest
from .test_home import tdata
from .. import create_ctx


def test_xor_bytes(mocker, m5stickv):
    from src.krux.pages.home_pages.mnemonic_xor import MnemonicXOR

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


def test_fail_private_functions(mocker, m5stickv):
    from src.krux.pages.home_pages.mnemonic_xor import MnemonicXOR

    a = b"\x05\xdc\x07\xde\x04\x20\x00\x7d\x06\x35\x00\xe1\x01\xbf\x07\x23\x05\x8e\x01\x94\x07\x4e\x00\x01"
    b = b"\x04\x11\x04\x6d\x01\xff\x03\x7d\x03\xeb\x02\xcd\x01\x06\x00\x1f\x03\x88\x03\xe0\x05\x78\x07\x63\x02\x27\x02\xe8\x06\x3e\x01\x05\x06\x20\x04\xb0\x07\x33\x01\xa2\x03\xbd\x06\x1a\x01\xd9\x04\x22"

    cases = [
        ([a, "bytes"], "_xor_bytes", "Sequences should be bytes or bytearray"),
        (["bytes", b], "_xor_bytes", "Sequences should be bytes or bytearray"),
        (["bytes"], "_bits_of_bytes", "Data should be bytes or bytearray"),
        (["bytes"], "_word11_histogram", "Entropy should be bytes or bytearray"),
    ]

    for args, fn, err in cases:
        print(f"{args}: {fn}")
        with pytest.raises(TypeError) as exc:
            _method = getattr(MnemonicXOR, fn)
            _method(*args)
        assert str(exc.value) == err


def test_fail_public_functions(mocker, m5stickv, tdata):
    from src.krux.pages.home_pages.mnemonic_xor import MnemonicXOR
    from krux.input import BUTTON_ENTER
    from krux.key import Key, TYPE_SINGLESIG
    from krux.wallet import Wallet
    from embit.networks import NETWORKS

    a = b"\x05\xdc\x07\xde\x04\x20\x00\x7d\x06\x35\x00\xe1\x01\xbf\x07\x23\x05\x8e\x01\x94\x07\x4e\x00\x01"
    b = b"\x04\x11\x04\x6d\x01\xff\x03\x7d\x03\xeb\x02\xcd\x01\x06\x00\x1f\x03\x88\x03\xe0\x05\x78\x07\x63\x02\x27\x02\xe8\x06\x3e\x01\x05\x06\x20\x04\xb0\x07\x33\x01\xa2\x03\xbd\x06\x1a\x01\xd9\x04\x22"

    key = Key(tdata.TEST_XOR_12_WORD_MNEMONIC_1, TYPE_SINGLESIG, NETWORKS["test"])
    wallet = Wallet(key)
    ctx = create_ctx(mocker, [BUTTON_ENTER, BUTTON_ENTER], wallet)
    xor = MnemonicXOR(ctx)

    cases = [
        ([a], "_xor_with_current_mnemonic", "Mnemonic should be str"),
        (["bytes"], "_validate_entropy", "Entropy should be bytes or bytearray"),
        (
            [a, "bytes", "bytes"],
            "_display_key_info",
            "Mnemonic, fingerprint and title should be str",
        ),
    ]

    for args, fn, err in cases:
        print(f"{args}: {fn}")
        with pytest.raises(TypeError) as exc:
            _method = getattr(xor, fn)
            _method(*args)
        assert str(exc.value) == err


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


def test_word11_count_and_validate_entropy(m5stickv, tdata):
    from embit.bip39 import mnemonic_to_bytes
    from krux.pages.home_pages.mnemonic_xor import MnemonicXOR, ENTROPY_THRESHOLD

    phrases = [
        tdata.TEST_XOR_12_WORD_MNEMONIC_1,
        tdata.TEST_XOR_12_WORD_MNEMONIC_2,
        tdata.TEST_XOR_12_WORD_MNEMONIC_INTERMEDIARY_RESULT,
        tdata.TEST_XOR_12_WORD_MNEMONIC_3,
        tdata.TEST_XOR_12_WORD_MNEMONIC_RESULT,
        tdata.TEST_XOR_24_WORD_MNEMONIC_1,
        tdata.TEST_XOR_24_WORD_MNEMONIC_2,
        tdata.TEST_XOR_24_WORD_MNEMONIC_INTERMEDIARY_RESULT,
        tdata.TEST_XOR_24_WORD_MNEMONIC_3,
        tdata.TEST_XOR_24_WORD_MNEMONIC_RESULT,
        tdata.SIGNING_MNEMONIC,
        "zoo zoo zoo zoo zoo zoo zoo zoo zoo zoo zoo wrong",
        "ghost spider ghost pumpkin ghost puzzle ghost spirit ghost scare ghost october",
        "you can barely avoid horror when you make seed word story mystery",
    ]

    for phrase in phrases:
        ent = mnemonic_to_bytes(phrase)
        ent_bits = len(ent) * 8
        cs_len = ent_bits // 32
        word11_count = (ent_bits + cs_len) // 11
        w11c = MnemonicXOR._word11_histogram(ent)
        assert sum(w11c) == word11_count

        bits_per_word = MnemonicXOR._shannon_sum(w11c, sum(w11c))
        is_zero = ent == bytes(len(ent))
        is_full_ff = ent == bytes([0xFF]) * len(ent)

        if is_zero or is_full_ff or bits_per_word < ENTROPY_THRESHOLD:
            with pytest.raises(ValueError, match="Low entropy"):
                MnemonicXOR._validate_entropy(ent)
        else:
            assert MnemonicXOR._validate_entropy(ent) is None


def test_mnemonic_len(mocker, m5stickv, tdata):
    from krux.pages.home_pages.mnemonic_xor import MnemonicXOR
    from krux.input import BUTTON_ENTER
    from krux.key import Key, TYPE_SINGLESIG
    from krux.wallet import Wallet
    from embit.networks import NETWORKS

    key = Key(tdata.TEST_XOR_12_WORD_MNEMONIC_1, TYPE_SINGLESIG, NETWORKS["test"])
    wallet = Wallet(key)
    ctx = create_ctx(mocker, [BUTTON_ENTER, BUTTON_ENTER], wallet)
    m = MnemonicXOR(ctx)
    assert m.choose_len_mnemonic() == 12

    key = Key(tdata.TEST_XOR_24_WORD_MNEMONIC_1, TYPE_SINGLESIG, NETWORKS["test"])
    ctx.wallet = Wallet(key)
    assert m.choose_len_mnemonic() == 24


def test_xor_with_current_mnemonic(mocker, m5stickv, tdata):
    from embit.networks import NETWORKS
    from krux.pages.home_pages.mnemonic_xor import MnemonicXOR
    from krux.key import Key, TYPE_SINGLESIG
    from krux.wallet import Wallet

    cases = [
        # https://github.com/Coldcard/firmware/blob/master/docs/seed-xor.md#12-words-xor-seed-example-using-3-parts
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
        # https://github.com/Coldcard/firmware/blob/master/docs/seed-xor.md#24-words-xor-seed-example-using-3-parts
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
        assert m._xor_with_current_mnemonic(case[1]) == case[2]
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
            m._xor_with_current_mnemonic(case[1])

        assert str(exc.value) == "Mnemonics should have same length"


def test_menu_load_and_back(mocker, m5stickv, tdata):
    from embit.networks import NETWORKS
    from krux.pages.home_pages.mnemonic_xor import MnemonicXOR
    from krux.key import Key, TYPE_SINGLESIG
    from krux.wallet import Wallet
    from krux.input import BUTTON_ENTER, BUTTON_PAGE, BUTTON_PAGE_PREV

    cases = [
        (
            BUTTON_PAGE_PREV,
            BUTTON_ENTER,
        ),
        (
            BUTTON_ENTER,
            BUTTON_PAGE_PREV,
            BUTTON_ENTER,
            BUTTON_PAGE_PREV,
            BUTTON_ENTER,
        ),
        (
            BUTTON_PAGE,
            BUTTON_ENTER,
            BUTTON_PAGE_PREV,
            BUTTON_ENTER,
            *([BUTTON_PAGE_PREV] * 2),
            BUTTON_ENTER,
        ),
        (
            *([BUTTON_PAGE] * 2),
            BUTTON_ENTER,
            BUTTON_PAGE_PREV,
            BUTTON_ENTER,
            BUTTON_PAGE,
            BUTTON_ENTER,
        ),
    ]

    n = 0
    for case in cases:
        print(f"Case {n}")
        key = Key(tdata.TEST_XOR_12_WORD_MNEMONIC_1, TYPE_SINGLESIG, NETWORKS["test"])
        wallet = Wallet(key)
        ctx = create_ctx(mocker, case, wallet)
        m = MnemonicXOR(ctx)
        m.load_key()

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
        (
            BUTTON_ENTER,
            BUTTON_ENTER,
            BUTTON_PAGE_PREV,
            BUTTON_ENTER,
            BUTTON_PAGE_PREV,
            BUTTON_ENTER,
            BUTTON_PAGE_PREV,
            BUTTON_ENTER,
        ),
        (
            BUTTON_ENTER,
            BUTTON_ENTER,
            BUTTON_ENTER,
            BUTTON_PAGE_PREV,
            BUTTON_ENTER,
            BUTTON_PAGE_PREV,
            BUTTON_ENTER,
            BUTTON_PAGE_PREV,
            BUTTON_ENTER,
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
        m.load_key()

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
        # https://github.com/Coldcard/firmware/blob/master/docs/seed-xor.md#12-words-xor-seed-example-using-3-parts
        (
            [
                BUTTON_ENTER,
                BUTTON_ENTER,
                BUTTON_ENTER,
                BUTTON_ENTER,
                BUTTON_ENTER,
            ],
            (
                tdata.TEST_XOR_12_WORD_MNEMONIC_1,
                tdata.TEST_XOR_12_WORD_MNEMONIC_2,
                tdata.TEST_XOR_12_WORD_MNEMONIC_INTERMEDIARY_RESULT,
            ),
            ("a70e2c26", "d9987b75"),
        ),
        (
            [
                BUTTON_ENTER,
                BUTTON_ENTER,
                BUTTON_ENTER,
                BUTTON_ENTER,
                BUTTON_ENTER,
            ],
            (
                tdata.TEST_XOR_12_WORD_MNEMONIC_INTERMEDIARY_RESULT,
                tdata.TEST_XOR_12_WORD_MNEMONIC_3,
                tdata.TEST_XOR_12_WORD_MNEMONIC_RESULT,
            ),
            ("d9987b75", "60259e7d"),
        ),
        # https://github.com/Coldcard/firmware/blob/master/docs/seed-xor.md#24-words-xor-seed-example-using-3-parts
        (
            [
                BUTTON_ENTER,
                BUTTON_ENTER,
                BUTTON_ENTER,
                BUTTON_ENTER,
                BUTTON_ENTER,
            ],
            (
                tdata.TEST_XOR_24_WORD_MNEMONIC_1,
                tdata.TEST_XOR_24_WORD_MNEMONIC_2,
                tdata.TEST_XOR_24_WORD_MNEMONIC_INTERMEDIARY_RESULT,
            ),
            ("e51c20a3", "0849dc5e"),
        ),
        (
            [
                BUTTON_ENTER,
                BUTTON_ENTER,
                BUTTON_ENTER,
                BUTTON_ENTER,
                BUTTON_ENTER,
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
        m.load_key()

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
        # https://github.com/Coldcard/firmware/blob/master/docs/seed-xor.md#12-words-xor-seed-example-using-3-parts
        (
            [
                BUTTON_ENTER,
                BUTTON_ENTER,
                BUTTON_ENTER,
                BUTTON_ENTER,
                BUTTON_ENTER,
            ],
            (
                tdata.TEST_XOR_12_WORD_MNEMONIC_1,
                tdata.TEST_XOR_12_WORD_MNEMONIC_2,
                tdata.TEST_XOR_12_WORD_MNEMONIC_INTERMEDIARY_RESULT,
            ),
            ("a70e2c26", "d9987b75"),
        ),
        (
            [
                BUTTON_ENTER,
                BUTTON_ENTER,
                BUTTON_ENTER,
                BUTTON_ENTER,
                BUTTON_ENTER,
            ],
            (
                tdata.TEST_XOR_12_WORD_MNEMONIC_INTERMEDIARY_RESULT,
                tdata.TEST_XOR_12_WORD_MNEMONIC_3,
                tdata.TEST_XOR_12_WORD_MNEMONIC_RESULT,
            ),
            ("d9987b75", "60259e7d"),
        ),
        # https://github.com/Coldcard/firmware/blob/master/docs/seed-xor.md#24-words-xor-seed-example-using-3-parts
        (
            [
                BUTTON_ENTER,
                BUTTON_ENTER,
                BUTTON_ENTER,
                BUTTON_ENTER,
                BUTTON_ENTER,
            ],
            (
                tdata.TEST_XOR_24_WORD_MNEMONIC_1,
                tdata.TEST_XOR_24_WORD_MNEMONIC_2,
                tdata.TEST_XOR_24_WORD_MNEMONIC_INTERMEDIARY_RESULT,
            ),
            ("e51c20a3", "0849dc5e"),
        ),
        (
            [
                BUTTON_ENTER,
                BUTTON_ENTER,
                BUTTON_ENTER,
                BUTTON_ENTER,
                BUTTON_ENTER,
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
        m.load_key()

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
        # https://github.com/Coldcard/firmware/blob/master/docs/seed-xor.md#12-words-xor-seed-example-using-3-parts
        (
            [
                BUTTON_PAGE,
                BUTTON_ENTER,
                BUTTON_ENTER,
                BUTTON_ENTER,
                *([BUTTON_ENTER] * 12),
                BUTTON_ENTER,
                BUTTON_ENTER,
                BUTTON_ENTER,
                BUTTON_ENTER,
            ],
            (
                tdata.TEST_XOR_12_WORD_MNEMONIC_1,
                tdata.TEST_XOR_12_WORD_MNEMONIC_2,
                tdata.TEST_XOR_12_WORD_MNEMONIC_INTERMEDIARY_RESULT,
            ),
            ("a70e2c26", "d9987b75"),
        ),
        (
            [
                BUTTON_PAGE,
                BUTTON_ENTER,
                BUTTON_ENTER,
                BUTTON_ENTER,
                *([BUTTON_ENTER] * 12),
                BUTTON_ENTER,
                BUTTON_ENTER,
                BUTTON_ENTER,
                BUTTON_ENTER,
            ],
            (
                tdata.TEST_XOR_12_WORD_MNEMONIC_INTERMEDIARY_RESULT,
                tdata.TEST_XOR_12_WORD_MNEMONIC_3,
                tdata.TEST_XOR_12_WORD_MNEMONIC_RESULT,
            ),
            ("d9987b75", "60259e7d"),
        ),
        # https://github.com/Coldcard/firmware/blob/master/docs/seed-xor.md#24-words-xor-seed-example-using-3-parts
        (
            [
                BUTTON_PAGE,
                BUTTON_ENTER,
                BUTTON_ENTER,
                BUTTON_ENTER,
                *([BUTTON_ENTER] * 12),
                BUTTON_PAGE_PREV,
                BUTTON_ENTER,
                *([BUTTON_ENTER] * 12),
                BUTTON_ENTER,
                BUTTON_ENTER,
                BUTTON_ENTER,
            ],
            (
                tdata.TEST_XOR_24_WORD_MNEMONIC_1,
                tdata.TEST_XOR_24_WORD_MNEMONIC_2,
                tdata.TEST_XOR_24_WORD_MNEMONIC_INTERMEDIARY_RESULT,
            ),
            ("e51c20a3", "0849dc5e"),
        ),
        (
            [
                BUTTON_PAGE,
                BUTTON_ENTER,
                BUTTON_ENTER,
                BUTTON_ENTER,
                *([BUTTON_ENTER] * 12),
                BUTTON_PAGE_PREV,
                BUTTON_ENTER,
                *([BUTTON_ENTER] * 12),
                BUTTON_ENTER,
                BUTTON_ENTER,
                BUTTON_ENTER,
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
        mocker.spy(m, "_xor_with_current_mnemonic")
        m.load_key()

        m._xor_with_current_mnemonic.assert_called_once_with(case[1][1])
        assert ctx.wallet.key.mnemonic == case[1][2]
        assert ctx.wallet.key.fingerprint.hex() == case[2][1]
        assert ctx.input.wait_for_button.call_count == len(case[0])
        n += 1


def test_export_xor_fail_low_entropy(mocker, amigo, tdata):
    from embit.networks import NETWORKS
    from krux.pages.home_pages.mnemonic_xor import MnemonicXOR
    from krux.key import Key, TYPE_SINGLESIG
    from krux.wallet import Wallet
    from krux.input import BUTTON_ENTER, BUTTON_PAGE
    from krux.qr import FORMAT_NONE
    from krux.pages.qr_capture import QRCodeCapture

    cases = [
        (
            (
                BUTTON_ENTER,
                BUTTON_ENTER,
                BUTTON_ENTER,
                *([BUTTON_PAGE] * 5),
                BUTTON_ENTER,
                *([BUTTON_PAGE] * 3),
                BUTTON_ENTER,
            ),
            tdata.SIGNING_MNEMONIC,
            "⊚\u200973c5da0a:\nLow entropy",
        ),
        (
            (
                BUTTON_ENTER,
                BUTTON_ENTER,
                BUTTON_ENTER,
                *([BUTTON_PAGE] * 5),
                BUTTON_ENTER,
                *([BUTTON_PAGE] * 3),
                BUTTON_ENTER,
            ),
            "zoo zoo zoo zoo zoo zoo zoo zoo zoo zoo zoo wrong",
            "⊚\u20093f635a63:\nLow entropy",
        ),
        (
            (
                BUTTON_ENTER,
                BUTTON_ENTER,
                BUTTON_ENTER,
                BUTTON_ENTER,
                *([BUTTON_PAGE] * 5),
                BUTTON_ENTER,
                *([BUTTON_PAGE] * 3),
                BUTTON_ENTER,
            ),
            "ghost spider ghost pumpkin ghost puzzle ghost spirit ghost scare ghost october",
            "⊚\u20096a9b363b:\nLow entropy",
        ),
        (
            (
                BUTTON_ENTER,
                BUTTON_ENTER,
                BUTTON_ENTER,
                BUTTON_ENTER,
                *([BUTTON_PAGE] * 5),
                BUTTON_ENTER,
                *([BUTTON_PAGE] * 3),
                BUTTON_ENTER,
            ),
            "you can barely avoid horror when you make seed word story mystery",
            "⊚\u2009a856927b:\nLow entropy",
        ),
    ]

    n = 0
    for case in cases:
        print(f"Case {n}")
        key = Key(tdata.TEST_XOR_12_WORD_MNEMONIC_1, TYPE_SINGLESIG, NETWORKS["test"])
        wallet = Wallet(key)
        ctx = create_ctx(mocker, case[0], wallet)

        assert ctx.wallet.key.mnemonic == tdata.TEST_XOR_12_WORD_MNEMONIC_1
        assert ctx.wallet.key.fingerprint.hex() == "a70e2c26"

        mocker.spy(ctx.display, "draw_hcentered_text")
        mocker.patch.object(
            QRCodeCapture,
            "qr_capture_loop",
            new=lambda self: (case[1], FORMAT_NONE),
        )

        m = MnemonicXOR(ctx)
        m.load_key()
        assert mocker.call([case[2]]) in ctx.display.draw_hcentered_text.mock_calls
        n += 1
