import pytest
from unittest.mock import patch
from . import create_ctx
from ..shared_mocks import mock_context
from ..test_sd_card import mocker_sd_card_ok


@pytest.fixture
def mocker_printer(mocker):
    mocker.patch("krux.printers.thermal.AdafruitPrinter", new=mocker.MagicMock())


################### Test menus


def test_settings_m5stickv(m5stickv, mocker, mocker_printer):
    import krux
    from krux.pages.settings_page import SettingsPage
    from krux.input import BUTTON_ENTER, BUTTON_PAGE, BUTTON_PAGE_PREV
    from krux.krux_settings import Settings, CategorySetting, NumberSetting
    from krux.translations import translation_table
    from krux.themes import WHITE, RED, GREEN, ORANGE

    tlist = list(translation_table)
    index_pt = tlist.index("pt-BR")
    index_next = (index_pt + 1) % (len(tlist))
    text_pt = translation_table[tlist[index_pt]][1177338798] + "\n" + tlist[index_pt]
    text_next = (
        translation_table[tlist[index_next]][1177338798] + "\n" + tlist[index_next]
    )

    cases = [
        (  # 0
            (
                # Bitcoin
                BUTTON_ENTER,
                # Change network
                BUTTON_PAGE,
                BUTTON_ENTER,
                # Leave Settings
                BUTTON_PAGE_PREV,
                BUTTON_ENTER,
            ),
            [
                mocker.call("Network\nmain", ORANGE),
                mocker.call("Network\ntest", GREEN),
            ],
            lambda: Settings().bitcoin.network == "test",
            CategorySetting,
        ),
        (  # 1
            (
                # Hardware
                BUTTON_PAGE,
                BUTTON_PAGE,
                BUTTON_ENTER,
                # TODO: Identify it's printer settings
                # Thermal
                BUTTON_PAGE,
                BUTTON_ENTER,
                # Change Baudrate
                BUTTON_ENTER,
                BUTTON_PAGE,
                BUTTON_ENTER,
                # Back to Thermal
                BUTTON_PAGE_PREV,
                BUTTON_ENTER,
                # Back to Printer
                BUTTON_PAGE,
                BUTTON_PAGE,
                BUTTON_ENTER,
                # Leave Settings
                BUTTON_PAGE,
                BUTTON_PAGE,
                BUTTON_PAGE,
                BUTTON_PAGE,
                BUTTON_PAGE,
                BUTTON_ENTER,
            ),
            [
                mocker.call("Baudrate\n9600", WHITE),
                mocker.call("Baudrate\n19200", WHITE),
            ],
            lambda: Settings().hardware.printer.thermal.adafruit.baudrate == 19200,
            CategorySetting,
        ),
        (  # 2
            (
                # Language
                BUTTON_PAGE,
                BUTTON_PAGE,
                BUTTON_PAGE,
                BUTTON_ENTER,
                # Change Locale
                BUTTON_PAGE,
                BUTTON_ENTER,
            ),
            [
                mocker.call(text_pt, WHITE),
                mocker.call(text_next, WHITE),
            ],
            lambda: Settings().i18n.locale == tlist[index_next],
            CategorySetting,
        ),
        (  # 3
            (
                # Printer
                BUTTON_PAGE,
                BUTTON_PAGE,
                BUTTON_ENTER,
                # Thermal
                BUTTON_PAGE,
                BUTTON_ENTER,
                # Paper Width
                BUTTON_PAGE,
                BUTTON_PAGE,
                BUTTON_ENTER,
                # Change width
                # Remove digit
                BUTTON_PAGE_PREV,
                BUTTON_PAGE_PREV,
                BUTTON_PAGE_PREV,
                BUTTON_ENTER,
                # Add 9
                BUTTON_PAGE_PREV,
                BUTTON_ENTER,
                # Go
                BUTTON_PAGE,
                BUTTON_PAGE,
                BUTTON_PAGE,
                BUTTON_ENTER,
                # Back to Thermal
                BUTTON_PAGE,
                BUTTON_PAGE,
                BUTTON_PAGE,
                BUTTON_PAGE,
                BUTTON_ENTER,
                # Back to Printer
                BUTTON_PAGE,
                BUTTON_PAGE,
                BUTTON_ENTER,
                # Leave Settings
                BUTTON_PAGE,
                BUTTON_PAGE,
                BUTTON_PAGE,
                BUTTON_PAGE,
                BUTTON_PAGE,
                BUTTON_ENTER,
            ),
            [
                mocker.call("Paper Width", 10),
            ],
            lambda: Settings().hardware.printer.thermal.adafruit.paper_width == 389,
            NumberSetting,
        ),
    ]
    case_num = 0
    for case in cases:
        print("test_settings cases[" + str(case_num) + "]")
        case_num = case_num + 1

        ctx = create_ctx(mocker, case[0])
        settings_page = SettingsPage(ctx)

        Settings().i18n.locale = "pt-BR"
        settings_page.settings()

        assert ctx.input.wait_for_button.call_count == len(case[0])

        assert case[2]()


def test_settings_on_amigo_tft(amigo_tft, mocker, mocker_printer):
    import krux
    from krux.pages.settings_page import SettingsPage
    from krux.input import BUTTON_TOUCH
    from krux.krux_settings import Settings, CategorySetting, NumberSetting
    from krux.translations import translation_table
    from krux.themes import WHITE, RED, GREEN, ORANGE

    tlist = list(translation_table)
    index_pt = tlist.index("pt-BR")
    index_next = (index_pt + 1) % (len(tlist))
    text_pt = translation_table[tlist[index_pt]][1177338798] + "\n" + tlist[index_pt]
    text_next = (
        translation_table[tlist[index_next]][1177338798] + "\n" + tlist[index_next]
    )

    PREV_INDEX = 0
    GO_INDEX = 1
    NEXT_INDEX = 2

    HARDWARE_INDEX = 2
    LOCALE_INDEX = 3
    PRINTER_INDEX = 1
    LEAVE_INDEX = 7

    cases = [
        (
            # Case 0
            (
                # Bitcoin
                0,
                # Change network
                NEXT_INDEX,
                GO_INDEX,
                # Leave Settings
                LEAVE_INDEX,
            ),
            [
                mocker.call("Network\nmain", ORANGE),
                mocker.call("Network\ntest", GREEN),
            ],
            lambda: Settings().bitcoin.network == "test",
            CategorySetting,
        ),
        (
            # Case 1
            (
                # Hardware
                HARDWARE_INDEX,
                # Printer
                PRINTER_INDEX,
                # Thermal
                1,
                # Change Baudrate
                0,
                NEXT_INDEX,
                GO_INDEX,
                # Back from Thermal
                6,
                # Back from Printer
                3,
                # Back from Hardware
                3,
                # Leave Settings
                LEAVE_INDEX,
            ),
            [
                mocker.call("Baudrate\n9600", WHITE),
                mocker.call("Baudrate\n19200", WHITE),
            ],
            lambda: Settings().hardware.printer.thermal.adafruit.baudrate == 19200,
            CategorySetting,
        ),
        (
            # Case 2
            (
                # Language
                LOCALE_INDEX,
                # Change Locale
                NEXT_INDEX,
                GO_INDEX,
            ),
            [
                mocker.call(text_pt, WHITE),
                mocker.call(text_next, WHITE),
            ],
            lambda: Settings().i18n.locale == tlist[index_next],
            CategorySetting,
        ),
    ]
    case_num = 0
    for case in cases:
        print("test_settings_on_amigo_tft cases[" + str(case_num) + "]")
        case_num = case_num + 1

        ctx = mock_context(mocker)
        ctx.power_manager.battery_charge_remaining.return_value = 1
        ctx.input.wait_for_button = mocker.MagicMock(return_value=BUTTON_TOUCH)
        ctx.input.touch = mocker.MagicMock(
            current_index=mocker.MagicMock(side_effect=case[0])
        )

        mocker.patch.object(ctx.input.touch, "x_regions", (0, 100, 200, 300))
        mocker.patch.object(ctx.input.touch, "y_regions", (100, 200))

        settings_page = SettingsPage(ctx)

        Settings().i18n.locale = "pt-BR"
        settings_page.settings()

        assert ctx.input.wait_for_button.call_count == len(case[0])

        assert case[2]()


def test_encryption_pbkdf2_setting(m5stickv, mocker):
    from krux.pages.settings_page import SettingsPage
    from krux.krux_settings import Settings, EncryptionSettings

    ctx = mock_context(mocker)
    settings_page = SettingsPage(ctx)

    # pbkdf2_iterations has default value
    assert Settings().encryption.pbkdf2_iterations == 100000

    # try to change the value
    settings_page.capture_from_keypad = mocker.MagicMock(return_value=100001)
    settings_page.number_setting(
        EncryptionSettings(), EncryptionSettings.pbkdf2_iterations
    )

    # continue with default value because it must be multiple of 10000
    assert Settings().encryption.pbkdf2_iterations == 100000

    # try to change the value to a multiple of 10000
    settings_page.capture_from_keypad = mocker.MagicMock(return_value=110000)
    settings_page.number_setting(
        EncryptionSettings(), EncryptionSettings.pbkdf2_iterations
    )

    # value changed!
    assert Settings().encryption.pbkdf2_iterations == 110000


def test_restore_settings(amigo_tft, mocker, mocker_sd_card_ok):
    from krux.pages.settings_page import SettingsPage
    from krux.settings import FLASH_PATH, SETTINGS_FILENAME
    from krux.input import BUTTON_ENTER

    BTN_SEQUENCE = [BUTTON_ENTER]  # Confirm restore

    with patch("os.remove") as mock_remove:
        with patch("krux.sd_card.SDHandler.delete") as mock_delete_sd:
            ctx = create_ctx(mocker, BTN_SEQUENCE)
            settings_page = SettingsPage(ctx)
            settings_page.restore_settings()
    mock_delete_sd.assert_called_once_with(SETTINGS_FILENAME)
    mock_remove.assert_called_once_with("/" + FLASH_PATH + "/" + SETTINGS_FILENAME)


def test_save_settings_on_sd(amigo_tft, mocker, mocker_sd_card_ok):
    from krux.pages.settings_page import SettingsPage
    from krux.krux_settings import Settings, SD_PATH
    from krux.input import BUTTON_ENTER, BUTTON_PAGE_PREV

    BTN_SEQUENCE = [
        BUTTON_PAGE_PREV,  # Move to "Back"
        BUTTON_ENTER,  # Confirm "Back"
    ]

    ctx = create_ctx(mocker, BTN_SEQUENCE)
    settings_page = SettingsPage(ctx)
    settings_page.flash_text = mocker.MagicMock()
    Settings().persist.location = SD_PATH
    settings_page.settings()
    settings_page.flash_text.assert_has_calls(
        [
            mocker.call("Your changes will be kept on the SD card.", duration=2500),
            mocker.call("Changes persisted to SD card!", duration=2500),
        ]
    )


def test_leave_settings_without_changes(amigo_tft, mocker):
    from krux.pages.settings_page import SettingsPage
    from krux.input import BUTTON_ENTER, BUTTON_PAGE, BUTTON_PAGE_PREV

    mocker.patch(
        "os.listdir",
        new=mocker.MagicMock(return_value=["somefile", "otherfile"]),
    )

    BTN_SEQUENCES = [
        [
            # Change something then give up
            BUTTON_ENTER,  # Change "Bitcoin"
            BUTTON_PAGE,  # Change to testnet
            BUTTON_ENTER,  # Confirm testnet
            BUTTON_ENTER,  # Change "Bitcoin" again
            BUTTON_PAGE,  # Change back to mainnet
            BUTTON_ENTER,  # Confirm mainnet
            BUTTON_PAGE_PREV,  # Move to "Back"
            BUTTON_ENTER,  # Confirm "Back"
        ],
        [
            # Change persist then give up
            [BUTTON_PAGE] * 3,  # Move to "Persist"
            BUTTON_ENTER,  # Change "Persist"
            BUTTON_PAGE,  # Change to SD
            BUTTON_ENTER,  # Confirm SD
            BUTTON_ENTER,  # Change "Persist" again
            BUTTON_PAGE,  # Change back to flash
            BUTTON_ENTER,  # Confirm flash
            BUTTON_PAGE_PREV,  # Move to "Back"
            BUTTON_ENTER,  # Confirm "Back"
        ],
        [
            # Don't change anything
            BUTTON_PAGE_PREV,  # Move to "Back"
            BUTTON_ENTER,  # Confirm "Back"
        ],
    ]

    for btn_sequence in BTN_SEQUENCES:
        ctx = create_ctx(mocker, btn_sequence)
        settings_page = SettingsPage(ctx)
        settings_page.flash_text = mocker.MagicMock()
        settings_page.settings()
        settings_page.flash_text.assert_has_calls(
            [
                mocker.call(
                    "Your changes will be kept on device flash storage.", duration=2500
                ),
            ]
        )
        persisted_to_flash_call = mocker.call(
            "Changes persisted to Flash!", duration=2500
        )
        assert persisted_to_flash_call not in settings_page.flash_text.call_args_list


def test_leave_settings_with_changes(amigo_tft, mocker, mocker_sd_card_ok):
    # mocker_sd_card_ok will mock os.listdir so it will also mock flash storage
    from krux.pages.settings_page import SettingsPage
    from krux.input import BUTTON_ENTER, BUTTON_PAGE, BUTTON_PAGE_PREV

    BTN_SEQUENCE = [
        BUTTON_ENTER,  # Change "Bitcoin"
        BUTTON_PAGE,  # Change to testnet
        BUTTON_ENTER,  # Confirm "testnet"
        BUTTON_PAGE_PREV,  # Move to "Back"
        BUTTON_ENTER,  # Confirm "Back"
    ]
    ctx = create_ctx(mocker, BTN_SEQUENCE)
    settings_page = SettingsPage(ctx)
    settings_page.flash_text = mocker.MagicMock()

    # Leave settings without changes
    settings_page.settings()
    settings_page.flash_text.assert_has_calls(
        [
            mocker.call(
                "Your changes will be kept on device flash storage.", duration=2500
            ),
            mocker.call("Changes persisted to Flash!", duration=2500),
        ]
    )


def test_persist_to_sd_without_sd(amigo_tft, mocker):
    from krux.pages.settings_page import SettingsPage
    from krux.krux_settings import Settings, SD_PATH
    from krux.input import BUTTON_ENTER, BUTTON_PAGE_PREV

    BTN_SEQUENCE = [
        BUTTON_PAGE_PREV,  # Move to "Back"
        BUTTON_ENTER,  # Confirm "Back"
    ]

    ctx = create_ctx(mocker, BTN_SEQUENCE)
    settings_page = SettingsPage(ctx)
    settings_page.flash_text = mocker.MagicMock()
    Settings().persist.location = SD_PATH
    settings_page.settings()
    settings_page.flash_text.assert_has_calls(
        [
            mocker.call(
                "SD card not detected.\n\nChanges will last until shutdown.",
                duration=2500,
            ),
        ]
    )
