TEST_QR = """
111111100111000100010011001111111
100000101001100100101111001000001
101110101001100001000001001011101
101110100010101000110011101011101
101110101101001110000101001011101
100000101010100111011110101000001
111111101010101010101010101111111
000000001111101101101111000000000
110100110101111010010110101110110
001101000100111011101100101000001
010101101010100000011000111110101
001101010101010100111100010011001
010110110010110011001100001000000
011100011010100010010110101010001
100110100001101011101101000110110
000100001001011001110100010011011
001011111100100011011110001010001
111100011111010010100001110000000
000111111110011000000010000110111
101101000111100111001100101010001
100010111100110010110100110100011
011001011000110011001010111000011
110111100110111010111000111000101
011000000100011110011100001111001
100101110101110011011111111110000
000000001000101000011111100010001
111111101111110010000010101010110
100000100101110111011100100010011
101110100010000101010110111110000
101110101111101010100100001111111
101110100100001000000010110110011
100000101001000011110101100111000
111111101000011010001101101011010
""".strip()

TEST_QR_WITH_BORDER = """
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

DEFAULT_BG_COLOR = 0x0000  # Black


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


def test_draw_line_hcentered_with_fullw_bg(mocker, m5stickv):
    mocker.patch("krux.display.lcd", new=mocker.MagicMock())
    import krux
    from krux.display import Display

    d = Display()
    mocker.patch.object(d, "width", new=lambda: 135)
    mocker.spy(d, "draw_string")

    d.draw_line_hcentered_with_fullw_bg(
        "Hello world", 10, krux.display.lcd.WHITE, krux.display.lcd.BLACK
    )

    d.draw_string.assert_called_with(
        23,
        d.font_height * 10,
        "Hello world",
        krux.display.lcd.WHITE,
        krux.display.lcd.BLACK,
    )
    krux.display.lcd.fill_rectangle.assert_called()


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

    krux.display.lcd.draw_qr_code.assert_called_with(
        0, TEST_QR_WITH_BORDER, 135, QR_DARK_COLOR, QR_LIGHT_COLOR, DEFAULT_BG_COLOR
    )
