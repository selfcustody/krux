import pytest

TEST_QR = """
00000000000000000000000000000000000
01111111001110001000100110011111110
01000001010011001001011110010000010
01011101010011000010000010010111010
01011101000101010001100111010111010
01011101011010011100001010010111010
01000001010101001110111101010000010
01111111010101010101010101011111110
00000000011111011011011110000000000
01101001101011110100101101011101100
00011010001001110111011001010000010
00101011010101000000110001111101010
00011010101010101001111000100110010
00101101100101100110011000010000000
00111000110101000100101101010100010
01001101000011010111011010001101100
00001000010010110011101000100110110
00010111111001000110111100010100010
01111000111110100101000011100000000
00001111111100110000000100001101110
01011010001111001110011001010100010
01000101111001100101101001101000110
00110010110001100110010101110000110
01101111001101110101110001110001010
00110000001000111100111000011110010
01001011101011100110111111111100000
00000000010001010000111111000100010
01111111011111100100000101010101100
01000001001011101110111001000100110
01011101000100001010101101111100000
01011101011111010101001000011111110
01011101001000010000000101101100110
01000001010010000111101011001110000
01111111010000110100011011010110100
00000000000000000000000000000000000
""".strip()


@pytest.fixture
def mocker_sd_card(mocker):
    mocker.patch(
        "os.listdir",
        new=mocker.MagicMock(return_value=["somefile", "otherfile"]),
    )


def test_init(mocker, m5stickv):
    from krux.printers.cnc import FilePrinter

    p = FilePrinter()

    assert isinstance(p, FilePrinter)


def test_clear(mocker, m5stickv):
    from krux.printers.cnc import FilePrinter

    p = FilePrinter()

    p.file = "somefilehandle"
    p.clear()

    assert p.file is None


def test_print_qr_code_with_row_cutmethod(mocker, m5stickv, mocker_sd_card):
    import krux
    from krux.printers.cnc import FilePrinter
    from krux.krux_settings import Settings
    import os

    gcode = list(
        map(
            mocker.call,
            open(
                os.path.join(os.path.dirname(__file__), "qr_row_cutmethod.nc"), "r"
            ).readlines(),
        )
    )

    Settings().hardware.printer.cnc.cut_method = "row"
    Settings().hardware.printer.cnc.invert = False

    p = FilePrinter()

    m = mocker.mock_open()
    mocker.patch("builtins.open", m, create=True)

    p.print_qr_code(TEST_QR)

    handle = m()
    handle.write.assert_has_calls(gcode)

    krux.printers.cnc.wdt.feed.assert_called()


def test_print_qr_code_with_spiral_cutmethod(mocker, m5stickv, mocker_sd_card):
    import krux
    from krux.printers.cnc import FilePrinter
    from krux.krux_settings import Settings
    import os

    gcode = list(
        map(
            mocker.call,
            open(
                os.path.join(os.path.dirname(__file__), "qr_spiral_cutmethod.nc"), "r"
            ).readlines(),
        )
    )

    Settings().hardware.printer.cnc.cut_method = "spiral"
    Settings().hardware.printer.cnc.invert = False

    p = FilePrinter()

    m = mocker.mock_open()
    mocker.patch("builtins.open", m, create=True)

    p.print_qr_code(TEST_QR)

    handle = m()
    handle.write.assert_has_calls(gcode)

    krux.printers.cnc.wdt.feed.assert_called()


def test_print_qr_code_inverted(mocker, m5stickv, mocker_sd_card):
    import krux
    from krux.printers.cnc import FilePrinter
    from krux.krux_settings import Settings
    import os

    gcode = list(
        map(
            mocker.call,
            open(
                os.path.join(os.path.dirname(__file__), "qr_invert.nc"), "r"
            ).readlines(),
        )
    )

    Settings().hardware.printer.cnc.cut_method = "spiral"
    Settings().hardware.printer.cnc.invert = True

    p = FilePrinter()

    m = mocker.mock_open()
    mocker.patch("builtins.open", m, create=True)

    p.print_qr_code(TEST_QR)

    handle = m()
    handle.write.assert_has_calls(gcode)

    krux.printers.cnc.wdt.feed.assert_called()
