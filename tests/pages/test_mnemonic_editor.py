from . import create_ctx

TEST_12_WORD_MNEMONIC = (
    "olympic term tissue route sense program under choose bean emerge velvet absurd"
)
TEST_24_WORD_MNEMONIC = "brush badge sing still venue panther kitchen please help panel bundle excess sign couch stove increase human once effort candy goat top tiny major"
MNEMONICS = [TEST_12_WORD_MNEMONIC, TEST_24_WORD_MNEMONIC]


def test_confirm_given_words(mocker, all_devices):
    from krux.pages.mnemonic_editor import MnemonicEditor
    from krux.input import BUTTON_ENTER, BUTTON_PAGE_PREV
    import board

    for mnemonic in MNEMONICS:
        btn_sequence = [BUTTON_ENTER]
        # if using m5stickv, add BUTTON_ENTER to btn_sequence
        if board.config["type"] == "m5stickv" and len(mnemonic.split()) == 24:
            btn_sequence.append(BUTTON_ENTER)
        ctx = create_ctx(mocker, btn_sequence)
        mnemonic_editor = MnemonicEditor(ctx, mnemonic)
        edited_mnemonic = mnemonic_editor.edit()
        assert edited_mnemonic == mnemonic
        assert ctx.input.wait_for_button.call_count == len(btn_sequence)
