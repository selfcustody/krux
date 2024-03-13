import pytest


@pytest.fixture
def tdata(mocker):
    from collections import namedtuple
    from ur.ur import UR
    from urtypes.crypto.psbt import PSBT

    TEST_DATA_BYTES = b'psbt\xff\x01\x00q\x02\x00\x00\x00\x01\xcf<X\xc3)\x82\xae P\x88\xd9\xbdI\xeb\x9b\x02\xac\xdfM=\xaev\xa5\x16\xc6\xb3\x06\xb1]\xe3\xa1N\x00\x00\x00\x00\x00\xfd\xff\xff\xff\x02|?]\x05\x00\x00\x00\x00\x16\x00\x14/4\xaa\x1c\xf0\nS\xb0U\xa2\x91\xa0:}E\xf0\xa6\x98\x8bR\x80\x96\x98\x00\x00\x00\x00\x00\x16\x00\x14\xe6j\xfe\xff\xc3\x83\x8eq\xf0\xa2{\x07\xe3\xb0\x0e\xdej\xe8\xe1`\x00\x00\x00\x00\x00\x01\x01\x1f\x00\xe1\xf5\x05\x00\x00\x00\x00\x16\x00\x14\xd0\xc4\xa3\xef\t\xe9\x97\xb6\xe9\x9e9~Q\x8f\xe3\xe4\x1a\x11\x8c\xa1"\x06\x02\xe7\xab%7\xb5\xd4\x9e\x97\x03\t\xaa\xe0n\x9eI\xf3l\xe1\xc9\xfe\xbb\xd4N\xc8\xe0\xd1\xcc\xa0\xb4\xf9\xc3\x19\x18s\xc5\xda\nT\x00\x00\x80\x01\x00\x00\x80\x00\x00\x00\x80\x00\x00\x00\x00\x00\x00\x00\x00\x00"\x02\x03]I\xec\xcdT\xd0\t\x9eCgbw\xc7\xa6\xd4b]a\x1d\xa8\x8a]\xf4\x9b\xf9Qzw\x91\xa7w\xa5\x18s\xc5\xda\nT\x00\x00\x80\x01\x00\x00\x80\x00\x00\x00\x80\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00'
    TEST_DATA_B58 = "UUucvki6KWyS35DhetbWPw1DiaccbHKywScF96E8VUwEnN1gss947UasRfkNxtrkzCeHziHyMCuoiQ2mSYsbYXuV3YwYBZwFh1c6xtBAEK1aDgPwMgqf74xTzf3m4KH4iUU5nHTqroDpoRZR59meafTCUBChZ5NJ8MoUdKE6avyYdSm5kUb4npmFpMpJ9S3qd2RedHMoQFRiXK3jwdH81emAEsFYSW3Kb7caPcWjkza4S4EEWWbaggofGFmxE5gNNg4A4LNC2ZUGLsALZffNvg3yh3qg6rFxhkiyzWc44kx9Khp6Evm1j4Njh8kjifkngLTPFtX3uWNLAB1XrvpPMx6kkkhr7RnFVrA4JsDp5BwVGAXBoSBLTqweFevZ5"
    TEST_DATA_UR = UR("crypto-psbt", PSBT(TEST_DATA_BYTES).to_cbor())

    TEST_PARTS_FORMAT_NONE = [
        "UUucvki6KWyS35DhetbWPw1DiaccbHKywScF96E8VUwEnN1gss947UasRfkNxtrkzCeHziHyMCuoiQ2mSYsbYXuV3YwYBZwFh1c6xtBAEK1aDgPwMgqf74xTzf3m4KH4iUU5nHTqroDpoRZR59meafTCUBChZ5NJ8MoUdKE6avyYdSm5kUb4npmFpMpJ9S3qd2RedHMoQFRiXK3jwdH81emAEsFYSW3Kb7caPcWjkza4S4EEWWbaggofGFmxE5gNNg4A4LNC2ZUGLsALZffNvg3yh3qg6rFxhkiyzWc44kx9Khp6Evm1j4Njh8kjifkngLTPFtX3uWNLAB1XrvpPMx6kkkhr7RnFVrA4JsDp5BwVGAXBoSBLTqweFevZ5"
    ]
    TEST_PARTS_FORMAT_PMOFN = [
        "p2of3 4iUU5nHTqroDpoRZR59meafTCUBChZ5NJ8MoUdKE6avyYdSm5kUb4npmFpMpJ9S3qd2RedHMoQFRiXK3jwdH81emAEsFYSW3Kb7caPcWjkza4S4EEWWbaggofGFmxE5",
        "p1of3 UUucvki6KWyS35DhetbWPw1DiaccbHKywScF96E8VUwEnN1gss947UasRfkNxtrkzCeHziHyMCuoiQ2mSYsbYXuV3YwYBZwFh1c6xtBAEK1aDgPwMgqf74xTzf3m4KH",
        "p3of3 gNNg4A4LNC2ZUGLsALZffNvg3yh3qg6rFxhkiyzWc44kx9Khp6Evm1j4Njh8kjifkngLTPFtX3uWNLAB1XrvpPMx6kkkhr7RnFVrA4JsDp5BwVGAXBoSBLTqweFevZ5",
    ]
    TEST_PARTS_FORMAT_SINGLEPART_UR = [
        "ur:crypto-psbt/hkadchjojkidjyzmadaejsaoaeaeaeadtkfnhdsrdtlfplcxgdlotarygawmndaopsurgtfsplkooncmswqdampahlvloyglaeaeaeaeaezczmzmzmaokefhhlahaeaeaeaecmaebbdleepkcewtbkgupfgooemenbftkifewtolmklugmlamtmkaeaeaeaeaecmaebbvaimzezmsrlsmnjswtoekgatvlpfbaueimvsvyhnaeaeaeaeaeadadctaevyykahaeaeaeaecmaebbtissotwsaswlmsrpwlnneskbgymyvlvecybylkoycpamaovdpydaemretynnmsaxaspkvtjtnngawfjzvysozerktyglspvtttsfnbqzytsrcfcsjksktnbkghaeaelaadaeaelaaeaeaelaaeaeaeaeaeaeaeaeaecpaoaxhlgawpsnghtiasnnfxioidktstoltyidhlhscapdlehlwkndytgyknktmeosktoncsjksktnbkghaeaelaadaeaelaaeaeaelaadaeaeaeaeaeaeaeaeaeamgrmswl"
    ]
    TEST_PARTS_FORMAT_MULTIPART_UR = [
        "ur:crypto-psbt/2-8/lpaoaycfadcycyamgrmswlhddkplkooncmswqdampahlvloyglaeaeaeaeaezczmzmzmaokefhhlahaeaeaeaecmaebbdleepktpcpnyde",
        "ur:crypto-psbt/1-8/lpadaycfadcycyamgrmswlhddkhkadchjojkidjyzmadaejsaoaeaeaeadtkfnhdsrdtlfplcxgdlotarygawmndaopsurgtfswmwkinva",
        "ur:crypto-psbt/3-8/lpaxaycfadcycyamgrmswlhddkcewtbkgupfgooemenbftkifewtolmklugmlamtmkaeaeaeaeaecmaebbvaimzezmsrlsmnjseylanegy",
        "ur:crypto-psbt/4-8/lpaaaycfadcycyamgrmswlhddkwtoekgatvlpfbaueimvsvyhnaeaeaeaeaeadadctaevyykahaeaeaeaecmaebbtissotwsaskeisuold",
        "ur:crypto-psbt/5-8/lpahaycfadcycyamgrmswlhddkwlmsrpwlnneskbgymyvlvecybylkoycpamaovdpydaemretynnmsaxaspkvtjtnngawfjzvychtbfxax",
        "ur:crypto-psbt/6-8/lpamaycfadcycyamgrmswlhddksozerktyglspvtttsfnbqzytsrcfcsjksktnbkghaeaelaadaeaelaaeaeaelaaeaeaeaeaestwncstl",
        "ur:crypto-psbt/7-8/lpataycfadcycyamgrmswlhddkaeaeaeaecpaoaxhlgawpsnghtiasnnfxioidktstoltyidhlhscapdlehlwkndytgyknktmevltdqzhn",
        "ur:crypto-psbt/8-8/lpayaycfadcycyamgrmswlhddkosktoncsjksktnbkghaeaelaadaeaelaaeaeaelaadaeaeaeaeaeaeaeaeaeaeaeaeaeaeaefxktbtbb",
    ]

    return namedtuple(
        "TestData",
        [
            "TEST_DATA_BYTES",
            "TEST_DATA_B58",
            "TEST_DATA_UR",
            "TEST_PARTS_FORMAT_NONE",
            "TEST_PARTS_FORMAT_PMOFN",
            "TEST_PARTS_FORMAT_SINGLEPART_UR",
            "TEST_PARTS_FORMAT_MULTIPART_UR",
        ],
    )(
        TEST_DATA_BYTES,
        TEST_DATA_B58,
        TEST_DATA_UR,
        TEST_PARTS_FORMAT_NONE,
        TEST_PARTS_FORMAT_PMOFN,
        TEST_PARTS_FORMAT_SINGLEPART_UR,
        TEST_PARTS_FORMAT_MULTIPART_UR,
    )


def test_init(mocker, m5stickv):
    from ur.ur_decoder import URDecoder
    from krux.qr import QRPartParser

    parser = QRPartParser()

    assert isinstance(parser, QRPartParser)
    assert parser.parts == {}
    assert parser.total == -1
    assert parser.format is None
    assert isinstance(parser.decoder, URDecoder)


def test_parser(mocker, m5stickv, tdata):
    from ur.ur import UR
    from urtypes.crypto.psbt import PSBT
    from krux.qr import QRPartParser, FORMAT_NONE, FORMAT_PMOFN, FORMAT_UR

    cases = [
        (FORMAT_NONE, tdata.TEST_PARTS_FORMAT_NONE),
        (FORMAT_PMOFN, tdata.TEST_PARTS_FORMAT_PMOFN),
        (FORMAT_UR, tdata.TEST_PARTS_FORMAT_SINGLEPART_UR),
        (FORMAT_UR, tdata.TEST_PARTS_FORMAT_MULTIPART_UR),
    ]
    num = 0
    for case in cases:
        print("case: ", num)
        num += 1
        fmt = case[0]
        parts = case[1]

        parser = QRPartParser()
        for i, part in enumerate(parts):
            parser.parse(part)

            assert parser.format == fmt

            if num == 4:
                assert parser.total_count() == len(parts) * 2
            else:
                assert parser.total_count() == len(parts)
            if parser.format == FORMAT_UR:
                assert parser.parsed_count() > 0
            else:
                assert parser.parsed_count() == i + 1

            if i < len(parts) - 1:
                assert not parser.is_complete()

        assert parser.is_complete()

        # Re-parse the first part to test that redundant parts are ignored
        parser.parse(parts[0])

        if num == 4:
            assert parser.total_count() == len(parts) * 2
        else:
            assert parser.total_count() == len(parts)

        if parser.format == FORMAT_UR:
            assert parser.parsed_count() > 0
        else:
            assert parser.parsed_count() == len(parts)

        res = parser.result()
        if fmt == FORMAT_UR:
            assert isinstance(res, UR)
            assert PSBT.from_cbor(res.cbor).data == tdata.TEST_DATA_BYTES
        else:
            assert isinstance(res, str)
            assert res == tdata.TEST_DATA_B58


def test_to_qr_codes(mocker, m5stickv, tdata):
    from krux.qr import to_qr_codes, FORMAT_NONE, FORMAT_PMOFN, FORMAT_UR
    from krux.display import Display

    cases = [
        # Test 135 pixels wide display
        (FORMAT_NONE, tdata.TEST_DATA_B58, 135, 1),
        (FORMAT_PMOFN, tdata.TEST_DATA_B58, 135, 9),
        (FORMAT_UR, tdata.TEST_DATA_UR, 135, 26),
        # Test 320 pixels wide display
        (FORMAT_NONE, tdata.TEST_DATA_B58, 320, 1),
        (FORMAT_PMOFN, tdata.TEST_DATA_B58, 320, 3),
        (FORMAT_UR, tdata.TEST_DATA_UR, 320, 6),
    ]
    for case in cases:
        mocker.patch(
            "krux.display.lcd",
            new=mocker.MagicMock(width=mocker.MagicMock(return_value=case[2])),
        )
        display = Display()
        qr_data_width = display.qr_data_width()
        fmt = case[0]
        data = case[1]
        expected_parts = case[3]

        codes = []
        code_generator = to_qr_codes(data, qr_data_width, fmt)
        i = 0
        while True:
            try:
                code, total = next(code_generator)
                codes.append(code)
                assert total == expected_parts
                if i == total - 1:
                    break
            except Exception as e:
                print("Error:", e)
                break
            i += 1
        assert len(codes) == expected_parts


def test_detect_plaintext_qr(mocker, m5stickv):
    from krux.qr import detect_format

    PLAINTEXT_QR_DATA = (
        "process swim repair fit artist rebuild remove vanish city opinion hawk coconut"
    )

    detect_format(PLAINTEXT_QR_DATA)


def test_find_min_num_parts(m5stickv):
    from krux.qr import find_min_num_parts

    with pytest.raises(ValueError) as raised_ex:
        find_min_num_parts("", 10, "format unknown")

    assert raised_ex.type is ValueError
    assert raised_ex.value.args[0] == "Invalid format type"
