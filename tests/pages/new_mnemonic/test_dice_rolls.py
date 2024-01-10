from ..test_login import create_ctx
from embit import bip39



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
    MNEMONIC = "diet glad hat rural panther lawsuit act drop gallery urge where fit"

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
    MNEMONIC = "wheel erase puppy pistol chapter accuse carpet drop quote final attend near scrap satisfy limit style crunch person south inspire lunch meadow enact tattoo"

    ctx = create_ctx(mocker, BTN_SEQUENCE)
    dice_entropy = DiceEntropy(ctx)
    entropy = dice_entropy.new_key()
    words = bip39.mnemonic_from_bytes(entropy)

    assert ctx.input.wait_for_button.call_count == len(BTN_SEQUENCE)
    assert words == MNEMONIC



def test_new_12w_from_d6_on_amigo_device(amigo_tft, mocker):
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
    MNEMONIC = "diet glad hat rural panther lawsuit act drop gallery urge where fit"

    ctx = create_ctx(mocker, BTN_SEQUENCE)
    dice_entropy = DiceEntropy(ctx)
    entropy = dice_entropy.new_key()
    words = bip39.mnemonic_from_bytes(entropy)

    assert ctx.input.wait_for_button.call_count == len(BTN_SEQUENCE)
    assert words == MNEMONIC


def test_new_24w_from_d6_on_amigo_device(amigo_tft, mocker):
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
    MNEMONIC = "wheel erase puppy pistol chapter accuse carpet drop quote final attend near scrap satisfy limit style crunch person south inspire lunch meadow enact tattoo"

    ctx = create_ctx(mocker, BTN_SEQUENCE)
    dice_entropy = DiceEntropy(ctx, )
    entropy = dice_entropy.new_key()
    words = bip39.mnemonic_from_bytes(entropy)

    assert ctx.input.wait_for_button.call_count == len(BTN_SEQUENCE)
    assert words == MNEMONIC


def test_cancel_new_12w_from_d6_on_amigo_device(amigo_tft, mocker):
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
    MNEMONIC = (
        "erupt remain ride bleak year cabin orange sure ghost gospel husband oppose"
    )

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
    MNEMONIC = "fun island vivid slide cable pyramid device tuition only essence thought gain silk jealous eternal anger response virus couple faculty ozone test key vocal"

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