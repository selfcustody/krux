from krux import bip39 as kruxbip39
from embit import bip39
from embit.wordlists.bip39 import WORDLIST
import secrets


def test_one_word_mnemonics():
    for word in WORDLIST:
        mnemonic = (word + " ") * 12
        assert kruxbip39.mnemonic_is_valid(mnemonic) == bip39.mnemonic_is_valid(
            mnemonic
        )

    for word in WORDLIST:
        mnemonic = (word + " ") * 24
        assert kruxbip39.mnemonic_is_valid(mnemonic) == bip39.mnemonic_is_valid(
            mnemonic
        )


def test_edge_cases():
    cases = [8, 16]  # 12w and 24w
    for case in cases:
        ALL_ZERO_BYTES = int(0).to_bytes(16, "big")
        ALL_ONE_BYTES = int.from_bytes(bytearray([255] * case)).to_bytes(16, "big")

        assert (
            kruxbip39.mnemonic_to_bytes(bip39.mnemonic_from_bytes(ALL_ZERO_BYTES))
            == ALL_ZERO_BYTES
        )
        assert (
            kruxbip39.mnemonic_to_bytes(bip39.mnemonic_from_bytes(ALL_ONE_BYTES))
            == ALL_ONE_BYTES
        )

        int_val = max_val = int.from_bytes(ALL_ONE_BYTES)
        while int_val > 0:
            int_val = int_val // 2
            b = int_val.to_bytes(16, "big")
            assert kruxbip39.mnemonic_to_bytes(bip39.mnemonic_from_bytes(b)) == b

            b = (max_val - int_val).to_bytes(16, "big")
            assert kruxbip39.mnemonic_to_bytes(bip39.mnemonic_from_bytes(b)) == b


def test_random_cases():
    for _ in range(20000):
        token12w = secrets.token_bytes(16)
        token24w = secrets.token_bytes(32)

        assert (
            kruxbip39.mnemonic_to_bytes(bip39.mnemonic_from_bytes(token12w)) == token12w
        )
        assert (
            kruxbip39.mnemonic_to_bytes(bip39.mnemonic_from_bytes(token24w)) == token24w
        )
