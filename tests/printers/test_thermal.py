import pytest

TEST_QR_CODE = bytearray(
    b"\x7fn\xfd\x830\x08v9\xd6\xedj\xa0\xdbUU7\xc8\xa0\xe0_U\x7f\x00i\x00\xe3\xd61P\x08\xf5Q\xef^\xfe`\xe8\xc1\x7f\xdex\x936Y\x91\xb8\xeb\xd29c\xd5\xd4\x7f\x00\n#\xfe\xcd\xd7\rJ\x8e\xd9\xe5\xf8\xb9K\xe6x\x17\xb9\xca\xa0\x9a\x9a\x7f\xbb\x1b\x01"
)


@pytest.fixture
def mock_uart_cls(mocker):
    class MockUART(mocker.MagicMock):
        UART2 = 0

        def read(self, bytes):
            return 0b00000000.to_bytes(1, "big")

        def write(self, bytes):
            pass

    return MockUART


def test_init(mocker, m5stickv, mock_uart_cls):
    mocker.patch("krux.printers.thermal.UART", new=mock_uart_cls)
    from krux.printers.thermal import AdafruitPrinter

    p = AdafruitPrinter()

    assert isinstance(p, AdafruitPrinter)


def test_clear(mocker, m5stickv, mock_uart_cls):
    mocker.patch("krux.printers.thermal.UART", new=mock_uart_cls)
    from krux.printers.thermal import AdafruitPrinter

    p = AdafruitPrinter()
    mocker.spy(p, "write_bytes")

    p.clear()

    assert p.write_bytes.call_count == 5


def test_print_qr_code(mocker, amigo, mock_uart_cls):
    mocker.patch("krux.printers.thermal.UART", new=mock_uart_cls)
    import krux
    from krux.printers.thermal import AdafruitPrinter

    p = AdafruitPrinter()
    mocker.spy(p, "write_bytes")
    mocker.spy(p, "feed")

    # Patch the write method of p.uart_conn
    mock_write = mocker.patch.object(p.uart_conn, "write")

    p.print_qr_code(TEST_QR_CODE)

    mock_write.assert_has_calls(
        [
            mocker.call(b"\x1dv0\x03\x10\x00}\x00"),
            mocker.call(
                bytearray(
                    b"\xff\xff\xff\xff\xe0\x07\xff\xf0\x7f\xe0\xf8?\xff\xff\xff\xf8"
                )
            ),
        ]
    )
    assert mock_write.call_count == 130
    p.write_bytes.assert_has_calls(
        [
            mocker.call(10),
        ]
    )

    p.feed.assert_called_once()
    krux.printers.thermal.wdt.feed.assert_called()


def test_print_string(mocker, m5stickv, mock_uart_cls):
    mocker.patch("krux.printers.thermal.UART", new=mock_uart_cls)
    from krux.printers.thermal import AdafruitPrinter

    p = AdafruitPrinter()
    mocker.spy(p, "write_bytes")
    mocker.spy(p, "feed")

    # Patch the write method of p.uart_conn
    mock_write = mocker.patch.object(p.uart_conn, "write")

    p.print_string("Hello, World!")

    mock_write.assert_called_with("Hello, World!")


def test_qr_data_width(mocker, m5stickv, mock_uart_cls):
    mocker.patch("krux.printers.thermal.UART", new=mock_uart_cls)
    from krux.printers.thermal import AdafruitPrinter

    p = AdafruitPrinter()
    assert p.qr_data_width() == 33


def test_print_bitmap_line(mocker, m5stickv, mock_uart_cls):
    mocker.patch("krux.printers.thermal.UART", new=mock_uart_cls)
    mock_sleep = mocker.patch("krux.printers.thermal.time.sleep_ms")
    from krux.printers.thermal import AdafruitPrinter

    p = AdafruitPrinter()
    mock_write = mocker.patch.object(p.uart_conn, "write")

    test_data = b"\xff\x00\xff\x00"
    p.print_bitmap_line(test_data)

    mock_write.assert_called_once_with(test_data)
    mock_sleep.assert_called_once_with(p.dot_print_time)
