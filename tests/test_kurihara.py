import itertools
import pytest
from src.krux.kurihara import (
    KuriharaScheme,
    xor_bytes,
    is_prime,
    smallest_prime_gte,
    entropy_to_mnemonic,
    mnemonic_to_entropy,
    share_to_mnemonic,
    share_from_mnemonic,
)

# Profiles exercised: (n, m, num_bits)
PROFILES = [(2, 3, 128), (2, 5, 256), (3, 5, 256), (4, 5, 256), (2, 2, 128)]


def counter_randfunc(seed=0):
    """Deterministic, non-crypto byte source for reproducible test vectors."""
    state = [seed & 0xFF]

    def randfunc(nbytes):
        out = bytearray(nbytes)
        for i in range(nbytes):
            state[0] = (state[0] * 1103515245 + 12345) & 0xFF
            out[i] = state[0]
        return bytes(out)

    return randfunc


def test_xor_bytes():
    assert xor_bytes(b"\x0f", b"\xf0") == b"\xff"
    assert xor_bytes(b"\xff", b"\xff", b"\xff") == b"\xff"
    assert xor_bytes(b"\xaa\x55", b"\x55\xaa") == b"\xff\xff"


def test_is_prime():
    assert not is_prime(1)
    assert is_prime(2)
    assert is_prime(3)
    assert not is_prime(4)
    assert is_prime(7)
    assert not is_prime(9)
    assert not is_prime(25)


def test_smallest_prime_gte():
    assert smallest_prime_gte(1) == 2
    assert smallest_prime_gte(2) == 2
    assert smallest_prime_gte(3) == 3
    assert smallest_prime_gte(4) == 5
    assert smallest_prime_gte(6) == 7
    assert smallest_prime_gte(9) == 11


def test_rejects_bad_params():
    with pytest.raises(ValueError):
        KuriharaScheme(1, 3, 128)  # n < 2
    with pytest.raises(ValueError):
        KuriharaScheme(4, 3, 128)  # n > m
    with pytest.raises(ValueError):
        KuriharaScheme(2, 3, 100)  # non-BIP39 entropy size
    with pytest.raises(ValueError):
        KuriharaScheme(3, 6, 256)  # prime-1 = 6 does not divide 256


def test_share_size_equals_secret():
    for n, m, num_bits in PROFILES:
        sch = KuriharaScheme(n, m, num_bits)
        secret = counter_randfunc(1)(num_bits // 8)
        shares = sch.generate(secret, counter_randfunc(2))
        assert len(shares) == m
        for share in shares:
            assert len(share.to_bytes()) * 8 == num_bits


def test_generate_rejects_wrong_secret_length():
    sch = KuriharaScheme(3, 5, 256)
    with pytest.raises(ValueError):
        sch.generate(b"\x00" * 31, counter_randfunc())


def test_all_coalitions_reconstruct():
    for n, m, num_bits in PROFILES:
        sch = KuriharaScheme(n, m, num_bits)
        secret = counter_randfunc(7)(num_bits // 8)
        shares = sch.generate(secret, counter_randfunc(8))
        for combo in itertools.combinations(range(m), n):
            picked = [shares[i] for i in combo]
            assert sch.reconstruct(picked) == secret


def test_oversized_coalition_reconstructs():
    sch = KuriharaScheme(3, 5, 256)
    secret = counter_randfunc(3)(32)
    shares = sch.generate(secret, counter_randfunc(4))
    assert sch.reconstruct(shares) == secret


def test_subthreshold_rejected():
    sch = KuriharaScheme(3, 5, 256)
    secret = counter_randfunc(5)(32)
    shares = sch.generate(secret, counter_randfunc(6))
    with pytest.raises(ValueError):
        sch.reconstruct(shares[:2])


def test_mixed_instances_rejected():
    sch = KuriharaScheme(3, 5, 256)
    secret = counter_randfunc(0)(32)
    coalition_a = sch.generate(secret, counter_randfunc(10))
    coalition_b = sch.generate(secret, counter_randfunc(20))
    with pytest.raises(ValueError):
        sch.reconstruct([coalition_a[0], coalition_a[1], coalition_b[2]])


def test_duplicate_shares_rejected():
    sch = KuriharaScheme(2, 3, 128)
    secret = counter_randfunc(0)(16)
    shares = sch.generate(secret, counter_randfunc(1))
    # Two copies of one share are rank-deficient: a fragment stays undetermined.
    with pytest.raises(ValueError):
        sch.reconstruct([shares[0], shares[0]])


def test_regenerate_lost_share_bit_identical():
    for n, m, num_bits in PROFILES:
        if m <= n:
            continue
        sch = KuriharaScheme(n, m, num_bits)
        secret = counter_randfunc(42)(num_bits // 8)
        shares = sch.generate(secret, counter_randfunc(43))
        coalition = shares[:n]
        for lost in range(n, m):
            regen = sch.reconstruct_lost(coalition, lost + 1)
            assert regen.pieces == shares[lost].pieces


def test_regenerated_share_usable():
    sch = KuriharaScheme(3, 5, 256)
    secret = counter_randfunc(99)(32)
    shares = sch.generate(secret, counter_randfunc(100))
    regen = sch.reconstruct_lost(shares[:3], 5)
    assert sch.reconstruct([shares[0], shares[3], regen]) == secret


def test_reconstruct_lost_out_of_range():
    sch = KuriharaScheme(3, 5, 256)
    secret = counter_randfunc(0)(32)
    shares = sch.generate(secret, counter_randfunc(1))
    with pytest.raises(ValueError):
        sch.reconstruct_lost(shares[:3], 0)
    with pytest.raises(ValueError):
        sch.reconstruct_lost(shares[:3], 6)


def test_reconstruct_lost_present_share_rejected():
    sch = KuriharaScheme(3, 5, 256)
    secret = counter_randfunc(0)(32)
    shares = sch.generate(secret, counter_randfunc(1))
    with pytest.raises(ValueError):
        sch.reconstruct_lost(shares[:3], 1)


def test_each_share_is_valid_mnemonic():
    from embit import bip39

    sch = KuriharaScheme(3, 5, 256)
    secret = counter_randfunc(8)(32)
    shares = sch.generate(secret, counter_randfunc(9))
    for share in shares:
        mnemonic = share_to_mnemonic(share)
        assert bip39.mnemonic_is_valid(mnemonic)
        assert len(mnemonic.split()) == 24


def test_secret_roundtrips_through_mnemonics():
    n, m, num_bits = 3, 5, 256
    sch = KuriharaScheme(n, m, num_bits)
    secret = counter_randfunc(11)(32)
    shares = sch.generate(secret, counter_randfunc(12))
    instance = shares[0].meta["instance"]
    rebuilt = [
        share_from_mnemonic(s.part_id, share_to_mnemonic(s), n, m, num_bits, instance)
        for s in shares[:n]
    ]
    assert sch.reconstruct(rebuilt) == secret


def test_mnemonic_entropy_roundtrip():
    entropy = bytes(range(16))
    mnemonic = entropy_to_mnemonic(entropy)
    assert mnemonic_to_entropy(mnemonic) == entropy


def test_share_from_mnemonic_size_mismatch():
    sch = KuriharaScheme(2, 3, 128)
    secret = counter_randfunc(0)(16)
    shares = sch.generate(secret, counter_randfunc(1))
    mnemonic = share_to_mnemonic(shares[0])  # 12 words / 128 bits
    with pytest.raises(ValueError):
        share_from_mnemonic(1, mnemonic, 3, 5, 256)  # claims 256 bits


def test_known_answer():
    sch = KuriharaScheme(2, 3, 128)
    secret = bytes(range(16))
    shares = sch.generate(secret, counter_randfunc(0))
    assert sch.reconstruct([shares[0], shares[1]]) == secret
    assert sch.reconstruct([shares[0], shares[2]]) == secret
    assert sch.reconstruct([shares[1], shares[2]]) == secret
    blobs = [s.to_bytes() for s in shares]
    assert blobs[0] != blobs[1]
    assert blobs[0] != secret
