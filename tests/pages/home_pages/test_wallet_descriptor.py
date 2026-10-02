import pytest
from ...shared_mocks import MockPrinter
from .. import create_ctx, assert_not_flashed
from .test_home import tdata
from ...test_wallet import tdata as wallet_tdata


def test_wallet(mocker, m5stickv, tdata):
    from krux.pages.home_pages.wallet_descriptor import WalletDescriptor
    from krux.wallet import Wallet
    from krux.input import BUTTON_ENTER, BUTTON_PAGE
    from krux.qr import FORMAT_PMOFN
    from krux.pages.qr_capture import QRCodeCapture

    cases = [
        # 0 Don't load
        (
            False,  # if descriptor will be automatically loaded
            tdata.SINGLESIG_12_WORD_KEY,  # mnemonic for wallet
            tdata.SPECTER_SINGLESIG_WALLET_DATA,  # wallet descriptor
            None,  # Printer
            [BUTTON_PAGE],  # btn_seq
        ),
        # 1 Load, from camera, good data - accept
        (
            False,
            tdata.SINGLESIG_12_WORD_KEY,
            tdata.SPECTER_SINGLESIG_WALLET_DATA,
            None,
            [BUTTON_ENTER, BUTTON_ENTER, BUTTON_ENTER],
        ),
        # 2 Load, from camera, good data, decline
        (
            False,
            tdata.SINGLESIG_12_WORD_KEY,
            tdata.SPECTER_SINGLESIG_WALLET_DATA,
            None,
            [BUTTON_ENTER, BUTTON_ENTER, BUTTON_PAGE],
        ),
        # 3 Load, from camera, bad capture
        (False, tdata.SINGLESIG_12_WORD_KEY, None, None, [BUTTON_ENTER, BUTTON_ENTER]),
        # 4 Load, from camera, bad wallet data
        (
            False,
            tdata.SINGLESIG_12_WORD_KEY,
            "{}",
            None,
            [BUTTON_ENTER, BUTTON_ENTER, BUTTON_ENTER],
        ),
        # 5 No print prompt
        (
            True,
            tdata.SINGLESIG_12_WORD_KEY,
            tdata.SPECTER_SINGLESIG_WALLET_DATA,
            None,
            [BUTTON_ENTER, BUTTON_ENTER],
        ),
        # 6 Print
        (
            True,
            tdata.SINGLESIG_12_WORD_KEY,
            tdata.SPECTER_SINGLESIG_WALLET_DATA,
            MockPrinter(),
            [BUTTON_ENTER, BUTTON_ENTER, BUTTON_ENTER],
        ),
        # 7 Decline to print
        (
            True,
            tdata.SINGLESIG_12_WORD_KEY,
            tdata.SPECTER_SINGLESIG_WALLET_DATA,
            MockPrinter(),
            [BUTTON_ENTER, BUTTON_ENTER, BUTTON_PAGE],
        ),
        # 8 Multisig wallet, no print prompt
        (
            True,
            tdata.MULTISIG_12_WORD_KEY,
            tdata.SPECTER_MULTISIG_WALLET_DATA,
            None,
            [BUTTON_ENTER, BUTTON_ENTER],
        ),
        # 9 Load, from SD card, good data, accept
        (
            False,
            tdata.SINGLESIG_12_WORD_KEY,
            tdata.SPECTER_SINGLESIG_WALLET_DATA,
            None,
            [BUTTON_ENTER, BUTTON_PAGE, BUTTON_ENTER, BUTTON_ENTER],
        ),
    ]

    num = 0
    for case in cases:
        print("case: %d" % num)
        num = num + 1
        wallet = Wallet(case[1])
        if case[0]:
            wallet.load(case[2], FORMAT_PMOFN)
            assert wallet.has_change_addr()

        ctx = create_ctx(mocker, case[4], wallet, case[3])
        wallet_descriptor = WalletDescriptor(ctx)
        mocker.patch.object(wallet_descriptor, "has_sd_card", return_value=True)
        mocker.patch.object(
            QRCodeCapture, "qr_capture_loop", new=lambda self: (case[2], FORMAT_PMOFN)
        )
        qr_capturer = mocker.spy(QRCodeCapture, "qr_capture_loop")
        mocker.patch.object(
            wallet_descriptor,
            "display_qr_codes",
            new=lambda data, qr_format, title=None: ctx.input.wait_for_button(),
        )
        mocker.spy(wallet_descriptor, "display_loading_wallet")
        mocker.spy(wallet_descriptor, "display_wallet")

        # Mock SD card descriptor loading
        if case[4][:3] == [BUTTON_ENTER, BUTTON_PAGE, BUTTON_ENTER]:
            mock_utils = mocker.patch("krux.pages.utils.Utils")
            mock_utils.return_value.load_file.return_value = (
                "descriptor.txt",
                case[2],
            )

        wallet_descriptor.wallet()

        if case[0]:
            # If wallet is already loaded
            wallet_descriptor.display_wallet.assert_called_once()
            assert ctx.wallet.has_change_addr()
        else:
            # If accepted the message and choose to load from camera
            if case[4][:2] == [BUTTON_ENTER, BUTTON_ENTER]:
                qr_capturer.assert_called_once()
                if case[2] is not None and case[2] != "{}":
                    wallet_descriptor.display_loading_wallet.assert_called_once()
                    assert ctx.wallet.has_change_addr()
            # If accepted the message and choose to load from SD
            elif case[4][:3] == [BUTTON_ENTER, BUTTON_PAGE, BUTTON_ENTER]:
                if case[2] is not None and case[2] != "{}":
                    wallet_descriptor.display_loading_wallet.assert_called_once()
                    assert ctx.wallet.has_change_addr()
        assert ctx.input.wait_for_button.call_count == len(case[4])


def test_wallet_load_sd_back_is_silent(mocker, m5stickv, tdata):
    from krux.pages.home_pages.wallet_descriptor import WalletDescriptor
    from krux.wallet import Wallet
    from krux.input import BUTTON_ENTER, BUTTON_PAGE
    from krux.pages import MENU_CONTINUE

    btn_seq = [
        BUTTON_ENTER,  # confirm load
        BUTTON_PAGE,  # go to "Load from SD card"
        BUTTON_ENTER,  # select "Load from SD card"
    ]

    wallet = Wallet(tdata.SINGLESIG_12_WORD_KEY)
    ctx = create_ctx(mocker, btn_seq, wallet)
    wallet_descriptor = WalletDescriptor(ctx)
    mocker.patch.object(wallet_descriptor, "has_sd_card", return_value=True)
    mock_utils = mocker.patch("krux.pages.utils.Utils")
    # user backed out of the SD file browser
    mock_utils.return_value.load_file.return_value = ("", None)

    assert wallet_descriptor.wallet() == MENU_CONTINUE
    assert ctx.input.wait_for_button.call_count == len(btn_seq)

    # "Back" is not a failure - it must not flash an error
    assert_not_flashed(ctx, "Failed to load")


def test_wallet_load_fails_on_decrypt_kef_key_error(mocker, m5stickv, tdata):
    from krux.input import BUTTON_ENTER, BUTTON_PAGE, BUTTON_PAGE_PREV
    from krux.pages.home_pages.wallet_descriptor import WalletDescriptor
    from krux.wallet import Wallet
    from krux.pages.qr_capture import QRCodeCapture
    from krux.pages import MENU_CONTINUE

    # nonsensical 0x8f byte encrypted w/ key="a" to test decryption failure
    mocker.patch.object(
        QRCodeCapture,
        "qr_capture_loop",
        new=lambda self: (
            b"\x06binkey\x05\x01\x88WB\xb9\xab\xb6\xe9\x83\x97y\x1ab\xb0F\xe2|\xd3E\x84\x2b\x2c",
            0,
        ),
    )

    btn_seq = [
        BUTTON_ENTER,  # confirm load
        BUTTON_ENTER,  # go load from camera
        BUTTON_ENTER,  # confirm decrypt
        BUTTON_ENTER,  # type key
        BUTTON_PAGE,  # to "b"
        BUTTON_ENTER,  # enter "b"
        BUTTON_PAGE_PREV,  # back to "a"
        BUTTON_PAGE_PREV,  # back to Go
        BUTTON_ENTER,  # go Go
        BUTTON_ENTER,  # confirm key "b" (while "a" is correct key)
    ]
    wallet = Wallet(tdata.SINGLESIG_12_WORD_KEY)
    ctx = create_ctx(mocker, btn_seq, wallet)
    walletdescriptor_ui = WalletDescriptor(ctx)
    assert walletdescriptor_ui.wallet() == MENU_CONTINUE
    assert ctx.input.wait_for_button.call_count == len(btn_seq)
    ctx.display.flash_text.assert_called_with(
        "Failed to decrypt", 248, 2000, highlight_prefix=""
    )


def test_wallet_load_fails_on_encrypted_non_ascii_bytes(mocker, m5stickv, tdata):
    from krux.input import BUTTON_ENTER, BUTTON_PAGE_PREV
    from krux.pages.home_pages.wallet_descriptor import WalletDescriptor
    from krux.wallet import Wallet
    from krux.pages.qr_capture import QRCodeCapture
    from krux.pages import MENU_CONTINUE

    # non-ascii 0x8f byte encrypted w/ key="a" to test decoding failure
    # in Cpython: UnicodeDecodeError is raised; in MaixPy: TypeError is raised
    mocker.patch.object(
        QRCodeCapture,
        "qr_capture_loop",
        new=lambda self: (
            b"\x06binkey\x05\x01\x88WB\xb9\xab\xb6\xe9\x83\x97y\x1ab\xb0F\xe2|\xd3E\x84\x2b\x2c",
            0,
        ),
    )

    btn_seq = [
        BUTTON_ENTER,  # confirm load
        BUTTON_ENTER,  # go load from camera
        BUTTON_ENTER,  # confirm decrypt
        BUTTON_ENTER,  # type key
        BUTTON_ENTER,  # enter "a"
        BUTTON_PAGE_PREV,  # back to Go
        BUTTON_ENTER,  # go Go
        BUTTON_ENTER,  # confirm key "a"
    ]
    wallet = Wallet(tdata.SINGLESIG_12_WORD_KEY)
    ctx = create_ctx(mocker, btn_seq, wallet)
    walletdescriptor_ui = WalletDescriptor(ctx)
    assert walletdescriptor_ui.wallet() == MENU_CONTINUE
    assert ctx.input.wait_for_button.call_count == len(btn_seq)
    ctx.display.flash_text.assert_called_with(
        "Failed to load", 248, 2000, highlight_prefix=""
    )


def test_load_desc_without_change(mocker, m5stickv, tdata):
    import krux

    mocker.patch("krux.krux_settings.t", side_effect=lambda slug: slug)

    from krux.pages.home_pages.wallet_descriptor import WalletDescriptor
    from krux.wallet import Wallet
    from krux.input import BUTTON_ENTER, BUTTON_PAGE
    from krux.qr import FORMAT_PMOFN
    from krux.pages.qr_capture import QRCodeCapture
    from krux.display import BOTTOM_PROMPT_LINE

    btn_seq = [
        BUTTON_ENTER,  # Load wallet descriptor?
        BUTTON_ENTER,  # Load from camera menu item
        BUTTON_ENTER,  # Could not determine change Proceed anyway?
        BUTTON_ENTER,  # Load?
    ]
    wallet = Wallet(tdata.SINGLESIG_ACTION_KEY_TEST_P2WPKH)
    ctx = create_ctx(mocker, btn_seq, wallet)

    wallet_descriptor = WalletDescriptor(ctx)
    mocker.spy(wallet_descriptor, "prompt")

    descriptor = b"wpkh([e0c595c5/84h/1h/0h]tpubDCberYHnzBMaKUa34hXGTNXECt9bKprGKtqYt2Bm4qGFK3bqMkMA6KxRR1kPPSh73QoX6LtmsArgNYXRw8HnkWwc8ywf7Ru6XcxRnJo9HfW/2/*)#tykcfujt"
    mocker.patch.object(
        QRCodeCapture, "qr_capture_loop", new=lambda self: (descriptor, FORMAT_PMOFN)
    )

    assert not ctx.wallet.is_loaded()

    wallet_descriptor.wallet()

    krux.krux_settings.t.assert_has_calls(
        [
            mocker.call("Could not determine change address."),
        ]
    )

    wallet_descriptor.prompt.assert_has_calls(
        [
            mocker.call("Proceed anyway?", BOTTOM_PROMPT_LINE),
        ]
    )

    assert ctx.wallet.is_loaded()
    assert (
        not ctx.wallet.has_change_addr()
    )  # the loaded descriptor doesn't have change addr

    assert ctx.input.wait_for_button.call_count == len(btn_seq)


def test_cancel_load_desc_without_change(mocker, m5stickv, tdata):
    import krux

    mocker.patch("krux.krux_settings.t", side_effect=lambda slug: slug)

    from krux.pages.home_pages.wallet_descriptor import WalletDescriptor
    from krux.wallet import Wallet
    from krux.input import BUTTON_ENTER, BUTTON_PAGE
    from krux.qr import FORMAT_PMOFN
    from krux.pages.qr_capture import QRCodeCapture
    from krux.display import BOTTOM_PROMPT_LINE

    btn_seq = [
        BUTTON_ENTER,  # Load wallet descriptor?
        BUTTON_ENTER,  # Load from camera menu item
        BUTTON_PAGE,  # Could not determine change Proceed anyway?
    ]
    wallet = Wallet(tdata.SINGLESIG_ACTION_KEY_TEST_P2WPKH)
    ctx = create_ctx(mocker, btn_seq, wallet)

    wallet_descriptor = WalletDescriptor(ctx)
    mocker.spy(wallet_descriptor, "prompt")

    descriptor = b"wpkh([e0c595c5/84h/1h/0h]tpubDCberYHnzBMaKUa34hXGTNXECt9bKprGKtqYt2Bm4qGFK3bqMkMA6KxRR1kPPSh73QoX6LtmsArgNYXRw8HnkWwc8ywf7Ru6XcxRnJo9HfW/2/*)#tykcfujt"
    mocker.patch.object(
        QRCodeCapture, "qr_capture_loop", new=lambda self: (descriptor, FORMAT_PMOFN)
    )

    assert not ctx.wallet.is_loaded()

    wallet_descriptor.wallet()

    krux.krux_settings.t.assert_has_calls(
        [
            mocker.call("Could not determine change address."),
        ]
    )

    wallet_descriptor.prompt.assert_has_calls(
        [
            mocker.call("Proceed anyway?", BOTTOM_PROMPT_LINE),
        ]
    )

    assert not ctx.wallet.is_loaded()  # continue unloaded
    assert ctx.wallet.has_change_addr()  # single-sig per default has change addr

    assert ctx.input.wait_for_button.call_count == len(btn_seq)


def test_loading_miniscript_descriptors(mocker, amigo, wallet_tdata):
    """Miniscript specific tests. Always load from camera"""
    from krux.pages.home_pages.wallet_descriptor import WalletDescriptor
    from krux.wallet import Wallet
    from krux.input import BUTTON_ENTER, BUTTON_PAGE
    from krux.qr import FORMAT_PMOFN
    from krux.pages.qr_capture import QRCodeCapture

    TRIDENT_DESCRIPTOR = "wsh(andor(multi(2,[fbf14e49/45h/1h/0h/3h]tpubDEPmZmWcL9G3XEbhBy6A5UG7tR4hAT7zvhu4cVmCSbVPhjkfuYRgqFnUfG4Gm1NSaoo412nzyRe3UAtC73BHQbVDLz4nAkrhJDSxcYSpUnz/<0;1>/*,[525cb3d5/45h/1h/0h/3h]tpubDF4yVr6ohjK1hQgyHvtLpanC4JxkshsMVUDHfmDvpXcBzdD2peXKdhfLFVNWQekAYAN1vU81dUNfgokZb1foUQfDMtf6X8mb3vMs7cYHbcr/<0;1>/*,[5fc83bce/45h/1h/0h/3h]tpubDFMqbP9gd34rd5Db2hHVYsJA3LnBD2fZo6zWFzeAA2kUC27cndyN2axBs55K9qJSghbvZx1Nyrrvb2ixgLXRzyK7dLLnXHGAmHe7apv4XwU/<0;1>/*),or_i(and_v(v:pkh([5acaced1/49h/1h/0h]tpubDDXMHf1PVPUPYHKyR9b5pbsfcd4SDC5FHtx7msTwazX4gkZPCRjoTYB2mFR4HsiybdptPtKH7yyoogx9d2gvc92SaoCYANEdZYqRR6FJKGx/<0;1>/*),after(230436)),thresh(2,pk([5ecc195f/48h/1h/0h/2h]tpubDFfTpjFSFT9FFvWwXand2JfnRBSpekQQpzdoz5qm8fy6cUhjLdTBuNrqxdsFgyTJ6xr5oeUAqa28VHPMprbosXLhGEgJW4SPa31tuSmp9Ub/<0;1>/*),s:pk([a1088994/48h/1h/0h/2h]tpubDFE64qjVGZ8L31gXFNtRUUpbaZ5viPgkFpth8j3XfGNWgaM6Vsm3F4z1nNE1soY3cQc6YZtNqMqfrywkeAQMiiYnR8N1oyFP5YuuFYTQ2nx/<0;1>/*),s:pk([8faeabe8/48h/1h/0h/2h]tpubDEMz5Gib3V3i1xzY4yaKH2k2J4MBRjNYNSace1YHMr6MgaM1oLZ4qiF7mWQvGPm9gH5bgroqPMr44viw16XWYoig6rbCQrkzakJw6hsapFw/<0;1>/*),snl:after(230220))),and_v(v:thresh(2,pkh([2bd4a49f/84h/1h/1h]tpubDCtwDKhf7tMtt2NDNrWsN7tFQSEvoKt9qvSBMUPuZVnoR52FwSaQS37UT5skDddUyzhVEGJozGxu8CBJPPc8MXhXidD7azaubMHgNCPvq28/<0;1>/*),a:pkh([d38f3599/84h/1h/2h]tpubDDYgycbJd7DgJjKFd4W8Dp8RRNhDDYfLs93cjhBP6boyXiZxdUyZc8fuLMJyetQXq6i9xfYSJwEf1GYxmND6jXExLS9q9ibP2YXZxtqe7mK/<0;1>/*),a:pkh([001ceab0/84h/1h/3h]tpubDCuJUyHrMq4PY4fXEHyADTkFwgy498AnuhrhFzgT7tWuuwp9JAeopqMTre99nzEVnqJNsJk21VRLeLsGz4cA5hboULrupdHqiZdxKRLJV9R/<0;1>/*)),after(230775))))#5flg0r73"

    cases = [
        # 0 - Key
        # 1 - Wallet descriptor
        # 2 - Button sequence
        (  # Miniscript key, Liana miniscript descriptor
            wallet_tdata.MINISCRIPT_KEY,
            wallet_tdata.LIANA_MINISCRIPT_DESCRIPTOR,
            [
                BUTTON_ENTER,  # Load? Yes
                BUTTON_ENTER,  # Load from camera
                BUTTON_ENTER,  # Accept
            ],
        ),
        (  # No key, Liana miniscript descriptor
            None,
            wallet_tdata.LIANA_MINISCRIPT_DESCRIPTOR,
            [
                BUTTON_ENTER,  # Load? Yes
                BUTTON_ENTER,  # Load from camera
                BUTTON_ENTER,  # Accept
            ],
        ),
        (  # No Key, Trident descriptor
            None,
            TRIDENT_DESCRIPTOR,
            [
                BUTTON_ENTER,  # Load? Yes
                BUTTON_ENTER,  # Load from camera
                BUTTON_ENTER,  # To next page
                BUTTON_ENTER,  # To next page
                BUTTON_ENTER,  # To next page
                BUTTON_ENTER,  # Accept
            ],
        ),
        (  # Taproot miniscript key, Liana taproot miniscript descriptor
            wallet_tdata.TAP_MINISCRIPT_KEY,
            wallet_tdata.LIANA_TAPROOT_MINISCRIPT_DESCRIPTOR,
            [
                BUTTON_ENTER,  # Load? Yes
                BUTTON_ENTER,  # Load from camera
                BUTTON_ENTER,  # Accept
            ],
        ),
        (  # Taproot miniscript key, Liana taproot expanding multisig miniscript descriptor
            wallet_tdata.TAP_MINISCRIPT_KEY,
            wallet_tdata.LIANA_TAP_EXPANDING_MINISCRIPT_DESCRIPTOR,
            [
                BUTTON_ENTER,  # Load? Yes
                BUTTON_ENTER,  # Load from camera
                BUTTON_ENTER,  # To next page
                BUTTON_ENTER,  # Accept
            ],
        ),
    ]

    for case in cases:
        ctx = create_ctx(mocker, case[2], Wallet(case[0]))
        wallet_descriptor = WalletDescriptor(ctx)
        mocker.patch.object(
            QRCodeCapture, "qr_capture_loop", new=lambda self: (case[1], FORMAT_PMOFN)
        )
        mocker.patch.object(
            wallet_descriptor,
            "display_qr_codes",
            new=lambda data, qr_format, title=None: ctx.input.wait_for_button(),
        )
        mocker.spy(wallet_descriptor, "display_loading_wallet")
        wallet_descriptor.wallet()
        wallet_descriptor.display_loading_wallet.assert_called_once()
        assert ctx.wallet.has_change_addr()
        assert ctx.input.wait_for_button.call_count == len(case[2])


def test_policy_mismatch_singlesig_to_multisig_accept(
    mocker, m5stickv, tdata, wallet_tdata
):
    """Test: Singlesig key loading multisig descriptor - user accepts change"""
    from krux.pages.home_pages.wallet_descriptor import WalletDescriptor
    from krux.wallet import Wallet
    from krux.input import BUTTON_ENTER
    from krux.qr import FORMAT_PMOFN
    from krux.pages.qr_capture import QRCodeCapture
    from krux.key import TYPE_MULTISIG

    btn_seq = [
        BUTTON_ENTER,  # Load wallet descriptor? Yes
        BUTTON_ENTER,  # Load from camera
        BUTTON_ENTER,  # Accept policy change (singlesig -> multisig)
        BUTTON_ENTER,  # Accept wallet load
    ]

    wallet = Wallet(tdata.SINGLESIG_12_WORD_KEY)
    ctx = create_ctx(mocker, btn_seq, wallet)

    wallet_descriptor = WalletDescriptor(ctx)
    mocker.patch.object(
        QRCodeCapture,
        "qr_capture_loop",
        new=lambda self: (wallet_tdata.UNAMBIGUOUS_MULTISIG_DESCRIPTOR, FORMAT_PMOFN),
    )
    mocker.patch.object(
        wallet_descriptor,
        "display_qr_codes",
        new=lambda data, qr_format, title=None: ctx.input.wait_for_button(),
    )
    # Mock display_loading_wallet to avoid pagination button presses
    mocker.patch.object(wallet_descriptor, "display_loading_wallet", return_value=None)
    mocker.spy(wallet_descriptor, "_handle_policy_mismatch")

    wallet_descriptor.wallet()

    # Verify mismatch was handled
    wallet_descriptor._handle_policy_mismatch.assert_called_once()
    # Verify key was re-derived with multisig policy
    assert ctx.wallet.key.policy_type == TYPE_MULTISIG
    # Verify wallet was loaded
    assert ctx.wallet.is_loaded()
    assert ctx.input.wait_for_button.call_count == len(btn_seq)


def test_policy_mismatch_singlesig_to_multisig_decline(
    mocker, m5stickv, tdata, wallet_tdata
):
    """Test: Singlesig key loading multisig descriptor - user declines change"""
    from krux.pages.home_pages.wallet_descriptor import WalletDescriptor
    from krux.wallet import Wallet
    from krux.input import BUTTON_ENTER, BUTTON_PAGE
    from krux.qr import FORMAT_PMOFN
    from krux.pages.qr_capture import QRCodeCapture
    from krux.key import TYPE_SINGLESIG

    btn_seq = [
        BUTTON_ENTER,  # Load wallet descriptor? Yes
        BUTTON_ENTER,  # Load from camera
        BUTTON_PAGE,  # Decline policy change
    ]

    wallet = Wallet(tdata.SINGLESIG_12_WORD_KEY)
    ctx = create_ctx(mocker, btn_seq, wallet)

    wallet_descriptor = WalletDescriptor(ctx)
    mocker.patch.object(
        QRCodeCapture,
        "qr_capture_loop",
        new=lambda self: (wallet_tdata.UNAMBIGUOUS_MULTISIG_DESCRIPTOR, FORMAT_PMOFN),
    )
    mocker.spy(wallet_descriptor, "_handle_policy_mismatch")

    wallet_descriptor.wallet()

    # Verify mismatch was handled
    wallet_descriptor._handle_policy_mismatch.assert_called_once()
    # Verify key was NOT changed (still singlesig)
    assert ctx.wallet.key.policy_type == TYPE_SINGLESIG
    # Verify wallet was NOT loaded
    assert not ctx.wallet.is_loaded()
    assert ctx.input.wait_for_button.call_count == len(btn_seq)


def test_policy_mismatch_singlesig_to_miniscript_accept(
    mocker, m5stickv, tdata, wallet_tdata
):
    """Test: Singlesig key loading miniscript descriptor - user accepts change"""
    from krux.pages.home_pages.wallet_descriptor import WalletDescriptor
    from krux.wallet import Wallet
    from krux.input import BUTTON_ENTER
    from krux.qr import FORMAT_PMOFN
    from krux.pages.qr_capture import QRCodeCapture
    from krux.key import TYPE_MINISCRIPT, P2WSH

    btn_seq = [
        BUTTON_ENTER,  # Load wallet descriptor? Yes
        BUTTON_ENTER,  # Load from camera
        BUTTON_ENTER,  # Accept policy change (singlesig -> miniscript)
        BUTTON_ENTER,  # Accept wallet load
    ]

    wallet = Wallet(tdata.SINGLESIG_12_WORD_KEY)
    ctx = create_ctx(mocker, btn_seq, wallet)

    wallet_descriptor = WalletDescriptor(ctx)
    mocker.patch.object(
        QRCodeCapture,
        "qr_capture_loop",
        new=lambda self: (wallet_tdata.LIANA_MINISCRIPT_DESCRIPTOR, FORMAT_PMOFN),
    )
    mocker.patch.object(
        wallet_descriptor,
        "display_qr_codes",
        new=lambda data, qr_format, title=None: ctx.input.wait_for_button(),
    )
    # Mock display_loading_wallet to avoid pagination button presses
    mocker.patch.object(wallet_descriptor, "display_loading_wallet", return_value=None)
    mocker.spy(wallet_descriptor, "_handle_policy_mismatch")

    wallet_descriptor.wallet()

    # Verify mismatch was handled
    wallet_descriptor._handle_policy_mismatch.assert_called_once()
    # Verify key was re-derived with miniscript policy and P2WSH script type
    assert ctx.wallet.key.policy_type == TYPE_MINISCRIPT
    assert ctx.wallet.key.script_type == P2WSH
    # Verify wallet was loaded
    assert ctx.wallet.is_loaded()
    assert ctx.input.wait_for_button.call_count == len(btn_seq)


def test_policy_mismatch_singlesig_to_taproot_miniscript_accept(
    mocker, m5stickv, tdata, wallet_tdata
):
    """Test: Singlesig key loading taproot miniscript descriptor - user accepts change"""
    from krux.pages.home_pages.wallet_descriptor import WalletDescriptor
    from krux.wallet import Wallet
    from krux.input import BUTTON_ENTER
    from krux.qr import FORMAT_PMOFN
    from krux.pages.qr_capture import QRCodeCapture
    from krux.key import TYPE_MINISCRIPT, P2TR

    btn_seq = [
        BUTTON_ENTER,  # Load wallet descriptor? Yes
        BUTTON_ENTER,  # Load from camera
        BUTTON_ENTER,  # Accept policy change (singlesig -> miniscript)
        BUTTON_ENTER,  # Accept wallet load
    ]

    wallet = Wallet(tdata.SINGLESIG_12_WORD_KEY)
    ctx = create_ctx(mocker, btn_seq, wallet)

    wallet_descriptor = WalletDescriptor(ctx)
    mocker.patch.object(
        QRCodeCapture,
        "qr_capture_loop",
        new=lambda self: (
            wallet_tdata.LIANA_TAPROOT_MINISCRIPT_DESCRIPTOR,
            FORMAT_PMOFN,
        ),
    )
    mocker.patch.object(
        wallet_descriptor,
        "display_qr_codes",
        new=lambda data, qr_format, title=None: ctx.input.wait_for_button(),
    )
    # Mock display_loading_wallet to avoid pagination button presses
    mocker.patch.object(wallet_descriptor, "display_loading_wallet", return_value=None)
    mocker.spy(wallet_descriptor, "_handle_policy_mismatch")

    wallet_descriptor.wallet()

    # Verify mismatch was handled
    wallet_descriptor._handle_policy_mismatch.assert_called_once()
    # Verify key was re-derived with miniscript policy and P2TR script type
    assert ctx.wallet.key.policy_type == TYPE_MINISCRIPT
    assert ctx.wallet.key.script_type == P2TR
    # Verify wallet was loaded
    assert ctx.wallet.is_loaded()
    assert ctx.input.wait_for_button.call_count == len(btn_seq)


def test_policy_mismatch_multisig_to_singlesig_accept(
    mocker, m5stickv, tdata, wallet_tdata
):
    """Test: Multisig key loading singlesig descriptor - user accepts change"""
    from krux.pages.home_pages.wallet_descriptor import WalletDescriptor
    from krux.wallet import Wallet
    from krux.input import BUTTON_ENTER
    from krux.qr import FORMAT_PMOFN
    from krux.pages.qr_capture import QRCodeCapture
    from krux.key import TYPE_SINGLESIG

    btn_seq = [
        BUTTON_ENTER,  # Load wallet descriptor? Yes
        BUTTON_ENTER,  # Load from camera
        BUTTON_ENTER,  # Accept policy change (multisig -> singlesig)
        BUTTON_ENTER,  # Accept wallet load
    ]

    wallet = Wallet(tdata.MULTISIG_12_WORD_KEY)
    ctx = create_ctx(mocker, btn_seq, wallet)

    wallet_descriptor = WalletDescriptor(ctx)
    mocker.patch.object(
        QRCodeCapture,
        "qr_capture_loop",
        new=lambda self: (wallet_tdata.UNAMBIGUOUS_SINGLESIG_DESCRIPTOR, FORMAT_PMOFN),
    )
    mocker.patch.object(
        wallet_descriptor,
        "display_qr_codes",
        new=lambda data, qr_format, title=None: ctx.input.wait_for_button(),
    )
    # Mock display_loading_wallet to avoid pagination button presses
    mocker.patch.object(wallet_descriptor, "display_loading_wallet", return_value=None)
    mocker.spy(wallet_descriptor, "_handle_policy_mismatch")

    wallet_descriptor.wallet()

    # Verify mismatch was handled
    wallet_descriptor._handle_policy_mismatch.assert_called_once()
    # Verify key was re-derived with singlesig policy
    assert ctx.wallet.key.policy_type == TYPE_SINGLESIG
    # Verify wallet was loaded
    assert ctx.wallet.is_loaded()
    assert ctx.input.wait_for_button.call_count == len(btn_seq)


def test_policy_mismatch_multisig_to_miniscript_accept(
    mocker, m5stickv, tdata, wallet_tdata
):
    """Test: Multisig key loading miniscript descriptor - user accepts change"""
    from krux.pages.home_pages.wallet_descriptor import WalletDescriptor
    from krux.wallet import Wallet
    from krux.input import BUTTON_ENTER
    from krux.qr import FORMAT_PMOFN
    from krux.pages.qr_capture import QRCodeCapture
    from krux.key import TYPE_MINISCRIPT, P2WSH

    btn_seq = [
        BUTTON_ENTER,  # Load wallet descriptor? Yes
        BUTTON_ENTER,  # Load from camera
        BUTTON_ENTER,  # Accept policy change (multisig -> miniscript)
        BUTTON_ENTER,  # Accept wallet load
    ]

    wallet = Wallet(tdata.MULTISIG_12_WORD_KEY)
    ctx = create_ctx(mocker, btn_seq, wallet)

    wallet_descriptor = WalletDescriptor(ctx)
    mocker.patch.object(
        QRCodeCapture,
        "qr_capture_loop",
        new=lambda self: (wallet_tdata.LIANA_MINISCRIPT_DESCRIPTOR, FORMAT_PMOFN),
    )
    mocker.patch.object(
        wallet_descriptor,
        "display_qr_codes",
        new=lambda data, qr_format, title=None: ctx.input.wait_for_button(),
    )
    # Mock display_loading_wallet to avoid pagination button presses
    mocker.patch.object(wallet_descriptor, "display_loading_wallet", return_value=None)
    mocker.spy(wallet_descriptor, "_handle_policy_mismatch")

    wallet_descriptor.wallet()

    # Verify mismatch was handled
    wallet_descriptor._handle_policy_mismatch.assert_called_once()
    # Verify key was re-derived with miniscript policy
    assert ctx.wallet.key.policy_type == TYPE_MINISCRIPT
    assert ctx.wallet.key.script_type == P2WSH
    # Verify wallet was loaded
    assert ctx.wallet.is_loaded()
    assert ctx.input.wait_for_button.call_count == len(btn_seq)


def test_policy_mismatch_miniscript_to_singlesig_accept(
    mocker, amigo, tdata, wallet_tdata
):
    """Test: Miniscript key loading singlesig descriptor - user accepts change"""
    from krux.pages.home_pages.wallet_descriptor import WalletDescriptor
    from krux.wallet import Wallet
    from krux.input import BUTTON_ENTER
    from krux.qr import FORMAT_PMOFN
    from krux.pages.qr_capture import QRCodeCapture
    from krux.key import TYPE_SINGLESIG

    btn_seq = [
        BUTTON_ENTER,  # Load wallet descriptor? Yes
        BUTTON_ENTER,  # Load from camera
        BUTTON_ENTER,  # Accept policy change (miniscript -> singlesig)
        BUTTON_ENTER,  # Accept wallet load
    ]

    wallet = Wallet(wallet_tdata.MINISCRIPT_KEY)
    ctx = create_ctx(mocker, btn_seq, wallet)

    wallet_descriptor = WalletDescriptor(ctx)
    # Use UNAMBIGUOUS_SINGLESIG_DESCRIPTOR which has /<0;1>/* (change branch)
    mocker.patch.object(
        QRCodeCapture,
        "qr_capture_loop",
        new=lambda self: (wallet_tdata.UNAMBIGUOUS_SINGLESIG_DESCRIPTOR, FORMAT_PMOFN),
    )
    mocker.patch.object(
        wallet_descriptor,
        "display_qr_codes",
        new=lambda data, qr_format, title=None: ctx.input.wait_for_button(),
    )
    # Mock display_loading_wallet to avoid pagination button presses
    mocker.patch.object(wallet_descriptor, "display_loading_wallet", return_value=None)
    mocker.spy(wallet_descriptor, "_handle_policy_mismatch")

    wallet_descriptor.wallet()

    # Verify mismatch was handled
    wallet_descriptor._handle_policy_mismatch.assert_called_once()
    # Verify key was re-derived with singlesig policy
    assert ctx.wallet.key.policy_type == TYPE_SINGLESIG
    # Verify wallet was loaded
    assert ctx.wallet.is_loaded()
    assert ctx.input.wait_for_button.call_count == len(btn_seq)


def test_network_mismatch_mainnet_to_testnet_accept(mocker, m5stickv, tdata):
    """Test: Mainnet key loading testnet descriptor - user accepts change"""
    from krux.pages.home_pages.wallet_descriptor import WalletDescriptor
    from krux.wallet import Wallet
    from krux.input import BUTTON_ENTER
    from krux.qr import FORMAT_PMOFN
    from krux.pages.qr_capture import QRCodeCapture
    from embit.networks import NETWORKS

    # Testnet singlesig descriptor matching TEST_12_WORD_MNEMONIC
    # Derived from [55f8fc5d/84'/1'/0'] for testnet
    TESTNET_SINGLESIG_DESCRIPTOR = "wpkh([55f8fc5d/84h/1h/0h]tpubDCDuqu5HtBX2aD7wxvnHcj1DgFN1UVgzLkA1Ms4Va4P7TpJ3jDknkPLwWT2SqrKXNNAtJBCPcbJ8Tcpm6nLxgFapCZyhKgqwcEGv1BVpD7s/<0;1>/*)"

    btn_seq = [
        BUTTON_ENTER,  # Load wallet descriptor? Yes
        BUTTON_ENTER,  # Load from camera
        BUTTON_ENTER,  # Accept network change (mainnet -> testnet)
        BUTTON_ENTER,  # Accept wallet load
    ]

    wallet = Wallet(tdata.SINGLESIG_12_WORD_KEY)
    ctx = create_ctx(mocker, btn_seq, wallet)

    wallet_descriptor = WalletDescriptor(ctx)
    mocker.patch.object(
        QRCodeCapture,
        "qr_capture_loop",
        new=lambda self: (TESTNET_SINGLESIG_DESCRIPTOR, FORMAT_PMOFN),
    )
    mocker.patch.object(
        wallet_descriptor,
        "display_qr_codes",
        new=lambda data, qr_format, title=None: ctx.input.wait_for_button(),
    )
    # Mock display_loading_wallet to avoid pagination button presses
    mocker.patch.object(wallet_descriptor, "display_loading_wallet", return_value=None)
    mocker.spy(wallet_descriptor, "_handle_policy_mismatch")

    wallet_descriptor.wallet()

    # Verify mismatch was handled
    wallet_descriptor._handle_policy_mismatch.assert_called_once()
    # Verify key was re-derived with testnet network
    assert ctx.wallet.key.network == NETWORKS["test"]
    # Verify wallet was loaded
    assert ctx.wallet.is_loaded()
    assert ctx.input.wait_for_button.call_count == len(btn_seq)


def test_network_mismatch_mainnet_to_testnet_decline(mocker, m5stickv, tdata):
    """Test: Mainnet key loading testnet descriptor - user declines change"""
    from krux.pages.home_pages.wallet_descriptor import WalletDescriptor
    from krux.wallet import Wallet
    from krux.input import BUTTON_ENTER, BUTTON_PAGE
    from krux.qr import FORMAT_PMOFN
    from krux.pages.qr_capture import QRCodeCapture
    from embit.networks import NETWORKS

    # Testnet singlesig descriptor matching TEST_12_WORD_MNEMONIC
    TESTNET_SINGLESIG_DESCRIPTOR = "wpkh([55f8fc5d/84h/1h/0h]tpubDCDuqu5HtBX2aD7wxvnHcj1DgFN1UVgzLkA1Ms4Va4P7TpJ3jDknkPLwWT2SqrKXNNAtJBCPcbJ8Tcpm6nLxgFapCZyhKgqwcEGv1BVpD7s/<0;1>/*)"

    btn_seq = [
        BUTTON_ENTER,  # Load wallet descriptor? Yes
        BUTTON_ENTER,  # Load from camera
        BUTTON_PAGE,  # Decline network change
    ]

    wallet = Wallet(tdata.SINGLESIG_12_WORD_KEY)
    ctx = create_ctx(mocker, btn_seq, wallet)

    wallet_descriptor = WalletDescriptor(ctx)
    mocker.patch.object(
        QRCodeCapture,
        "qr_capture_loop",
        new=lambda self: (TESTNET_SINGLESIG_DESCRIPTOR, FORMAT_PMOFN),
    )
    mocker.spy(wallet_descriptor, "_handle_policy_mismatch")

    wallet_descriptor.wallet()

    # Verify mismatch was handled
    wallet_descriptor._handle_policy_mismatch.assert_called_once()
    # Verify key was NOT changed (still mainnet)
    assert ctx.wallet.key.network == NETWORKS["main"]
    # Verify wallet was NOT loaded
    assert not ctx.wallet.is_loaded()
    assert ctx.input.wait_for_button.call_count == len(btn_seq)


def test_script_type_mismatch_p2wpkh_to_p2tr_accept(
    mocker, m5stickv, tdata, wallet_tdata
):
    """Test: P2WPKH singlesig key loading P2TR descriptor - user accepts change"""
    from krux.pages.home_pages.wallet_descriptor import WalletDescriptor
    from krux.wallet import Wallet
    from krux.input import BUTTON_ENTER
    from krux.qr import FORMAT_PMOFN
    from krux.pages.qr_capture import QRCodeCapture
    from krux.key import P2TR, TYPE_SINGLESIG

    # Taproot singlesig descriptor for same mnemonic (TEST_12_WORD_MNEMONIC)
    TAPROOT_SINGLESIG_DESCRIPTOR = "tr([55f8fc5d/86h/0h/0h]xpub6CNGwJbVG9sQq4vfRxk6zpE4iiES3XsdVjn3SRkbHB8zDe66vhtPJUH7dCuVMmTcQ8fuozNYDYxcQJeJZE28eSD2sZYDHCYgC3Dq48kjbKy/<0;1>/*)"

    btn_seq = [
        BUTTON_ENTER,  # Load wallet descriptor? Yes
        BUTTON_ENTER,  # Load from camera
        BUTTON_ENTER,  # Accept script type change (P2WPKH -> P2TR)
        BUTTON_ENTER,  # Accept wallet load
    ]

    wallet = Wallet(tdata.SINGLESIG_12_WORD_KEY)
    ctx = create_ctx(mocker, btn_seq, wallet)

    wallet_descriptor = WalletDescriptor(ctx)
    mocker.patch.object(
        QRCodeCapture,
        "qr_capture_loop",
        new=lambda self: (TAPROOT_SINGLESIG_DESCRIPTOR, FORMAT_PMOFN),
    )
    mocker.patch.object(
        wallet_descriptor,
        "display_qr_codes",
        new=lambda data, qr_format, title=None: ctx.input.wait_for_button(),
    )
    # Mock display_loading_wallet to avoid pagination button presses
    mocker.patch.object(wallet_descriptor, "display_loading_wallet", return_value=None)
    mocker.spy(wallet_descriptor, "_handle_policy_mismatch")

    wallet_descriptor.wallet()

    # Verify mismatch was handled
    wallet_descriptor._handle_policy_mismatch.assert_called_once()
    # Verify key was re-derived with P2TR script type
    assert ctx.wallet.key.policy_type == TYPE_SINGLESIG
    assert ctx.wallet.key.script_type == P2TR
    # Verify wallet was loaded
    assert ctx.wallet.is_loaded()
    assert ctx.input.wait_for_button.call_count == len(btn_seq)


def test_combined_policy_and_network_mismatch_accept(mocker, m5stickv, tdata):
    """Test: Combined policy and network mismatch - user accepts change"""
    from krux.pages.home_pages.wallet_descriptor import WalletDescriptor
    from krux.wallet import Wallet
    from krux.input import BUTTON_ENTER
    from krux.qr import FORMAT_PMOFN
    from krux.pages.qr_capture import QRCodeCapture
    from krux.key import TYPE_MINISCRIPT, P2WSH
    from embit.networks import NETWORKS

    # Testnet miniscript descriptor (different policy + different network)
    # Key matches TEST_12_WORD_MNEMONIC at path 48'/1'/0'/2' on testnet
    # Using simple wsh(pk(...)) which is a valid miniscript construct
    TESTNET_MINISCRIPT_DESCRIPTOR = "wsh(pk([55f8fc5d/48h/1h/0h/2h]tpubDDyrxYEe6bifecFTgj8vzsoUhoJmtVWeARR5xRun6haVnVrC2oTAYhj7Ja2KTkcnkW1mZPPuWGDxEsHMtRf8aAf4WfrqhLDN7xi9zAZMphv/<0;1>/*))"

    btn_seq = [
        BUTTON_ENTER,  # Load wallet descriptor? Yes
        BUTTON_ENTER,  # Load from camera
        BUTTON_ENTER,  # Accept combined policy + network change
        BUTTON_ENTER,  # Accept wallet load
    ]

    wallet = Wallet(tdata.SINGLESIG_12_WORD_KEY)
    ctx = create_ctx(mocker, btn_seq, wallet)

    wallet_descriptor = WalletDescriptor(ctx)
    mocker.patch.object(
        QRCodeCapture,
        "qr_capture_loop",
        new=lambda self: (TESTNET_MINISCRIPT_DESCRIPTOR, FORMAT_PMOFN),
    )
    mocker.patch.object(
        wallet_descriptor,
        "display_qr_codes",
        new=lambda data, qr_format, title=None: ctx.input.wait_for_button(),
    )
    # Mock display_loading_wallet to avoid pagination button presses
    mocker.patch.object(wallet_descriptor, "display_loading_wallet", return_value=None)
    mocker.spy(wallet_descriptor, "_handle_policy_mismatch")

    wallet_descriptor.wallet()

    # Verify mismatch was handled
    wallet_descriptor._handle_policy_mismatch.assert_called_once()
    # Verify key was re-derived with miniscript policy AND testnet network
    assert ctx.wallet.key.policy_type == TYPE_MINISCRIPT
    assert ctx.wallet.key.script_type == P2WSH
    assert ctx.wallet.key.network == NETWORKS["test"]
    # Verify wallet was loaded
    assert ctx.wallet.is_loaded()
    assert ctx.input.wait_for_button.call_count == len(btn_seq)


def test_wallet_load_camera_back_is_silent(mocker, m5stickv, tdata):
    from krux.pages.home_pages.wallet_descriptor import WalletDescriptor
    from krux.pages import MENU_CONTINUE
    from krux.pages.qr_capture import QRCodeCapture
    from krux.wallet import Wallet
    from krux.input import BUTTON_ENTER

    btn_seq = [
        BUTTON_ENTER,  # confirm load
        BUTTON_ENTER,  # select "Load from camera"
    ]

    wallet = Wallet(tdata.SINGLESIG_12_WORD_KEY)
    ctx = create_ctx(mocker, btn_seq, wallet)
    # user left the QR scanner without scanning anything
    mocker.patch.object(QRCodeCapture, "qr_capture_loop", new=lambda self: (None, None))

    assert WalletDescriptor(ctx).wallet() == MENU_CONTINUE
    assert ctx.input.wait_for_button.call_count == len(btn_seq)

    # "Back" is not a failure - it must not flash an error
    assert_not_flashed(ctx, "Failed to load")


# ---------- NFC card ----------
#
# The point of these is that NFC adds a medium and not a parser: a card hands
# back a sealed envelope, and everything that decides whether it is a descriptor
# is the same code a QR code or an SD card file goes through.


def _descriptor_of(specter_json):
    """The raw descriptor, which is what an export actually writes to a card"""
    import json

    return json.loads(specter_json)["descriptor"]


def _seal(plaintext, label="2 of 3 multisig", key="pass", iterations=10000):
    """A genuine KEF envelope - real AES, the bytes a card actually carries"""
    from krux import kef

    version = 0
    cipher = kef.Cipher(key, label, iterations)
    payload = cipher.encrypt(plaintext, version)
    return kef.wrap(label, version, iterations, payload), key


def _mock_nfc_card(mocker, envelope, key):
    """An NFC facade holding one descriptor record, with the password answered"""
    from krux.pages.encryption_ui import KEFEnvelope

    nfc = mocker.MagicMock()
    nfc.read_record.return_value = envelope
    mocker.patch("krux.nfc.NFC", mocker.MagicMock(return_value=nfc))
    mocker.patch.object(KEFEnvelope, "public_info_ui", return_value=True)

    def supply_key(self, creating=True):
        setattr(self, "_KEFEnvelope__key", key)
        return True

    mocker.patch.object(KEFEnvelope, "input_key_ui", supply_key)
    return nfc


@pytest.fixture
def nfc_on(m5stickv):
    from krux.krux_settings import Settings

    Settings().hardware.nfc.enabled = True
    yield m5stickv
    Settings().hardware.nfc.enabled = False


def test_load_descriptor_from_nfc_card(mocker, nfc_on, tdata):
    """End to end: a sealed 2 of 3 comes off a card and becomes the wallet"""
    from krux.pages.home_pages.wallet_descriptor import WalletDescriptor
    from krux.wallet import Wallet
    from krux.input import BUTTON_ENTER, BUTTON_PAGE
    from krux.nfc import RECORD_DESCRIPTOR

    descriptor = _descriptor_of(tdata.SPECTER_MULTISIG_WALLET_DATA)
    envelope, key = _seal(descriptor.encode())
    nfc = _mock_nfc_card(mocker, envelope, key)

    btn_seq = [
        BUTTON_ENTER,  # Load?
        BUTTON_PAGE,  # Load from camera -> Load from SD card
        BUTTON_PAGE,  # -> Load from NFC card
        BUTTON_ENTER,  # Load from NFC card
        BUTTON_ENTER,  # Loaded wallet confirmation
    ]
    ctx = create_ctx(mocker, btn_seq, Wallet(tdata.MULTISIG_12_WORD_KEY))
    WalletDescriptor(ctx).wallet()

    nfc.read_record.assert_called_once_with(RECORD_DESCRIPTOR)
    nfc.deinit.assert_called_once()  # antenna down before the password prompt
    assert ctx.wallet.is_loaded()
    assert ctx.wallet.is_multisig()
    assert ctx.input.wait_for_button.call_count == len(btn_seq)


@pytest.mark.parametrize(
    "payload",
    [
        bytes(range(16)),  # raw BIP39 entropy - decrypts, is not text
        b"abandon abandon abandon",  # decrypts, is text, is not a descriptor
        b"wsh(sortedmulti(2,truncated",  # decrypts, looks like one, is not
    ],
)
def test_a_card_that_is_not_a_descriptor_loads_nothing(mocker, nfc_on, tdata, payload):
    """Decrypting does not make these bytes a wallet. The password can be right
    and the record type can match, and the descriptor parser still has the last
    word - the same one it has over a QR code."""
    from krux.pages.home_pages.wallet_descriptor import WalletDescriptor
    from krux.wallet import Wallet
    from krux.input import BUTTON_ENTER, BUTTON_PAGE

    envelope, key = _seal(payload)
    _mock_nfc_card(mocker, envelope, key)

    btn_seq = [
        BUTTON_ENTER,  # Load?
        BUTTON_PAGE,  # -> Load from SD card
        BUTTON_PAGE,  # -> Load from NFC card
        BUTTON_ENTER,  # Load from NFC card
        BUTTON_ENTER,  # dismiss the failure
    ]
    ctx = create_ctx(mocker, btn_seq, Wallet(tdata.MULTISIG_12_WORD_KEY))
    WalletDescriptor(ctx).wallet()

    assert not ctx.wallet.is_loaded()


def test_the_card_option_is_absent_while_nfc_is_off(mocker, m5stickv, tdata):
    """With the setting off the load menu is the one it has always been, which
    is also why no existing button sequence in this file had to change."""
    from krux.pages.home_pages.wallet_descriptor import WalletDescriptor
    from krux.wallet import Wallet
    import krux.pages as pages

    captured = []

    class FakeMenu:
        back_index = 2

        def __init__(self, _ctx, items, **_kwargs):
            captured.extend(items)

        def run_loop(self, *_args, **_kwargs):
            return 2, None  # Back

        def run(self, *_args, **_kwargs):
            return 2, None

    mocker.patch.object(pages, "Menu", FakeMenu)
    ctx = create_ctx(mocker, [], Wallet(tdata.MULTISIG_12_WORD_KEY))
    WalletDescriptor(ctx)._load_wallet_data()

    labels = [item[0] for item in captured]
    assert labels == ["Load from camera", "Load from SD card"]


def test_store_descriptor_on_nfc_card(mocker, nfc_on, tdata):
    """The encrypted export gains a card as a destination, next to SD"""
    from krux.pages.home_pages.wallet_descriptor import WalletDescriptor
    from krux.pages.encryption_ui import KEFEnvelope
    from krux.pages.qr_view import SeedQRView
    from krux.wallet import Wallet
    from krux.input import BUTTON_ENTER, BUTTON_PAGE
    from krux.nfc import RECORD_DESCRIPTOR
    from krux.qr import FORMAT_NONE

    envelope = b"SEALED-DESCRIPTOR-ENVELOPE"
    mocker.patch.object(KEFEnvelope, "seal_ui", return_value=envelope)
    mocker.patch.object(SeedQRView, "display_qr", return_value=None)

    nfc = mocker.MagicMock()
    nfc.has_record.return_value = False
    mocker.patch("krux.nfc.NFC", mocker.MagicMock(return_value=nfc))

    wallet = Wallet(tdata.MULTISIG_12_WORD_KEY)
    wallet.load(tdata.SPECTER_MULTISIG_WALLET_DATA, FORMAT_NONE)

    btn_seq = [
        BUTTON_PAGE,  # Plaintext -> Encrypted
        BUTTON_ENTER,  # Encrypted
        BUTTON_ENTER,  # Store on NFC Card?
    ]
    ctx = create_ctx(mocker, btn_seq, wallet)
    WalletDescriptor(ctx).wallet()

    nfc.write_record.assert_called_once_with(envelope, RECORD_DESCRIPTOR)
    nfc.deinit.assert_called_once()
    assert ctx.input.wait_for_button.call_count == len(btn_seq)


def test_declining_the_card_leaves_the_reader_alone(mocker, nfc_on, tdata):
    from krux.pages.home_pages.wallet_descriptor import WalletDescriptor
    from krux.pages.encryption_ui import KEFEnvelope
    from krux.pages.qr_view import SeedQRView
    from krux.wallet import Wallet
    from krux.input import BUTTON_ENTER, BUTTON_PAGE
    from krux.qr import FORMAT_NONE

    mocker.patch.object(KEFEnvelope, "seal_ui", return_value=b"SEALED")
    mocker.patch.object(SeedQRView, "display_qr", return_value=None)
    nfc = mocker.MagicMock()
    mocker.patch("krux.nfc.NFC", mocker.MagicMock(return_value=nfc))

    wallet = Wallet(tdata.MULTISIG_12_WORD_KEY)
    wallet.load(tdata.SPECTER_MULTISIG_WALLET_DATA, FORMAT_NONE)

    btn_seq = [
        BUTTON_PAGE,  # Plaintext -> Encrypted
        BUTTON_ENTER,  # Encrypted
        BUTTON_PAGE,  # Store on NFC Card? -> No
    ]
    ctx = create_ctx(mocker, btn_seq, wallet)
    WalletDescriptor(ctx).wallet()

    nfc.init.assert_not_called()  # declining never opens the bus
    assert ctx.input.wait_for_button.call_count == len(btn_seq)


# ---------- Plaintext records ----------
#
# A card may hold a descriptor unsealed, the same way a .txt on SD may. What it
# may never hold unsealed is a seed.


def _plain_card(mocker, payload):
    """An NFC facade holding one unsealed descriptor record"""
    nfc = mocker.MagicMock()
    nfc.read_record.return_value = payload
    mocker.patch("krux.nfc.NFC", mocker.MagicMock(return_value=nfc))
    return nfc


def _load_from_card_btns():
    from krux.input import BUTTON_ENTER, BUTTON_PAGE

    return [
        BUTTON_ENTER,  # Load?
        BUTTON_PAGE,  # -> Load from SD card
        BUTTON_PAGE,  # -> Load from NFC card
        BUTTON_ENTER,  # Load from NFC card
        BUTTON_ENTER,  # confirmation or failure
    ]


def test_load_a_plaintext_descriptor_from_a_card(mocker, nfc_on, tdata):
    from krux.pages.home_pages.wallet_descriptor import WalletDescriptor
    from krux.wallet import Wallet
    from embit.descriptor.checksum import add_checksum

    descriptor = add_checksum(_descriptor_of(tdata.SPECTER_MULTISIG_WALLET_DATA))
    _plain_card(mocker, descriptor.encode())

    ctx = create_ctx(mocker, _load_from_card_btns(), Wallet(tdata.MULTISIG_12_WORD_KEY))
    WalletDescriptor(ctx).wallet()

    assert ctx.wallet.is_loaded()
    assert ctx.wallet.is_multisig()


def test_an_unsealed_card_without_a_checksum_is_refused(mocker, nfc_on, tdata):
    """Unsealed, the checksum is the only integrity the record has, so it is
    required rather than merely honoured when present."""
    from krux.pages.home_pages.wallet_descriptor import WalletDescriptor
    from krux.wallet import Wallet

    descriptor = _descriptor_of(tdata.SPECTER_MULTISIG_WALLET_DATA).split("#")[0]
    _plain_card(mocker, descriptor.encode())

    ctx = create_ctx(mocker, _load_from_card_btns(), Wallet(tdata.MULTISIG_12_WORD_KEY))
    WalletDescriptor(ctx).wallet()

    assert not ctx.wallet.is_loaded()


def test_a_card_failing_its_checksum_reports_once(mocker, nfc_on, tdata):
    """The refusal ends the load the way every other failed load does. Only a
    bare None tells _load_wallet the failure was already reported; anything else
    goes on to load an empty wallet and stacks "Invalid wallet" on top of
    "Failed to load"."""
    from krux.pages.home_pages.wallet_descriptor import WalletDescriptor
    from krux.wallet import Wallet
    from krux.input import BUTTON_ENTER, BUTTON_PAGE

    descriptor = _descriptor_of(tdata.SPECTER_MULTISIG_WALLET_DATA).split("#")[0]
    _plain_card(mocker, descriptor.encode())

    btn_seq = [
        BUTTON_ENTER,  # Load?
        BUTTON_PAGE,  # -> Load from SD card
        BUTTON_PAGE,  # -> Load from NFC card
        BUTTON_ENTER,  # Load from NFC card
    ]
    ctx = create_ctx(mocker, btn_seq, Wallet(tdata.MULTISIG_12_WORD_KEY))
    WalletDescriptor(ctx).wallet()

    assert not ctx.wallet.is_loaded()
    assert ctx.display.flash_text.call_count == 1
    shown = [str(call[0][0]) for call in ctx.display.draw_centered_text.call_args_list]
    assert not any("Invalid wallet" in text for text in shown)
    assert ctx.input.wait_for_button.call_count == len(btn_seq)


@pytest.mark.parametrize(
    "payload",
    [
        b"\xff\xfe\x00\x01 not text at all",  # does not decode
        "wsh(\u00a3)#abcdefgh".encode(),  # decodes, not a checksummable string
        b"#",  # a separator and nothing else
        b"",
    ],
)
def test_an_unsealed_card_of_rubbish_is_refused(mocker, nfc_on, tdata, payload):
    """Whatever a card hands back, deciding it is not a descriptor happens
    without an exception reaching the user."""
    from krux.pages.home_pages.wallet_descriptor import WalletDescriptor
    from krux.wallet import Wallet

    _plain_card(mocker, payload)
    ctx = create_ctx(mocker, _load_from_card_btns(), Wallet(tdata.MULTISIG_12_WORD_KEY))
    WalletDescriptor(ctx).wallet()

    assert not ctx.wallet.is_loaded()


def test_a_corrupted_derivation_on_an_unsealed_card_is_caught(mocker, nfc_on, tdata):
    """The bit embit would have let through. Only the xpubs are base58check;
    a flipped bit in a derivation path changes which addresses the wallet
    watches and nothing else in the string would notice."""
    from krux.pages.home_pages.wallet_descriptor import WalletDescriptor
    from krux.wallet import Wallet
    from embit.descriptor.checksum import add_checksum
    from embit.descriptor import Descriptor

    descriptor = _descriptor_of(tdata.SPECTER_MULTISIG_WALLET_DATA)
    carded = add_checksum(descriptor)
    corrupted = carded.replace("/48h/0h/0h/2h]xpub6EKm", "/48h/0h/1h/2h]xpub6EKm", 1)
    assert corrupted != carded
    # embit itself has no objection, which is the whole point
    Descriptor.from_string(corrupted)

    _plain_card(mocker, corrupted.encode())
    ctx = create_ctx(mocker, _load_from_card_btns(), Wallet(tdata.MULTISIG_12_WORD_KEY))
    WalletDescriptor(ctx).wallet()

    assert not ctx.wallet.is_loaded()


def test_store_a_plaintext_descriptor_writes_its_checksum(mocker, nfc_on, tdata):
    from krux.pages.home_pages.wallet_descriptor import WalletDescriptor
    from krux.wallet import Wallet
    from krux.input import BUTTON_ENTER
    from krux.nfc import RECORD_DESCRIPTOR
    from krux.qr import FORMAT_NONE
    from embit.descriptor.checksum import checksum

    nfc = mocker.MagicMock()
    nfc.has_record.return_value = False
    mocker.patch("krux.nfc.NFC", mocker.MagicMock(return_value=nfc))
    # The QR display is not what this is about
    mocker.patch.object(WalletDescriptor, "display_wallet", return_value=None)

    wallet = Wallet(tdata.MULTISIG_12_WORD_KEY)
    wallet.load(tdata.SPECTER_MULTISIG_WALLET_DATA, FORMAT_NONE)

    btn_seq = [
        BUTTON_ENTER,  # Plaintext
        BUTTON_ENTER,  # Store on NFC Card?
    ]
    ctx = create_ctx(mocker, btn_seq, wallet)
    WalletDescriptor(ctx).wallet()

    written, record_type = nfc.write_record.call_args[0]
    assert record_type == RECORD_DESCRIPTOR
    body, separator, provided = written.decode().partition("#")
    assert separator and checksum(body) == provided
    assert body == wallet.descriptor.to_string()


def test_a_seed_card_is_never_read_unsealed(mocker, nfc_on):
    """The other half of allowing plaintext descriptors: the mnemonic loader
    takes only a sealed record, so a card carrying words in the clear has no
    way in however it is labelled."""
    from krux.pages.encryption_ui import LoadEncryptedMnemonic
    from krux.pages import MENU_CONTINUE
    from krux.nfc import RECORD_KEF

    nfc = mocker.MagicMock()
    nfc.read_record.return_value = (
        b"olympic term tissue route sense program under choose bean emerge "
        b"velvet absurd"
    )
    mocker.patch("krux.nfc.NFC", mocker.MagicMock(return_value=nfc))

    ctx = create_ctx(mocker, [])
    assert LoadEncryptedMnemonic(ctx).load_from_nfc() == MENU_CONTINUE
    nfc.read_record.assert_called_once_with(RECORD_KEF)
    ctx.display.flash_text.assert_called_once()
