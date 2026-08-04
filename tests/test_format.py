def test_format_btc(m5stickv):
    from krux.format import format_btc

    cases = [
        (0, "0.00 000 000"),
        (1, "0.00 000 001"),
        (10, "0.00 000 010"),
        (101, "0.00 000 101"),
        (1010, "0.00 001 010"),
        (10101, "0.00 010 101"),
        (101010, "0.00 101 010"),
        (1010101, "0.01 010 101"),
        (10101010, "0.10 101 010"),
        (101010101, "1.01 010 101"),
        (1010101010, "10.10 101 010"),
        (10101010101, "101.01 010 101"),
        (101010101010, "1 010.10 101 010"),
        (1010101010101, "10 101.01 010 101"),
        (10101010101010, "101 010.10 101 010"),
        (101010101010101, "1 010 101.01 010 101"),
        (2098989898989898, "20 989 898.98 989 898"),
    ]
    for case in cases:
        assert format_btc(case[0]) == case[1]


def test_format_btc_negative(m5stickv):
    """A negative amount is the positive one with a minus sign.

    Floor division and modulo round towards minus infinity, so splitting the
    amount before taking the sign out used to render -1000 as -1.99 999 000.
    """
    from krux.format import format_btc, THOUSANDS_SEPARATOR

    for amount in (1, 999, 1000, 100000000, 199999000, 2098989898989898):
        assert format_btc(-amount) == "-" + format_btc(amount)

    separator = THOUSANDS_SEPARATOR
    assert format_btc(-1000) == "-0.00" + separator + "001" + separator + "000"
