from . import create_ctx

def test_qr_passphrase(m5stickv, mocker):
    from krux.pages.wallet_settings import PassphraseEditor

    TEST_VALUE = "Test value"
    QR_DATA = (TEST_VALUE, None)
    ctx = create_ctx(mocker, None)
    passphrase_editor = PassphraseEditor(ctx)
    mocker.patch.object(
        passphrase_editor, "capture_qr_code", mocker.MagicMock(return_value=QR_DATA)
    )
    test_passphrase = passphrase_editor._load_qr_passphrase()

    assert test_passphrase == TEST_VALUE


def test_qr_passphrase_too_long(m5stickv, mocker):
    from krux.pages.wallet_settings import PassphraseEditor, MENU_CONTINUE

    TEST_VALUE = "Test value" * 25
    QR_DATA = (TEST_VALUE, None)
    ctx = create_ctx(mocker, None)
    passphrase_editor = PassphraseEditor(ctx)
    mocker.patch.object(
        passphrase_editor, "capture_qr_code", mocker.MagicMock(return_value=QR_DATA)
    )
    test_passphrase = passphrase_editor._load_qr_passphrase()

    assert test_passphrase == MENU_CONTINUE


def test_qr_passphrase_fail(m5stickv, mocker):
    from krux.pages.wallet_settings import PassphraseEditor, MENU_CONTINUE

    TEST_VALUE = None
    QR_DATA = (TEST_VALUE, None)
    ctx = create_ctx(mocker, None)
    passphrase_editor = PassphraseEditor(ctx)
    mocker.patch.object(
        passphrase_editor, "capture_qr_code", mocker.MagicMock(return_value=QR_DATA)
    )
    test_passphrase = passphrase_editor._load_qr_passphrase()

    assert test_passphrase == MENU_CONTINUE