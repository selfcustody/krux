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
    from krux.krux_settings import Settings
    from krux.printers.cnc import GCodeGenerator

    with pytest.raises(ValueError) as exc_info:
        Settings().hardware.printer.cnc.plunge_rate = 5
        Settings().hardware.printer.cnc.feed_rate = 2
        GCodeGenerator()

    assert str(exc_info.value) == "Plunge rate must be less than half of feed rate"


def test_init_pass_cut_value_compliance(mocker, m5stickv):
    from krux.krux_settings import Settings
    from krux.printers.cnc import GCodeGenerator

    with pytest.raises(ValueError) as exc_info:
        Settings().hardware.printer.cnc.depth_per_pass = 2
        Settings().hardware.printer.cnc.cut_depth = 1
        GCodeGenerator()

    assert (
        str(exc_info.value) == "Depth per pass must be less than or equal to cut depth"
    )


def test_on_xy_gcode(mocker, m5stickv):
    from krux.krux_settings import Settings
    from krux.printers.cnc import FilePrinter

    Settings().hardware.printer.cnc.head_type = "router"
    mocker.patch.object(FilePrinter, "on_gcode", return_value=None)
    p = FilePrinter()
    p.on_xy_gcode("TEST")
    p = FilePrinter()
    p.on_gcode.assert_called_with("TEST")

    Settings().hardware.printer.cnc.head_type = "laser"
    mocker.patch.object(FilePrinter, "on_gcode", return_value=None)
    p = FilePrinter()
    p.on_xy_gcode("TEST")
    p = FilePrinter()
    p.on_gcode.assert_called_with("TEST S1000")


def test_on_gcode(mocker, m5stickv):
    from krux.printers.cnc import GCodeGenerator

    with pytest.raises(NotImplementedError) as exc_info:
        p = GCodeGenerator()
        p.on_gcode("!")

    assert str(exc_info.value) == "Must implement 'on_gcode' method for GCodeGenerator"


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


def test_init_plunge_rate_gt_feed_rate_error(mocker, m5stickv):
    from krux.krux_settings import Settings
    from krux.printers.cnc import FilePrinter

    Settings().hardware.printer.cnc.plunge_rate = 100
    Settings().hardware.printer.cnc.feed_rate = 50

    with pytest.raises(ValueError) as exception_info:
        FilePrinter()

    assert (
        str(exception_info.value) == "Plunge rate must be less than half of feed rate"
    )


def test_init_on_gcode_not_implemented_error(mocker, m5stickv):
    from krux.printers.cnc import GCodeGenerator

    class TestGCodeGenerator(GCodeGenerator):
        def __init__(self):
            super().__init__()

    t = TestGCodeGenerator()
    with pytest.raises(NotImplementedError) as exc_info:
        t.on_gcode("M0")

    assert (
        str(exc_info.value) == "Must implement 'on_gcode' method for TestGCodeGenerator"
    )


def test_init_pass_depth_gt_cut_depth_error(mocker, m5stickv):
    from krux.krux_settings import Settings
    from krux.printers.cnc import FilePrinter

    Settings().hardware.printer.cnc.depth_per_pass = 10
    Settings().hardware.printer.cnc.cut_depth = 5

    with pytest.raises(ValueError) as exception_info:
        FilePrinter()

    assert (
        str(exception_info.value)
        == "Depth per pass must be less than or equal to cut depth"
    )


def test_print_qr_code_on_sdcard_error(mocker, m5stickv):
    from krux.printers.cnc import FilePrinter

    mocker.patch("builtins.open", side_effect=OSError("No SD card found"))
    mocker.patch("krux.printers.cnc.SDHandler", return_value=mocker.MagicMock())
    p = FilePrinter()
    with pytest.raises(ValueError):
        p.print_qr_code("FAKE_QR")
    assert p.file is None


def test_print_string_not_implemented_error(mocker, m5stickv):
    from krux.printers.cnc import GCodeGenerator

    class TestFilePrinter(GCodeGenerator):
        def __init__(self):
            super().__init__()

    t = TestFilePrinter()

    with pytest.raises(NotImplementedError) as exc_info:
        t.print_string("FAKE DATA")

    assert (
        str(exc_info.value)
        == "Must implement 'print_string' method for TestFilePrinter"
    )


def test_clear_not_implemented_error(mocker, m5stickv):
    from krux.printers.cnc import GCodeGenerator

    class TestFilePrinter(GCodeGenerator):
        def __init__(self):
            super().__init__()

    t = TestFilePrinter()

    with pytest.raises(NotImplementedError) as exc_info:
        t.clear()

    assert str(exc_info.value) == "Must implement 'clear' method for TestFilePrinter"


def test_init_qr_width(mocker, m5stickv):
    from krux.printers.cnc import FilePrinter

    f = FilePrinter()
    width = f.qr_data_width()
    assert width == 33


def test_print_router_qr_code_with_row_cutmethod(mocker, m5stickv, mocker_sd_card):
    import os

    import krux
    from krux.krux_settings import Settings
    from krux.printers.cnc import FilePrinter

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
    import os

    import krux
    from krux.krux_settings import Settings
    from krux.printers.cnc import FilePrinter

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
    import os

    import krux
    from krux.krux_settings import Settings
    from krux.printers.cnc import FilePrinter

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
    import os

    import krux
    from krux.krux_settings import Settings
    from krux.printers.cnc import FilePrinter

    gcode = list(
        map(
            mocker.call,
            open(
                os.path.join(os.path.dirname(__file__), FILES_FOLDER, "qr_laser.nc"),
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
    mocker.patch("machine.UART", new=mock_uart_cls)
    from krux.krux_settings import Settings
    from krux.printers.cnc import GRBLPrinter

    Settings().hardware.printer.cnc.cut_method = "spiral"
    Settings().hardware.printer.cnc.invert = False

    p = GRBLPrinter()
    mocker.spy(p, "write_bytes")

    # Patch the write method of p.uart_conn
    mock_write = mocker.patch.object(p.uart_conn, "write")

    # now test with a valid connection, a valid IO and a valid handshake
    mocker.patch.object(p.uart_conn, "read", return_value="[VER:1.1\n".encode())
    p.print_qr_code(bytearray(b"\x00"))
    mock_write.assert_has_calls(
        [
            mocker.call(b"$"),
            mocker.call(b"I"),
            mocker.call(b"\n"),
        ]
    )

    mocker.patch.object(p.uart_conn, "read", return_value="ok")
    assert p.transmit("M4") == "ok"


def test_print_qr_code_to_grbl_timeout(mocker, m5stickv, mock_uart_cls):
    mocker.patch("machine.UART", new=mock_uart_cls)
    from krux.krux_settings import Settings
    from krux.printers.cnc import GRBLPrinter

    Settings().hardware.printer.cnc.cut_method = "spiral"
    Settings().hardware.printer.cnc.invert = False

    p = GRBLPrinter()
    mocker.spy(p, "write_bytes")

    # Patch the write method of p.uart_conn
    mock_write = mocker.patch.object(p.uart_conn, "write")

    # now test with a valid connection, a valid IO and a valid handshake
    mocker.patch.object(p.uart_conn, "read", return_value="[VER:1.1\n".encode())
    p.print_qr_code(bytearray(b"\x00"))
    mock_write.assert_has_calls(
        [
            mocker.call(b"$"),
            mocker.call(b"I"),
            mocker.call(b"\n"),
        ]
    )

    # raise an exception when the write method fails
    mocker.patch.object(p.uart_conn, "read", return_value=None)
    with pytest.raises(TimeoutError) as exc_info:
        p.transmit("!")

    assert str(exc_info.value) == "Timeout while waiting for response from GRBL"


def test_print_qr_code_to_grbl_connection_error(mocker, m5stickv, mock_uart_cls):
    mocker.patch("machine.UART", new=mock_uart_cls)
    from krux.krux_settings import Settings
    from krux.printers.cnc import GRBLPrinter

    Settings().hardware.printer.cnc.cut_method = "spiral"
    Settings().hardware.printer.cnc.invert = False

    p = GRBLPrinter()

    # test a connection error
    with pytest.raises(ConnectionError) as exc_info:
        mocker.patch.object(p.uart_conn, "read", return_value=None)
        p.print_qr_code(bytearray(b"\x00"))
    assert str(exc_info.value) == "Cannot read from UART connection"

    # First read returns something, second read returns None
    # so this simulates a connection error
    mocker.patch.object(p.uart_conn, "read", side_effect=["[VER:0.1".encode(), None])
    with pytest.raises(ConnectionError) as exc_info:
        p.print_qr_code(bytearray(b"\x00"))

    assert str(exc_info.value) == "Cannot read from UART connection"


def test_print_qr_code_to_grbl_statuses_error(mocker, m5stickv, mock_uart_cls):
    mocker.patch("machine.UART", new=mock_uart_cls)
    from krux.krux_settings import Settings
    from krux.printers.cnc import GRBLPrinter

    Settings().hardware.printer.cnc.cut_method = "spiral"
    Settings().hardware.printer.cnc.invert = False

    p = GRBLPrinter()

    # test a IOError when the value of data isnt accepted
    # (reason: it always expect at least two lines of data, lets give 1)
    with pytest.raises(IOError) as exc_info:
        mocker.patch.object(p.uart_conn, "read", return_value="nok".encode())
        p.print_qr_code(bytearray(b"\x00"))
    assert str(exc_info.value) == "Cannot read, expected at least 2 lines of data"

    # First read returns something, second read return the version
    # so this simulates a IOError
    mocker.patch.object(p.uart_conn, "read", side_effect=[b"init", b"[VER:0.1]"])
    with pytest.raises(IOError) as exc_info:
        p.print_qr_code(bytearray(b"\x00"))

    assert str(exc_info.value) == "Cannot read, expected at least 2 lines of data"


def test_print_qr_code_to_grbl_handshake_error(mocker, m5stickv, mock_uart_cls):
    mocker.patch("machine.UART", new=mock_uart_cls)
    from krux.krux_settings import Settings
    from krux.printers.cnc import GRBLPrinter

    Settings().hardware.printer.cnc.cut_method = "spiral"
    Settings().hardware.printer.cnc.invert = False

    p = GRBLPrinter()

    # Test an value error during the handshake
    with pytest.raises(ValueError) as exc_info:
        mocker.patch.object(p.uart_conn, "read", return_value="nok\n".encode())
        p.print_qr_code(bytearray(b"\x00"))
    assert (
        str(exc_info.value)
        == "Cannot handshake, version mismatch. Expected [VER:1.1, got nok"
    )

    # Simulate valid response with at least 2 lines, but wrong version
    mocker.patch.object(p.uart_conn, "read", side_effect=[b"init", b"[VER:0.1\nREADY"])
    with pytest.raises(ValueError) as exc_info:
        p.print_qr_code(bytearray(b"\x00"))

    assert (
        str(exc_info.value)
        == "Cannot handshake, version mismatch. Expected [VER:1.1, got [VER:0.1"
    )


def test_transmit_calls_sleep_on_retry(mocker, m5stickv, mock_uart_cls):
    mocker.patch("machine.UART", new=mock_uart_cls)
    from krux.krux_settings import Settings
    from krux.printers.cnc import GRBLPrinter

    Settings().hardware.printer.cnc.cut_method = "spiral"
    Settings().hardware.printer.cnc.invert = False

    p = GRBLPrinter()

    # First read fails, second succeeds
    # Then it will call the write method
    # after 1000ms
    mocker.patch.object(p.uart_conn, "read", side_effect=[None, b"ok"])
    mocker.patch.object(p, "write_bytes")
    sleep_mock = mocker.patch("krux.printers.cnc.time.sleep_ms")

    res = p.transmit("G90")
    assert res == b"ok"
    sleep_mock.assert_called_once_with(1000)


def test_grblprinter_print_string_not_implemented_error(
    mocker, m5stickv, mock_uart_cls
):
    from krux.printers.cnc import GRBLPrinter

    mocker.patch("machine.UART", new=mock_uart_cls)
    p = GRBLPrinter()
    with pytest.raises(NotImplementedError) as exc_info:
        p.print_string("FAKE DATA")
    assert str(exc_info.value) == "Must implement 'print_string' method for GRBLPrinter"


def test_grblprinter_clear_not_implemented_error(mocker, m5stickv, mock_uart_cls):
    from krux.printers.cnc import GRBLPrinter

    mocker.patch("machine.UART", new=mock_uart_cls)
    p = GRBLPrinter()
    with pytest.raises(NotImplementedError) as exc_info:
        p.clear()
    assert str(exc_info.value) == "Must implement 'clear' method for GRBLPrinter"
