import pytest
from ...shared_mocks import MockPrinter
from .test_home import tdata, create_ctx
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
            mock_utils.return_value.load_file.return_value = (None, case[2])

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
