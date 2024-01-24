TEST_QR = bytearray(
    b"\x7fn\xfd\x830\x08v9\xd6\xedj\xa0\xdbUU7\xc8\xa0\xe0_U\x7f\x00i\x00\xe3\xd61P\x08\xf5Q\xef^\xfe`\xe8\xc1\x7f\xdex\x936Y\x91\xb8\xeb\xd29c\xd5\xd4\x7f\x00\n#\xfe\xcd\xd7\rJ\x8e\xd9\xe5\xf8\xb9K\xe6x\x17\xb9\xca\xa0\x9a\x9a\x7f\xbb\x1b\x01"
)


def test_init(mocker, m5stickv):
    mocker.patch("krux.display.lcd", new=mocker.MagicMock())
    import krux
    from krux.display import Display
    import board

    mocker.spy(Display, "initialize_lcd")

    d = Display()
    d.initialize_lcd()

    assert isinstance(d, Display)
    d.initialize_lcd.assert_called()

    krux.display.lcd.init.assert_called_once()
    assert "type" in krux.display.lcd.init.call_args.kwargs
    assert (
        krux.display.lcd.init.call_args.kwargs["type"]
        == board.config["lcd"]["lcd_type"]
    )


def test_width(mocker, m5stickv):
    mocker.patch("krux.display.lcd", new=mocker.MagicMock())
    import krux
    from krux.display import Display

    d = Display()
    d.initialize_lcd()

    d.to_portrait()

    assert d.width() == krux.display.lcd.width()
    krux.display.lcd.width.assert_called()

    d.to_landscape()

    assert d.width() == krux.display.lcd.height()
    krux.display.lcd.height.assert_called()


def test_height(mocker, m5stickv):
    mocker.patch("krux.display.lcd", new=mocker.MagicMock())
    import krux
    from krux.display import Display

    d = Display()

    d.to_portrait()

    assert d.height() == krux.display.lcd.height()
    krux.display.lcd.height.assert_called()

    d.to_landscape()

    assert d.height() == krux.display.lcd.width()
    krux.display.lcd.width.assert_called()


def test_qr_data_width(mocker, m5stickv):
    from krux.display import Display

    d = Display()
    d.to_portrait()

    mocker.patch.object(d, "width", new=lambda: 135)
    width = d.width()
    mocker.spy(d, "width")
    assert d.qr_data_width() == width // 4

    mocker.patch.object(d, "width", new=lambda: 320)
    width = d.width()
    mocker.spy(d, "width")
    assert d.qr_data_width() == width // 6

    d.width.assert_called()


def test_to_landscape(mocker, m5stickv):
    mocker.patch("krux.display.lcd", new=mocker.MagicMock())
    import krux
    from krux.display import Display

    d = Display()

    d.to_landscape()

    krux.display.lcd.rotation.assert_called()


def test_to_portrait(mocker, m5stickv):
    mocker.patch("krux.display.lcd", new=mocker.MagicMock())
    import krux
    from krux.display import Display

    d = Display()

    d.to_portrait()

    krux.display.lcd.rotation.assert_called()


def test_to_lines(mocker, m5stickv):
    from krux.display import Display

    cases = [
        (135, "Two Words", ["Two Words"]),
        (135, "Two  Words", ["Two  Words"]),
        (135, "Two   Words", ["Two   Words"]),
        (135, "Two        Words", ["Two        Words"]),
        (135, "Two\nWords", ["Two", "Words"]),
        (135, "Two\n\nWords", ["Two", "", "Words"]),
        (135, "Two\n\n\nWords", ["Two", "", "", "Words"]),
        (135, "Two\n\n\n\nWords", ["Two", "", "", "", "Words"]),
        (135, "Two\n\n\n\n\nWords", ["Two", "", "", "", "", "Words"]),
        (135, "\nTwo\nWords\n", ["", "Two", "Words"]),
        (135, "\n\nTwo\nWords\n\n", ["", "", "Two", "Words", ""]),
        (135, "\n\n\nTwo\nWords\n\n\n", ["", "", "", "Two", "Words", "", ""]),
        (135, "More Than Two Words", ["More Than", "Two Words"]),
        (
            135,
            "A bunch of words that span multiple lines..",
            ["A bunch of", "words that span", "multiple lines.."],
        ),
        (
            135,
            "tpubDCDuqu5HtBX2aD7wxvnHcj1DgFN1UVgzLkA1Ms4Va4P7TpJ3jDknkPLwWT2SqrKXNNAtJBCPcbJ8Tcpm6nLxgFapCZyhKgqwcEGv1BVpD7s",
            [
                "tpubDCDuqu5HtBX2",
                "aD7wxvnHcj1DgFN1",
                "UVgzLkA1Ms4Va4P7",
                "TpJ3jDknkPLwWT2S",
                "qrKXNNAtJBCPcbJ8",
                "Tcpm6nLxgFapCZyh",
                "KgqwcEGv1BVpD7s",
            ],
        ),
        (
            135,
            "xpub: tpubDCDuqu5HtBX2aD7wxvnHcj1DgFN1UVgzLkA1Ms4Va4P7TpJ3jDknkPLwWT2SqrKXNNAtJBCPcbJ8Tcpm6nLxgFapCZyhKgqwcEGv1BVpD7s",
            [
                "xpub:",
                "tpubDCDuqu5HtBX2",
                "aD7wxvnHcj1DgFN1",
                "UVgzLkA1Ms4Va4P7",
                "TpJ3jDknkPLwWT2S",
                "qrKXNNAtJBCPcbJ8",
                "Tcpm6nLxgFapCZyh",
                "KgqwcEGv1BVpD7s",
            ],
        ),
        (135, "Log Level\nNONE", ["Log Level", "NONE"]),
        (
            135,
            "New firmware detected.\n\nSHA256:\n1621f9c0e9ccb7995a29327066566adfd134e19109d7ce8e52aad7bd7dcce121\n\n\n\nInstall?",
            [
                "New firmware",
                "detected.",
                "",
                "SHA256:",
                "1621f9c0e9ccb799",
                "5a29327066566adf",
                "d134e19109d7ce8e",
                "52aad7bd7dcce121",
                "",
                "",
                "",
                "Install?",
            ],
        ),
        (240, "Two Words", ["Two Words"]),
        (240, "Two\nWords", ["Two", "Words"]),
        (240, "Two\n\nWords", ["Two", "", "Words"]),
        (240, "Two\n\n\nWords", ["Two", "", "", "Words"]),
        (240, "Two\n\n\n\nWords", ["Two", "", "", "", "Words"]),
        (240, "Two\n\n\n\n\nWords", ["Two", "", "", "", "", "Words"]),
        (240, "\nTwo\nWords\n", ["", "Two", "Words"]),
        (240, "\n\nTwo\nWords\n\n", ["", "", "Two", "Words", ""]),
        (240, "\n\n\nTwo\nWords\n\n\n", ["", "", "", "Two", "Words", "", ""]),
        (240, "More Than Two Words", ["More Than Two Words"]),
        (
            240,
            "A bunch of text that spans multiple lines..",
            ["A bunch of text that", "spans multiple lines.."],
        ),
        (
            240,
            "tpubDCDuqu5HtBX2aD7wxvnHcj1DgFN1UVgzLkA1Ms4Va4P7TpJ3jDknkPLwWT2SqrKXNNAtJBCPcbJ8Tcpm6nLxgFapCZyhKgqwcEGv1BVpD7s",
            [
                "tpubDCDuqu5HtBX2aD7wxvnHcj1",
                "DgFN1UVgzLkA1Ms4Va4P7TpJ3jD",
                "knkPLwWT2SqrKXNNAtJBCPcbJ8T",
                "cpm6nLxgFapCZyhKgqwcEGv1BVp",
                "D7s",
            ],
        ),
        (
            240,
            "xpub: tpubDCDuqu5HtBX2aD7wxvnHcj1DgFN1UVgzLkA1Ms4Va4P7TpJ3jDknkPLwWT2SqrKXNNAtJBCPcbJ8Tcpm6nLxgFapCZyhKgqwcEGv1BVpD7s",
            [
                "xpub:",
                "tpubDCDuqu5HtBX2aD7wxvnHcj1",
                "DgFN1UVgzLkA1Ms4Va4P7TpJ3jD",
                "knkPLwWT2SqrKXNNAtJBCPcbJ8T",
                "cpm6nLxgFapCZyhKgqwcEGv1BVp",
                "D7s",
            ],
        ),
        (240, "Log Level\nNONE", ["Log Level", "NONE"]),
        (
            240,
            "New firmware detected.\n\nSHA256:\n1621f9c0e9ccb7995a29327066566adfd134e19109d7ce8e52aad7bd7dcce121\n\n\n\nInstall?",
            [
                "New firmware detected.",
                "",
                "SHA256:",
                "1621f9c0e9ccb7995a293270665",
                "66adfd134e19109d7ce8e52aad7",
                "bd7dcce121",
                "",
                "",
                "",
                "Install?",
            ],
        ),
    ]
    for case in cases:
        mocker.patch(
            "krux.display.lcd",
            new=mocker.MagicMock(width=mocker.MagicMock(return_value=case[0])),
        )
        d = Display()
        lines = d.to_lines(case[1])
        assert lines == case[2]


def test_to_lines_exact_match_amigo(mocker, amigo_tft):
    from krux.display import Display

    cases = [
        (320, "01234 0123456789012345678", ["01234 0123456789012345678"]),
        (320, "0123456789 01234567890 01234", ["0123456789", "01234567890 01234"]),
        (320, "01234567890123456789012345", ["0123456789012345678901234", "5"]),
        (
            320,
            "01234 0123456789012345678\n01234 0123456789012345678",
            ["01234 0123456789012345678", "01234 0123456789012345678"],
        ),
        (
            320,
            "01 34 0123456789012345678\n01234 0123456789012345678",
            ["01 34 0123456789012345678", "01234 0123456789012345678"],
        ),
        (
            320,
            "01 01 01 01 01 01 01 01 0\n01 01 01 01 01 01 01 0123",
            ["01 01 01 01 01 01 01 01 0", "01 01 01 01 01 01 01 0123"],
        ),
        (
            320,
            "0 0 0 0 0 0 0 0 0 0 0 0 0\n01 01 01 01 01 01 01 0123",
            ["0 0 0 0 0 0 0 0 0 0 0 0 0", "01 01 01 01 01 01 01 0123"],
        ),
        (
            320,
            "01 345 0123456789012345678\n01234 0123456789012345678",
            ["01 345", "0123456789012345678", "01234 0123456789012345678"],
        ),
    ]
    for case in cases:
        mocker.patch(
            "krux.display.lcd",
            new=mocker.MagicMock(width=mocker.MagicMock(return_value=case[0])),
        )
        d = Display()
        lines = d.to_lines(case[1])
        print(lines)
        assert lines == case[2]


def test_outline(mocker, m5stickv):
    mocker.patch("krux.display.lcd", new=mocker.MagicMock())
    import krux
    from krux.display import Display

    d = Display()
    mocker.patch.object(d, "fill_rectangle")

    d.outline(0, 0, 100, 100, krux.display.lcd.WHITE)

    d.fill_rectangle.assert_has_calls(
        [
            mocker.call(0, 0, 101, 1, krux.display.lcd.WHITE),
            mocker.call(0, 100, 101, 1, krux.display.lcd.WHITE),
            mocker.call(0, 0, 1, 101, krux.display.lcd.WHITE),
            mocker.call(100, 0, 1, 101, krux.display.lcd.WHITE),
        ]
    )


def test_fill_rectangle(mocker, m5stickv):
    mocker.patch("krux.display.lcd", new=mocker.MagicMock())
    import krux
    from krux.display import Display

    d = Display()

    d.fill_rectangle(0, 0, 100, 100, krux.display.lcd.WHITE)

    krux.display.lcd.fill_rectangle.assert_called_with(
        0, 0, 100, 100, krux.display.lcd.WHITE
    )


def test_fill_rectangle_on_inverted_display(mocker, amigo_tft):
    mocker.patch("krux.display.lcd", new=mocker.MagicMock())
    import krux
    from krux.display import Display

    d = Display()
    mocker.patch.object(d, "width", new=lambda: 480)

    d.fill_rectangle(0, 0, 100, 100, krux.display.lcd.WHITE)

    krux.display.lcd.fill_rectangle.assert_called_with(
        480 - 0 - 100, 0, 100, 100, krux.display.lcd.WHITE
    )


def test_draw_string(mocker, m5stickv):
    mocker.patch("krux.display.lcd", new=mocker.MagicMock())
    import krux
    from krux.display import Display

    d = Display()

    d.draw_string(0, 0, "Hello world", krux.display.lcd.WHITE, krux.display.lcd.BLACK)

    krux.display.lcd.draw_string.assert_called_with(
        0, 0, "Hello world", krux.display.lcd.WHITE, krux.display.lcd.BLACK
    )


def test_draw_string_on_inverted_display(mocker, amigo_tft):
    mocker.patch("krux.display.lcd", new=mocker.MagicMock())
    import krux
    from krux.display import Display

    d = Display()
    mocker.patch.object(d, "width", new=lambda: 480)

    d.draw_string(0, 0, "Hello world", krux.display.lcd.WHITE, krux.display.lcd.BLACK)

    krux.display.lcd.draw_string.assert_called_with(
        480 - 0 - 132, 0, "Hello world", krux.display.lcd.WHITE, krux.display.lcd.BLACK
    )


def test_draw_hcentered_text(mocker, m5stickv):
    mocker.patch("krux.display.lcd", new=mocker.MagicMock())
    import krux
    from krux.display import Display

    d = Display()
    mocker.patch.object(d, "width", new=lambda: 135)
    mocker.spy(d, "draw_string")

    d.draw_hcentered_text(
        "Hello world", 50, krux.display.lcd.WHITE, krux.display.lcd.BLACK
    )

    d.draw_string.assert_called_with(
        23, 50, "Hello world", krux.display.lcd.WHITE, krux.display.lcd.BLACK
    )


def test_draw_centered_text(mocker, m5stickv):
    mocker.patch("krux.display.lcd", new=mocker.MagicMock())
    import krux
    from krux.display import Display

    d = Display()
    mocker.patch.object(d, "width", new=lambda: 135)
    mocker.patch.object(d, "height", new=lambda: 240)
    mocker.spy(d, "draw_hcentered_text")

    d.draw_centered_text("Hello world", krux.display.lcd.WHITE, 0)

    d.draw_hcentered_text.assert_called_with(
        "Hello world", 113, krux.display.lcd.WHITE, 0
    )


def test_draw_qr_code(mocker, m5stickv):
    mocker.patch("krux.display.lcd", new=mocker.MagicMock())
    import krux
    from krux.display import Display, QR_DARK_COLOR, QR_LIGHT_COLOR

    d = Display()
    mocker.patch.object(d, "width", new=lambda: 135)

    d.draw_qr_code(0, TEST_QR)

    krux.display.lcd.draw_qr_code_binary.assert_called_with(
        0, TEST_QR, 135, QR_DARK_COLOR, QR_LIGHT_COLOR, QR_LIGHT_COLOR
    )
