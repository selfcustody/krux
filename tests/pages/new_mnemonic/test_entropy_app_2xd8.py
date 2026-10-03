from .. import create_ctx


def _dial(value, increment_btn, lock_btn=None):
    """Button/swipe presses to dial a wheel from its default (1) up to
    `value`, then lock it in."""
    from krux.input import BUTTON_ENTER

    return [increment_btn] * (value - 1) + [lock_btn or BUTTON_ENTER]


def test_new_12w_from_entropy_app_2xd8(m5stickv, mocker):
    """
    Draws 11 whole words via the 2XD8 booklet method's two-wheel picker
    (White, Black die faces 1..8 cycling), revealing the card and then the
    word after each roll pair, then confirms the computed checksum word
    makes a valid 12-word mnemonic.
    """
    from krux.pages.new_mnemonic.entropy_app_2xd8 import EntropyApp2XD8
    from krux.input import BUTTON_ENTER, BUTTON_PAGE

    # Die faces 1..8 cycling, 4 rolls (white/black x2) per word, 11 words = 44 rolls.
    # Independently verified offline (bit-packing + embit.bip39.mnemonic_from_bytes)
    # to draw "equal tattoo equal tattoo equal tattoo equal tattoo equal tattoo equal"
    # with "able" computed as the valid checksum word -- same math as the original
    # keypad-driven implementation, only the input method (wheel dial vs keypad tap)
    # changed, so the expected mnemonic is unchanged.
    ROLLS = [(i % 8) + 1 for i in range(44)]
    MNEMONIC = "equal tattoo equal tattoo equal tattoo equal tattoo equal tattoo equal able"

    BTN_SEQUENCE = [BUTTON_ENTER, BUTTON_ENTER]  # choose 12 words, then "Proceed?"
    roll_iter = iter(ROLLS)
    for _word in range(11):
        for _roll in range(4):  # white1, black1, white2, black2
            BTN_SEQUENCE += _dial(next(roll_iter), BUTTON_PAGE)
        BTN_SEQUENCE += [BUTTON_ENTER]  # dismiss the word-reveal screen
    BTN_SEQUENCE += [BUTTON_ENTER]  # dismiss the "Words Drawn" list
    BTN_SEQUENCE += [BUTTON_ENTER]  # confirm "Compute checksum word...?"

    ctx = create_ctx(mocker, BTN_SEQUENCE)
    entropy_app_2xd8 = EntropyApp2XD8(ctx)
    entropy = entropy_app_2xd8.new_key()

    assert entropy is not None
    assert len(entropy) == 16  # 128 bits for a 12-word mnemonic
    assert ctx.input.wait_for_button.call_count == len(BTN_SEQUENCE)

    from embit.bip39 import mnemonic_from_bytes

    words = mnemonic_from_bytes(entropy)
    assert words == MNEMONIC
    # The first 11 words are exactly what was drawn from the dice (not hashed).
    assert words.split()[:11] == MNEMONIC.split()[:11]


def test_new_12w_from_entropy_app_2xd8_via_swipe(m5stickv, mocker):
    """
    Same draw as test_new_12w_from_entropy_app_2xd8, but every wheel is dialed with
    SWIPE_DOWN (the code touchscreen devices like the Amigo produce on a
    real downward swipe) and locked with BUTTON_TOUCH (a tap), instead of
    the physical BUTTON_PAGE/BUTTON_ENTER a button-only device would send.
    The widget's own logic never branches on device type -- it only checks
    button-code membership in INCREMENT/DECREMENT/LOCK_IN -- so this proves
    the touchscreen input path end-to-end without needing the desktop
    simulator's sequence scripting, which has no drag/swipe support at all.
    """
    from krux.pages.new_mnemonic.entropy_app_2xd8 import EntropyApp2XD8
    from krux.input import BUTTON_ENTER, BUTTON_TOUCH, SWIPE_DOWN

    ROLLS = [(i % 8) + 1 for i in range(44)]
    MNEMONIC = "equal tattoo equal tattoo equal tattoo equal tattoo equal tattoo equal able"

    BTN_SEQUENCE = [BUTTON_ENTER, BUTTON_ENTER]  # choose 12 words, then "Proceed?"
    roll_iter = iter(ROLLS)
    for _word in range(11):
        for _roll in range(4):
            BTN_SEQUENCE += _dial(next(roll_iter), SWIPE_DOWN, BUTTON_TOUCH)
        BTN_SEQUENCE += [BUTTON_TOUCH]  # dismiss the word-reveal screen (a tap)
    BTN_SEQUENCE += [BUTTON_TOUCH]  # dismiss the "Words Drawn" list
    BTN_SEQUENCE += [BUTTON_ENTER]  # confirm "Compute checksum word...?"

    ctx = create_ctx(mocker, BTN_SEQUENCE)
    entropy_app_2xd8 = EntropyApp2XD8(ctx)
    entropy = entropy_app_2xd8.new_key()

    assert entropy is not None
    assert ctx.input.wait_for_button.call_count == len(BTN_SEQUENCE)

    from embit.bip39 import mnemonic_from_bytes

    assert mnemonic_from_bytes(entropy) == MNEMONIC


def test_new_12w_from_entropy_app_2xd8_not_proceed(m5stickv, mocker):
    """User declines the initial 'Proceed?' prompt -- no entropy is captured"""
    from krux.pages.new_mnemonic.entropy_app_2xd8 import EntropyApp2XD8
    from krux.input import BUTTON_ENTER, BUTTON_PAGE_PREV

    BTN_SEQUENCE = [BUTTON_ENTER] + [BUTTON_PAGE_PREV]  # 12 words, then decline

    ctx = create_ctx(mocker, BTN_SEQUENCE)
    entropy_app_2xd8 = EntropyApp2XD8(ctx)
    entropy = entropy_app_2xd8.new_key()

    assert entropy is None
    assert ctx.input.wait_for_button.call_count == len(BTN_SEQUENCE)


def test_cancel_new_12w_from_entropy_app_2xd8(m5stickv, mocker):
    """A swipe-left (long-press on button-only devices) mid-roll prompts to
    cancel; confirming exits the whole draw"""
    from krux.pages.new_mnemonic.entropy_app_2xd8 import EntropyApp2XD8
    from krux.input import BUTTON_ENTER, SWIPE_LEFT

    BTN_SEQUENCE = [
        BUTTON_ENTER,  # 12 words
        BUTTON_ENTER,  # Proceed
        SWIPE_LEFT,  # cancel mid-roll (before any dial presses)
        BUTTON_ENTER,  # confirm "Are you sure?" -> Yes
    ]

    ctx = create_ctx(mocker, BTN_SEQUENCE)
    entropy_app_2xd8 = EntropyApp2XD8(ctx)
    entropy = entropy_app_2xd8.new_key()

    assert entropy is None
    assert ctx.input.wait_for_button.call_count == len(BTN_SEQUENCE)
