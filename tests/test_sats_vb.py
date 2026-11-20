def test_get_vbytes_p2sh_p2wsh(m5stickv):
    from krux.sats_vb import SatsVB
    from krux.key import P2SH_P2WSH, P2WSH

    policy = {"type": P2SH_P2WSH, "m": 2, "n": 3}

    # 2-of-3 P2SH-P2WSH input:
    # txid 32 + vout 4 + scriptSig length 1 + scriptSig 35 + sequence 4 = 76
    # witness: dummy 1 + 2 * (1 + 72) + script length 1 + script 105 = 253 WU
    # 76 + 253 / 4 = 139.25 vB
    # overhead: 4 + 1 + 1 + 4 + marker/flag 0.5 + 2 * 0.25 item counts = 11
    # 11 + 2 * 139.25 + P2WSH output 43 = 332.5
    assert SatsVB.get_vbytes(policy, {P2WSH: 1}, 2, 1) == 333


def test_get_size_of_script_length_element(m5stickv):
    from krux.sats_vb import SatsVB

    cases = [
        (1, 1),
        (75, 1),
        (76, 2),
        (0xFF, 2),
        (0x100, 3),
        (0xFFFF, 3),
        (0x10000, 5),
    ]
    for length, size in cases:
        assert SatsVB._get_size_of_script_length_element(length) == size


def test_get_size_of_var_int(m5stickv):
    from krux.sats_vb import SatsVB

    cases = [
        (0, 1),
        (252, 1),
        (253, 3),
        (0xFFFF, 3),
        (0x10000, 5),
        (0xFFFFFFFF, 5),
        (0x100000000, 9),
    ]
    for length, size in cases:
        assert SatsVB._get_size_of_var_int(length) == size
