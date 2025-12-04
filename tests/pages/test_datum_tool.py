import pytest
from unittest.mock import patch
from . import create_ctx


@pytest.fixture
def mock_file_operations(mocker):
    mocker.patch(
        "os.listdir",
        new=mocker.MagicMock(return_value=["somefile", "otherfile"]),
    )
    mocker.patch(
        "krux.sd_card.SDHandler.dir_exists",
        mocker.MagicMock(side_effect=[True, False]),
    )
    mocker.patch(
        "krux.sd_card.SDHandler.file_exists",
        mocker.MagicMock(side_effect=[True, True]),
    )
    mocker.patch(
        "builtins.open", mocker.mock_open(read_data=b"These are file contents\n")
    )


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
        {"control": UR("crypto-bip39", UR_BIP39_WORDS_BYTES), "expected": MNEMONIC},
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

    # some bytes never appear in utf8, convert_encoding returns None
    non_utf8 = bytes([0xC0, 0xC1, 0xFE, 0xFF])
    assert convert_encoding(non_utf8, "utf8") == None


def test_identify_datum(m5stickv, mocker):
    """Test that identify_datum can identify various datum types."""
    from krux.pages.datum_tool import identify_datum

    # TODO: more samples
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
            "18cBEMRxXHqzWWCxZNtU91F5sbUNKhL5PX",
            "3FNchDWmk41bWhsBWjeBh1DaTvLW4nckk3",
            "bc1q0s2c09z42zjdndf8a6m8y7qu42sc8pmdgrsd4p",
            "bc1pkusdqe839xltdn5jk62rv0cx6c4nrrw3hr8rmf3478tnn88qs2ls4g77cl",
            "bc1qncuaqah98hypkxnpp465mqw7srjgm67s70gkzcs693kv9zp3dv8qa5w8fj",
            "mjJHCvVzKHT5ehH4TFm1BteUkqCuoND9Ny",
            "tb1qdpkupesz09wawwl03qmgq2d0hs3cnzkuyaj3n0",
            "tb1pruektj90gg8nysa7yuk07w7ucwlywrf4p02lq3sz49f05xd00djscyt2fw",
        ],
        "XPUB": [
            "[55f8fc5d/44h/0h/1h]xpub6C1dUaopHgps6X75i61KaJEDm4qkFeqjhm4by1ebvpgAsKDaEhGLgNX88bvuWPm4rSVe7GsYvQLDAXXLnxNsAbd3VwRihgM3q1kEkixBAbE",
            "xpub6C1dUaopHgps6X75i61KaJEDm4qkFeqjhm4by1ebvpgAsKDaEhGLgNX88bvuWPm4rSVe7GsYvQLDAXXLnxNsAbd3VwRihgM3q1kEkixBAbE",
            "[55f8fc5d/49h/0h/1h]xpub6Ca1JGnSFNZ7jjwturEn944t8B9kBgiTKtmr3maTbryEyDyYY9xycVSQaFxeUPjbHyX7MUvLUbdoDVK7XZ7Fib9We4BQRRk8bZjW2UPRjHV",
            "xpub6Ca1JGnSFNZ7jjwturEn944t8B9kBgiTKtmr3maTbryEyDyYY9xycVSQaFxeUPjbHyX7MUvLUbdoDVK7XZ7Fib9We4BQRRk8bZjW2UPRjHV",
            "[55f8fc5d/49h/0h/1h]ypub6XQGbwTMQ46bb391kD2QM9APJ9JC8JhxF1J4qAULysM82Knmnp8YEZ6YbTvEUJPWhcdv6xWtwFzM6mvgFFXGWpq7WPsq1LZcsHo9R97uuE4",
            "ypub6XQGbwTMQ46bb391kD2QM9APJ9JC8JhxF1J4qAULysM82Knmnp8YEZ6YbTvEUJPWhcdv6xWtwFzM6mvgFFXGWpq7WPsq1LZcsHo9R97uuE4",
            "[55f8fc5d/84h/0h/1h]zpub6s3t4jJ6fCirkdeAcGCSWpUCjEoWdSjwr5Nja522s2puPB8riPi8MdVJrDrZ9G8FSUNRBoxebGNuMa9nXrUAUQGAFNTKdm6pWskYrMahu1i",
            "zpub6s3t4jJ6fCirkdeAcGCSWpUCjEoWdSjwr5Nja522s2puPB8riPi8MdVJrDrZ9G8FSUNRBoxebGNuMa9nXrUAUQGAFNTKdm6pWskYrMahu1i",
        ],
    }
    for datum_type in cases:
        for case in cases[datum_type]:
            result = identify_datum(case)
            assert result == datum_type

    # TODO: false-positive cases and tests


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

    # no unverified checks for bech32 encodings
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

    # latin-1 and also utf8 (uPython has no latin-1)
    string = "Ceci est une ligne de latin1 en français. Esta é uma linha de latin1 em português"
    assert detect_encodings(string, verify=False) == ["latin-1", "utf8"]
    assert detect_encodings(string) == ["latin-1", "utf8"]

    # utf8 is assumed for all strings
    string = """This is a line of ascii text\nCeci est une ligne d'unicode en français\nEsta é uma linha de unicode em português
これは日本語のUnicodeの行です\n这是一行简体中文的unicode\nĐây là một dòng mã unicode trong tiếng Việt\nЭто строка юникода на русском языке.
이것은 한국어의 유니코드 줄입니다"""
    assert detect_encodings(string, verify=False) == ["utf8"]
    assert detect_encodings(string) == ["utf8"]


def test_datumtoolmenu_init_abort(m5stickv, mocker):
    """Into DatumToolMenu then abort via Back"""
    from krux.pages.datum_tool import DatumToolMenu
    from krux.input import BUTTON_ENTER, BUTTON_PAGE, BUTTON_PAGE_PREV

    # abort by moving backwards to Back
    BTN_SEQUENCE = (
        BUTTON_PAGE,  # to Text Entry
        BUTTON_PAGE,  # to Read File
        BUTTON_PAGE,  # to Back
        BUTTON_ENTER,  # go Back
    )
    ctx = create_ctx(mocker, BTN_SEQUENCE)
    DatumToolMenu(ctx).run()
    assert ctx.input.wait_for_button.call_count == len(BTN_SEQUENCE)

    # abort by moving forwards to Back
    BTN_SEQUENCE = (
        BUTTON_PAGE_PREV,  # to Back
        BUTTON_ENTER,  # go Back
    )
    ctx = create_ctx(mocker, BTN_SEQUENCE)
    DatumToolMenu(ctx).run()
    assert ctx.input.wait_for_button.call_count == len(BTN_SEQUENCE)


def test_datumtoolmenu_scan_qr_abort(m5stickv, mocker):
    """Into DatumToolMenu and Scan QR"""
    from krux.pages.datum_tool import DatumToolMenu
    from krux.input import BUTTON_ENTER, BUTTON_PAGE, BUTTON_PAGE_PREV

    # interrupt scan
    BTN_SEQUENCE = (
        BUTTON_ENTER,  # go Scan QR
        BUTTON_PAGE_PREV,  # interrupt
        BUTTON_PAGE,  # to Text Entry
        BUTTON_PAGE,  # to Read File
        BUTTON_PAGE,  # to Back
        BUTTON_ENTER,  # go Back
    )
    ctx = create_ctx(mocker, BTN_SEQUENCE)
    page = DatumToolMenu(ctx).run()
    assert ctx.input.wait_for_button.call_count == len(BTN_SEQUENCE)

    from krux.pages.qr_capture import QRCodeCapture

    # failed scan
    mocker.patch.object(QRCodeCapture, "qr_capture_loop", new=lambda self: (None, None))
    BTN_SEQUENCE = (
        BUTTON_ENTER,  # go Scan QR
        BUTTON_PAGE,  # to Text Entry
        BUTTON_PAGE,  # to Read File
        BUTTON_PAGE,  # to Back
        BUTTON_ENTER,  # go Back
    )
    ctx = create_ctx(mocker, BTN_SEQUENCE)
    page = DatumToolMenu(ctx).run()
    assert ctx.input.wait_for_button.call_count == len(BTN_SEQUENCE)

    from ur.ur import UR
    from urtypes import Bytes

    # scan UR-QR (for coverage), then back out of datum tool
    MULTISIG_DESCR = "wsh(multi(1,xpub661MyMwAqRbcFW31YEwpkMuc5THy2PSt5bDMsktWQcFF8syAmRUapSCGu8ED9W6oDMSgv6Zz8idoc4a6mr8BDzTJY47LJhkJ8UB7WEGuduB/1/0/*,xpub69H7F5d8KSRgmmdJg2KhpAK8SR3DjMwAdkxj3ZuxV27CprR9LgpeyGmXUbC6wb7ERfvrnKZjXoUmmDznezpbZb7ap6r1D3tgFxHmwMkQTPH/0/0/*))#t2zpj2eu"
    ur_obj = UR("bytes", Bytes(MULTISIG_DESCR.encode()).to_cbor())
    mocker.patch.object(QRCodeCapture, "qr_capture_loop", new=lambda self: (ur_obj, 2))
    BTN_SEQUENCE = (
        BUTTON_ENTER,  # go Scan QR
        BUTTON_PAGE_PREV,  # to Back
        BUTTON_ENTER,  # go Back
        BUTTON_PAGE,  # to Text Entry
        BUTTON_PAGE,  # to Read File
        BUTTON_PAGE,  # to Back
        BUTTON_ENTER,  # go Back
    )
    ctx = create_ctx(mocker, BTN_SEQUENCE)
    page = DatumToolMenu(ctx).run()
    assert ctx.input.wait_for_button.call_count == len(BTN_SEQUENCE)


def test_datumtoolmenu_text_entry_abort(m5stickv, mocker):
    """Into DatumToolMenu and text_entry"""
    from krux.pages.datum_tool import DatumToolMenu
    from krux.input import BUTTON_ENTER, BUTTON_PAGE, BUTTON_PAGE_PREV

    # abort w/o adding any text
    BTN_SEQUENCE = (
        BUTTON_PAGE,  # to Text Entry
        BUTTON_ENTER,  # go Text Entry
        BUTTON_PAGE_PREV,  # to Go
        BUTTON_PAGE_PREV,  # to ESC
        BUTTON_ENTER,  # go ESC
        BUTTON_PAGE,  # to Read File
        BUTTON_PAGE,  # to Back
        BUTTON_ENTER,  # go Back
    )
    ctx = create_ctx(mocker, BTN_SEQUENCE)
    page = DatumToolMenu(ctx).run()
    assert ctx.input.wait_for_button.call_count == len(BTN_SEQUENCE)

    # add text but then abort out of Datum Tool
    BTN_SEQUENCE = (
        BUTTON_PAGE,  # to Text Entry
        BUTTON_ENTER,  # go Text Entry
        BUTTON_ENTER,  # letter "a"
        BUTTON_PAGE_PREV,  # to Go
        BUTTON_ENTER,  # go Go
        BUTTON_ENTER,  # confirm
        BUTTON_PAGE_PREV,  # to Back
        BUTTON_ENTER,  # go Back
        BUTTON_PAGE,  # to Read File
        BUTTON_PAGE,  # to Back
        BUTTON_ENTER,  # go Back
    )
    ctx = create_ctx(mocker, BTN_SEQUENCE)
    page = DatumToolMenu(ctx).run()
    assert ctx.input.wait_for_button.call_count == len(BTN_SEQUENCE)


def test_datumtoolmenu_read_file_no_sd_card(m5stickv, mocker):
    """Into DatumToolMenu and read_file w/o sdcard"""
    from krux.pages.datum_tool import DatumToolMenu
    from krux.input import BUTTON_ENTER, BUTTON_PAGE, BUTTON_PAGE_PREV

    BTN_SEQUENCE = (
        BUTTON_PAGE,  # to Data Entry
        BUTTON_PAGE,  # to Read File
        BUTTON_ENTER,  # go Read File (no sdcard error flashed)
        BUTTON_PAGE,  # to Back
        BUTTON_ENTER,  # go Back
    )
    ctx = create_ctx(mocker, BTN_SEQUENCE)
    page = DatumToolMenu(ctx).run()
    assert ctx.input.wait_for_button.call_count == len(BTN_SEQUENCE)


def test_datumtoolmenu_avoid_read_file_abort(m5stickv, mocker, mock_file_operations):
    """Into DatumToolMenu and read_file w/ sdcard but abort w/o reading file"""
    from krux.pages.datum_tool import DatumToolMenu
    from krux.input import BUTTON_ENTER, BUTTON_PAGE, BUTTON_PAGE_PREV

    BTN_SEQUENCE = (
        BUTTON_PAGE,  # to Data Entry
        BUTTON_PAGE,  # to Read File
        BUTTON_ENTER,  # go Read File
        BUTTON_PAGE_PREV,  # to Back
        BUTTON_ENTER,  # go Back
        BUTTON_PAGE,  # to Back
        BUTTON_ENTER,  # go Back
    )
    ctx = create_ctx(mocker, BTN_SEQUENCE)
    page = DatumToolMenu(ctx).run()
    assert ctx.input.wait_for_button.call_count == len(BTN_SEQUENCE)


def test_datumtoolmenu_read_file_abort(m5stickv, mocker, mock_file_operations):
    """Into DatumToolMenu, read_file but abort once in DatumTool"""
    from krux.pages.datum_tool import DatumToolMenu
    from krux.input import BUTTON_ENTER, BUTTON_PAGE, BUTTON_PAGE_PREV

    BTN_SEQUENCE = (
        BUTTON_PAGE,  # to Data Entry
        BUTTON_PAGE,  # to Read File
        BUTTON_ENTER,  # go Read File
        BUTTON_PAGE,  # to next entry
        BUTTON_ENTER,  # select file
        BUTTON_ENTER,  # confirm load
        BUTTON_PAGE_PREV,  # to Back
        BUTTON_ENTER,  # go Back
        BUTTON_PAGE,  # to Back
        BUTTON_ENTER,  # go Back
    )
    ctx = create_ctx(mocker, BTN_SEQUENCE)
    page = DatumToolMenu(ctx).run()
    assert ctx.input.wait_for_button.call_count == len(BTN_SEQUENCE)


def test_datumtool_view_qr(m5stickv, mocker):
    from krux.pages.datum_tool import DatumTool
    from krux.input import BUTTON_ENTER, BUTTON_PAGE, BUTTON_PAGE_PREV

    text_sm = "small qr text"
    text_bg = "much longer text" * 100
    bytes_psbt = b'psbt\xff\x01\x00\xa4\x02\x00\x00\x00\x03\xae\xe25\xaf(\x9a\xc9\xee\xc23\xca"\x15\xbf?\xf4\xc1\xcaxAP\xd6\x0f[\x94kA\x87\x8b\x15\x04,\x00\x00\x00\x00\x00\xfd\xff\xff\xffT\xc9\x91i\xc4ZIg Z!\xd6)\xbf+z\x161\xc4uoS \xf0\x9d\x96\xcf#\xdc\xdbc\xa0\x00\x00\x00\x00\x00\xfd\xff\xff\xff\x04\x1eVt\x8d\x80H\x1f\x89k\x07T(\xca\xaf\x91\x1e"\x1a2\xef\xa5_\\s\xf9\x8b\xc2J\xa0\xc8\x11\x00\x00\x00\x00\x00\xfd\xff\xff\xff\x01\xe8\x03\x00\x00\x00\x00\x00\x00\x16\x00\x14\xae\xcd\x1e\xdc>\xffe\xaa \x9d\x02\x15\xe7=p\x90]\xc1hlZ\x0f+\x00O\x01\x045\x87\xcf\x03\x06\xb07\xf6\x80\x00\x00\x00k"\xc5\x12;\xa1\n\xde\xafK\xfc\xbbE\xd1\xa0-\x82\x8f%\xbf\x86F\x95z\x98\xd0b\x87\xc4\xe2\xb8P\x02\x8bB\xcdGv7l\x82y\x1bIAU\x15\x1fV\xc2\xd7\xb4q\xe0\xc7\xa5&\xa7\xce`\xdd\x87.8g\x10s\xc5\xda\n,\x00\x00\x80\x01\x00\x00\x80\x00\x00\x00\x80\x00\x01\x00~\x02\x00\x00\x00\x02\x9a\x9b\xe1\xca)\x10\\\x97t<\x0f\xd1\xeey\xc0\xe6\r"\x8aa\xc8\xec\xbft\xf9\xe7\xcf\xfa\x01\x19\x0c{\x02\x00\x00\x00\x00\xfd\xff\xff\xff\x9a\x9b\xe1\xca)\x10\\\x97t<\x0f\xd1\xeey\xc0\xe6\r"\x8aa\xc8\xec\xbft\xf9\xe7\xcf\xfa\x01\x19\x0c{\x01\x00\x00\x00\x00\xfd\xff\xff\xff\x01@\x07\x00\x00\x00\x00\x00\x00\x19v\xa9\x14:-AE\xa4\xf0\x98R;>\x81\'\xf1\xda\x87\xcf\xc5[\x8ey\x88\xacZ\x0f+\x00\x01\x03\x04\x01\x00\x00\x00"\x06\x02\xa7E\x13\x95sSi\xf2\xec\xdf\xc8)\xc0\xf7t\xe8\x8e\xf10=\xfe[/\x04\xdb\xaa\xb3\nS]\xfd\xd6\x18s\xc5\xda\n,\x00\x00\x80\x01\x00\x00\x80\x00\x00\x00\x80\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00U\x02\x00\x00\x00\x01\x873 i\xd7\x11\xa7\xcd*`\xd5\x84\x1c8\n,U\xe8\xa2\n\xdd\xdaV\xa2\x9c\x00\x84e\xef\xf6[\xa2\x01\x00\x00\x00\x00\xff\xff\xff\xff\x01\x00\x00\x00\x00\x00\x00\x00\x00\x19v\xa9\x14:-AE\xa4\xf0\x98R;>\x81\'\xf1\xda\x87\xcf\xc5[\x8ey\x88\xac\x00\x00\x00\x00\x01\x03\x04\x01\x00\x00\x00"\x06\x02\xa7E\x13\x95sSi\xf2\xec\xdf\xc8)\xc0\xf7t\xe8\x8e\xf10=\xfe[/\x04\xdb\xaa\xb3\nS]\xfd\xd6\x18s\xc5\xda\n,\x00\x00\x80\x01\x00\x00\x80\x00\x00\x00\x80\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00U\x02\x00\x00\x00\x01\x05j\xc0\xa7"\x1f\xe5\x82x\xc9\xa7h\xd0\x1a!\xe6\xb6GJ\x01\x9a\xf6\xe7?\x08\xc8R\xe6\x86|\xad\xa5\x00\x00\x00\x00\x00\xff\xff\xff\xff\x01\x00\x00\x00\x00\x00\x00\x00\x00\x19v\xa9\x14:-AE\xa4\xf0\x98R;>\x81\'\xf1\xda\x87\xcf\xc5[\x8ey\x88\xac\x00\x00\x00\x00\x01\x03\x04\x01\x00\x00\x00"\x06\x02\xa7E\x13\x95sSi\xf2\xec\xdf\xc8)\xc0\xf7t\xe8\x8e\xf10=\xfe[/\x04\xdb\xaa\xb3\nS]\xfd\xd6\x18s\xc5\xda\n,\x00\x00\x80\x01\x00\x00\x80\x00\x00\x00\x80\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
    text_desc = "wsh(multi(1,xpub661MyMwAqRbcFW31YEwpkMuc5THy2PSt5bDMsktWQcFF8syAmRUapSCGu8ED9W6oDMSgv6Zz8idoc4a6mr8BDzTJY47LJhkJ8UB7WEGuduB/1/0/*,xpub69H7F5d8KSRgmmdJg2KhpAK8SR3DjMwAdkxj3ZuxV27CprR9LgpeyGmXUbC6wb7ERfvrnKZjXoUmmDznezpbZb7ap6r1D3tgFxHmwMkQTPH/0/0/*))#t2zpj2eu"
    latin1 = "Ceci est une ligne de latin1 en français. Esta é uma linha de latin1 em português"
    unicode = """This is a line of ascii text\nCeci est une ligne d'unicode en français\nEsta é uma linha de unicode em português
これは日本語のUnicodeの行です\n这是一行简体中文的unicode\nĐây là một dòng mã unicode trong tiếng Việt\nЭто строка юникода на русском языке.
이것은 한국어의 유니코드 줄입니다"""

    BTN_SEQUENCE = (
        BUTTON_PAGE_PREV,  # skip updating qr title
        BUTTON_ENTER,  # leave QR view
        BUTTON_PAGE_PREV,  # to Back
        BUTTON_ENTER,  # go Back
    )

    # with short text
    ctx = create_ctx(mocker, BTN_SEQUENCE)
    page = DatumTool(ctx)
    page.contents = text_sm
    page.title = "QR contents"
    page.view_qr()
    assert ctx.input.wait_for_button.call_count == len(BTN_SEQUENCE)

    # with short bytestring
    ctx = create_ctx(mocker, BTN_SEQUENCE)
    page = DatumTool(ctx)
    page.contents = text_sm.encode()
    page.title = "QR contents"
    page.view_qr()
    assert ctx.input.wait_for_button.call_count == len(BTN_SEQUENCE)

    # with short text while updating qr label
    BTN_SEQUENCE = (
        BUTTON_ENTER,  # confirm updating qr title
        BUTTON_ENTER,  # add "a"
        BUTTON_PAGE_PREV,  # to Go
        BUTTON_ENTER,  # go Go
        BUTTON_PAGE_PREV,  # to skip updating qr title
        BUTTON_ENTER,  # leave QR view
        BUTTON_PAGE_PREV,  # to Back
        BUTTON_ENTER,  # go Back
    )
    ctx = create_ctx(mocker, BTN_SEQUENCE)
    page = DatumTool(ctx)
    page.contents = text_sm
    page.title = "QR contents"
    page.view_qr()
    assert ctx.input.wait_for_button.call_count == len(BTN_SEQUENCE)

    # with longer text for big static qr
    BTN_SEQUENCE = (
        BUTTON_ENTER,  # go Static
        BUTTON_ENTER,  # leave QR view
    )
    ctx = create_ctx(mocker, BTN_SEQUENCE)
    page = DatumTool(ctx)
    page.contents = text_bg
    page.title = "QR contents"
    page.view_qr()
    assert ctx.input.wait_for_button.call_count == len(BTN_SEQUENCE)

    # with longer text for big pMofN animated qr
    BTN_SEQUENCE = (
        BUTTON_PAGE,  # to pMofN
        BUTTON_ENTER,  # go pMofN
        BUTTON_ENTER,  # leave QR view
    )
    ctx = create_ctx(mocker, BTN_SEQUENCE)
    page = DatumTool(ctx)
    page.contents = text_bg
    page.title = "QR contents"
    page.view_qr()
    assert ctx.input.wait_for_button.call_count == len(BTN_SEQUENCE)

    # with longer text for UR-bytes
    BTN_SEQUENCE = (
        BUTTON_PAGE_PREV,  # to UR-bytes
        BUTTON_ENTER,  # go UR-bytes
        BUTTON_ENTER,  # leave QR view
    )
    ctx = create_ctx(mocker, BTN_SEQUENCE)
    page = DatumTool(ctx)
    page.contents = bytes_psbt
    page.title = "QR contents"
    page.datum = "PSBT"
    page.view_qr()
    assert ctx.input.wait_for_button.call_count == len(BTN_SEQUENCE)

    # with longer text for big UR-psbt
    BTN_SEQUENCE = (
        BUTTON_PAGE_PREV,  # to UR-bytes
        BUTTON_PAGE_PREV,  # to UR-psbt
        BUTTON_ENTER,  # go UR-psbt
        BUTTON_ENTER,  # leave QR view
    )
    ctx = create_ctx(mocker, BTN_SEQUENCE)
    page = DatumTool(ctx)
    page.contents = bytes_psbt
    page.title = "QR contents"
    page.datum = "PSBT"
    page.view_qr()
    assert ctx.input.wait_for_button.call_count == len(BTN_SEQUENCE)

    # with longer text for big BBQr
    BTN_SEQUENCE = (
        BUTTON_PAGE_PREV,  # to UR-bytes
        BUTTON_PAGE_PREV,  # to UR-psbt
        BUTTON_PAGE_PREV,  # to BBQr
        BUTTON_ENTER,  # go BBQr
        BUTTON_ENTER,  # leave QR view
    )
    ctx = create_ctx(mocker, BTN_SEQUENCE)
    page = DatumTool(ctx)
    page.contents = bytes_psbt
    page.title = "QR contents"
    page.datum = "PSBT"
    page.view_qr()
    assert ctx.input.wait_for_button.call_count == len(BTN_SEQUENCE)

    # with short latin-1 as a string works
    BTN_SEQUENCE = (
        BUTTON_PAGE_PREV,  # deny label update
        BUTTON_ENTER,  # dismiss QR
        BUTTON_PAGE_PREV,  # to Back
        BUTTON_ENTER,  # leave QR view
    )
    ctx = create_ctx(mocker, BTN_SEQUENCE)
    page = DatumTool(ctx)
    page.contents = latin1
    page.title = "QR contents"
    page.datum = None
    page.view_qr()
    assert ctx.input.wait_for_button.call_count == len(BTN_SEQUENCE)

    # with unicode as a string doesn't work
    ctx = create_ctx(mocker, [BUTTON_ENTER])
    page = DatumTool(ctx)
    page.contents = unicode
    page.title = "QR contents"
    page.datum = None
    page.view_qr()
    assert ctx.input.wait_for_button.call_count == 1
    ctx.display.flash_text.assert_called_with(
        "Failed encoding (('Static', (0,))), try as bytes. 'str' object has no attribute 'decode'",
        248,
        2000,
        highlight_prefix="",
    )
    print(ctx.display.method_calls)

    # but can work if encoding unicode string as utf-8 bytes
    BTN_SEQUENCE = (
        BUTTON_PAGE_PREV,  # deny label update
        BUTTON_ENTER,  # dismiss QR
        BUTTON_PAGE_PREV,  # to Back
        BUTTON_ENTER,  # leave QR view
    )
    ctx = create_ctx(mocker, BTN_SEQUENCE)
    page = DatumTool(ctx)
    page.contents = unicode.encode()
    page.title = "QR contents"
    page.datum = None
    page.view_qr()
    assert ctx.input.wait_for_button.call_count == len(BTN_SEQUENCE)


def test_datumtool_esc_on_save_sd(m5stickv, mocker, mock_file_operations):
    """With DatumTool already initialized, test .save_sd()"""
    from krux.pages.datum_tool import DatumTool
    from krux.input import BUTTON_PAGE_PREV, BUTTON_ENTER

    BTN_SEQ = [BUTTON_PAGE_PREV, BUTTON_PAGE_PREV, BUTTON_ENTER, BUTTON_ENTER]
    ctx = create_ctx(mocker, BTN_SEQ)
    page = DatumTool(ctx)
    page.contents = "String contents destined for file"
    page.title = "text contents"
    page.save_sd()
    assert ctx.input.wait_for_button.call_count == len(BTN_SEQ)


def test_datumtool__info_box(m5stickv, mocker):
    """With DatumTool already initialized, test ._info_box()"""
    from krux.pages.datum_tool import DatumTool

    # call with text
    ctx = create_ctx(mocker, [])
    page = DatumTool(ctx)
    page.contents = "Loaded string contents in DatumTool"
    page.title = "Text"
    page.datum = ""
    page.about_prefix = "t:"
    page.about = page.about_prefix + " about"
    page._info_box()
    assert ctx.input.wait_for_button.call_count == 0
    ctx.display.draw_hcentered_text.assert_has_calls(
        [
            mocker.call(
                'Text\nt: about\n"Loaded string …',
                info_box=True,
                highlight_prefix=page.about_prefix,
            )
        ]
    )

    # call with bytes
    ctx = create_ctx(mocker, [])
    page = DatumTool(ctx)
    page.contents = b"\xde\xad\xbe\xef"
    page.title = "Bytes"
    page.datum = ""
    page.about_prefix = "t:"
    page.about = page.about_prefix + " about"
    page._info_box()
    assert ctx.input.wait_for_button.call_count == 0
    ctx.display.draw_hcentered_text.assert_has_calls(
        [
            mocker.call(
                "Bytes\nt: about\n0xdeadbeef",
                info_box=True,
                highlight_prefix=page.about_prefix,
            )
        ]
    )


def test_datumtool__show_contents(m5stickv, mocker):
    """With DatumTool already initialized, test ._show_contents()"""
    from krux.pages.datum_tool import DatumTool
    from krux.input import BUTTON_ENTER, BUTTON_PAGE, BUTTON_PAGE_PREV

    # call with text
    ctx = create_ctx(mocker, [BUTTON_PAGE, BUTTON_PAGE_PREV, BUTTON_ENTER])
    page = DatumTool(ctx)
    page.contents = "Loaded string contents in DatumTool"
    page.title = "Text"
    page.datum = ""
    page.about_prefix = "t:"
    page.about = page.about_prefix + " about"
    page._show_contents()
    assert ctx.input.wait_for_button.call_count == 3
    ctx.display.draw_hcentered_text.assert_called_with(
        "Text\nt: about p.1", info_box=True, highlight_prefix=page.about_prefix
    )

    # call with bytes
    ctx = create_ctx(mocker, [BUTTON_ENTER])
    page = DatumTool(ctx)
    page.contents = b"\xde\xad\xbe\xef"
    page.title = "Bytes"
    page.datum = ""
    page.about_prefix = "t:"
    page.about = page.about_prefix + " about"
    page._show_contents()
    assert ctx.input.wait_for_button.call_count == 1
    ctx.display.draw_hcentered_text.assert_called_with(
        "Bytes\nt: about p.1", info_box=True, highlight_prefix=page.about_prefix
    )


def test_datumtool__analyze_contents(m5stickv, mocker):
    """With DatumTool already initialized, test ._analyze_contents()"""
    from krux.pages.datum_tool import DatumTool

    # call with short text
    ctx = create_ctx(mocker, [])
    page = DatumTool(ctx)
    page.contents = "simple text"
    page._analyze_contents()
    assert ctx.input.wait_for_button.call_count == 0
    assert page.about == "text: 11 chars"
    assert page.title == None
    assert page.sensitive == False
    assert page.oneline_viewable == True

    # call with longer text
    ctx = create_ctx(mocker, [])
    page = DatumTool(ctx)
    page.contents = "Loaded string contents in DatumTool"
    page._analyze_contents()
    assert ctx.input.wait_for_button.call_count == 0
    assert page.about == "text: 35 chars"
    assert page.title == None
    assert page.sensitive == False
    assert page.oneline_viewable == False

    # call with bytes
    ctx = create_ctx(mocker, [])
    page = DatumTool(ctx)
    page.contents = b"\xde\xad\xbe\xef"
    page._analyze_contents()
    assert ctx.input.wait_for_button.call_count == 0
    assert page.about == "binary: 4 bytes"
    assert page.encodings == []
    assert page.title == None
    assert page.sensitive == False
    assert page.oneline_viewable == True

    # call with sensitive bytes (bip39 compact SeedQR)
    ctx = create_ctx(mocker, [])
    page = DatumTool(ctx)
    page.contents = bytes([x * 16 for x in range(16)])
    page._analyze_contents()
    assert ctx.input.wait_for_button.call_count == 0
    assert page.about == "binary: 16 bytes"
    assert page.encodings == []
    assert page.title == None
    assert page.sensitive == True
    assert page.oneline_viewable == False

    # call with sensitive words (bip39 mnemonic)
    ctx = create_ctx(mocker, [])
    page = DatumTool(ctx)
    page.contents = " ".join(["zoo"] * 12)
    page._analyze_contents()
    assert ctx.input.wait_for_button.call_count == 0
    assert page.about == "text: 47 chars"
    assert page.encodings == ["ascii", "utf8"]
    assert page.title == None
    assert page.sensitive == True
    assert page.oneline_viewable == False

    # call with sensitive digits (bip39 standard SeedQR)
    ctx = create_ctx(mocker, [])
    page = DatumTool(ctx)
    page.contents = "".join(["{:04d}".format(x * 128) for x in range(12)])
    page._analyze_contents()
    assert ctx.input.wait_for_button.call_count == 0
    assert page.about == "text: 48 chars"
    assert page.encodings == ["HEX", 43, 64, "ascii", "utf8"]
    assert page.title == None
    assert page.sensitive == True
    assert page.oneline_viewable == False

    # call with bytes encoded from utf8 string
    ctx = create_ctx(mocker, [])
    page = DatumTool(ctx)
    page.contents = "octets décodables utf8".encode()
    page._analyze_contents()
    assert ctx.input.wait_for_button.call_count == 0
    assert page.about == "binary: 23 bytes"
    assert page.encodings == ["latin-1_via_utf8?"]
    assert page.title == None
    assert page.sensitive == False
    assert page.oneline_viewable == False


def test_datumtool__decrypt_as_kef_envelope(m5stickv, mocker):
    """With DatumTool already initialized, test ._decrypt_as_kef_envelope()"""
    from krux.pages.datum_tool import DatumTool
    from krux.input import BUTTON_ENTER, BUTTON_PAGE_PREV

    non_kef = bytes([x for x in range(128)])
    kef_a_hello_world = (
        b'\x07key="a"\x05\x01\xa7Z\xe8Z\x99k\xee\xa9\x13N5\xc9\x96\xc14M\xcdK\x15Qi'
    )
    kef_a_hello_world_w_0xdeadbeef_label = b"\x04\xde\xad\xbe\xef\x05\x00\x00\x01\xfa\x8f\xda\x13\x8b\xc8\x12J\xc32\xe7\x11\x93\xfb\x8b\xd4`\xd0\xf5"

    # call with non-kef bytes
    ctx = create_ctx(mocker, [])
    page = DatumTool(ctx)
    page.contents = non_kef
    page._decrypt_as_kef_envelope()
    assert ctx.input.wait_for_button.call_count == 0

    # now with kef encrypted envelopes
    BTN_SEQUENCE = (
        BUTTON_ENTER,  # confirm Decrypt
        BUTTON_ENTER,  # go Enter Key
        BUTTON_ENTER,  # go "a"
        BUTTON_PAGE_PREV,  # to Go
        BUTTON_ENTER,  # go Go
        BUTTON_ENTER,  # confirm key
    )

    # call with encrypted kef having string plaintext
    ctx = create_ctx(mocker, BTN_SEQUENCE)
    page = DatumTool(ctx)
    page.contents = kef_a_hello_world
    page._decrypt_as_kef_envelope()
    assert ctx.input.wait_for_button.call_count == len(BTN_SEQUENCE)
    assert page.title == 'key="a"'
    assert page.contents == b"hello world"
    assert page.decrypted == True

    # call with encrypted kef having bytes plaintext
    ctx = create_ctx(mocker, BTN_SEQUENCE)
    page = DatumTool(ctx)
    page.contents = kef_a_hello_world_w_0xdeadbeef_label
    page._decrypt_as_kef_envelope()
    assert ctx.input.wait_for_button.call_count == len(BTN_SEQUENCE)
    assert page.title == "0xdeadbeef"
    assert page.contents == b"hello world"
    assert page.decrypted == True


def test_datumtool__build_options_menu(m5stickv, mocker):
    """With DatumTool already initialized, test ._build_options_menu()"""
    from krux.pages.datum_tool import DatumTool

    some_chars = "This are characters"
    some_hex_plus = "deadbeef3456"
    some_bytes = b"These are bytes."

    # w/ text contents, default call
    ctx = create_ctx(mocker, [])
    page = DatumTool(ctx)
    page.contents = some_chars
    menu = page._build_options_menu()
    assert ctx.input.wait_for_button.call_count == 0
    assert [name for name, func in menu] == [
        "Show Datum",
        "Convert Datum",
        "QR Code",
        "Save to SD card",
    ]

    # w/ text content, w/ offer_convert and w/o offer_show
    ctx = create_ctx(mocker, [])
    page = DatumTool(ctx)
    page.contents = some_chars
    page._analyze_contents()
    menu = page._build_options_menu(offer_convert=True, offer_show=False)
    assert ctx.input.wait_for_button.call_count == 0
    assert [name for name, func in menu] == ["from utf8", "Done Converting"]

    # w/ HEX_plus content, w/ offer_convert and w/o offer_show
    ctx = create_ctx(mocker, [])
    page = DatumTool(ctx)
    page.contents = some_hex_plus.upper()
    page._analyze_contents()
    menu = page._build_options_menu(offer_convert=True, offer_show=False)
    assert ctx.input.wait_for_button.call_count == 0
    assert [name for name, func in menu] == [
        "from HEX",
        "shift case",
        "from base32",
        "from base43",
        "from base64",
        "from utf8",
        "Done Converting",
    ]

    # w/ hex_plus content, w/ offer_convert and w/o offer_show
    ctx = create_ctx(mocker, [])
    page = DatumTool(ctx)
    page.contents = some_hex_plus
    page._analyze_contents()
    menu = page._build_options_menu(offer_convert=True, offer_show=False)
    assert ctx.input.wait_for_button.call_count == 0
    assert [name for name, func in menu] == [
        "from hex",
        "shift case",
        "from base64",
        "from utf8",
        "Done Converting",
    ]

    # w/ bytes content, w/ offer_convert and w/o offer_show
    ctx = create_ctx(mocker, [])
    page = DatumTool(ctx)
    page.contents = some_bytes
    page._analyze_contents()
    menu = page._build_options_menu(offer_convert=True, offer_show=False)
    assert ctx.input.wait_for_button.call_count == 0
    assert [name for name, func in menu] == [
        "to hex",
        "to base32",
        "to base43",
        "to base64",
        "to utf8",
        "Encrypt",
        "Done Converting",
    ]

    # w/ hex_plus-ish bytes content and history, w/ offer_convert and w/o offer_show
    ctx = create_ctx(mocker, [])
    page = DatumTool(ctx)
    page.contents = some_hex_plus.encode()
    page.history = ["HEX"]
    page._analyze_contents()
    menu = page._build_options_menu(offer_convert=True, offer_show=False)
    assert ctx.input.wait_for_button.call_count == 0
    assert [name for name, func in menu] == [
        "to HEX (Undo)",
        "to base32",
        "to base43",
        "to base64",
        "to utf8",
        "Encrypt",
        "Done Converting",
    ]


def test_datumtool_view_contents(m5stickv, mocker, mock_file_operations):
    """With DatumTool already initialized, test .view_contents()"""
    from krux.pages.datum_tool import DatumTool
    from krux.input import BUTTON_ENTER, BUTTON_PAGE, BUTTON_PAGE_PREV

    some_bytes = b"These are bytes that won't fit on one-line."

    # escape to Back
    BTN_SEQUENCE = (
        BUTTON_PAGE_PREV,  # to Back
        BUTTON_ENTER,  # go Back
    )
    ctx = create_ctx(mocker, BTN_SEQUENCE)
    page = DatumTool(ctx)
    page.title = "title"
    page.contents = some_bytes
    page.view_contents()
    assert ctx.input.wait_for_button.call_count == len(BTN_SEQUENCE)

    # show and escape to Back
    BTN_SEQUENCE = (
        BUTTON_ENTER,  # go Show
        BUTTON_ENTER,
        BUTTON_PAGE_PREV,  # to Back
        BUTTON_ENTER,  # go Back
    )
    ctx = create_ctx(mocker, BTN_SEQUENCE)
    page = DatumTool(ctx)
    page.title = "title"
    page.contents = some_bytes
    page.view_contents()
    assert ctx.input.wait_for_button.call_count == len(BTN_SEQUENCE)

    # convert to hex, from hex (Undo), then escape to Back
    BTN_SEQUENCE = (
        BUTTON_PAGE,  # to Convert
        BUTTON_ENTER,  # go Convert
        BUTTON_PAGE,  # to "to hex"
        BUTTON_ENTER,  # go "to hex"
        BUTTON_PAGE,  # to "from hex (Undo)"
        BUTTON_ENTER,  # go "from hex (Undo)"
        BUTTON_PAGE_PREV,  # to Back
        BUTTON_ENTER,  # go Back
        BUTTON_PAGE_PREV,  # to Back
        BUTTON_ENTER,  # go Back
    )
    ctx = create_ctx(mocker, BTN_SEQUENCE)
    page = DatumTool(ctx)
    page.title = "title"
    page.contents = some_bytes
    page.view_contents()
    assert ctx.input.wait_for_button.call_count == len(BTN_SEQUENCE)

    # convert and Encrypt, then escape to Back
    BTN_SEQUENCE = (
        BUTTON_PAGE,  # to Convert
        BUTTON_ENTER,  # go Convert
        BUTTON_PAGE_PREV,  # to Done Converting
        BUTTON_PAGE_PREV,  # to Encrypt
        BUTTON_ENTER,  # go Encrypt
        BUTTON_ENTER,  # go Type Key
        BUTTON_ENTER,  # go "a"
        BUTTON_PAGE_PREV,  # to Go
        BUTTON_ENTER,  # go Go
        BUTTON_ENTER,  # confirm weak key "a"
        BUTTON_ENTER,  # confirm default key iterations
        BUTTON_ENTER,  # confirm default mode GCM
        BUTTON_ENTER,  # confirm additional cam entropy
        BUTTON_PAGE,  # decline updating KEF ID
        BUTTON_PAGE_PREV,  # to Done Converting
        BUTTON_ENTER,  # go Done Converting
        BUTTON_PAGE_PREV,  # to Back
        BUTTON_ENTER,  # go Back
    )
    I_VECTOR = b"OR\xa1\x93l>2q \x9e\x9dd\x05\x9e\xd7\x8e"
    mocker.patch(
        "krux.pages.capture_entropy.CameraEntropy.capture",
        mocker.MagicMock(return_value=I_VECTOR),
    )
    ctx = create_ctx(mocker, BTN_SEQUENCE)
    page = DatumTool(ctx)
    page.title = "title"
    page.contents = some_bytes
    page.view_contents()
    assert ctx.input.wait_for_button.call_count == len(BTN_SEQUENCE)

    # Export to SD, then escape to Back
    BTN_SEQUENCE = (
        BUTTON_PAGE_PREV,  # to Done
        BUTTON_PAGE_PREV,  # to Export-SD
        BUTTON_ENTER,  # go Export-SD
        BUTTON_ENTER,  # confirm Export-SD
        BUTTON_PAGE_PREV,  # to Go (w/o altering filename)
        BUTTON_ENTER,  # go Go
        BUTTON_ENTER,  # confirm filename
        BUTTON_ENTER,  # confirm Overwrite
        BUTTON_PAGE_PREV,  # to Back
        BUTTON_ENTER,  # go Back
        BUTTON_PAGE_PREV,  # to Back
        BUTTON_ENTER,  # go Back
    )
    ctx = create_ctx(mocker, BTN_SEQUENCE)
    page = DatumTool(ctx)
    page.title = "title"
    page.contents = some_bytes
    page.view_contents()
    assert ctx.input.wait_for_button.call_count == len(BTN_SEQUENCE)

    # Export to QR, then escape to Back
    BTN_SEQUENCE = (
        BUTTON_PAGE_PREV,  # to Done
        BUTTON_PAGE_PREV,  # to Export-SD
        BUTTON_PAGE_PREV,  # to Export-QR
        BUTTON_ENTER,  # go Export-QR
        BUTTON_PAGE_PREV,  # decline updating QR label
        BUTTON_ENTER,  # leave QR view
        BUTTON_PAGE_PREV,  # to Back
        BUTTON_ENTER,  # go Back
        BUTTON_PAGE_PREV,  # to Back
        BUTTON_ENTER,  # go Back
    )
    ctx = create_ctx(mocker, BTN_SEQUENCE)
    page = DatumTool(ctx)
    page.title = "title"
    page.contents = some_bytes
    page.view_contents()
    assert ctx.input.wait_for_button.call_count == len(BTN_SEQUENCE)


def test_datumtool_view_contents_multi_page(m5stickv, mocker):
    """simply to cover building of `pages` index, moving to `next page`, and `prev page`"""
    from binascii import hexlify
    from krux.pages.datum_tool import DatumTool
    from krux.input import PRESSED, BUTTON_ENTER, BUTTON_PAGE, BUTTON_PAGE_PREV

    # call with text that will span more than one page
    BTN_SEQUENCE = [
        BUTTON_ENTER,  # go Show Datum
        BUTTON_PAGE,  # page
        BUTTON_PAGE_PREV,  # page_prev
        BUTTON_ENTER,  # escape Show Datum
        BUTTON_PAGE_PREV,  # to Back
        BUTTON_ENTER,  # go Back
    ]
    ctx = create_ctx(mocker, BTN_SEQUENCE)
    ctx.display.to_lines_endpos = mocker.MagicMock(
        side_effect=[
            ([str(x) for x in range(15)] + ["15…"], 22),
            ([str(x) for x in range(16, 26)], 20),
            ([str(x) for x in range(15)] + ["15…"], 22),
        ]
    )
    page = DatumTool(ctx)
    page.contents = "\n".join([str(x) for x in range(26)])
    page.title = "title"
    page.view_contents()
    assert ctx.input.wait_for_button.call_count == len(BTN_SEQUENCE)

    # call with bytes that will span more than one page
    BTN_SEQUENCE = [
        BUTTON_ENTER,  # go Show Datum
        BUTTON_ENTER,  # escape Show Datum
        BUTTON_PAGE_PREV,  # to Back
        BUTTON_ENTER,  # go Back
    ]
    ctx = create_ctx(mocker, BTN_SEQUENCE)
    ctx.display.to_lines_endpos = mocker.MagicMock(
        side_effect=[
            (
                [hexlify(b"8 bytes.").decode() for _ in range(15)]
                + ["382062797465732…"],
                127,
            ),
            ([hexlify(b".8 bytes").decode() for _ in range(4)] + ["2e"], 33),
        ]
    )
    page = DatumTool(ctx)
    page.contents = b"8 bytes." * 20
    page.title = "title"
    page.view_contents()
    assert ctx.input.wait_for_button.call_count == len(BTN_SEQUENCE)


def test_datumtool_view_contents_convert_failure(mocker, m5stickv):
    """Contents cannot always be converted (ie: mem-alloc-err); flash_error"""
    from krux.pages.datum_tool import DatumTool
    from krux.input import BUTTON_ENTER, BUTTON_PAGE, BUTTON_PAGE_PREV

    # mock failure in convert_encoding so it returns None
    mocker.patch(
        "binascii.unhexlify",
        new=mocker.MagicMock(
            side_effect=[
                b"\xde\xad\xbe\xef",  # first call to unhexlify works, during detect_encoding()
                Exception(
                    "mocked failure"
                ),  # second call fails, during convert_encoding()
            ]
        ),
    )
    from binascii import unhexlify

    # call with bytes to be hexlified that will fail to convert via mocked unhexlify
    BTN_SEQUENCE = (
        BUTTON_ENTER,  # go Convert
        BUTTON_ENTER,  # go "to hex"
        BUTTON_ENTER,  # go "from hex", mocked failure
        BUTTON_PAGE_PREV,  # to Done Converting
        BUTTON_ENTER,  # go Done Converting
        BUTTON_PAGE_PREV,  # to Back
        BUTTON_ENTER,  # go Back
    )
    ctx = create_ctx(mocker, BTN_SEQUENCE)
    page = DatumTool(ctx)
    page.contents = b"\xde\xad\xbe\xef"
    page.title = "title"
    page.view_contents()
    assert ctx.input.wait_for_button.call_count == len(BTN_SEQUENCE)
    assert ctx.display.flash_text.call_count == 1
    ctx.display.flash_text.assert_called_with(
        "Failed to convert", 248, 2000, highlight_prefix=""
    )


def test_datumtool_show_contents_button_turbo(mocker, m5stickv):
    from krux.pages.datum_tool import DatumTool
    from krux.input import Input, PRESSED, BUTTON_ENTER, KEY_REPEAT_DELAY_MS
    import time

    ctx = create_ctx(mocker, [BUTTON_ENTER, BUTTON_ENTER])
    input = Input()
    input.wait_for_button = ctx.input.wait_for_button
    ctx.input.wait_for_fastnav_button = input.wait_for_fastnav_button
    datum = DatumTool(ctx)
    datum.contents = "testing 123 " * 250

    mocker.patch("time.sleep_ms", new=mocker.MagicMock())

    # fast forward
    input.page_value = mocker.MagicMock(side_effect=[PRESSED, None])

    datum._show_contents()

    time.sleep_ms.assert_called_with(KEY_REPEAT_DELAY_MS)

    # fast backward
    input.page_value = mocker.MagicMock(return_value=None)
    input.page_prev_value = mocker.MagicMock(side_effect=[PRESSED, None])

    datum._show_contents()

    time.sleep_ms.assert_called_with(KEY_REPEAT_DELAY_MS)


def test_datumtoolmenu_scan_qr_binary_decodable(m5stickv, mocker):
    """Test scan_qr when QR scanner returns binary data that can be decoded to text"""
    from krux.pages.datum_tool import DatumToolMenu
    from krux.pages.qr_capture import QRCodeCapture
    from krux.input import BUTTON_ENTER, BUTTON_PAGE, BUTTON_PAGE_PREV

    # Binary data that can be decoded to UTF-8 text
    binary_data = b"Hello World"

    # Mock QR scanner to return binary data
    mocker.patch.object(
        QRCodeCapture, "qr_capture_loop", new=lambda self: (binary_data, 0)
    )

    # Button sequence to exit from DatumTool view
    BTN_SEQUENCE = (
        BUTTON_ENTER,  # go Scan QR
        BUTTON_PAGE_PREV,  # to Back
        BUTTON_ENTER,  # go Back
        BUTTON_PAGE,  # to Text Entry
        BUTTON_PAGE,  # to Read File
        BUTTON_PAGE,  # to Back
        BUTTON_ENTER,  # go Back
    )

    ctx = create_ctx(mocker, BTN_SEQUENCE)
    page = DatumToolMenu(ctx).run()

    # Verify that the button sequence was executed
    assert ctx.input.wait_for_button.call_count == len(BTN_SEQUENCE)

    # Verify that the decoded text "Hello World" was displayed in the info box
    # The display should show the decoded string, not the hex representation
    display_calls = [
        str(call) for call in ctx.display.draw_hcentered_text.call_args_list
    ]
    assert any(
        '"Hello World"' in call for call in display_calls
    ), f"Expected to find decoded text 'Hello World' in display calls, but got: {display_calls}"


def test_datumtoolmenu_scan_qr_binary_non_decodable(m5stickv, mocker):
    """Test scan_qr when QR scanner returns binary data that cannot be decoded to text"""
    from krux.pages.datum_tool import DatumToolMenu
    from krux.pages.qr_capture import QRCodeCapture
    from krux.input import BUTTON_ENTER, BUTTON_PAGE, BUTTON_PAGE_PREV

    # Binary data that cannot be decoded to UTF-8 (invalid UTF-8 sequence)
    # 0xFF and 0xFE are not valid UTF-8 byte sequences
    binary_data = b"\xff\xfe\xfd\xfc"

    # Mock QR scanner to return binary data
    mocker.patch.object(
        QRCodeCapture, "qr_capture_loop", new=lambda self: (binary_data, 0)
    )

    # Button sequence to exit from DatumTool view after scanning binary data
    BTN_SEQUENCE = (
        BUTTON_ENTER,  # go Scan QR
        BUTTON_PAGE_PREV,  # to Back
        BUTTON_ENTER,  # go Back
        BUTTON_PAGE,  # to Text Entry
        BUTTON_PAGE,  # to Read File
        BUTTON_PAGE,  # to Back
        BUTTON_ENTER,  # go Back
    )

    ctx = create_ctx(mocker, BTN_SEQUENCE)
    page = DatumToolMenu(ctx).run()

    # Verify that the button sequence was executed
    assert ctx.input.wait_for_button.call_count == len(BTN_SEQUENCE)

    # Verify that the hex representation was displayed in the info box
    # Since the data cannot be decoded to text, it should be shown as hex
    display_calls = [
        str(call) for call in ctx.display.draw_hcentered_text.call_args_list
    ]
    assert any(
        "0xfffefdfc" in call for call in display_calls
    ), f"Expected to find hex representation '0xfffefdfc' in display calls, but got: {display_calls}"
