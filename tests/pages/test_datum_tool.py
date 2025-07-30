import pytest
from . import create_ctx


def test_urobj_to_data(m5stickv, mocker):
    """Test that urobj_to_data returns flattened data from UR objects."""
    from krux.pages.datum_tool import urobj_to_data
    from ur.ur import UR
    from urtypes.crypto.psbt import PSBT
    from urtypes.bytes import Bytes

    UR_BIP39_WORDS_BYTES = b"\xa2\x01\x8cfshieldegroupeerodeeawakedlockgsausagedcasheglaredwavedcreweflameeglove\x02ben"
    MNEMONIC = "shield group erode awake lock sausage cash glare wave crew flame glove"
    P2PKH_PSBT_BYTES = b'psbt\xff\x01\x00\xa4\x02\x00\x00\x00\x03\xae\xe25\xaf(\x9a\xc9\xee\xc23\xca"\x15\xbf?\xf4\xc1\xcaxAP\xd6\x0f[\x94kA\x87\x8b\x15\x04,\x00\x00\x00\x00\x00\xfd\xff\xff\xffT\xc9\x91i\xc4ZIg Z!\xd6)\xbf+z\x161\xc4uoS \xf0\x9d\x96\xcf#\xdc\xdbc\xa0\x00\x00\x00\x00\x00\xfd\xff\xff\xff\x04\x1eVt\x8d\x80H\x1f\x89k\x07T(\xca\xaf\x91\x1e"\x1a2\xef\xa5_\\s\xf9\x8b\xc2J\xa0\xc8\x11\x00\x00\x00\x00\x00\xfd\xff\xff\xff\x01\xe8\x03\x00\x00\x00\x00\x00\x00\x16\x00\x14\xae\xcd\x1e\xdc>\xffe\xaa \x9d\x02\x15\xe7=p\x90]\xc1hlZ\x0f+\x00O\x01\x045\x87\xcf\x03\x06\xb07\xf6\x80\x00\x00\x00k"\xc5\x12;\xa1\n\xde\xafK\xfc\xbbE\xd1\xa0-\x82\x8f%\xbf\x86F\x95z\x98\xd0b\x87\xc4\xe2\xb8P\x02\x8bB\xcdGv7l\x82y\x1bIAU\x15\x1fV\xc2\xd7\xb4q\xe0\xc7\xa5&\xa7\xce`\xdd\x87.8g\x10s\xc5\xda\n,\x00\x00\x80\x01\x00\x00\x80\x00\x00\x00\x80\x00\x01\x00~\x02\x00\x00\x00\x02\x9a\x9b\xe1\xca)\x10\\\x97t<\x0f\xd1\xeey\xc0\xe6\r"\x8aa\xc8\xec\xbft\xf9\xe7\xcf\xfa\x01\x19\x0c{\x02\x00\x00\x00\x00\xfd\xff\xff\xff\x9a\x9b\xe1\xca)\x10\\\x97t<\x0f\xd1\xeey\xc0\xe6\r"\x8aa\xc8\xec\xbft\xf9\xe7\xcf\xfa\x01\x19\x0c{\x01\x00\x00\x00\x00\xfd\xff\xff\xff\x01@\x07\x00\x00\x00\x00\x00\x00\x19v\xa9\x14:-AE\xa4\xf0\x98R;>\x81\'\xf1\xda\x87\xcf\xc5[\x8ey\x88\xacZ\x0f+\x00\x01\x03\x04\x01\x00\x00\x00"\x06\x02\xa7E\x13\x95sSi\xf2\xec\xdf\xc8)\xc0\xf7t\xe8\x8e\xf10=\xfe[/\x04\xdb\xaa\xb3\nS]\xfd\xd6\x18s\xc5\xda\n,\x00\x00\x80\x01\x00\x00\x80\x00\x00\x00\x80\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00U\x02\x00\x00\x00\x01\x873 i\xd7\x11\xa7\xcd*`\xd5\x84\x1c8\n,U\xe8\xa2\n\xdd\xdaV\xa2\x9c\x00\x84e\xef\xf6[\xa2\x01\x00\x00\x00\x00\xff\xff\xff\xff\x01\x00\x00\x00\x00\x00\x00\x00\x00\x19v\xa9\x14:-AE\xa4\xf0\x98R;>\x81\'\xf1\xda\x87\xcf\xc5[\x8ey\x88\xac\x00\x00\x00\x00\x01\x03\x04\x01\x00\x00\x00"\x06\x02\xa7E\x13\x95sSi\xf2\xec\xdf\xc8)\xc0\xf7t\xe8\x8e\xf10=\xfe[/\x04\xdb\xaa\xb3\nS]\xfd\xd6\x18s\xc5\xda\n,\x00\x00\x80\x01\x00\x00\x80\x00\x00\x00\x80\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00U\x02\x00\x00\x00\x01\x05j\xc0\xa7"\x1f\xe5\x82x\xc9\xa7h\xd0\x1a!\xe6\xb6GJ\x01\x9a\xf6\xe7?\x08\xc8R\xe6\x86|\xad\xa5\x00\x00\x00\x00\x00\xff\xff\xff\xff\x01\x00\x00\x00\x00\x00\x00\x00\x00\x19v\xa9\x14:-AE\xa4\xf0\x98R;>\x81\'\xf1\xda\x87\xcf\xc5[\x8ey\x88\xac\x00\x00\x00\x00\x01\x03\x04\x01\x00\x00\x00"\x06\x02\xa7E\x13\x95sSi\xf2\xec\xdf\xc8)\xc0\xf7t\xe8\x8e\xf10=\xfe[/\x04\xdb\xaa\xb3\nS]\xfd\xd6\x18s\xc5\xda\n,\x00\x00\x80\x01\x00\x00\x80\x00\x00\x00\x80\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
    UR_OUTPUT_MULTISIG_DESCR_BYTES = b'\xd9\x01\x91\xd9\x01\x96\xa2\x01\x01\x02\x82\xd9\x01/\xa4\x03X!\x03\xcb\xca\xa9\xc9\x8c\x87z&\x97}\x00\x82\\\x95j#\x8e\x8d\xdd\xfb\xd3"\xcc\xe4\xf7K\x0b[\xd6\xac\xe4\xa7\x04X `I\x9f\x80\x1b\x89m\x83\x17\x9aCt\xae\xb7\x82*\xae\xac\xea\xa0\xdb\x1f\x85\xee>\x90LM\xef\xbd\x96\x89\x06\xd9\x010\xa2\x01\x80\x03\x00\x07\xd9\x010\xa1\x01\x86\x01\xf4\x00\xf4\x80\xf4\xd9\x01/\xa4\x03X!\x02\xfc\x9eZ\xf0\xac\x8d\x9b<\xec\xfe*\x88\x8e!\x17\xba=\x08\x9d\x85\x85\x88l\x9c\x82kk"\xa9\x8d\x12\xea\x04X \xf0\x90\x9a\xff\xaa~\xe7\xab\xe5\xddN\x10\x05\x98\xd4\xdcS\xcdp\x9dZ\\,\xac@\xe7A/#/|\x9c\x06\xd9\x010\xa2\x01\x82\x00\xf4\x02\x1a\xbd\x16\xbe\xe5\x07\xd9\x010\xa1\x01\x86\x00\xf4\x00\xf4\x80\xf4'
    MULTISIG_DESCR = "wsh(multi(1,xpub661MyMwAqRbcFW31YEwpkMuc5THy2PSt5bDMsktWQcFF8syAmRUapSCGu8ED9W6oDMSgv6Zz8idoc4a6mr8BDzTJY47LJhkJ8UB7WEGuduB/1/0/*,xpub69H7F5d8KSRgmmdJg2KhpAK8SR3DjMwAdkxj3ZuxV27CprR9LgpeyGmXUbC6wb7ERfvrnKZjXoUmmDznezpbZb7ap6r1D3tgFxHmwMkQTPH/0/0/*))#t2zpj2eu"

    cases = [
        {
            "control": UR("crypto-bip39", UR_BIP39_WORDS_BYTES),
            "expected": MNEMONIC.split(" "),
        },
        {
            "control": UR("crypto-output", UR_OUTPUT_MULTISIG_DESCR_BYTES),
            "expected": MULTISIG_DESCR,
        },
        {
            "control": UR("crypto-psbt", PSBT(P2PKH_PSBT_BYTES).to_cbor()),
            "expected": P2PKH_PSBT_BYTES,
        },
        {
            "control": UR("bytes", Bytes(MULTISIG_DESCR.encode()).to_cbor()),
            "expected": MULTISIG_DESCR.encode(),
        },
        {
            "control": UR("bytes", Bytes(P2PKH_PSBT_BYTES).to_cbor()),
            "expected": P2PKH_PSBT_BYTES,
        },
    ]

    for case in cases:
        result = urobj_to_data(case["control"])
        assert result == case["expected"]


def test_convert_encoding(m5stickv, mocker):
    """Test that conversions work and can be reversed else return None."""
    from krux.pages.datum_tool import convert_encoding

    cases = [
        {  # bytes can be converted to/from hex, HEX, base32, base43, and base64
            "control": bytes([x for x in range(0, 256, 15)]),
            "hex": "000f1e2d3c4b5a69788796a5b4c3d2e1f0ff",
            "HEX": "000F1E2D3C4B5A69788796A5B4C3D2E1F0FF",
            32: "AAHR4LJ4JNNGS6EHS2S3JQ6S4HYP6",
            43: "039M/12TG9MDYO5F+*31RY*BFT",
            64: "AA8eLTxLWml4h5altMPS4fD/",
            "utf8": None,
        },
        {  # for hex: as long as as string is all one case, can be shifted and back
            "control": "0123456789abcdef",
            "shift_case": "0123456789ABCDEF",
        },
        {  # when a conversion doesn't make sense or cannot be undone:
            # instead of raising an error, convert_encoding returns None
            "control": "This is a CamelCase string.",
            "shift_case": None,
            "hex": None,
            "HEX": None,
            32: None,
            43: None,
            64: None,
            "utf8": b"This is a CamelCase string.",
        },
    ]

    for case in cases:
        control = case["control"]
        for conv in [x for x in case.keys() if x != "control"]:
            result = convert_encoding(control, conv)
            assert result == case[conv]
            if result is not None:
                # ensure that converting back gives the original value
                assert convert_encoding(result, conv) == control


def test_identify_datum(m5stickv, mocker):
    """Test that identify_datum can identify various datum types."""
    from krux.pages.datum_tool import identify_datum

    cases = {
        "PSBT": [
            b'psbt\xff\x01\x00\xa4\x02\x00\x00\x00\x03\xae\xe25\xaf(\x9a\xc9\xee\xc23\xca"\x15\xbf?\xf4\xc1\xcaxAP\xd6\x0f[\x94kA\x87\x8b\x15\x04,\x00\x00\x00\x00\x00\xfd\xff\xff\xffT\xc9\x91i\xc4ZIg Z!\xd6)\xbf+z\x161\xc4uoS \xf0\x9d\x96\xcf#\xdc\xdbc\xa0\x00\x00\x00\x00\x00\xfd\xff\xff\xff\x04\x1eVt\x8d\x80H\x1f\x89k\x07T(\xca\xaf\x91\x1e"\x1a2\xef\xa5_\\s\xf9\x8b\xc2J\xa0\xc8\x11\x00\x00\x00\x00\x00\xfd\xff\xff\xff\x01\xe8\x03\x00\x00\x00\x00\x00\x00\x16\x00\x14\xae\xcd\x1e\xdc>\xffe\xaa \x9d\x02\x15\xe7=p\x90]\xc1hlZ\x0f+\x00O\x01\x045\x87\xcf\x03\x06\xb07\xf6\x80\x00\x00\x00k"\xc5\x12;\xa1\n\xde\xafK\xfc\xbbE\xd1\xa0-\x82\x8f%\xbf\x86F\x95z\x98\xd0b\x87\xc4\xe2\xb8P\x02\x8bB\xcdGv7l\x82y\x1bIAU\x15\x1fV\xc2\xd7\xb4q\xe0\xc7\xa5&\xa7\xce`\xdd\x87.8g\x10s\xc5\xda\n,\x00\x00\x80\x01\x00\x00\x80\x00\x00\x00\x80\x00\x01\x00~\x02\x00\x00\x00\x02\x9a\x9b\xe1\xca)\x10\\\x97t<\x0f\xd1\xeey\xc0\xe6\r"\x8aa\xc8\xec\xbft\xf9\xe7\xcf\xfa\x01\x19\x0c{\x02\x00\x00\x00\x00\xfd\xff\xff\xff\x9a\x9b\xe1\xca)\x10\\\x97t<\x0f\xd1\xeey\xc0\xe6\r"\x8aa\xc8\xec\xbft\xf9\xe7\xcf\xfa\x01\x19\x0c{\x01\x00\x00\x00\x00\xfd\xff\xff\xff\x01@\x07\x00\x00\x00\x00\x00\x00\x19v\xa9\x14:-AE\xa4\xf0\x98R;>\x81\'\xf1\xda\x87\xcf\xc5[\x8ey\x88\xacZ\x0f+\x00\x01\x03\x04\x01\x00\x00\x00"\x06\x02\xa7E\x13\x95sSi\xf2\xec\xdf\xc8)\xc0\xf7t\xe8\x8e\xf10=\xfe[/\x04\xdb\xaa\xb3\nS]\xfd\xd6\x18s\xc5\xda\n,\x00\x00\x80\x01\x00\x00\x80\x00\x00\x00\x80\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00U\x02\x00\x00\x00\x01\x873 i\xd7\x11\xa7\xcd*`\xd5\x84\x1c8\n,U\xe8\xa2\n\xdd\xdaV\xa2\x9c\x00\x84e\xef\xf6[\xa2\x01\x00\x00\x00\x00\xff\xff\xff\xff\x01\x00\x00\x00\x00\x00\x00\x00\x00\x19v\xa9\x14:-AE\xa4\xf0\x98R;>\x81\'\xf1\xda\x87\xcf\xc5[\x8ey\x88\xac\x00\x00\x00\x00\x01\x03\x04\x01\x00\x00\x00"\x06\x02\xa7E\x13\x95sSi\xf2\xec\xdf\xc8)\xc0\xf7t\xe8\x8e\xf10=\xfe[/\x04\xdb\xaa\xb3\nS]\xfd\xd6\x18s\xc5\xda\n,\x00\x00\x80\x01\x00\x00\x80\x00\x00\x00\x80\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00U\x02\x00\x00\x00\x01\x05j\xc0\xa7"\x1f\xe5\x82x\xc9\xa7h\xd0\x1a!\xe6\xb6GJ\x01\x9a\xf6\xe7?\x08\xc8R\xe6\x86|\xad\xa5\x00\x00\x00\x00\x00\xff\xff\xff\xff\x01\x00\x00\x00\x00\x00\x00\x00\x00\x19v\xa9\x14:-AE\xa4\xf0\x98R;>\x81\'\xf1\xda\x87\xcf\xc5[\x8ey\x88\xac\x00\x00\x00\x00\x01\x03\x04\x01\x00\x00\x00"\x06\x02\xa7E\x13\x95sSi\xf2\xec\xdf\xc8)\xc0\xf7t\xe8\x8e\xf10=\xfe[/\x04\xdb\xaa\xb3\nS]\xfd\xd6\x18s\xc5\xda\n,\x00\x00\x80\x01\x00\x00\x80\x00\x00\x00\x80\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00',
        ],
        "DESC": [
            "pkh([55f8fc5d/44h/0h/1h]xpub6C1dUaopHgps6X75i61KaJEDm4qkFeqjhm4by1ebvpgAsKDaEhGLgNX88bvuWPm4rSVe7GsYvQLDAXXLnxNsAbd3VwRihgM3q1kEkixBAbE)",
            "sh(wpkh([55f8fc5d/49h/0h/1h]xpub6Ca1JGnSFNZ7jjwturEn944t8B9kBgiTKtmr3maTbryEyDyYY9xycVSQaFxeUPjbHyX7MUvLUbdoDVK7XZ7Fib9We4BQRRk8bZjW2UPRjHV))",
            "wpkh([55f8fc5d/84h/0h/1h]xpub6DPMTPxGMqdu43FvwYdC6eHCPJWckCkx1rLJ1HEG7259GyWQD5P17WB2oowP9SpQdC8ogrmXfwfoazvf6Te8svtxWh4UTwTqyRdG5G54FxW)",
            "wsh(multi(1,xpub661MyMwAqRbcFW31YEwpkMuc5THy2PSt5bDMsktWQcFF8syAmRUapSCGu8ED9W6oDMSgv6Zz8idoc4a6mr8BDzTJY47LJhkJ8UB7WEGuduB/1/0/*,xpub69H7F5d8KSRgmmdJg2KhpAK8SR3DjMwAdkxj3ZuxV27CprR9LgpeyGmXUbC6wb7ERfvrnKZjXoUmmDznezpbZb7ap6r1D3tgFxHmwMkQTPH/0/0/*))#t2zpj2eu",
            "tr([55f8fc5d/86h/0h/1h]xpub6CNGwJbVG9sQsJjtwLiemRFAfvDafL8zRthnHWNQbRz1PwAm28T1v5hLmJhFft71oEDCbA3xHemnScW5VWheP1BxXNVnoYboyw6t4wuKu5q)",
        ],
        "ADDR": [
            "bc1pkusdqe839xltdn5jk62rv0cx6c4nrrw3hr8rmf3478tnn88qs2ls4g77cl",
            "bc1qncuaqah98hypkxnpp465mqw7srjgm67s70gkzcs693kv9zp3dv8qa5w8fj",
        ],
        "XPUB": [
            "[55f8fc5d/44h/0h/1h]xpub6C1dUaopHgps6X75i61KaJEDm4qkFeqjhm4by1ebvpgAsKDaEhGLgNX88bvuWPm4rSVe7GsYvQLDAXXLnxNsAbd3VwRihgM3q1kEkixBAbE",
            "[55f8fc5d/49h/0h/1h]xpub6Ca1JGnSFNZ7jjwturEn944t8B9kBgiTKtmr3maTbryEyDyYY9xycVSQaFxeUPjbHyX7MUvLUbdoDVK7XZ7Fib9We4BQRRk8bZjW2UPRjHV",
            "[55f8fc5d/49h/0h/1h]ypub6XQGbwTMQ46bb391kD2QM9APJ9JC8JhxF1J4qAULysM82Knmnp8YEZ6YbTvEUJPWhcdv6xWtwFzM6mvgFFXGWpq7WPsq1LZcsHo9R97uuE4",
            "[55f8fc5d/84h/0h/1h]zpub6s3t4jJ6fCirkdeAcGCSWpUCjEoWdSjwr5Nja522s2puPB8riPi8MdVJrDrZ9G8FSUNRBoxebGNuMa9nXrUAUQGAFNTKdm6pWskYrMahu1i",
        ],
    }
    for datum_type in cases:
        for case in cases[datum_type]:
            result = identify_datum(case)
            assert result == datum_type


def test_detect_encodings_strict_on_input(m5stickv, mocker):
    """Test that detect_encodings raises TypeError on non-string inputs."""
    from krux.pages.datum_tool import detect_encodings

    for input_type in (
        b"bytes is not str",
        ["list of str is not str"],
        ("tuple of str is not str",),
    ):
        with pytest.raises(TypeError, match="detect_encodings\\(\\) expected str"):
            detect_encodings(input_type)


def test_detect_encodings(mocker, m5stickv):
    """Test that detect_encodings can identify various string encodings."""
    from krux.pages.datum_tool import detect_encodings
    from krux.baseconv import base_encode
    from embit.bech32 import bech32_encode, convertbits
    from binascii import hexlify

    bytestring = bytes([i for i in range(256)])

    bech32_hrp = "hrp"
    bech32_data = convertbits(bytestring[:50], 8, 5)
    tests = {
        "hex": hexlify(bytestring).decode(),
        "HEX": hexlify(bytestring).decode().upper(),
        "bech32": bech32_encode(1, bech32_hrp, bech32_data),
        "BECH32": bech32_encode(1, bech32_hrp, bech32_data).upper(),
        "bech32m": bech32_encode(2, bech32_hrp, bech32_data),
        "BECH32M": bech32_encode(2, bech32_hrp, bech32_data).upper(),
        32: base_encode(bytestring, 32),
        43: base_encode(bytestring, 43),
        58: base_encode(bytestring, 58),
        64: base_encode(bytestring, 64),
        "latin-1": bytestring.decode("latin-1"),
        "utf8": bytestring[:127].decode()
        + bytestring[:127].decode("latin-1").encode().decode(),
    }

    for encoding, input_str in tests.items():
        print(encoding, input_str)
        result = detect_encodings(input_str)
        assert isinstance(result, list)
        assert encoding in result


def test_detect_encodings_no_verify(mocker, m5stickv):
    """detect_encodings can run quicker w/ verify=False, but caller cannot trust it."""
    from krux.pages.datum_tool import detect_encodings
    from krux.baseconv import base_decode
    from binascii import unhexlify, a2b_base64

    def get_range(min_chr, max_chr):
        return range(ord(min_chr), ord(max_chr) + 1)

    # "hex" starts at "0", finishes at "f" (invalid: >= ":" and <= "`")
    string = "".join(chr(i) for i in get_range("0", "f")) + "f"
    assert "hex" in detect_encodings(string, verify=False)
    assert "hex" not in detect_encodings(string)

    # "HEX" starts at "0", finishes at "F" (invalid: >= ":" and <= "@")
    string = "".join(chr(i) for i in get_range("0", "F")) + "F"
    assert "HEX" in detect_encodings(string, verify=False)
    assert "HEX" not in detect_encodings(string)

    # no unverified checks for bech32 encodings, but just to hit exception branches
    # string = "qpzry9x8gf2tvdw0s3jn54khce6mua7l"
    # assert "bech32" not in detect_encodings(string)
    # assert "BECH32" not in detect_encodings(string.upper())

    # base 32 starts at "2", finishes at "Z" (invalid: >= "8" and <= "@")
    string = "".join(chr(i) for i in get_range("2", "Z"))
    assert 32 in detect_encodings(string, verify=False)
    assert 32 not in detect_encodings(string)

    # base 43 starts at "$", finishes at "Z" (invalid: "%&'(),/", >= ":" and <= "@")
    string = "".join(chr(i) for i in get_range("$", "Z"))
    assert 43 in detect_encodings(string, verify=False)
    assert 43 not in detect_encodings(string)

    # base 58 starts at "1", finishes at "z"
    # (invalid: >= ":" and <= "@", >= "[" and <= "`", "I", "O", "l")
    string = "".join(chr(i) for i in get_range("1", "z"))
    assert 58 in detect_encodings(string, verify=False)
    assert 58 not in detect_encodings(string)

    # base 64 starts at "0", finishes at "z" (invalid: >= ":" and <= "<", >= ">" and <= "@")
    string = "".join(chr(i) for i in get_range("0", "z")) + "=="
    assert 64 in detect_encodings(string, verify=False)
    assert 64 not in detect_encodings(string)

    # no test for ascii, checking max(ord) <= 127 will always be correct
    # no test for latin-1, it doesn't exist in uPython, but range will be correct
    # no test for utf-8, yet; but some byte-combos are not allowed in utf-8
