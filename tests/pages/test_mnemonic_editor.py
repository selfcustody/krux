from . import create_ctx

TEST_12_WORD_MNEMONIC = (
    "olympic term tissue route sense program under choose bean emerge velvet absurd"
)
TEST_24_WORD_MNEMONIC = "brush badge sing still venue panther kitchen please help panel bundle excess sign couch stove increase human once effort candy goat top tiny major"
MNEMONICS = [TEST_12_WORD_MNEMONIC, TEST_24_WORD_MNEMONIC]


def test_confirm_given_words(mocker, multiple_devices):
    from krux.pages.mnemonic_editor import MnemonicEditor
    from krux.input import BUTTON_ENTER
    import board

    for mnemonic in MNEMONICS:
        btn_sequence = [BUTTON_ENTER]
        if board.config["type"] == "m5stickv" and len(mnemonic.split()) == 24:
            btn_sequence.append(BUTTON_ENTER)
        ctx = create_ctx(mocker, btn_sequence)
        mnemonic_editor = MnemonicEditor(ctx, mnemonic)
        edited_mnemonic = mnemonic_editor.edit()
        assert edited_mnemonic == mnemonic
        assert ctx.input.wait_for_button.call_count == len(btn_sequence)


def test_loop_through_words(mocker, cube):
    from krux.pages.mnemonic_editor import MnemonicEditor
    from krux.input import BUTTON_PAGE, BUTTON_PAGE_PREV, BUTTON_ENTER

    for mnemonic in MNEMONICS:
        len_words = len(mnemonic.split())
        btn_sequence = [
            *([BUTTON_PAGE] * (len_words + 2)),  # Loop forward
            *([BUTTON_PAGE_PREV] * (len_words + 2)),  # Loop backward
            BUTTON_ENTER,  # Confirm
        ]
        ctx = create_ctx(mocker, btn_sequence)
        mnemonic_editor = MnemonicEditor(ctx, mnemonic)
        edited_mnemonic = mnemonic_editor.edit()
        assert edited_mnemonic == mnemonic
        assert ctx.input.wait_for_button.call_count == len(btn_sequence)


def test_edit_new_mnemonic_using_buttons(mocker, cube):
    from krux.pages.mnemonic_editor import MnemonicEditor
    from krux.input import BUTTON_ENTER, BUTTON_PAGE, BUTTON_PAGE_PREV

    EDITED_MNEMONIC_12W = (
        "ability term tissue route sense program under choose bean emerge velvet above"
    )
    EDITED_MNEMONIC_24W = "ability badge sing still venue panther kitchen please help panel bundle excess sign couch stove increase human once effort candy goat top tiny obscure"

    BTN_SEQUENCE = [
        BUTTON_PAGE,  # Navigate to first word
        BUTTON_ENTER,  # Edit first word
        *([BUTTON_ENTER] * 4),  # Type ability and confirm
        BUTTON_PAGE_PREV,  # Navigate to "Go"
        BUTTON_ENTER,  # "Go"
    ]

    for mnemonic in MNEMONICS:
        ctx = create_ctx(mocker, BTN_SEQUENCE)
        mnemonic_editor = MnemonicEditor(ctx, mnemonic, new=True)
        edited_mnemonic = mnemonic_editor.edit()
        assert edited_mnemonic != mnemonic
        if len(mnemonic.split()) == 24:
            assert edited_mnemonic == EDITED_MNEMONIC_24W
        else:
            assert edited_mnemonic == EDITED_MNEMONIC_12W
        assert ctx.input.wait_for_button.call_count == len(BTN_SEQUENCE)


def test_edit_new_mnemonic_using_touch(mocker, amigo):
    from krux.pages.mnemonic_editor import MnemonicEditor
    from krux.input import BUTTON_TOUCH

    EDITED_MNEMONIC_12W = "olympic cabbage tissue route sense program under choose bean emerge velvet absorb"
    EDITED_MNEMONIC_24W = "brush badge sing still venue panther kitchen please help panel bundle excess sign cabbage stove increase human once effort candy goat top tiny lizard"

    BTN_SEQUENCE = [
        *([BUTTON_TOUCH] * 7),
    ]
    TOUCH_SEQUENCE = [
        # Each word in 12w mnemonic uses two touch indexes
        # For 24w mnemonic, indexes are w1=0, w2=2, w3=4 ... w13=1, w14=3, w15=5 ...
        3,  # index 3 = 2nd word for 12w mnemonic, 14th word for 24w mnemonic
        2,  # Type c,a,b,b,-> cabbage
        0,
        1,
        1,
        1,  # Confirm cabbage
        25,  # Press "Go"
    ]

    for mnemonic in MNEMONICS:
        ctx = create_ctx(mocker, BTN_SEQUENCE, touch_seq=TOUCH_SEQUENCE)
        ctx.input.buttons_active = False
        mnemonic_editor = MnemonicEditor(ctx, mnemonic, new=True)
        edited_mnemonic = mnemonic_editor.edit()
        assert edited_mnemonic != mnemonic
        if len(mnemonic.split()) == 24:
            assert edited_mnemonic == EDITED_MNEMONIC_24W
        else:
            assert edited_mnemonic == EDITED_MNEMONIC_12W
        assert ctx.input.wait_for_button.call_count == len(BTN_SEQUENCE)


def test_edit_new_mnemonic_last_word_using_touch(mocker, amigo):
    from krux.pages.mnemonic_editor import MnemonicEditor
    from krux.input import BUTTON_TOUCH

    EDITED_MNEMONIC_12W = (
        "olympic term tissue route sense program under choose bean emerge velvet choose"
    )

    TOUCH_SEQUENCE_12W = [
        # Each word in 12w mnemonic uses two touch indexes
        # For 24w mnemonic, indexes are w1=0, w2=2, w3=4 ... w13=1, w14=3, w15=5 ...
        23,  # index 23 = 12th word for 12w mnemonic
        2,  # Type c, h, o-> choose
        7,
        14,
        1,  # Confirm choose
        25,  # Press "Go"
    ]
    BTN_SEQUENCE = [*([BUTTON_TOUCH] * len(TOUCH_SEQUENCE_12W))]
    ctx = create_ctx(mocker, BTN_SEQUENCE, touch_seq=TOUCH_SEQUENCE_12W)
    mnemonic_editor = MnemonicEditor(ctx, TEST_12_WORD_MNEMONIC, new=True)
    edited_mnemonic = mnemonic_editor.edit()
    assert edited_mnemonic != TEST_12_WORD_MNEMONIC
    assert edited_mnemonic == EDITED_MNEMONIC_12W
    assert ctx.input.wait_for_button.call_count == len(BTN_SEQUENCE)


def test_edit_try_to_go_incomplete_word(mocker, amigo):
    from krux.pages.mnemonic_editor import MnemonicEditor
    from krux.input import BUTTON_TOUCH

    EDITED_MNEMONIC_12W = "olympic cabbage tissue route sense program under choose bean emerge velvet absorb"

    TOUCH_SEQUENCE_12W = [
        3,  # index 3 = 2nd word for 12w mnemonic, 14th word for 24w mnemonic
        0,  # Type a
        29,  # Press Keypad's "Go" with an inconplete word
        2,  # Type c,a,b,b,-> cabbage
        0,
        1,
        1,
        1,  # Confirm cabbage
        25,  # Press "Go"
    ]

    BTN_SEQUENCE = [*([BUTTON_TOUCH] * len(TOUCH_SEQUENCE_12W))]
    ctx = create_ctx(mocker, BTN_SEQUENCE, touch_seq=TOUCH_SEQUENCE_12W)
    mnemonic_editor = MnemonicEditor(ctx, TEST_12_WORD_MNEMONIC, new=True)
    edited_mnemonic = mnemonic_editor.edit()
    assert edited_mnemonic != TEST_12_WORD_MNEMONIC
    assert edited_mnemonic == EDITED_MNEMONIC_12W
    assert ctx.input.wait_for_button.call_count == len(BTN_SEQUENCE)


def test_esc_when_editing_a_word(mocker, amigo):
    from krux.pages.mnemonic_editor import MnemonicEditor
    from krux.input import BUTTON_TOUCH

    TOUCH_SEQUENCE_12W = [
        3,  # index 3 = 2nd word for 12w mnemonic, 14th word for 24w mnemonic
        28,  # Press Keypad's "Esc"
        1,  # Confirm Esc
        25,  # Press "Go"
    ]

    BTN_SEQUENCE = [*([BUTTON_TOUCH] * len(TOUCH_SEQUENCE_12W))]
    ctx = create_ctx(mocker, BTN_SEQUENCE, touch_seq=TOUCH_SEQUENCE_12W)
    mnemonic_editor = MnemonicEditor(ctx, TEST_12_WORD_MNEMONIC, new=True)
    edited_mnemonic = mnemonic_editor.edit()
    assert edited_mnemonic == TEST_12_WORD_MNEMONIC
    assert ctx.input.wait_for_button.call_count == len(BTN_SEQUENCE)


def test_esc_from_mnemic_editor(mocker, amigo):
    from krux.pages.mnemonic_editor import MnemonicEditor
    from krux.input import BUTTON_TOUCH

    TOUCH_SEQUENCE_12W = [
        24,  # Press "Esc"
        1,  # Confirm Esc
    ]

    BTN_SEQUENCE = [*([BUTTON_TOUCH] * len(TOUCH_SEQUENCE_12W))]
    ctx = create_ctx(mocker, BTN_SEQUENCE, touch_seq=TOUCH_SEQUENCE_12W)
    mnemonic_editor = MnemonicEditor(ctx, TEST_12_WORD_MNEMONIC, new=True)
    edited_mnemonic = mnemonic_editor.edit()
    assert edited_mnemonic == None
    assert ctx.input.wait_for_button.call_count == len(BTN_SEQUENCE)


def test_edit_existing_mnemonic_using_touch(mocker, amigo):
    from krux.pages.mnemonic_editor import MnemonicEditor
    from krux.input import BUTTON_TOUCH

    EDITED_MNEMONIC_12W = "olympic cabbage tissue route sense program under choose bean emerge velvet vendor"
    EDITED_MNEMONIC_24W = "brush badge sing still venue panther kitchen please help panel bundle excess sign cabbage stove increase human once effort candy goat top tiny witness"

    TOUCH_SEQUENCE_12W = [
        # Each word in 12w mnemonic uses two touch indexes
        # For 24w mnemonic, indexes are w1=0, w2=2, w3=4 ... w13=1, w14=3, w15=5 ...
        3,  # index 3 = 2nd word for 12w mnemonic, 14th word for 24w mnemonic
        2,  # Type c,a,b,b,-> cabbage
        0,
        1,
        1,
        1,  # Confirm cabbage
        25,  # Try to "Go" with invalid checksum word
        24,  # Press "Esc"
        0,  # Give up to Esc
        22,  # index 23 = word 12
        21,  # Type v, e, n, d-> vendor
        4,
        13,
        3,
        1,  # Confirm vendor
        25,  # Press "Go"
    ]
    TOUCH_SEQUENCE_24W = [
        3,  # index 3 = 2nd word for 12w mnemonic
        2,  # Type c,a,b,b,-> cabbage
        0,
        1,
        1,
        1,  # Confirm cabbage
        25,  # Try to "Go" with invalid checksum word
        23,  # index 23 = word 24
        22,  # Type w, i, t -> witness
        8,
        19,
        1,  # Confirm witness
        25,  # Press "Go"
    ]

    for mnemonic in MNEMONICS:
        btn_sequence = [
            *([BUTTON_TOUCH] * len(TOUCH_SEQUENCE_12W)),
        ]
        touch_seq = (
            TOUCH_SEQUENCE_12W if len(mnemonic.split()) == 12 else TOUCH_SEQUENCE_24W
        )
        ctx = create_ctx(mocker, btn_sequence, touch_seq=touch_seq)
        mnemonic_editor = MnemonicEditor(ctx, mnemonic)
        edited_mnemonic = mnemonic_editor.edit()
        assert edited_mnemonic != mnemonic
        if len(mnemonic.split()) == 24:
            assert edited_mnemonic == EDITED_MNEMONIC_24W
        else:
            assert edited_mnemonic == EDITED_MNEMONIC_12W
        assert ctx.input.wait_for_button.call_count == len(touch_seq)


def test_button_used_but_touch_enabled(mocker, amigo):
    from krux.pages.mnemonic_editor import MnemonicEditor
    from krux.input import BUTTON_TOUCH, BUTTON_ENTER, BUTTON_PAGE_PREV

    mnemonic = "olympic cabbage tissue route sense program under choose bean emerge velvet vendor"
    ctx = create_ctx(mocker, None)
    mnemonic_editor = MnemonicEditor(ctx, mnemonic)
    mnemonic_editor._map_words()
    ctx.input.touch.x_regions.append.assert_called()
    ctx.input.touch.y_regions.append.assert_called()
