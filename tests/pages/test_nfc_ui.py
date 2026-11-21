# NFC page tests
#
# The card stack itself is covered in tests/test_nfc.py; these are about the
# pages around it - that the reader is never touched while the feature is off,
# that the field comes down on every exit path, and that a card carrying
# something other than a Krux backup cannot walk a seed onto the device.

import pytest
from . import create_ctx
from .home_pages.test_home import tdata

ENVELOPE = b"KEF-ENVELOPE-BYTES"
ENTROPY_12 = bytes(range(16))


@pytest.fixture
def nfc_on(m5stickv):
    """NFC switched on in settings, as the menus require"""
    from krux.krux_settings import Settings

    Settings().hardware.nfc.enabled = True
    yield m5stickv
    Settings().hardware.nfc.enabled = False


def mock_nfc(mocker, has_record=False, record=ENVELOPE):
    """A stand-in for the NFC facade, with the card stack already exercised"""
    nfc = mocker.MagicMock()
    nfc.has_record.return_value = has_record
    nfc.read_record.return_value = record
    mocker.patch("krux.nfc.NFC", mocker.MagicMock(return_value=nfc))
    return nfc


# ---------- The setting is the hardware boundary ----------


def test_disabled_nfc_never_touches_the_bus(m5stickv, mocker):
    from krux.pages.nfc_ui import NFCTapPage
    from krux.krux_settings import Settings

    Settings().hardware.nfc.enabled = False
    nfc = mock_nfc(mocker)

    assert not NFCTapPage(create_ctx(mocker, [])).open_reader()
    nfc.init.assert_not_called()


def test_missing_reader_is_reported(nfc_on, mocker):
    from krux.pages.nfc_ui import NFCTapPage
    from krux.nfc import NFCNotFound

    nfc = mock_nfc(mocker)
    nfc.init.side_effect = NFCNotFound("No reader")

    page = NFCTapPage(create_ctx(mocker, []))
    assert not page.open_reader()
    assert page.nfc is None


def test_reader_probe_leaves_nothing_attached(nfc_on, mocker):
    from krux.pages.nfc_ui import NFCTapPage

    nfc = mock_nfc(mocker)
    NFCTapPage(create_ctx(mocker, [])).test_reader()

    nfc.init.assert_called_once()
    nfc.deinit.assert_called_once()
    nfc.field.assert_not_called()  # a probe never energizes the antenna


# ---------- Tap page ----------


def test_cancelling_the_tap_page_drops_the_field(nfc_on, mocker):
    from krux.pages.nfc_ui import NFCTapPage
    from krux.input import BUTTON_PAGE
    from krux.nfc import NFCNotFound

    nfc = mock_nfc(mocker)
    nfc.poll.side_effect = NFCNotFound("No card")

    page = NFCTapPage(create_ctx(mocker, [BUTTON_PAGE]))
    page.open_reader()
    assert not page.wait_for_tag("Store on NFC Card")
    nfc.field.assert_any_call(True)
    nfc.field.assert_any_call(False)


def test_polling_continues_until_a_card_shows_up(nfc_on, mocker):
    from krux.pages.nfc_ui import NFCTapPage
    from krux.nfc import NFCNotFound

    nfc = mock_nfc(mocker)
    nfc.poll.side_effect = [NFCNotFound("No card"), NFCNotFound("No card"), None]

    page = NFCTapPage(create_ctx(mocker, [None, None]))
    page.open_reader()
    assert page.wait_for_tag("Store on NFC Card")


# ---------- Store ----------


def test_store_writes_the_envelope(nfc_on, mocker):
    from krux.pages.nfc_ui import StoreOnNFC
    from krux.input import BUTTON_ENTER
    from krux.nfc import RECORD_KEF

    nfc = mock_nfc(mocker)
    # One press dismisses the confirmation screen
    StoreOnNFC(create_ctx(mocker, [BUTTON_ENTER])).write(ENVELOPE, "abcd1234")

    nfc.write_record.assert_called_once_with(ENVELOPE, RECORD_KEF)
    nfc.deinit.assert_called_once()


def test_store_asks_before_overwriting(nfc_on, mocker):
    from krux.pages.nfc_ui import StoreOnNFC
    from krux.input import BUTTON_ENTER
    from krux.nfc import RECORD_KEF

    nfc = mock_nfc(mocker, has_record=True)
    StoreOnNFC(create_ctx(mocker, [BUTTON_ENTER, BUTTON_ENTER])).write(
        ENVELOPE, "abcd1234"
    )
    nfc.write_record.assert_called_once_with(ENVELOPE, RECORD_KEF)


def test_store_declining_the_overwrite_leaves_the_card_alone(nfc_on, mocker):
    from krux.pages.nfc_ui import StoreOnNFC
    from krux.input import BUTTON_PAGE

    nfc = mock_nfc(mocker, has_record=True)
    # BUTTON_PAGE answers "No" on a minimal display
    StoreOnNFC(create_ctx(mocker, [BUTTON_PAGE])).write(ENVELOPE, "abcd1234")

    nfc.write_record.assert_not_called()
    nfc.deinit.assert_called_once()


def test_store_reports_a_card_that_cannot_hold_the_backup(nfc_on, mocker):
    from krux.pages.nfc_ui import StoreOnNFC
    from krux.nfc import NFCSizeError

    nfc = mock_nfc(mocker)
    nfc.write_record.side_effect = NFCSizeError("too big")

    ctx = create_ctx(mocker, [])
    StoreOnNFC(ctx).write(ENVELOPE, "abcd1234")
    ctx.display.flash_text.assert_called_once()
    nfc.deinit.assert_called_once()


def test_store_descriptor_tags_the_record_as_a_descriptor(nfc_on, mocker):
    """The type byte is what keeps this card out of the mnemonic loader"""
    from krux.pages.nfc_ui import StoreOnNFC
    from krux.nfc import RECORD_DESCRIPTOR

    nfc = mock_nfc(mocker)
    StoreOnNFC(create_ctx(mocker, [])).write_descriptor(ENVELOPE)

    nfc.write_record.assert_called_once_with(ENVELOPE, RECORD_DESCRIPTOR)
    nfc.field.assert_any_call(True)
    nfc.deinit.assert_called_once()


def test_store_descriptor_reports_a_card_that_cannot_hold_it(nfc_on, mocker):
    """A 3 of 5 is several times the size of a seed, so this path is reachable"""
    from krux.pages.nfc_ui import StoreOnNFC
    from krux.nfc import NFCSizeError

    nfc = mock_nfc(mocker)
    nfc.write_record.side_effect = NFCSizeError("too big")

    ctx = create_ctx(mocker, [])
    StoreOnNFC(ctx).write_descriptor(ENVELOPE)
    ctx.display.flash_text.assert_called_once()
    nfc.deinit.assert_called_once()


def test_store_descriptor_warns_before_replacing_a_seed(nfc_on, mocker):
    """has_record() takes no type, so the card holding a seed still warns"""
    from krux.pages.nfc_ui import StoreOnNFC
    from krux.input import BUTTON_PAGE

    nfc = mock_nfc(mocker, has_record=True)
    # BUTTON_PAGE answers "No" on a minimal display
    StoreOnNFC(create_ctx(mocker, [BUTTON_PAGE])).write_descriptor(ENVELOPE)

    nfc.write_record.assert_not_called()
    nfc.deinit.assert_called_once()


def test_a_write_that_fails_mid_card_is_reported(nfc_on, mocker):
    """Not a size problem - the card moved, or a block refused the write"""
    from krux.pages.nfc_ui import StoreOnNFC
    from krux.nfc import NFCError

    for store in ("write", "write_descriptor"):
        nfc = mock_nfc(mocker)
        nfc.write_record.side_effect = NFCError("write not acknowledged")

        ctx = create_ctx(mocker, [])
        page = StoreOnNFC(ctx)
        if store == "write":
            page.write(ENVELOPE, "abcd1234")
        else:
            page.write_descriptor(ENVELOPE)

        ctx.display.flash_text.assert_called_once()
        nfc.deinit.assert_called_once()


def test_leaving_the_tap_page_stores_nothing(nfc_on, mocker):
    from krux.pages.nfc_ui import StoreOnNFC
    from krux.input import BUTTON_PAGE
    from krux.nfc import NFCNotFound

    nfc = mock_nfc(mocker)
    nfc.poll.side_effect = NFCNotFound("No card")

    StoreOnNFC(create_ctx(mocker, [BUTTON_PAGE])).write_descriptor(ENVELOPE)

    nfc.write_record.assert_not_called()
    nfc.field.assert_any_call(False)
    nfc.deinit.assert_called_once()


# ---------- Load ----------


def test_load_returns_the_envelope_and_drops_the_reader(nfc_on, mocker):
    from krux.pages.nfc_ui import LoadFromNFC

    nfc = mock_nfc(mocker)
    assert LoadFromNFC(create_ctx(mocker, [])).read() == ENVELOPE
    # The password prompt only ever runs with the antenna already down
    nfc.deinit.assert_called_once()


def test_load_from_a_card_with_no_backup(nfc_on, mocker):
    from krux.pages.nfc_ui import LoadFromNFC
    from krux.nfc import NFCNotFound

    nfc = mock_nfc(mocker)
    nfc.read_record.side_effect = NFCNotFound("no record")

    assert LoadFromNFC(create_ctx(mocker, [])).read() is None
    nfc.deinit.assert_called_once()


def test_load_asks_the_card_for_the_type_the_caller_can_parse(nfc_on, mocker):
    from krux.pages.nfc_ui import LoadFromNFC
    from krux.nfc import RECORD_DESCRIPTOR, RECORD_KEF

    nfc = mock_nfc(mocker)
    LoadFromNFC(create_ctx(mocker, [])).read(RECORD_DESCRIPTOR)
    nfc.read_record.assert_called_once_with(RECORD_DESCRIPTOR)

    nfc = mock_nfc(mocker)
    LoadFromNFC(create_ctx(mocker, [])).read()
    nfc.read_record.assert_called_once_with(RECORD_KEF)


def test_load_decrypts_into_words(nfc_on, mocker):
    from krux.pages.encryption_ui import LoadEncryptedMnemonic, KEFEnvelope

    mock_nfc(mocker)
    mocker.patch.object(KEFEnvelope, "parse", return_value=True)
    mocker.patch.object(KEFEnvelope, "unseal_ui", return_value=ENTROPY_12)

    assert len(LoadEncryptedMnemonic(create_ctx(mocker, [])).load_from_nfc()) == 12


@pytest.mark.parametrize(
    "parse_ok, unseal",
    [
        # A card that decrypts to plaintext words - a format Krux never writes
        # to one, and therefore one no genuine card can present
        (True, b"abandon abandon abandon"),
        (True, KeyError("Failed to decrypt")),  # wrong password
        (False, None),  # not a KEF envelope at all
    ],
)
def test_a_card_that_is_not_a_krux_backup_loads_nothing(
    nfc_on, mocker, parse_ok, unseal
):
    from krux.pages.encryption_ui import LoadEncryptedMnemonic, KEFEnvelope
    from krux.pages import MENU_CONTINUE

    mock_nfc(mocker)
    mocker.patch.object(KEFEnvelope, "parse", return_value=parse_ok)
    if isinstance(unseal, Exception):
        mocker.patch.object(KEFEnvelope, "unseal_ui", side_effect=unseal)
    else:
        mocker.patch.object(KEFEnvelope, "unseal_ui", return_value=unseal)

    ctx = create_ctx(mocker, [])
    assert LoadEncryptedMnemonic(ctx).load_from_nfc() == MENU_CONTINUE
    ctx.display.flash_text.assert_called_once()


# ---------- Erase ----------


def test_erase_wipes_the_card(nfc_on, mocker):
    from krux.pages.nfc_ui import EraseNFC
    from krux.input import BUTTON_ENTER

    nfc = mock_nfc(mocker, has_record=True)
    EraseNFC(create_ctx(mocker, [BUTTON_ENTER])).erase()

    nfc.erase.assert_called_once_with()
    nfc.field.assert_any_call(True)
    nfc.deinit.assert_called_once()


def test_erase_asks_first(nfc_on, mocker):
    from krux.pages.nfc_ui import EraseNFC
    from krux.input import BUTTON_PAGE

    nfc = mock_nfc(mocker, has_record=True)
    # BUTTON_PAGE answers "No" on a minimal display
    EraseNFC(create_ctx(mocker, [BUTTON_PAGE])).erase()

    nfc.erase.assert_not_called()
    nfc.deinit.assert_called_once()


def test_erase_does_not_probe_for_a_record_first(nfc_on, mocker):
    """It takes the whole data area, so what Krux recognises is beside the
    point and reporting it would reassure the wrong way."""
    from krux.pages.nfc_ui import EraseNFC
    from krux.input import BUTTON_ENTER

    nfc = mock_nfc(mocker)
    EraseNFC(create_ctx(mocker, [BUTTON_ENTER])).erase()

    nfc.has_record.assert_not_called()
    nfc.erase.assert_called_once_with()


def test_a_card_pulled_away_mid_erase_is_reported(nfc_on, mocker):
    from krux.pages.nfc_ui import EraseNFC
    from krux.nfc import NFCError
    from krux.input import BUTTON_ENTER

    nfc = mock_nfc(mocker)
    nfc.erase.side_effect = NFCError("write not acknowledged")

    ctx = create_ctx(mocker, [BUTTON_ENTER])
    EraseNFC(ctx).erase()

    ctx.display.flash_text.assert_called_once()
    nfc.deinit.assert_called_once()


def test_leaving_the_erase_tap_page_wipes_nothing(nfc_on, mocker):
    from krux.pages.nfc_ui import EraseNFC
    from krux.input import BUTTON_PAGE
    from krux.nfc import NFCNotFound

    nfc = mock_nfc(mocker)
    nfc.poll.side_effect = NFCNotFound("No card")

    EraseNFC(create_ctx(mocker, [BUTTON_PAGE])).erase()

    nfc.erase.assert_not_called()
    nfc.field.assert_any_call(False)
    nfc.deinit.assert_called_once()


def test_a_card_that_drifts_off_after_the_prompt_is_not_erased(nfc_on, mocker):
    """The confirmation screen was up in between, and the card only had to move
    a centimetre. It is asked for again rather than trusted."""
    from krux.pages.nfc_ui import EraseNFC
    from krux.nfc import NFCNotFound
    from krux.input import BUTTON_ENTER, BUTTON_PAGE

    nfc = mock_nfc(mocker)
    nfc.poll.side_effect = [None] + [NFCNotFound("gone")] * 10

    EraseNFC(create_ctx(mocker, [BUTTON_ENTER, BUTTON_PAGE])).erase()

    nfc.erase.assert_not_called()
    nfc.deinit.assert_called_once()


def test_erase_without_a_reader_touches_nothing(nfc_on, mocker):
    from krux.pages.nfc_ui import EraseNFC
    from krux.nfc import NFCNotFound

    nfc = mock_nfc(mocker)
    nfc.init.side_effect = NFCNotFound("No reader")

    EraseNFC(create_ctx(mocker, [])).erase()

    nfc.field.assert_not_called()
    nfc.erase.assert_not_called()


# ---------- Menu gating ----------


def _menu_labels(mocker, module, run):
    """The labels a menu offers, without running its loop"""
    captured = []

    class FakeMenu:
        back_index = 0

        def __init__(self, _ctx, items, **_kwargs):
            captured.extend(items)

        def run_loop(self, *_args, **_kwargs):
            return 0, None

    mocker.patch.object(module, "Menu", FakeMenu)
    run()
    return [item[0] for item in captured]


def _load_menu(mocker):
    from krux.pages.login import Login
    import krux.pages.mnemonic_loader as loader

    login = Login(create_ctx(mocker, []))
    return _menu_labels(mocker, loader, login.load_key)


def test_load_menu_hides_nfc_while_it_is_off(m5stickv, mocker):
    from krux.krux_settings import Settings

    Settings().hardware.nfc.enabled = False
    labels = _load_menu(mocker)
    assert "From Storage" in labels
    assert not any("NFC" in label for label in labels)


def test_load_menu_offers_nfc_when_it_is_on(nfc_on, mocker):
    assert "From NFC Card" in _load_menu(mocker)


def test_backup_menu_offers_nfc_when_it_is_on(nfc_on, mocker):
    import krux.pages.encryption_ui as encryption_ui

    page = encryption_ui.EncryptMnemonic(create_ctx(mocker, []))
    labels = _menu_labels(mocker, encryption_ui, page.encrypt_menu)
    assert labels.index("Store on NFC Card") == 2


def _tools_menu(mocker):
    import krux.pages.tools as tools

    captured = []

    class FakeMenu:
        back_index = 0

        def __init__(self, _ctx, items, **_kwargs):
            captured.extend(items)

        def run_loop(self, *_args, **_kwargs):
            return 0, None

    mocker.patch.object(tools, "Menu", FakeMenu)
    tools.Tools(create_ctx(mocker, []))
    return [item[0] for item in captured]


def test_tools_hides_the_erase_tool_while_nfc_is_off(m5stickv, mocker):
    from krux.krux_settings import Settings

    Settings().hardware.nfc.enabled = False
    labels = _tools_menu(mocker)
    assert "Descriptor Addresses" in labels
    assert not any("NFC" in label for label in labels)


def test_tools_offers_the_erase_tool_when_nfc_is_on(nfc_on, mocker):
    assert "Erase NFC Card" in _tools_menu(mocker)


def test_the_tools_entry_reaches_the_erase_page(nfc_on, mocker):
    from krux.pages.tools import Tools
    from krux.input import BUTTON_ENTER

    nfc = mock_nfc(mocker)
    Tools(create_ctx(mocker, [BUTTON_ENTER])).erase_nfc_card()

    nfc.erase.assert_called_once_with()


# ---------- Datum tool ----------


def _datum_view(mocker, contents):
    """A DatumToolView holding contents, with its analysis already run"""
    from krux.pages.datum_tool import DatumTool

    page = DatumTool(create_ctx(mocker, []))
    page.contents = contents
    page.title = "Datum"
    page._analyze_contents()
    return page


def test_datum_offers_a_card_alongside_sd(nfc_on, mocker):
    labels = [item[0] for item in _datum_view(mocker, "hello")._build_options_menu()]
    assert "Save to SD card" in labels
    assert "Store on NFC Card" in labels


def test_datum_hides_the_card_while_nfc_is_off(m5stickv, mocker):
    from krux.krux_settings import Settings

    Settings().hardware.nfc.enabled = False
    labels = [item[0] for item in _datum_view(mocker, "hello")._build_options_menu()]
    assert "Save to SD card" in labels
    assert not any("NFC" in label for label in labels)


@pytest.mark.parametrize(
    "contents",
    [
        "olympic term tissue route sense program under choose bean emerge "
        "velvet absurd",  # 12 words
        bytes(range(1, 16)) + b"\xff",  # 16 bytes of what looks like entropy
    ],
)
def test_a_datum_that_looks_like_a_seed_reaches_no_card(nfc_on, mocker, contents):
    """The card is behind the same gate as the SD card. A mnemonic the datum
    tool is holding does not leave the device in the clear by either road."""
    page = _datum_view(mocker, contents)
    assert page.sensitive

    labels = [item[0] for item in page._build_options_menu()]
    assert "Save to SD card" not in labels
    assert not any("NFC" in label for label in labels)


def test_datum_write_tags_the_record_as_a_datum(nfc_on, mocker):
    """Its own type, so a datum card loads in neither the wallet nor the
    mnemonic loader."""
    from krux.nfc import RECORD_DATUM

    nfc = mock_nfc(mocker)
    page = _datum_view(mocker, "hello")
    page.ctx = create_ctx(mocker, [])
    page.save_nfc()

    nfc.write_record.assert_called_once_with(b"hello", RECORD_DATUM)


def test_datum_read_accepts_any_krux_record(nfc_on, mocker):
    """The inspection tool: a seed card, a descriptor card and a datum card all
    open here, as the bytes they are."""
    from krux.pages.datum_tool import DatumTool, DatumToolMenu
    from krux.nfc import KNOWN_RECORD_TYPES

    nfc = mock_nfc(mocker, record=b"\x01\x02\x03")
    mocker.patch.object(DatumTool, "view_contents", return_value=None)

    DatumToolMenu(create_ctx(mocker, [])).read_nfc()
    nfc.read_record.assert_called_once_with(KNOWN_RECORD_TYPES)


def test_datum_input_menu_offers_the_card_only_when_on(nfc_on, mocker):
    import krux.pages.datum_tool as datum_tool

    labels = _menu_labels(
        mocker, datum_tool, lambda: datum_tool.DatumToolMenu(create_ctx(mocker, []))
    )
    assert "From NFC Card" in labels


# ---------- Extended public key ----------


def test_storing_an_xpub_on_a_card_end_to_end(nfc_on, mocker, tdata):
    """Through the real menus, so the entry is where a user would find it"""
    from krux.pages.home_pages.pub_key_view import PubkeyView
    from krux.wallet import Wallet
    from krux.input import BUTTON_ENTER, BUTTON_PAGE, BUTTON_PAGE_PREV
    from krux.nfc import RECORD_XPUB

    nfc = mock_nfc(mocker)
    wallet = Wallet(tdata.SINGLESIG_12_WORD_KEY)

    btn_seq = [
        BUTTON_ENTER,  # XPUB - Text
        BUTTON_PAGE,  # Save to SD card -> Store on NFC Card
        BUTTON_ENTER,  # Store on NFC Card
        BUTTON_PAGE,  # -> Back
        BUTTON_ENTER,  # Back to the version menu
        BUTTON_PAGE_PREV,  # -> Back
        BUTTON_ENTER,  # leave
    ]
    ctx = create_ctx(mocker, btn_seq, wallet)
    PubkeyView(ctx).public_key()

    payload, record_type = nfc.write_record.call_args[0]
    assert record_type == RECORD_XPUB
    # The same bytes the .pub file and the QR code from this page carry
    assert payload == wallet.key.key_expression(None).encode()
    nfc.deinit.assert_called_once()


def test_the_xpub_card_entry_is_absent_while_nfc_is_off(m5stickv, mocker, tdata):
    from krux.pages.home_pages.pub_key_view import PubkeyView
    from krux.wallet import Wallet
    from krux.input import BUTTON_ENTER, BUTTON_PAGE, BUTTON_PAGE_PREV
    from krux.krux_settings import Settings

    Settings().hardware.nfc.enabled = False
    nfc = mock_nfc(mocker)

    btn_seq = [
        BUTTON_ENTER,  # XPUB - Text
        BUTTON_PAGE,  # Save to SD card -> Back (no NFC entry in between)
        BUTTON_ENTER,  # Back to the version menu
        BUTTON_PAGE_PREV,  # -> Back
        BUTTON_ENTER,  # leave
    ]
    ctx = create_ctx(mocker, btn_seq, Wallet(tdata.SINGLESIG_12_WORD_KEY))
    PubkeyView(ctx).public_key()

    nfc.init.assert_not_called()
    assert ctx.input.wait_for_button.call_count == len(btn_seq)


def test_an_xpub_card_is_not_a_wallet(nfc_on, mocker, tdata):
    """A key expression is not a descriptor - parse_wallet refuses it - so the
    type keeps an xpub card out of the wallet loader rather than letting it
    fail deeper in."""
    from krux.wallet import parse_wallet, Wallet
    from krux.nfc import (
        RECORD_XPUB,
        RECORD_DESCRIPTOR,
        NFCNotFound,
        build_header,
        parse_header,
    )

    expression = Wallet(tdata.SINGLESIG_12_WORD_KEY).key.key_expression(None)
    with pytest.raises(ValueError):
        parse_wallet(expression)

    header = build_header(44, 720, RECORD_XPUB)
    with pytest.raises(NFCNotFound):
        parse_header(header, 720, RECORD_DESCRIPTOR)


@pytest.mark.parametrize(
    "written, expected",
    [
        (b"hello from the keypad", "hello from the keypad"),  # text round trips
        (b"\x00\x01\xff\xfe", b"\x00\x01\xff\xfe"),  # binary stays binary
        (b"trailing newline\n", "trailing newline\n"),  # kept, unlike a file
    ],
)
def test_a_datum_comes_back_as_what_was_written(nfc_on, mocker, written, expected):
    """A card hands back binary. Text written from manual input has to come back
    as text, or the tool shows its hex and offers binary conversions instead of
    the string the user typed."""
    from krux.pages.datum_tool import DatumTool, DatumToolMenu

    mock_nfc(mocker, record=written)
    captured = {}

    def capture(self, *_args, **_kwargs):
        captured["contents"] = self.contents
        return None

    mocker.patch.object(DatumTool, "view_contents", capture)
    DatumToolMenu(create_ctx(mocker, [])).read_nfc()

    assert captured["contents"] == expected
    assert isinstance(captured["contents"], type(expected))


# ---------- Parity with the SD card and QR paths ----------


def test_the_overwrite_warning_says_what_is_at_stake(nfc_on, mocker):
    """Shaped like the SD card's, which names the file it would replace before
    asking. "Overwrite?" alone does not say what is about to be lost."""
    from krux.pages.nfc_ui import StoreOnNFC
    from krux.display import BOTTOM_PROMPT_LINE
    from krux.input import BUTTON_ENTER

    mock_nfc(mocker, has_record=True)
    page = StoreOnNFC(create_ctx(mocker, [BUTTON_ENTER, BUTTON_ENTER]))
    mocker.spy(page, "prompt")
    page.write(ENVELOPE, "abcd1234")

    page.prompt.assert_any_call("Overwrite?", BOTTOM_PROMPT_LINE)


def test_a_write_says_processing_like_the_sd_card_does(nfc_on, mocker):
    from krux.pages.nfc_ui import StoreOnNFC
    from krux.input import BUTTON_ENTER

    mock_nfc(mocker)
    ctx = create_ctx(mocker, [BUTTON_ENTER])
    StoreOnNFC(ctx).write(ENVELOPE, "abcd1234")

    shown = [call[0][0] for call in ctx.display.draw_centered_text.call_args_list]
    assert any("Processing" in str(text) for text in shown)


def test_a_failed_descriptor_read_says_it_once(nfc_on, mocker, tdata):
    """The page already reports why. Falling through to the shared handler
    would stack a second "Failed to load" on top of it."""
    from krux.pages.home_pages.wallet_descriptor import WalletDescriptor
    from krux.wallet import Wallet
    from krux.nfc import NFCNotFound
    from krux.input import BUTTON_ENTER, BUTTON_PAGE

    nfc = mock_nfc(mocker)
    nfc.read_record.side_effect = NFCNotFound("no record")

    btn_seq = [
        BUTTON_ENTER,  # Load?
        BUTTON_PAGE,  # -> Load from SD card
        BUTTON_PAGE,  # -> Load from NFC card
        BUTTON_ENTER,  # Load from NFC card
    ]
    ctx = create_ctx(mocker, btn_seq, Wallet(tdata.MULTISIG_12_WORD_KEY))
    WalletDescriptor(ctx).wallet()

    assert ctx.display.flash_text.call_count == 1
    assert not ctx.wallet.is_loaded()
