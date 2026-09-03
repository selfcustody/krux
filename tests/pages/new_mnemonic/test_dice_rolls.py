from .. import create_ctx
from embit import bip39

# rolls which will result in good entropy
PATTERN_ROLLS_TOUCH_SEQUENCE = (
    [0] * 9  # 9 number 1 presses
    + [1] * 9  # 9 number 2 presses
    + [2] * 6  # 6 number 3 presses
    + [3] * 10  # 10 number 4 presses
    + [4] * 7  # 7 number 5 presses
    + [5] * 9  # 9 number 6 presses
)

# rolls which will result in poor min-entropy AND a detectable pattern: cycling
# through only faces 1,2,3 skews the distribution (p_max ~= 1/3) and produces a
# constant derivative between consecutive rolls
POOR_ROLLS_TOUCH_SEQUENCE = [0, 1, 2] * 23 + [0]

GOOD_ROLLS_SEQUENCE = [
    5,
    0,
    0,
    5,
    2,
    1,
    1,
    1,
    5,
    0,
    5,
    5,
    4,
    0,
    4,
    3,
    0,
    0,
    0,
    1,
    1,
    4,
    4,
    0,
    4,
    1,
    5,
    5,
    5,
    4,
    3,
    1,
    3,
    4,
    2,
    0,
    1,
    5,
    3,
    2,
    2,
    1,
    1,
    2,
    0,
    0,
    3,
    0,
    2,
    2,
    4,
    2,
    0,
    5,
    3,
    4,
    0,
    3,
    0,
    4,
    2,
    5,
    4,
    2,
    4,
    1,
    5,
    0,
    0,
    5,
]


def test_entropy_but_not_proceed(m5stickv, mocker):
    """
    Test a situation where the user begin the creation of an entropy on m5stickv but, in the middle
    time, stop the procedure (when krux ask "proceed" and the user choose "No")
    """
    from krux.pages.new_mnemonic.dice_rolls import DiceEntropy
    from krux.input import BUTTON_ENTER, BUTTON_PAGE, BUTTON_PAGE_PREV

    BTN_SEQUENCE = (
        # 1 press to proceed to 12 words
        [BUTTON_ENTER]
        +
        # 1 press to cancel the proceed
        [BUTTON_PAGE_PREV]
    )
    ctx = create_ctx(mocker, BTN_SEQUENCE)
    dice_entropy = DiceEntropy(ctx)
    entropy = dice_entropy.new_key()

    assert entropy is None
    assert ctx.input.wait_for_button.call_count == len(BTN_SEQUENCE)


def test_entropy_on_amigo_device_but_not_proceed(amigo, mocker):
    """
    Test a situation where the user begin the creation of an entropy in Amigo but, in the
    middle time, stop the procedure (when krux ask "proceed" and the user choose "No")
    """
    from krux.pages.new_mnemonic.dice_rolls import DiceEntropy
    from krux.input import BUTTON_ENTER, BUTTON_PAGE, BUTTON_PAGE_PREV

    BTN_SEQUENCE = (
        # 1 press to proceed to 12 words
        [BUTTON_ENTER]
        +
        # 1 press to cancel the proceed and then confirm the cancelation
        [BUTTON_PAGE, BUTTON_ENTER]
    )

    ctx = create_ctx(mocker, BTN_SEQUENCE)
    dice_entropy = DiceEntropy(ctx)
    entropy = dice_entropy.new_key()

    assert entropy is None
    assert ctx.input.wait_for_button.call_count == len(BTN_SEQUENCE)


def test_new_12w_from_d6(m5stickv, mocker):
    from krux.pages.new_mnemonic.dice_rolls import DiceEntropy, D6_12W_MIN_ROLLS
    from krux.input import BUTTON_ENTER, BUTTON_PAGE, BUTTON_PAGE_PREV

    BTN_SEQUENCE = (
        # 1 press to proceed to 12 words
        [BUTTON_ENTER]
        +
        # 1 press to proceed msg
        [BUTTON_ENTER]
        +
        # 1 presses per roll
        [BUTTON_ENTER for _ in range(D6_12W_MIN_ROLLS)]
        +
        # 1 press prev and 1 press on btn Go
        [BUTTON_PAGE_PREV, BUTTON_ENTER]
        + [
            BUTTON_ENTER,  # proceed with poor entropy,
            BUTTON_PAGE,  # move to Generate Words, while seeing rolls
            BUTTON_ENTER,  # generate words
            BUTTON_ENTER,  # 1 press to confirm SHA
        ]
    )
    MNEMONIC = (
        "reflect net crush light tobacco cat boil begin laptop fish kangaroo speed"
    )

    ctx = create_ctx(mocker, BTN_SEQUENCE)
    dice_entropy = DiceEntropy(ctx)
    entropy = dice_entropy.new_key()
    words = bip39.mnemonic_from_bytes(entropy)

    assert ctx.input.wait_for_button.call_count == len(BTN_SEQUENCE)
    assert words == MNEMONIC


def test_new_24w_from_d6(m5stickv, mocker):
    from krux.pages.new_mnemonic.dice_rolls import DiceEntropy, D6_24W_MIN_ROLLS
    from krux.input import BUTTON_ENTER, BUTTON_PAGE, BUTTON_PAGE_PREV

    BTN_SEQUENCE = (
        # 1 press change to 24 words and 1 press to proceed
        [BUTTON_PAGE, BUTTON_ENTER]
        +
        # 1 press to proceed msg
        [BUTTON_ENTER]
        +
        # 1 presses per roll
        [BUTTON_ENTER for _ in range(D6_24W_MIN_ROLLS)]
        +
        # 1 press prev and 1 press on btn Go
        [BUTTON_PAGE_PREV, BUTTON_ENTER]
        + [
            BUTTON_ENTER,  # proceed with poor entropy,
            BUTTON_PAGE,  # move to Generate Words, while seeing rolls
            BUTTON_ENTER,  # generate words
            BUTTON_ENTER,  # 1 press to confirm SHA
        ]
    )
    MNEMONIC = "artist glimpse decade mountain deliver latin forum permit clown wheat digital report parent hockey replace control awesome afford rough assume rain long village soup"

    ctx = create_ctx(mocker, BTN_SEQUENCE)
    dice_entropy = DiceEntropy(ctx)
    entropy = dice_entropy.new_key()
    words = bip39.mnemonic_from_bytes(entropy)

    assert ctx.input.wait_for_button.call_count == len(BTN_SEQUENCE)
    assert words == MNEMONIC


def test_new_12w_from_d6_on_amigo_device(amigo, mocker):
    from krux.pages.new_mnemonic.dice_rolls import DiceEntropy, D6_12W_MIN_ROLLS
    from krux.input import BUTTON_ENTER, BUTTON_PAGE, BUTTON_PAGE_PREV

    BTN_SEQUENCE = (
        # 1 press to proceed to 12 words
        [BUTTON_ENTER]
        +
        # 1 press to proceed msg
        [BUTTON_ENTER]
        +
        # 1 presses per roll
        [BUTTON_ENTER for _ in range(D6_12W_MIN_ROLLS)]
        +
        # 1 press prev and 1 press on btn Go
        [BUTTON_PAGE_PREV, BUTTON_ENTER]
        + [
            BUTTON_ENTER,  # proceed with poor entropy,
            BUTTON_PAGE,  # move to Generate Words, while seeing rolls
            BUTTON_ENTER,  # generate words
            BUTTON_ENTER,  # 1 press to confirm SHA
        ]
    )
    MNEMONIC = (
        "reflect net crush light tobacco cat boil begin laptop fish kangaroo speed"
    )

    ctx = create_ctx(mocker, BTN_SEQUENCE)
    dice_entropy = DiceEntropy(ctx)
    entropy = dice_entropy.new_key()
    words = bip39.mnemonic_from_bytes(entropy)

    assert ctx.input.wait_for_button.call_count == len(BTN_SEQUENCE)
    assert words == MNEMONIC


def test_new_24w_from_d6_on_amigo_device(amigo, mocker):
    from krux.pages.new_mnemonic.dice_rolls import DiceEntropy, D6_24W_MIN_ROLLS
    from krux.input import BUTTON_ENTER, BUTTON_PAGE, BUTTON_PAGE_PREV

    BTN_SEQUENCE = (
        # 1 press change to 24 words and 1 press to proceed
        [BUTTON_PAGE, BUTTON_ENTER]
        +
        # 1 press to proceed msg
        [BUTTON_ENTER]
        +
        # 1 presses per roll
        [BUTTON_ENTER for _ in range(D6_24W_MIN_ROLLS)]
        +
        # 1 press prev and 1 press on btn Go
        [BUTTON_PAGE_PREV, BUTTON_ENTER]
        + [
            BUTTON_ENTER,  # proceed with poor entropy,
            BUTTON_PAGE,  # move to Generate Words, while seeing rolls
            BUTTON_ENTER,  # generate words
            BUTTON_ENTER,  # 1 press to confirm SHA
        ]
    )
    MNEMONIC = "artist glimpse decade mountain deliver latin forum permit clown wheat digital report parent hockey replace control awesome afford rough assume rain long village soup"

    ctx = create_ctx(mocker, BTN_SEQUENCE)
    dice_entropy = DiceEntropy(
        ctx,
    )
    entropy = dice_entropy.new_key()
    words = bip39.mnemonic_from_bytes(entropy)

    assert ctx.input.wait_for_button.call_count == len(BTN_SEQUENCE)
    assert words == MNEMONIC


def test_cancel_new_12w_from_d6_on_amigo_device(amigo, mocker):
    "Will test the Esc button on the roll screen"
    from krux.pages.new_mnemonic.dice_rolls import DiceEntropy
    from krux.input import BUTTON_ENTER, BUTTON_PAGE_PREV

    BTN_SEQUENCE = (
        # 1 press to proceed to 12 words
        [BUTTON_ENTER]
        +
        # 1 press to proceed msg
        [BUTTON_ENTER]
        +
        # 2 press prev and 1 press on btn Esc
        [BUTTON_PAGE_PREV, BUTTON_PAGE_PREV, BUTTON_ENTER]
        +
        # 1 press to proceed confirm exit msg
        [BUTTON_ENTER]
    )

    ctx = create_ctx(mocker, BTN_SEQUENCE)
    dice_entropy = DiceEntropy(ctx, is_d20=True)
    dice_entropy.new_key()

    assert ctx.input.wait_for_button.call_count == len(BTN_SEQUENCE)


def test_new_12w_from_d20(m5stickv, mocker):
    from krux.pages.new_mnemonic.dice_rolls import DiceEntropy, D20_12W_MIN_ROLLS
    from krux.input import BUTTON_ENTER, BUTTON_PAGE, BUTTON_PAGE_PREV

    BTN_SEQUENCE = (
        # 1 press to proceed to 12 words
        [BUTTON_ENTER]
        +
        # 1 press to proceed msg
        [BUTTON_ENTER]
        +
        # 1 presses per roll
        [BUTTON_ENTER for _ in range(D20_12W_MIN_ROLLS)]
        +
        # 1 press prev and 1 press on btn Go
        [BUTTON_PAGE_PREV, BUTTON_ENTER]
        + [
            BUTTON_ENTER,  # proceed with poor entropy,
            BUTTON_PAGE,  # move to Generate Words, while seeing rolls
            BUTTON_ENTER,  # generate words
            BUTTON_ENTER,  # 1 press to confirm SHA
        ]
    )
    MNEMONIC = "fun island vivid slide cable pyramid device tuition only essence thought gadget"

    ctx = create_ctx(mocker, BTN_SEQUENCE)
    dice_entropy = DiceEntropy(ctx, is_d20=True)
    entropy = dice_entropy.new_key()
    words = bip39.mnemonic_from_bytes(entropy)

    assert ctx.input.wait_for_button.call_count == len(BTN_SEQUENCE)
    assert words == MNEMONIC


def test_new_24w_from_d20(m5stickv, mocker):
    from krux.pages.new_mnemonic.dice_rolls import DiceEntropy, D20_24W_MIN_ROLLS
    from krux.input import BUTTON_ENTER, BUTTON_PAGE, BUTTON_PAGE_PREV

    BTN_SEQUENCE = (
        # 1 press change to 24 words and 1 press to proceed
        [BUTTON_PAGE, BUTTON_ENTER]
        +
        # 1 press to proceed msg
        [BUTTON_ENTER]
        +
        # 1 presses per roll
        [BUTTON_ENTER for _ in range(D20_24W_MIN_ROLLS)]
        +
        # 1 press prev and 1 press on btn Go
        [BUTTON_PAGE_PREV, BUTTON_ENTER]
        + [
            BUTTON_ENTER,  # proceed with poor entropy,
            BUTTON_PAGE,  # move to Generate Words, while seeing rolls
            BUTTON_ENTER,  # generate words
            BUTTON_ENTER,  # 1 press to confirm SHA
        ]
    )
    MNEMONIC = "source foster human mind myself floor breeze fire people exit horse erosion home barely imitate tunnel ribbon enroll mosquito pilot pumpkin ignore resemble pizza"

    ctx = create_ctx(mocker, BTN_SEQUENCE)
    dice_entropy = DiceEntropy(ctx, is_d20=True)
    entropy = dice_entropy.new_key()
    words = bip39.mnemonic_from_bytes(entropy)

    assert ctx.input.wait_for_button.call_count == len(BTN_SEQUENCE)
    assert words == MNEMONIC


def test_cancel_new_12w_from_d20(m5stickv, mocker):
    "Will test the Deletion button and the minimum roll on the roll screen"
    from krux.pages.new_mnemonic.dice_rolls import DiceEntropy, D20_12W_MIN_ROLLS
    from krux.input import BUTTON_ENTER, BUTTON_PAGE, BUTTON_PAGE_PREV

    BTN_SEQUENCE = (
        # 1 press to proceed to 12 words
        [BUTTON_ENTER]
        +
        # 1 press to proceed msg
        [BUTTON_ENTER]
        +
        # 1 presses per roll
        [BUTTON_ENTER for _ in range(D20_12W_MIN_ROLLS)]
        +
        # 3 press prev and 1 press on btn < (delete last roll)
        [BUTTON_PAGE_PREV, BUTTON_PAGE_PREV, BUTTON_PAGE_PREV, BUTTON_ENTER]
        +
        # 1 press prev and 1 press on btn Go
        [BUTTON_PAGE_PREV, BUTTON_ENTER]
        +
        # 1 press for msg not enough rolls!
        [BUTTON_ENTER]
        +
        # 2 press prev and 1 press on btn Esc
        [BUTTON_PAGE_PREV, BUTTON_PAGE_PREV, BUTTON_ENTER]
        +
        # 1 press to proceed confirm exit msg
        [BUTTON_ENTER]
    )

    ctx = create_ctx(mocker, BTN_SEQUENCE)
    dice_entropy = DiceEntropy(ctx, is_d20=True)
    dice_entropy.new_key()

    assert ctx.input.wait_for_button.call_count == len(BTN_SEQUENCE)


# Test low entropy warning
def test_low_shannon_entropy_warning(amigo, mocker):
    from krux.pages.new_mnemonic.dice_rolls import DiceEntropy, D6_12W_MIN_ROLLS
    from krux.input import BUTTON_ENTER, BUTTON_PAGE, BUTTON_PAGE_PREV, BUTTON_TOUCH
    from krux.themes import theme

    BTN_SEQUENCE = (
        # 1 press to proceed to 12 words
        [BUTTON_ENTER]
        +
        # 1 press to proceed msg
        [BUTTON_ENTER]
        +
        # 10 number 1 presses
        [BUTTON_TOUCH for _ in range(D6_12W_MIN_ROLLS)]
        +
        # 1 press prev and 1 press on btn Go
        [BUTTON_PAGE_PREV, BUTTON_ENTER]
        + [
            BUTTON_ENTER,  # proceed with poor entropy,
            BUTTON_PAGE,  # move to Generate Words, while seeing rolls
            BUTTON_ENTER,  # generate words
            BUTTON_ENTER,  # 1 press to confirm SHA
        ]
    )

    ctx = create_ctx(mocker, BTN_SEQUENCE, touch_seq=POOR_ROLLS_TOUCH_SEQUENCE)
    dice_entropy = DiceEntropy(ctx)
    dice_entropy.new_key()

    assert ctx.input.wait_for_button.call_count == len(BTN_SEQUENCE)

    # Assert ctx.display.draw_centered_text was called with poor entropy warning"
    call_message = mocker.call(
        "Estimated entropy: Poor!\nPattern detected!", theme.error_color
    )
    ctx.display.draw_centered_text.assert_has_calls([call_message])


# Test low entropy warning is not shown when Shannon's entropy is good
def test_good_rolls(amigo, mocker):
    from krux.pages.new_mnemonic.dice_rolls import DiceEntropy, D6_12W_MIN_ROLLS
    from krux.input import BUTTON_ENTER, BUTTON_PAGE, BUTTON_PAGE_PREV, BUTTON_TOUCH

    BTN_SEQUENCE = (
        # 1 press to proceed to 12 words
        [BUTTON_ENTER]
        +
        # 1 press to proceed msg
        [BUTTON_ENTER]
        +
        # 10 number 1 presses
        [BUTTON_TOUCH for _ in range(D6_12W_MIN_ROLLS)]
        +
        # 1 press prev and 1 press on btn Go
        [BUTTON_PAGE_PREV, BUTTON_ENTER]
        + [
            # No warning should be shown here
            BUTTON_PAGE,  # move to Generate Words, while seeing rolls
            BUTTON_ENTER,  # generate words
            BUTTON_ENTER,  # 1 press to confirm SHA
        ]
    )

    ctx = create_ctx(mocker, BTN_SEQUENCE, touch_seq=GOOD_ROLLS_SEQUENCE)
    dice_entropy = DiceEntropy(ctx)
    dice_entropy.new_key()

    assert ctx.input.wait_for_button.call_count == len(BTN_SEQUENCE)

    # Assert ctx.display.draw_centered_text was not called with poor entropy warning"
    call_message = mocker.call("Poor entropy detected. More rolls are recommended")
    for args in ctx.display.draw_hcentered_text.call_args_list:
        assert args != call_message


# Test stats for nerds
def test_stats_for_nerds(amigo, mocker):
    from krux.pages.new_mnemonic.dice_rolls import DiceEntropy, D6_12W_MIN_ROLLS
    from krux.input import BUTTON_ENTER, BUTTON_PAGE, BUTTON_PAGE_PREV, BUTTON_TOUCH

    BTN_SEQUENCE = (
        # 1 press to proceed to 12 words
        [BUTTON_ENTER]
        +
        # 1 press to proceed msg
        [BUTTON_ENTER]
        +
        # 10 number 1 presses
        [BUTTON_TOUCH for _ in range(D6_12W_MIN_ROLLS)]
        +
        # 1 press prev and 1 press on btn Go
        [BUTTON_PAGE_PREV, BUTTON_ENTER]
        + [
            BUTTON_ENTER,  # show stats for nerds
            BUTTON_ENTER,  # generate words
            BUTTON_ENTER,  # 1 press to confirm SHA
        ]
    )

    ctx = create_ctx(mocker, BTN_SEQUENCE, touch_seq=GOOD_ROLLS_SEQUENCE)
    dice_entropy = DiceEntropy(ctx)
    mocker.spy(dice_entropy, "stats_for_nerds")
    dice_entropy.new_key()

    assert ctx.input.wait_for_button.call_count == len(BTN_SEQUENCE)

    # Assert stats for nerds was called
    dice_entropy.stats_for_nerds.assert_called_once()
