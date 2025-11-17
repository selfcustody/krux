from . import create_ctx
from .home_pages.test_home import tdata
import pytest


def test_type_passphrase(m5stickv, mocker):
    from krux.pages.wallet_settings import PassphraseEditor

    TEST_VALUE = "Test value"
    ctx = create_ctx(mocker, TEST_VALUE)
    passphrase_editor = PassphraseEditor(ctx)
    mocker.patch.object(
        passphrase_editor,
        "capture_from_keypad",
        return_value=TEST_VALUE,
    )
    test_passphrase = passphrase_editor._load_passphrase()

    assert test_passphrase == TEST_VALUE


def test_type_passphrase_esc(m5stickv, mocker):
    from krux.pages.wallet_settings import PassphraseEditor
    from krux.pages import BUTTON_ENTER, BUTTON_PAGE_PREV

    BTN_SEQUENCE = [
        BUTTON_ENTER,  # Type BIP39 Passphrase
        *([BUTTON_PAGE_PREV] * 2),  # Go to "Esc"
        BUTTON_ENTER,  # Press Esc
        BUTTON_ENTER,  # Confirm Esc
    ]
    ctx = create_ctx(mocker, BTN_SEQUENCE)
    passphrase_editor = PassphraseEditor(ctx)
    test_passphrase = passphrase_editor.load_passphrase_menu(ctx.key.mnemonic)

    assert test_passphrase is None
    assert ctx.input.wait_for_button.call_count == len(BTN_SEQUENCE)


def test_qr_passphrase(m5stickv, mocker):
    from krux.pages.wallet_settings import PassphraseEditor
    from krux.pages.qr_capture import QRCodeCapture

    TEST_VALUE = "Test value"
    QR_DATA = (TEST_VALUE, None)
    ctx = create_ctx(mocker, None)
    passphrase_editor = PassphraseEditor(ctx)
    mocker.patch.object(QRCodeCapture, "qr_capture_loop", new=lambda self: (QR_DATA))
    qr_capturer = mocker.spy(QRCodeCapture, "qr_capture_loop")
    test_passphrase = passphrase_editor._load_qr_passphrase()

    assert test_passphrase == TEST_VALUE
    qr_capturer.assert_called_once()


def test_qr_passphrase_too_long(m5stickv, mocker):
    from krux.pages.wallet_settings import (
        PassphraseEditor,
        MENU_CONTINUE,
        PASSPHRASE_MAX_LEN,
    )
    from krux.pages.qr_capture import QRCodeCapture

    TEST_VALUE = "Test value" * 25
    QR_DATA = (TEST_VALUE, None)
    ctx = create_ctx(mocker, None)
    passphrase_editor = PassphraseEditor(ctx)
    mocker.patch.object(QRCodeCapture, "qr_capture_loop", new=lambda self: (QR_DATA))
    qr_capturer = mocker.spy(QRCodeCapture, "qr_capture_loop")

    error_message = "Maximum length exceeded (%s)" % PASSPHRASE_MAX_LEN
    with pytest.raises(ValueError) as error:
        test_passphrase = passphrase_editor._load_qr_passphrase()

        assert error_message in str(error.value)
        assert test_passphrase == MENU_CONTINUE
        qr_capturer.assert_called_once()


def test_qr_passphrase_fail(m5stickv, mocker):
    from krux.pages.wallet_settings import PassphraseEditor, MENU_CONTINUE
    from krux.pages.qr_capture import QRCodeCapture

    TEST_VALUE = None
    QR_DATA = (TEST_VALUE, None)
    ctx = create_ctx(mocker, None)
    passphrase_editor = PassphraseEditor(ctx)
    mocker.patch.object(QRCodeCapture, "qr_capture_loop", new=lambda self: (QR_DATA))
    qr_capturer = mocker.spy(QRCodeCapture, "qr_capture_loop")
    test_passphrase = passphrase_editor._load_qr_passphrase()

    assert test_passphrase == MENU_CONTINUE
    qr_capturer.assert_called_once()


def test_qr_passphrase_fails_on_decrypt_kef_key_error(mocker, m5stickv, tdata):
    from krux.input import BUTTON_ENTER, BUTTON_PAGE, BUTTON_PAGE_PREV
    from krux.pages.wallet_settings import PassphraseEditor
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
        BUTTON_ENTER,  # confirm decrypt
        BUTTON_ENTER,  # type key
        BUTTON_PAGE,  # to "b"
        BUTTON_ENTER,  # enter "b"
        BUTTON_PAGE_PREV,  # back to "a"
        BUTTON_PAGE_PREV,  # back to Go
        BUTTON_ENTER,  # go Go
        BUTTON_ENTER,  # confirm key "b" (while "a" is correct key)
    ]
    ctx = create_ctx(mocker, btn_seq)
    passphrase_editor = PassphraseEditor(ctx)
    assert passphrase_editor._load_qr_passphrase() == MENU_CONTINUE
    assert ctx.input.wait_for_button.call_count == len(btn_seq)
    ctx.display.flash_text.assert_called_with(
        "Failed to decrypt", 248, 2000, highlight_prefix=""
    )


def test_qr_passphrase_fails_on_encrypted_non_ascii_bytes(mocker, m5stickv, tdata):
    from krux.input import BUTTON_ENTER, BUTTON_PAGE, BUTTON_PAGE_PREV
    from krux.pages.wallet_settings import PassphraseEditor
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
        BUTTON_ENTER,  # confirm decrypt
        BUTTON_ENTER,  # type key
        BUTTON_ENTER,  # enter "a"
        BUTTON_PAGE_PREV,  # back to Go
        BUTTON_ENTER,  # go Go
        BUTTON_ENTER,  # confirm key "a"
    ]
    ctx = create_ctx(mocker, btn_seq)
    passphrase_editor = PassphraseEditor(ctx)
    assert passphrase_editor._load_qr_passphrase() == MENU_CONTINUE
    assert ctx.input.wait_for_button.call_count == len(btn_seq)
    ctx.display.flash_text.assert_called_with(
        "Failed to load", 248, 2000, highlight_prefix=""
    )


def test_qr_passphrase_fails_on_encrypted_non_ascii_bytes(mocker, m5stickv, tdata):
    from krux.input import BUTTON_ENTER, BUTTON_PAGE, BUTTON_PAGE_PREV
    from krux.pages.wallet_settings import PassphraseEditor
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
        BUTTON_ENTER,  # confirm decrypt
        BUTTON_ENTER,  # type key
        BUTTON_ENTER,  # enter "a"
        BUTTON_PAGE_PREV,  # back to Go
        BUTTON_ENTER,  # go Go
        BUTTON_ENTER,  # confirm key "a"
    ]
    ctx = create_ctx(mocker, btn_seq)
    passphrase_editor = PassphraseEditor(ctx)
    assert passphrase_editor._load_qr_passphrase() == MENU_CONTINUE
    assert ctx.input.wait_for_button.call_count == len(btn_seq)
    ctx.display.flash_text.assert_called_with(
        "Failed to load", 248, 2000, highlight_prefix=""
    )


def test_passphrase_non_ascii_validation(m5stickv, mocker, tdata):
    from krux.pages.wallet_settings import PassphraseEditor
    from krux.pages import Menu, MENU_EXIT
    from krux.input import BUTTON_PAGE_PREV

    # Test non-ASCII passphrase rejection
    NON_ASCII_PASSPHRASE = "Testá"  # Contains non-ASCII character
    ctx = create_ctx(mocker, [BUTTON_PAGE_PREV], tdata.SINGLESIG_12_WORD_KEY)
    passphrase_editor = PassphraseEditor(ctx)

    # Mock the Menu's run_loop to return non-ASCII passphrase first, then exit
    menu_returns = [
        (0, NON_ASCII_PASSPHRASE),  # First call returns non-ASCII passphrase
        (0, MENU_EXIT),  # Second call exits
    ]
    mocker.patch.object(
        Menu,
        "run_loop",
        side_effect=menu_returns,
    )

    # Mock prompt to track if it was called
    prompt_spy = mocker.spy(passphrase_editor, "prompt")

    result = passphrase_editor.load_passphrase_menu(
        tdata.SINGLESIG_12_WORD_KEY.mnemonic
    )

    # Verify that it was called
    prompt_spy.assert_called()
    # Get the actual call arguments
    call_args = prompt_spy.call_args[0][0]
    assert call_args == "Proceed?"

    # Verify that the method returned None (exited without accepting passphrase)
    assert result is None


def test_passphrase_non_decodeable_validation(m5stickv, mocker, tdata):
    from krux.pages.wallet_settings import PassphraseEditor
    from krux.pages import Menu, MENU_EXIT

    # Test non-ASCII passphrase rejection
    BINARY_PASSPHRASE = b"\xde\xad\xbe\xef"  # Contains 0xdeadbeef, not decodeable
    ctx = create_ctx(mocker, None, tdata.SINGLESIG_12_WORD_KEY)
    passphrase_editor = PassphraseEditor(ctx)

    # Mock the Menu's run_loop to return non-ASCII passphrase first, then exit
    menu_returns = [
        (0, BINARY_PASSPHRASE),  # First call returns binary passphrase
        (0, MENU_EXIT),  # Second call exits
    ]
    mocker.patch.object(
        Menu,
        "run_loop",
        side_effect=menu_returns,
    )

    # Mock flash_error to track if it was called
    flash_error_spy = mocker.spy(passphrase_editor, "flash_error")

    result = passphrase_editor.load_passphrase_menu(
        tdata.SINGLESIG_12_WORD_KEY.mnemonic
    )

    # Verify that flash_error was called with error message
    flash_error_spy.assert_called()
    # Get the actual call arguments
    call_args = flash_error_spy.call_args[0][0]
    assert call_args == "Failed to load"

    # Verify that the method returned None (exited without accepting passphrase)
    assert result is None


def test_change_policy_types(m5stickv, mocker, tdata):
    from krux.pages.wallet_settings import WalletSettings
    from krux.wallet import Wallet
    from krux.key import Key, TYPE_SINGLESIG, TYPE_MULTISIG, TYPE_MINISCRIPT
    from krux.pages import BUTTON_ENTER, BUTTON_PAGE, BUTTON_PAGE_PREV

    BTN_SEQUENCE = [
        BUTTON_PAGE,  # Go to "Policy Type"
        BUTTON_ENTER,  # Enter "Policy Type"
        BUTTON_PAGE,  # Change to Multisig
        BUTTON_ENTER,  # Confirm Multisig
        BUTTON_PAGE_PREV,  # Go to Back
        BUTTON_ENTER,  # Leave policy type menu
        BUTTON_PAGE_PREV,  # Go to Back
        BUTTON_ENTER,  # Leave
    ]

    ctx = create_ctx(mocker, BTN_SEQUENCE, Wallet(tdata.SINGLESIG_12_WORD_KEY))

    # assert wallet starts as single-sig, native segwit
    assert ctx.wallet.is_multisig() is False
    assert ctx.wallet.is_miniscript() is False
    assert ctx.wallet.key.policy_type == TYPE_SINGLESIG
    assert ctx.wallet.key.script_type == "p2wpkh"

    mnemonic = ctx.wallet.key.mnemonic
    wallet_settings = WalletSettings(ctx)
    network, policy_type, script_type, account, derivation_path = (
        wallet_settings.customize_wallet(ctx.wallet.key)
    )
    ctx.wallet = Wallet(
        Key(
            mnemonic,
            policy_type,
            network,
            "",  # passphrase
            account,
            script_type,
            derivation_path,
        )
    )

    # Assert wallet is now multisig and changed to p2wsh
    assert ctx.wallet.is_multisig() is True
    assert ctx.wallet.is_miniscript() is False
    assert ctx.wallet.key.policy_type == TYPE_MULTISIG
    assert ctx.wallet.key.script_type == "p2wsh"
    assert ctx.input.wait_for_button.call_count == len(BTN_SEQUENCE)

    # Change to miniscript
    BTN_SEQUENCE = [
        BUTTON_PAGE,  # Go to "Policy Type"
        BUTTON_ENTER,  # Enter "Policy Type"
        *([BUTTON_PAGE] * 2),  # Change to Miniscript
        BUTTON_ENTER,  # Confirm Miniscript
        BUTTON_PAGE_PREV,  # Go to Back
        BUTTON_ENTER,  # Leave
    ]
    ctx = create_ctx(mocker, BTN_SEQUENCE, ctx.wallet)
    wallet_settings = WalletSettings(ctx)
    network, policy_type, script_type, account, derivation_path = (
        wallet_settings.customize_wallet(ctx.wallet.key)
    )
    ctx.wallet = Wallet(
        Key(
            mnemonic,
            policy_type,
            network,
            "",  # passphrase
            account,
            script_type,
            derivation_path,
        )
    )

    # Assert wallet is now miniscript and remained p2wsh
    assert ctx.wallet.is_multisig() is False
    assert ctx.wallet.is_miniscript() is True
    assert ctx.wallet.key.policy_type == TYPE_MINISCRIPT
    assert ctx.wallet.key.script_type == "p2wsh"
    assert ctx.input.wait_for_button.call_count == len(BTN_SEQUENCE)

    # Change back to singlesig
    BTN_SEQUENCE = [
        BUTTON_PAGE,  # Go to "Single/Multisig"
        BUTTON_ENTER,  # Enter "Single/Multisig"
        BUTTON_ENTER,  # Confirm Single
        *([BUTTON_PAGE] * 2),  # Choose Native Segwit
        BUTTON_ENTER,  # Confirm Native Segwit
        BUTTON_PAGE_PREV,  # Go to Back
        BUTTON_ENTER,  # Leave
    ]

    ctx = create_ctx(mocker, BTN_SEQUENCE, ctx.wallet)
    wallet_settings = WalletSettings(ctx)
    network, policy_type, script_type, account, derivation_path = (
        wallet_settings.customize_wallet(ctx.wallet.key)
    )
    ctx.wallet = Wallet(
        Key(
            mnemonic,
            policy_type,
            network,
            "",  # passphrase
            account,
            script_type,
            derivation_path,
        )
    )
    assert ctx.wallet.is_multisig() is False
    assert ctx.wallet.is_miniscript() is False
    assert ctx.wallet.key.policy_type == TYPE_SINGLESIG
    assert ctx.wallet.key.script_type == "p2wpkh"
    assert ctx.input.wait_for_button.call_count == len(BTN_SEQUENCE)

    # Going from single-sig to miniscript forces to change to script type
    BTN_SEQUENCE = [
        BUTTON_PAGE,  # Go to "Policy Type"
        BUTTON_ENTER,  # Enter "Policy Type"
        *([BUTTON_PAGE] * 2),  # Change to Miniscript
        BUTTON_ENTER,  # Confirm Miniscript
        BUTTON_PAGE,  # Change from Native Segwit to Taproot
        BUTTON_ENTER,  # Confirm Taproot
        BUTTON_PAGE_PREV,  # Go to Back
        BUTTON_ENTER,  # Leave
    ]

    ctx = create_ctx(mocker, BTN_SEQUENCE, ctx.wallet)
    wallet_settings = WalletSettings(ctx)
    network, policy_type, script_type, account, derivation_path = (
        wallet_settings.customize_wallet(ctx.wallet.key)
    )
    ctx.wallet = Wallet(
        Key(
            mnemonic,
            policy_type,
            network,
            "",  # passphrase
            account,
            script_type,
            derivation_path,
        )
    )
    assert ctx.wallet.is_multisig() is False
    assert ctx.wallet.is_miniscript() is True
    assert ctx.wallet.key.policy_type == TYPE_MINISCRIPT
    assert ctx.wallet.key.script_type == "p2tr"
    assert ctx.input.wait_for_button.call_count == len(BTN_SEQUENCE)


def test_change_script_type(m5stickv, mocker, tdata):
    from krux.pages.wallet_settings import WalletSettings
    from krux.wallet import Wallet
    from krux.key import Key
    from krux.pages import BUTTON_ENTER, BUTTON_PAGE, BUTTON_PAGE_PREV

    BTN_SEQUENCE_1 = [
        *([BUTTON_PAGE] * 2),  # Go to "Script Type"
        BUTTON_ENTER,  # Enter "Script Type"
        *([BUTTON_PAGE] * 3),  # Move to Taproot
        BUTTON_ENTER,  # Confirm Taproot
        BUTTON_PAGE_PREV,  # Go to Back
        BUTTON_ENTER,  # Leave
    ]
    ctx = create_ctx(mocker, BTN_SEQUENCE_1, Wallet(tdata.SINGLESIG_12_WORD_KEY))
    mnemonic = ctx.wallet.key.mnemonic
    wallet_settings = WalletSettings(ctx)
    network, policy_type, script_type, account, derivation_path = (
        wallet_settings.customize_wallet(ctx.wallet.key)
    )
    ctx.wallet = Wallet(
        Key(
            mnemonic,
            policy_type,
            network,
            "",  # passphrase
            account,
            script_type,
        )
    )

    assert ctx.wallet.key.script_type == "p2tr"
    assert ctx.input.wait_for_button.call_count == len(BTN_SEQUENCE_1)

    # Change back to legacy
    BTN_SEQUENCE_2 = [
        *([BUTTON_PAGE] * 2),  # Go to "Script Type"
        BUTTON_ENTER,  # Enter "Script Type"
        BUTTON_ENTER,  # Confirm Legacy
        BUTTON_PAGE_PREV,  # Go to Back
        BUTTON_ENTER,  # Leave
    ]
    ctx = create_ctx(mocker, BTN_SEQUENCE_2, ctx.wallet)
    wallet_settings = WalletSettings(ctx)
    network, policy_type, script_type, account, derivation_path = (
        wallet_settings.customize_wallet(ctx.wallet.key)
    )
    ctx.wallet = Wallet(
        Key(
            mnemonic,
            policy_type,
            network,
            "",  # passphrase
            account,
            script_type,
        )
    )
    assert ctx.wallet.key.script_type == "p2pkh"
    assert ctx.input.wait_for_button.call_count == len(BTN_SEQUENCE_2)

    # Change to nested segwit single-sig
    BTN_SEQUENCE_3 = [
        *([BUTTON_PAGE] * 2),  # Go to "Script Type"
        BUTTON_ENTER,  # Enter "Script Type"
        BUTTON_PAGE,  # Change from Legacy to Nested Segwit
        BUTTON_ENTER,  # Confirm Nested Segwit
        BUTTON_PAGE_PREV,  # Go to Back
        BUTTON_ENTER,  # Leave
    ]
    ctx = create_ctx(mocker, BTN_SEQUENCE_3, ctx.wallet)
    wallet_settings = WalletSettings(ctx)
    network, policy_type, script_type, account, derivation_path = (
        wallet_settings.customize_wallet(ctx.wallet.key)
    )
    ctx.wallet = Wallet(
        Key(
            mnemonic,
            policy_type,
            network,
            "",  # passphrase
            account,
            script_type,
        )
    )
    assert ctx.wallet.key.script_type == "p2sh-p2wpkh"
    assert ctx.input.wait_for_button.call_count == len(BTN_SEQUENCE_3)

    # Change native segwit single-sig
    BTN_SEQUENCE_4 = [
        *([BUTTON_PAGE] * 2),  # Go to "Script Type"
        BUTTON_ENTER,  # Enter "Script Type"
        *([BUTTON_PAGE] * 2),  # Change from Legacy to Native Segwit
        BUTTON_ENTER,  # Confirm Native Segwit
        BUTTON_PAGE_PREV,  # Go to Back
        BUTTON_ENTER,  # Leave
    ]
    ctx = create_ctx(mocker, BTN_SEQUENCE_4, ctx.wallet)
    wallet_settings = WalletSettings(ctx)
    network, policy_type, script_type, account, derivation_path = (
        wallet_settings.customize_wallet(ctx.wallet.key)
    )
    ctx.wallet = Wallet(
        Key(
            mnemonic,
            policy_type,
            network,
            "",  # passphrase
            account,
            script_type,
        )
    )
    assert ctx.wallet.key.script_type == "p2wpkh"
    assert ctx.input.wait_for_button.call_count == len(BTN_SEQUENCE_4)


def test_change_multisig_script_types(m5stickv, mocker, tdata):
    from krux.pages.wallet_settings import WalletSettings
    from krux.wallet import Wallet
    from krux.key import Key, TYPE_MULTISIG
    from krux.pages import BUTTON_ENTER, BUTTON_PAGE, BUTTON_PAGE_PREV

    # Start with p2sh multisig, move to change to another script type, but back out
    BTN_SEQUENCE = [
        BUTTON_PAGE,  # Go to "Policy Type"
        BUTTON_ENTER,  # Enter "Policy Type"
        BUTTON_PAGE,  # Change to Multisig
        BUTTON_ENTER,  # Confirm Multisig
        BUTTON_ENTER,  # Choose Legacy - 45
        *([BUTTON_PAGE] * 2),  # Move to script type
        BUTTON_ENTER,  # Enter "Script Type"
        BUTTON_PAGE_PREV,  # Go to Back
        BUTTON_ENTER,  # Leave
        BUTTON_PAGE_PREV,  # Go to Back
        BUTTON_ENTER,  # Leave
    ]

    ctx = create_ctx(mocker, BTN_SEQUENCE, Wallet(tdata.SINGLESIG_12_WORD_KEY))
    wallet_settings = WalletSettings(ctx)
    mnemonic = ctx.wallet.key.mnemonic
    network, policy_type, script_type, account, derivation_path = (
        wallet_settings.customize_wallet(ctx.wallet.key)
    )
    ctx.wallet = Wallet(
        Key(
            mnemonic,
            policy_type,
            network,
            "",  # passphrase
            account,
            script_type,
        )
    )

    # assert wallet is legacy multisig sh
    assert ctx.wallet.is_multisig() is True
    assert ctx.wallet.is_miniscript() is False
    assert ctx.wallet.key.policy_type == TYPE_MULTISIG
    assert ctx.wallet.key.script_type == "p2sh"
    assert ctx.input.wait_for_button.call_count == len(BTN_SEQUENCE)

    # Change to nested segwit multisig
    BTN_SEQUENCE = [
        BUTTON_PAGE,  # Go to "Policy Type"
        BUTTON_ENTER,  # Enter "Policy Type"
        BUTTON_PAGE,  # Change to Multisig
        BUTTON_ENTER,  # Confirm Multisig
        BUTTON_PAGE,  # Choose Nested Segwit - 48
        BUTTON_ENTER,  # Choose Nested Segwit - 48
        *([BUTTON_PAGE] * 2),  # Move to script type
        BUTTON_ENTER,  # Enter "Script Type"
        BUTTON_PAGE_PREV,  # Go to Back
        BUTTON_ENTER,  # Leave
        BUTTON_PAGE_PREV,  # Go to Back
        BUTTON_ENTER,  # Leave
    ]

    ctx = create_ctx(mocker, BTN_SEQUENCE, Wallet(tdata.SINGLESIG_12_WORD_KEY))
    wallet_settings = WalletSettings(ctx)
    mnemonic = ctx.wallet.key.mnemonic
    network, policy_type, script_type, account, derivation_path = (
        wallet_settings.customize_wallet(ctx.wallet.key)
    )
    ctx.wallet = Wallet(
        Key(
            mnemonic,
            policy_type,
            network,
            "",  # passphrase
            account,
            script_type,
        )
    )

    # assert wallet is legacy multisig sh
    assert ctx.wallet.is_multisig() is True
    assert ctx.wallet.is_miniscript() is False
    assert ctx.wallet.key.policy_type == TYPE_MULTISIG
    assert ctx.wallet.key.script_type == "p2sh-p2wsh"
    assert ctx.input.wait_for_button.call_count == len(BTN_SEQUENCE)

    # Change to native segwit multisig
    BTN_SEQUENCE = [
        BUTTON_PAGE,  # Go to "Policy Type"
        BUTTON_ENTER,  # Enter "Policy Type"
        BUTTON_PAGE,  # Change to Multisig
        BUTTON_ENTER,  # Confirm Multisig
        *([BUTTON_PAGE] * 2),  # Choose Native Segwit - 48
        BUTTON_ENTER,  # Choose Native Segwit - 48
        *([BUTTON_PAGE] * 2),  # Move to script type
        BUTTON_ENTER,  # Enter "Script Type"
        BUTTON_PAGE_PREV,  # Go to Back
        BUTTON_ENTER,  # Leave
        BUTTON_PAGE_PREV,  # Go to Back
        BUTTON_ENTER,  # Leave
    ]

    ctx = create_ctx(mocker, BTN_SEQUENCE, Wallet(tdata.SINGLESIG_12_WORD_KEY))
    wallet_settings = WalletSettings(ctx)
    mnemonic = ctx.wallet.key.mnemonic
    network, policy_type, script_type, account, derivation_path = (
        wallet_settings.customize_wallet(ctx.wallet.key)
    )
    ctx.wallet = Wallet(
        Key(
            mnemonic,
            policy_type,
            network,
            "",  # passphrase
            account,
            script_type,
        )
    )

    # assert wallet is legacy multisig sh
    assert ctx.wallet.is_multisig() is True
    assert ctx.wallet.is_miniscript() is False
    assert ctx.wallet.key.policy_type == TYPE_MULTISIG
    assert ctx.wallet.key.script_type == "p2wsh"
    assert ctx.input.wait_for_button.call_count == len(BTN_SEQUENCE)


def test_change_account(m5stickv, mocker, tdata):
    from krux.pages.wallet_settings import WalletSettings
    from krux.wallet import Wallet
    from krux.key import Key
    from krux.pages import BUTTON_ENTER, BUTTON_PAGE, BUTTON_PAGE_PREV

    BTN_SEQUENCE_1 = [
        *([BUTTON_PAGE] * 3),  # Go to "Account"
        BUTTON_ENTER,  # Enter "Account"
        BUTTON_PAGE,  # Move to number 2
        BUTTON_ENTER,  # Confirm number 2
        *([BUTTON_PAGE_PREV] * 2),  # Move to "Go"
        BUTTON_ENTER,  # Go
        BUTTON_PAGE_PREV,  # Go to Back
        BUTTON_ENTER,  # Leave
    ]
    ctx = create_ctx(mocker, BTN_SEQUENCE_1, Wallet(tdata.SINGLESIG_12_WORD_KEY))
    mnemonic = ctx.wallet.key.mnemonic
    wallet_settings = WalletSettings(ctx)
    network, policy_type, script_type, account, derivation_path = (
        wallet_settings.customize_wallet(ctx.wallet.key)
    )
    ctx.wallet = Wallet(
        Key(
            mnemonic,
            policy_type,
            network,
            "",  # passphrase
            account,
            script_type,
        )
    )

    assert ctx.wallet.key.account_index == 2
    assert ctx.input.wait_for_button.call_count == len(BTN_SEQUENCE_1)

    # Change back to account 0
    BTN_SEQUENCE_2 = [
        *([BUTTON_PAGE] * 3),  # Go to "Account"
        BUTTON_ENTER,  # Enter "Account"
        *([BUTTON_PAGE_PREV] * 3),  # Move to del number
        BUTTON_ENTER,  # Confirm del number
        BUTTON_PAGE_PREV,  # Move to "0"
        BUTTON_ENTER,  # Enter 0
        *([BUTTON_PAGE] * 3),  # Move to "Go"
        BUTTON_ENTER,  # Go
        BUTTON_PAGE_PREV,  # Move to Back
        BUTTON_ENTER,  # Leave
    ]
    ctx = create_ctx(mocker, BTN_SEQUENCE_2, ctx.wallet)
    wallet_settings = WalletSettings(ctx)
    network, policy_type, script_type, account, derivation_path = (
        wallet_settings.customize_wallet(ctx.wallet.key)
    )
    ctx.wallet = Wallet(
        Key(
            mnemonic,
            policy_type,
            network,
            "",  # passphrase
            account,
            script_type,
        )
    )
    assert ctx.wallet.key.account_index == 0
    assert ctx.input.wait_for_button.call_count == len(BTN_SEQUENCE_2)


def test_change_account_esc(m5stickv, mocker, tdata):
    from krux.pages.wallet_settings import WalletSettings
    from krux.wallet import Wallet
    from krux.key import Key
    from krux.pages import BUTTON_ENTER, BUTTON_PAGE, BUTTON_PAGE_PREV

    BTN_SEQUENCE_1 = [
        *([BUTTON_PAGE] * 3),  # Go to "Account"
        BUTTON_ENTER,  # Enter "Account"
        *([BUTTON_PAGE_PREV] * 2),  # Move to Esc
        BUTTON_ENTER,  # Press Esc
        BUTTON_ENTER,  # Confirm Esc
        BUTTON_PAGE_PREV,  # Move to Back
        BUTTON_ENTER,  # Leave
    ]

    ctx = create_ctx(mocker, BTN_SEQUENCE_1, Wallet(tdata.SINGLESIG_12_WORD_KEY))
    mnemonic = ctx.wallet.key.mnemonic
    wallet_settings = WalletSettings(ctx)
    network, policy_type, script_type, account, derivation_path = (
        wallet_settings.customize_wallet(ctx.wallet.key)
    )
    ctx.wallet = Wallet(
        Key(
            mnemonic,
            policy_type,
            network,
            "",  # passphrase
            account,
            script_type,
        )
    )
    assert ctx.wallet.key.account_index == 0
    assert ctx.input.wait_for_button.call_count == len(BTN_SEQUENCE_1)


def test_account_out_of_range(m5stickv, mocker, tdata):
    from krux.pages.wallet_settings import WalletSettings
    from krux.wallet import Wallet
    from krux.key import Key
    from krux.pages import BUTTON_ENTER, BUTTON_PAGE, BUTTON_PAGE_PREV
    from krux.pages.utils import Utils

    BTN_SEQUENCE_1 = [
        *([BUTTON_PAGE] * 3),  # Go to "Account"
        BUTTON_ENTER,  # Enter "Account"
        BUTTON_PAGE,  # Move to number 2
        *([BUTTON_ENTER] * 11),  # Press number 2 11 times
        *([BUTTON_PAGE_PREV] * 2),  # Move to "Go"
        BUTTON_ENTER,  # Go
        BUTTON_PAGE_PREV,  # Go to Back
        BUTTON_ENTER,  # Leave
    ]

    ctx = create_ctx(mocker, BTN_SEQUENCE_1, Wallet(tdata.SINGLESIG_12_WORD_KEY))
    mnemonic = ctx.wallet.key.mnemonic
    wallet_settings = WalletSettings(ctx)
    Utils.flash_error = mocker.MagicMock()
    network, policy_type, script_type, account, derivation_path = (
        wallet_settings.customize_wallet(ctx.wallet.key)
    )
    ctx.wallet = Wallet(
        Key(
            mnemonic,
            policy_type,
            network,
            "",  # passphrase
            account,
            script_type,
        )
    )

    Utils.flash_error.assert_called_with(
        "Value 22222222222 out of range: [0, 2147483647]"
    )
    assert ctx.wallet.key.account_index == 0
    assert ctx.input.wait_for_button.call_count == len(BTN_SEQUENCE_1)


def test_change_derivation_path(amigo, mocker, tdata):
    from krux.pages.wallet_settings import WalletSettings
    from krux.wallet import Wallet
    from krux.key import Key
    from krux.pages import BUTTON_ENTER, BUTTON_PAGE, BUTTON_PAGE_PREV

    BTN_SEQUENCE = [
        BUTTON_PAGE,  # Go to "Policy Type"
        BUTTON_ENTER,  # Enter "Policy Type"
        *([BUTTON_PAGE] * 2),  # Change to Miniscript
        BUTTON_ENTER,  # Confirm Miniscript
        BUTTON_PAGE,  # Change from Native Segwit to Taproot
        BUTTON_ENTER,  # Confirm Taproot
        *([BUTTON_PAGE] * 3),  # Go to "Derivation Path"
        BUTTON_ENTER,  # Enter "Derivation Path"
        *([BUTTON_PAGE_PREV] * 3),  # Move to "Del"
        *([BUTTON_ENTER] * 2),  # Del "2h" from the derivation path
        *([BUTTON_PAGE] * 2),  # Move to "Go"
        BUTTON_ENTER,  # Go
        # Get invalid derivation path (m/48h/0h/0h/), we need to delete trailing "/"
        *([BUTTON_PAGE_PREV] * 3),  # Move to "Del" again
        BUTTON_ENTER,  # Del "/"
        *([BUTTON_PAGE] * 2),  # Move to "Go"
        BUTTON_ENTER,  # Go
        BUTTON_PAGE_PREV,  # Go to Back
        BUTTON_ENTER,  # Leave
    ]

    ctx = create_ctx(mocker, BTN_SEQUENCE, Wallet(tdata.SINGLESIG_12_WORD_KEY))
    mnemonic = ctx.wallet.key.mnemonic
    wallet_settings = WalletSettings(ctx)
    network, policy_type, script_type, account, derivation_path = (
        wallet_settings.customize_wallet(ctx.wallet.key)
    )
    ctx.wallet = Wallet(
        Key(
            mnemonic,
            policy_type,
            network,
            "",  # passphrase
            account,
            script_type,
            derivation_path,
        )
    )

    assert ctx.wallet.key.derivation_str() == "m/48h/0h/0h"
    assert ctx.input.wait_for_button.call_count == len(BTN_SEQUENCE)


def test_change_derivation_path_not_hardened_node(amigo, mocker, tdata):
    from krux.pages.wallet_settings import WalletSettings
    from krux.wallet import Wallet
    from krux.key import Key
    from krux.pages import BUTTON_ENTER, BUTTON_PAGE, BUTTON_PAGE_PREV

    # test derivation path with non-hardened node for multisig p2sh
    # should not get warning/prompt as last node is hardened
    BTN_SEQUENCE = [
        BUTTON_PAGE,  # Go to "Policy Type"
        BUTTON_ENTER,  # Enter "Policy Type"
        BUTTON_PAGE,  # Change to Multisig
        BUTTON_ENTER,  # Confirm Multisig
        BUTTON_ENTER,  # Choose Legacy - 45
        *([BUTTON_PAGE] * 3),  # Go to "Derivation Path"
        BUTTON_ENTER,  # Enter "Derivation Path"
        *([BUTTON_PAGE_PREV] * 5),  # Move to "/"
        BUTTON_ENTER,  # Add "/"
        BUTTON_PAGE_PREV,  # Move to "0"
        BUTTON_ENTER,  # Add "0"
        *([BUTTON_PAGE] * 5),  # Move to "Go"
        BUTTON_ENTER,  # Go
        BUTTON_PAGE_PREV,  # Go to Back
        BUTTON_ENTER,  # Leave
    ]

    ctx = create_ctx(mocker, BTN_SEQUENCE, Wallet(tdata.SINGLESIG_12_WORD_KEY))
    mnemonic = ctx.wallet.key.mnemonic
    wallet_settings = WalletSettings(ctx)
    mocker.spy(wallet_settings, "prompt")

    network, policy_type, script_type, account, derivation_path = (
        wallet_settings.customize_wallet(ctx.wallet.key)
    )
    ctx.wallet = Wallet(
        Key(
            mnemonic,
            policy_type,
            network,
            "",  # passphrase
            account,
            script_type,
            derivation_path,
        )
    )

    assert ctx.wallet.key.derivation_str() == "m/45h/0"
    assert ctx.input.wait_for_button.call_count == len(BTN_SEQUENCE)
    wallet_settings.prompt.assert_not_called()

    # Test derivation path with non-hardened node for miniscript p2wsh
    # should get warning/prompt as last node is not hardened
    BTN_SEQUENCE = [
        BUTTON_PAGE,  # Go to "Policy Type"
        BUTTON_ENTER,  # Enter "Policy Type"
        *([BUTTON_PAGE] * 2),  # Change to Miniscript
        BUTTON_ENTER,  # Confirm Miniscript
        BUTTON_ENTER,  # Confirm Native Segwit
        *([BUTTON_PAGE] * 3),  # Go to "Derivation Path"
        BUTTON_ENTER,  # Enter "Derivation Path"
        *([BUTTON_PAGE_PREV] * 3),  # Move to "Del"
        BUTTON_ENTER,  # Del last "h" from the derivation path
        *([BUTTON_PAGE] * 2),  # Move to "Go"
        BUTTON_ENTER,  # Go
        # Get not hardened warning/prompt, but not accept it
        BUTTON_PAGE_PREV,  # Move to "No"
        BUTTON_ENTER,  # Do not accept warning
        BUTTON_PAGE_PREV,  # Move to "Go"
        BUTTON_ENTER,  # Go
        # Get not hardened warning/prompt, accept it this time
        BUTTON_ENTER,  # Accept warning
        BUTTON_PAGE_PREV,  # Go to Back
        BUTTON_ENTER,  # Leave
    ]

    ctx = create_ctx(mocker, BTN_SEQUENCE, Wallet(tdata.SINGLESIG_12_WORD_KEY))
    mnemonic = ctx.wallet.key.mnemonic
    wallet_settings = WalletSettings(ctx)
    mocker.spy(wallet_settings, "prompt")

    network, policy_type, script_type, account, derivation_path = (
        wallet_settings.customize_wallet(ctx.wallet.key)
    )
    ctx.wallet = Wallet(
        Key(
            mnemonic,
            policy_type,
            network,
            "",  # passphrase
            account,
            script_type,
            derivation_path,
        )
    )

    prompt_calls = [
        *(
            [
                mocker.call(
                    "".join(
                        [
                            "Some nodes are not hardened:",
                            "\n\n",
                            "Node 3: 2",
                            "\n\n",
                            "Proceed?",
                        ]
                    ),
                    ctx.display.height() // 2,
                    highlight_prefix=":",
                )
            ]
            * 2
        )
    ]

    assert ctx.wallet.key.derivation_str() == "m/48h/0h/0h/2"
    assert ctx.input.wait_for_button.call_count == len(BTN_SEQUENCE)
    wallet_settings.prompt.assert_has_calls(prompt_calls)

    # Test derivation path with non-hardened node for miniscript p2tr
    # should get warning/prompt as last node is not hardened
    BTN_SEQUENCE = [
        BUTTON_PAGE,  # Go to "Policy Type"
        BUTTON_ENTER,  # Enter "Policy Type"
        *([BUTTON_PAGE] * 2),  # Change to Miniscript
        BUTTON_ENTER,  # Confirm Miniscript
        BUTTON_PAGE,  # Change from Native Segwit to Taproot
        BUTTON_ENTER,  # Confirm Taproot
        *([BUTTON_PAGE] * 3),  # Go to "Derivation Path"
        BUTTON_ENTER,  # Enter "Derivation Path"
        *([BUTTON_PAGE_PREV] * 3),  # Move to "Del"
        BUTTON_ENTER,  # Del last "h" from the derivation path
        *([BUTTON_PAGE] * 2),  # Move to "Go"
        BUTTON_ENTER,  # Go
        # Get not hardened warning/prompt, but not accept it
        BUTTON_PAGE_PREV,  # Move to "No"
        BUTTON_ENTER,  # Do not accept warning
        BUTTON_PAGE_PREV,  # Move to "Go"
        BUTTON_ENTER,  # Go
        # Get not hardened warning/prompt, accept it this time
        BUTTON_ENTER,  # Accept warning
        BUTTON_PAGE_PREV,  # Go to Back
        BUTTON_ENTER,  # Leave
    ]

    ctx = create_ctx(mocker, BTN_SEQUENCE, Wallet(tdata.SINGLESIG_12_WORD_KEY))
    mnemonic = ctx.wallet.key.mnemonic
    wallet_settings = WalletSettings(ctx)
    mocker.spy(wallet_settings, "prompt")

    network, policy_type, script_type, account, derivation_path = (
        wallet_settings.customize_wallet(ctx.wallet.key)
    )
    ctx.wallet = Wallet(
        Key(
            mnemonic,
            policy_type,
            network,
            "",  # passphrase
            account,
            script_type,
            derivation_path,
        )
    )

    prompt_calls = [
        *(
            [
                mocker.call(
                    "".join(
                        [
                            "Some nodes are not hardened:",
                            "\n\n",
                            "Node 3: 2",
                            "\n\n",
                            "Proceed?",
                        ]
                    ),
                    ctx.display.height() // 2,
                    highlight_prefix=":",
                )
            ]
            * 2
        )
    ]

    assert ctx.wallet.key.derivation_str() == "m/48h/0h/0h/2"
    assert ctx.input.wait_for_button.call_count == len(BTN_SEQUENCE)
    wallet_settings.prompt.assert_has_calls(prompt_calls)
