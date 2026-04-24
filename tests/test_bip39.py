import secrets

import pytest
from embit import bip39
from embit.wordlists.bip39 import WORDLIST

from krux import bip39 as kruxbip39


def test_one_word_mnemonics():
    for numwords in (12, 15, 18, 21, 24):
        for word in WORDLIST:
            mnemonic = (word + " ") * (numwords - 1) + word
            assert kruxbip39.k_mnemonic_is_valid(mnemonic) == bip39.mnemonic_is_valid(
                mnemonic
            )


def test_edge_cases():
    cases = [16, 20, 24, 28, 32]  # 12w, 15w, 18w, 21w and 24w
    for case in cases:
        ALL_ZERO_BYTES = b"\x00" * case
        ALL_ONE_BYTES = b"\xff" * case

        assert (
            kruxbip39.k_mnemonic_bytes(bip39.mnemonic_from_bytes(ALL_ZERO_BYTES))
            == ALL_ZERO_BYTES
        )
        assert (
            kruxbip39.k_mnemonic_bytes(bip39.mnemonic_from_bytes(ALL_ONE_BYTES))
            == ALL_ONE_BYTES
        )

        int_val = max_val = int.from_bytes(ALL_ONE_BYTES, "big")
        while int_val > 0:
            int_val = int_val // 2
            b = int_val.to_bytes(case, "big")
            assert kruxbip39.k_mnemonic_bytes(bip39.mnemonic_from_bytes(b)) == b

            b = (max_val - int_val).to_bytes(case, "big")
            assert kruxbip39.k_mnemonic_bytes(bip39.mnemonic_from_bytes(b)) == b


def test_random_cases():
    for _ in range(10000):
        for size in (16, 20, 24, 28, 32):
            token_bytes = secrets.token_bytes(size)
            assert (
                kruxbip39.k_mnemonic_bytes(bip39.mnemonic_from_bytes(token_bytes))
                == token_bytes
            )


def test_random_cases_custom_wordlist():
    wordlist = tuple(kruxbip39.WORDLIST)
    for _ in range(200):
        for size in (16, 20, 24, 28, 32):
            token_bytes = secrets.token_bytes(size)
            assert (
                kruxbip39.k_mnemonic_bytes(
                    bip39.mnemonic_from_bytes(token_bytes), wordlist=wordlist
                )
                == token_bytes
            )


def test_random_cases_custom_wordlist_without_checksum():
    wordlist = tuple(kruxbip39.WORDLIST)
    for _ in range(200):
        for size in (16, 20, 24, 28, 32):
            token_bytes = secrets.token_bytes(size)
            assert (
                kruxbip39.k_mnemonic_bytes(
                    bip39.mnemonic_from_bytes(token_bytes),
                    wordlist=wordlist,
                    ignore_checksum=True,
                )
                == token_bytes
            )


def test_invalid_words():
    cases = [
        "not all twelve of these words are in the english bip39 wordslist",
        "not all fifteen of these words are in the english bip39 wordslist thirteen fourteen fifteen",
        "not all eighteen of these words are in the english bip39 wordslist thirteen fourteen fifteen sixteen seventeen eighteen",
        "not all twenty-one of these words are in the english bip39 wordslist thirteen fourteen fifteen sixteen seventeen eighteen nineteen twenty twenty-one",
        "not all twenty-four of these words are in the english bip39 wordslist thirteen fourteen fifteen sixteen seventeen eighteen nineteen twenty twenty-one twenty-two twenty-three twenty-four",
    ]
    for case in cases:
        with pytest.raises(ValueError, match=" is not in the dictionary"):
            kruxbip39.k_mnemonic_bytes(case)


def test_invalid_mnemonic_length():
    cases = [
        "nine is divisible by three but is not valid",
        "thirteen is between twelve and twenty-four but it is not divisible by three",
        "twenty-seven is divisible by three but it is not a mnemonic with valid length because bip39 support mnemonics of length twelve fifteen eighteen twenty-one and twenty-four only",
    ]
    for case in cases:
        with pytest.raises(ValueError, match="Invalid recovery phrase"):
            kruxbip39.k_mnemonic_bytes(case)


def test_mnemonic_with_formatting_issues():
    # Use a valid 12-word mnemonic for testing
    valid_mnemonic = "abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon about"

    # Verify the base mnemonic is valid
    assert kruxbip39.k_mnemonic_is_valid(valid_mnemonic) == True

    # Test cases with formatting issues that should be invalid
    invalid_cases = [
        # Leading spaces
        " " + valid_mnemonic,
        "  " + valid_mnemonic,
        # Trailing spaces
        valid_mnemonic + " ",
        valid_mnemonic + "  ",
        # Double spaces between words
        valid_mnemonic.replace(" ", "  ", 1),  # One double space
        valid_mnemonic.replace(" ", "  "),  # All double spaces
        # Newlines instead of spaces
        valid_mnemonic.replace(" ", "\n", 1),  # One newline
        valid_mnemonic.replace(" ", "\n"),  # All newlines
        # Commas instead of spaces
        valid_mnemonic.replace(" ", ",", 1),  # One comma
        valid_mnemonic.replace(" ", ","),  # All commas
        # Semicolons instead of spaces
        valid_mnemonic.replace(" ", ";", 1),  # One semicolon
        valid_mnemonic.replace(" ", ";"),  # All semicolons
        # Mixed formatting issues
        " " + valid_mnemonic.replace(" ", "  ", 3) + " ",
    ]

    for case in invalid_cases:
        assert (
            kruxbip39.k_mnemonic_is_valid(case) == False
        ), f"Krux: Expected invalid for: {repr(case)}"
        assert (
            bip39.mnemonic_is_valid(case) == False
        ), f"Embit: Expected invalid for: {repr(case)}"
