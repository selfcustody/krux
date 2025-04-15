import pytest

TEST_QR_CODE = bytearray(
    b"\x7f\xd4?\x08\tv\x15\xdd.\xad\xdb%u\x83\x9c\xe0_\xf5\x07h\x00\xf7u\xc4\x91Py\xf3\x15\x80T\xbc\x7fe\x01V\xd7\xdfQ\r\xeaW]\x17\xb5\x8b\xd5tU\xc7\xa0\x16\xf5\xf7\xd7\x01"
)

FILES_FOLDER = "files"


@pytest.fixture
def mocker_sd_card(mocker):
    mocker.patch(
        "os.listdir",
        new=mocker.MagicMock(return_value=["somefile", "otherfile"]),
    )


@pytest.fixture
def mock_uart_cls(mocker):
    class MockUART(mocker.MagicMock):
        UART2 = 0

        def read(self):
            pass

        def write(self, bytes):
            pass

    return MockUART


def test_init_fileprinter(mocker, m5stickv):
    from krux.printers.cnc import FilePrinter

    p = FilePrinter()
    assert isinstance(p, FilePrinter)


def test_init_grblprinter(mocker, m5stickv):
    from krux.printers.cnc import GRBLPrinter

    p = GRBLPrinter()
    assert isinstance(p, GRBLPrinter)


def test_init_plunge_feed_value_compliance(mocker, m5stickv):
    from krux.printers.cnc import GCodeGenerator
    from krux.krux_settings import Settings

    with pytest.raises(ValueError) as e:
        Settings().hardware.printer.cnc.plunge_rate = 5
        Settings().hardware.printer.cnc.feed_rate = 2
        p = GCodeGenerator()


def test_init_pass_cut_value_compliance(mocker, m5stickv):
    from krux.printers.cnc import GCodeGenerator
    from krux.krux_settings import Settings

    with pytest.raises(ValueError) as e:
        Settings().hardware.printer.cnc.depth_per_pass = 2
        Settings().hardware.printer.cnc.cut_depth = 1
        p = GCodeGenerator()


def test_on_xy_gcode(mocker, m5stickv):
    from krux.printers.cnc import FilePrinter
    from krux.krux_settings import Settings

    Settings().hardware.printer.cnc.head_type = "router"
    with mocker.patch.object(FilePrinter, 'on_gcode', return_value=None) as mock_method:
        p = FilePrinter()
        p.on_xy_gcode("TEST")
    p = FilePrinter()
    p.on_gcode.assert_called_with("TEST")

    Settings().hardware.printer.cnc.head_type = "laser"
    with mocker.patch.object(FilePrinter, 'on_gcode', return_value=None) as mock_method:
        p = FilePrinter()
        p.on_xy_gcode("TEST")
    p = FilePrinter()
    p.on_gcode.assert_called_with("TEST S1000")


def test_on_gcode(mocker, m5stickv):
    from krux.printers.cnc import GCodeGenerator
    with pytest.raises(NotImplementedError) as e:
        p = GCodeGenerator()
        p.on_gcode("!")


def test_qr_data_width(mocker, m5stickv):
    from krux.printers.cnc import GCodeGenerator
    p = GCodeGenerator()
    assert 33 == p.qr_data_width()


def test_clear(mocker, m5stickv):
    from krux.printers.cnc import FilePrinter

    p = FilePrinter()

    p.file = "somefilehandle"
    p.clear()

    assert p.file is None


def test_print_router_qr_code_with_row_cutmethod(mocker, m5stickv, mocker_sd_card):
    import krux
    from krux.printers.cnc import FilePrinter
    from krux.krux_settings import Settings
    import os

    gcode = list(
        map(
            mocker.call,
            open(
                os.path.join(
                    os.path.dirname(__file__), FILES_FOLDER, "qr_row_cutmethod.nc"
                ),
                "r",
            ).readlines(),
        )
    )

    Settings().hardware.printer.cnc.cut_method = "row"
    Settings().hardware.printer.cnc.invert = False

    p = FilePrinter()

    m = mocker.mock_open()
    mocker.patch("builtins.open", m, create=True)

    p.print_qr_code(TEST_QR_CODE)

    handle = m()
    handle.write.assert_has_calls(gcode)

    krux.printers.cnc.wdt.feed.assert_called()


def test_print_router_qr_code_with_spiral_cutmethod(mocker, m5stickv, mocker_sd_card):
    import krux
    from krux.printers.cnc import FilePrinter
    from krux.krux_settings import Settings
    import os

    gcode = list(
        map(
            mocker.call,
            open(
                os.path.join(
                    os.path.dirname(__file__), FILES_FOLDER, "qr_spiral_cutmethod.nc"
                ),
                "r",
            ).readlines(),
        )
    )

    Settings().hardware.printer.cnc.cut_method = "spiral"
    Settings().hardware.printer.cnc.invert = False

    p = FilePrinter()

    m = mocker.mock_open()
    mocker.patch("builtins.open", m, create=True)

    p.print_qr_code(TEST_QR_CODE)

    handle = m()
    handle.write.assert_has_calls(gcode)

    krux.printers.cnc.wdt.feed.assert_called()


def test_print_router_qr_code_inverted(mocker, m5stickv, mocker_sd_card):
    import krux
    from krux.printers.cnc import FilePrinter
    from krux.krux_settings import Settings
    import os

    gcode = list(
        map(
            mocker.call,
            open(
                os.path.join(os.path.dirname(__file__), FILES_FOLDER, "qr_invert.nc"),
                "r",
            ).readlines(),
        )
    )

    Settings().hardware.printer.cnc.cut_method = "spiral"
    Settings().hardware.printer.cnc.invert = True

    p = FilePrinter()

    m = mocker.mock_open()
    mocker.patch("builtins.open", m, create=True)

    p.print_qr_code(TEST_QR_CODE)

    handle = m()
    handle.write.assert_has_calls(gcode)

    krux.printers.cnc.wdt.feed.assert_called()


def test_print_laser_qr_code(mocker, m5stickv, mocker_sd_card):
    import krux
    from krux.printers.cnc import FilePrinter
    from krux.krux_settings import Settings
    import os

    gcode = list(
        map(
            mocker.call,
            open(
                os.path.join(
                    os.path.dirname(__file__), FILES_FOLDER, "qr_laser.nc"
                ),
                "r",
            ).readlines(),
        )
    )

    Settings().hardware.printer.cnc.invert = False
    Settings().hardware.printer.cnc.cut_method = "row"
    Settings().hardware.printer.cnc.unit = "mm"
    Settings().hardware.printer.cnc.flute_diameter = 0.2
    Settings().hardware.printer.cnc.plunge_rate = 150
    Settings().hardware.printer.cnc.feed_rate = 300
    Settings().hardware.printer.cnc.cut_depth = 0.01
    Settings().hardware.printer.cnc.depth_per_pass = 0.01
    Settings().hardware.printer.cnc.part_size = 34
    Settings().hardware.printer.cnc.border_padding = 0.0
    Settings().hardware.printer.cnc.head_type = "laser"
    Settings().hardware.printer.cnc.head_power = 500

    p = FilePrinter()

    m = mocker.mock_open()
    mocker.patch("builtins.open", m, create=True)

    p.print_qr_code(TEST_QR_CODE)

    handle = m()
    handle.write.assert_has_calls(gcode)

    krux.printers.cnc.wdt.feed.assert_called()


def test_print_qr_code_to_grbl(mocker, m5stickv, mock_uart_cls):
    mocker.patch("krux.printers.cnc.UART", new=mock_uart_cls)
    import krux
    from krux.printers.cnc import GRBLPrinter
    from krux.krux_settings import Settings
    import os

    Settings().hardware.printer.cnc.cut_method = "spiral"
    Settings().hardware.printer.cnc.invert = False

    p = GRBLPrinter()
    mocker.spy(p, "write_bytes")

    mock_write = mocker.patch.object(p.uart_conn, "write")

    with pytest.raises(ValueError) as e:
        mocker.patch.object(
            p.uart_conn, "read", return_value=None
        )
        p.print_qr_code(bytearray(b"\x00"))

    with pytest.raises(ValueError) as e:
        mocker.patch.object(
            p.uart_conn, "read", return_value="nok".encode()
        )
        p.print_qr_code(bytearray(b"\x00"))

    with pytest.raises(ValueError) as e:
        mocker.patch.object(
            p.uart_conn, "read", return_value="nok\n".encode()
        )
        p.print_qr_code(bytearray(b"\x00"))

    mocker.patch.object(
        p.uart_conn, "read", return_value="[VER:1.1\n".encode()
    )
    p.print_qr_code(bytearray(b"\x00"))
    mock_write.assert_has_calls(
        [
            mocker.call(b"$"),
            mocker.call(b"I"),
            mocker.call(b"\n"),
        ]
    )

    mocker.patch.object(
        p.uart_conn, "read", return_value=None
    )
    assert None == p.transmit("!")

    mocker.patch.object(
        p.uart_conn, "read", return_value="ok"
    )
    assert "ok" == p.transmit("M4")
