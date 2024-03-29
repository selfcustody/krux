def test_format_btc(m5stickv):
    from krux.format import format_btc

    cases = [
        (0, "0.00 000 000"),
        (1, "0.00 000 001"),
        (10, "0.00 000 010"),
        (101, "0.00 000 101"),
        (1010, "0.00 001 010"),
        (10101, "0.00 010 101"),
        (101010, "0.00 101 010"),
        (1010101, "0.01 010 101"),
        (10101010, "0.10 101 010"),
        (101010101, "1.01 010 101"),
        (1010101010, "10.10 101 010"),
        (10101010101, "101.01 010 101"),
        (101010101010, "1 010.10 101 010"),
        (1010101010101, "10 101.01 010 101"),
        (10101010101010, "101 010.10 101 010"),
        (101010101010101, "1 010 101.01 010 101"),
        (2098989898989898, "20 989 898.98 989 898"),
    ]
    for case in cases:
        assert format_btc(case[0]) == case[1]
