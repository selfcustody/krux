import pytest


@pytest.fixture
def tdata(mocker):
    import binascii
    from collections import namedtuple

    PSBT = b"\xefN\xf7\xebn\xf8}\xfd5\xd3Ny\xd3m4\xd3M4\xd3]\xbb\xf5\xad\xb7\xdbv\xb9u\xf6\xf9\xd5\xf78\xe5\xfd\xb6\xd1\xf6\xb9\xf1\xbd\x1fs]\xde\xd5\xed\xf7\xe3n\xfd\xd9\xaf9w\xb7\xb7\xe9\xc7z\xdf}\xdb\xe5\xc6\xdc\xdf\xdd4\xd3M4\xd3M4}\xf7\xdf}\xf7\xdf\xd3V\xb4\xe5\xa7\x9a\xd1\xbd4\xd3M4\xd3M}\xef\xa6\xbd\xd7\x87\xdf{\xd74\xd3\xadt\xf7\xb7\x1c\xdd\xbe\xb7\xe9\xfd\x9coN:\xd1\xf6\xb8}\xce6\xed\xdd\x9b\xe3\x9f<i\xcd4\xd3M4\xd3M4\xd3]5\xdbOy\xe5\xe7\x9a\xd1\xbd4\xd3M4\xd3M{k\xddx\xeb~9\xdbM\x1f\xeb\xc7u\xf3\xd7\xb5i\xd74u\xfd\\\xe1\xddzy\xaf\x1f\xd7\x874u\xb7\x9b\xf3\xbd\xb6\xd3m7o]\xf8\xd5\xc7\x1bk\xbe\xbc\xdd\xbe\x9a\x7f\x87\xf5\xdb\x7f\x1cw\xa7\xbd\xed\xee\xf5\xeb\xb7y\xeb\xd7\xdas\x8e\xdf\xd5\xee<w\x8e\xf9\xe3_8\xe3~ym\xde:\xe3\xad\xf4\xe3}6\xdbM8\xdb\x86\xf9\xf1\xe7\xdfi\xa6\xba\xf7\x87\xb5\xe7\x9f^k\x97=\xdd\xb6\xdfw\x86\xbc\xf7N\xb8\xdbn4\xe7\x97\x1d\x7fN\xf4o\xae\xfb\xd7\x8e\xbd\xe3\x8d\x9d\xd3\xbd6\xd5\xfe\\\xf1\xe6\xf4}\xe6\xba\xe7^\x9d\xebF\xfci\xc6\xf7\xdd\xa7z\xe1\xe7^\xebG\xbc\xef\xce[}\xbd\xdak\xde\x1b\xf7\xd6\xdd\x7f\xce\xb5\xe7W[\xf5\xafZ\xd3]5\xd3\x8d\xb6\xd3M\xb4\xef\xbd_w_\x1aw\x8e}\xeb\xae\x9dw\x8f_\xdd\xdez\xe1\xed\xddm\xce6\x7f\x87<\xe3\xbe\xf8{~\xb4i\xd6\xb5\xeb\xcdzk\xc7\x9d\xe3\xcf\x1d\xe7\xaf5\xd3]9\xe3\xbev\xdb]7o]\xf8\xd5\xc7\x1bk\xbe\xbc\xdd\xbe\x9a\x7f\x87\xf5\xdb\x7f\x1cw\xa7\xbd\xed\xee\xf5\xeb\xb7y\xeb\xd7\xdas\x8e\xdf\xd5\xee<w\x8e\xf9\xe3_8\xe3~ym\xde:\xdb]7u\xeeywW\xb5u\xa7<\xd3\x97\xb7\x7f\xc6\xb9\xf1\xcd_m\xff[\xf7\x874\xd9\xfd\xddm\xa6\x9f{]\xbb}\xe7\xdck\x8f}\xe5\xfd\xba\x7f\xcd\xb4\xf3v\xdd\xe7f\x9e\xdbm:\xd3v\xf5\xdf\x8d\\q\xb6\xbb\xeb\xcd\xdb\xe9\xa7\xf8\x7f]\xb7\xf1\xc7z{\xde\xde\xef^\xbbw\x9e\xbd}\xa78\xed\xfd^\xe3\xc7x\xef\x9e5\xf3\x8e7\xe7\x96\xdd\xe3\xadto\x86\xbam\xae\xbb\xd3M4\xd3O4\xd3M4\xd3O4\xd3\x8d4\xd3O4\xdbm:\xd3w^\xe7\x97u{WZs\xcd9{w\xfck\x9f\x1c\xd5\xf6\xdf\xf5\xbfxsM\x9f\xdd\xd6\xdai\xf7\xb5\xdb\xb7\xde}\xc6\xb8\xf7\xde_\xdb\xa7\xfc\xdbO7m\xddto\x86\xbam\xae\xbb\xd3M4\xd3O4\xd3M4\xd3O4\xd3\x9d4\xd3O4\xd3M4"
    PSBT_BASE43 = "8FSM5IDB86G368O8AS/4F+-66::YUPT-8+DI8FX:YGXN1+.IWW0OS*AMDBWDU-MVA-DV7FCT44B3GG5.C74X5U54C9D8IQE0BG0G*367ULCKVA*X6RK0RW:0V9C543WK5J9G2+4XXLV:YPH9IPEQ:3Y56N098RD-CCT6EFVHV14UN*5YWV1YB5.+99989PBAKWSDFN*/36EZG0K0M31L0NMXD*3.3.G9:M*8VXT.EYFJQVZQ.X:DQ9Z*PDGL1+P*6QB0C/SPF74B37$HBPWLI2GBLVTH/:VJ-RDFGXJ1-ZPY-/VRV3LI2TV5E96I/QIP6I-/V12W4FZJK:JRJ.GAQS-K6BJW$1QEDF6FYH*NGO*QGYCF/VCZV2.FPWB/+-:W/1U6/AYFI3.5JWB$1AKLLDDD21$1KM1WY+8DUIV8FJWCALZ80G7R+QU$9VJH$*YLOU83LJ86T7.NEG.0J:IJIPJHB.BKII$1YKIUOX7IFMOB4WQSKE6/VG*.CTK9538PEKO$GJ*FO/+O40.6K-G8$QB*7XOH3.T7:E6U7:F1:P++DNT6.YX*D6-+374PBB$F60KQV9$Y*$KQ7T0.GWRMQVOCD:47WFZFCR9JZU:1VYW1D2URACQ9KFWXK3D4-JMI7EEP2:5C/9W03ZES:$Z:8BZ68E*O*PLSEHI2XFXLJYI.*4ONU/FQ78APS55$CQO8BZPD-NQ9KCHKPQ49WH0M8IFE*AP47PZ2-Q23T83O9K0IKX6XO20:VP3LP/2JSVAND*JK8DSTQYO9-*REXRMR8:*P-Q-4-WRL2GOWH4$$BC1+Z75EI9F-4RY:S6USAXPUNXPXN2++R1DXYNLV4C17JQN7VK*VHWFC/YGP1Q2QO0VSVZ:E.G1TFG.RC8SFQN3AO0MYPIPW6TM8A/BB1T+T.-6FLLGB$7A7V.AX9$+UFDRCWV302LQVEQBDEXZIPSRY6.ZH/PO3.9$T.WQCOJYOA7+QRIRDRZ0NQPT6+:K0"
    PSBT_BASE58 = "fbTSWjBRdizz5iPG78MHuK5tBpDcesUFdMUdm31xFAarazYQ7q1GFNezcB1mR8bwrh6yNxyo7MmsatJ33QPBaTBqQAdjW6nK4oPBdeHyzgoh9mHAqyWJoWvZ6j2fYubfzyvqU1Aj57cvSDmoaGZiZrUwp3Wfp1FPpMrr1NisiZ3jXChxDienPhMYgLkUbpTeoxf8S8kGefFFcSi9R7MU4H2kNiVRXSURW4sMh6LtN9F6x9C8s5qxHrQjgx7E3ssrPCvp6RpJPg2SfrsGrEKXgcuKtzmFWomUtnu4RUxetXxXYRAtwc8DhWUHch6Ydxpq6jkEB37pzFmVGUxfK7NgrN4dzfeCtTj1MTiVx1Kb7E9UiHbcE3ChopSr8zqWVdRDzfr1zDyYpEJMvAK5bsFea1cg6sKSWo9xZTKScrQrgZAzbRokDdaoLqB2vonrfzjuAzndSroSD7uRa26EzgWBQN7AkSPyjEgUwKziWww8BbGb4SyACqnGESbci6jehqL95H4oVhcRjLrfvwZFwyUYHHmhsLrBRAH5VNAyud1H358JbD9h5Pj63wQX1fbcas1Mb7Sk5Qfa7MAK7Kw9gpnECnm3rTqHj5mtLY3gg74dfU9DRVyGs7sP74uBsdxYvtxQzyTkxfDysCkzzmNgYQNdH2FyN2TNbzgfVuwhbWwkapFb9SdetNNrRL7crSXH9QEkQxq7j7NDJLsBExmARwXTJn8V9ZZDxeTQHzEt2csmbNxuQMT9dCiAP5oWPPg1ASw1xCx6pZ5X2E2dtgHJB3QxZLTGyy94NBUQJAynvxLPNzCYaEAe2RZGwyZyBY3udTDgboFy9owLFQWTAcdZCVYfBder8sXeVUR67iHvU7wWjES5aWFSNnQndaUD8aNVBx27d5gaVmJ1ngpF7CTxNCHXoJzyD1VQRh"
    PSBT_BASE64 = "70736274ff0100550200000001279a2323a5dfb51fc45f220fa58b0fc13e1e3342792a85d7e36cd6333b5cbc390000000000ffffffff01a05aea0b000000001976a914ffe9c0061097cc3b636f2cb0460fa4fc427d2b4588ac0000000000010120955eea0b0000000017a9146345200f68d189e1adc0df1c4d16ea8f14c0dbeb87220203b1341ccba7683b6af4f1238cd6e97e7167d569fac47f1e48d47541844355bd4646304302200424b58effaaa694e1559ea5c93bbfd4a89064224055cdf070b6771469442d07021f5c8eb0fea6516d60b8acb33ad64ede60e8785bfb3aa94b99bdf86151db9a9a010104220020771fd18ad459666dd49f3d564e3dbc42f4c84774e360ada16816a8ed488d5681010547522103b1341ccba7683b6af4f1238cd6e97e7167d569fac47f1e48d47541844355bd462103de55d1e1dac805e3f8a58c1fbf9b94c02f3dbaafe127fefca4995f26f82083bd52ae220603b1341ccba7683b6af4f1238cd6e97e7167d569fac47f1e48d47541844355bd4610b4a6ba67000000800000008004000080220603de55d1e1dac805e3f8a58c1fbf9b94c02f3dbaafe127fefca4995f26f82083bd10b4a6ba670000008000000080050000800000"

    # Adapted from https://github.com/bitcoin/bitcoin/blob/master/src/test/data/base58_encode_decode.json
    return namedtuple(
        "TestData", ["PSBT", "PSBT_BASE43", "PSBT_BASE58", "PSBT_BASE64", "TEST_CASES"]
    )(
        PSBT,
        PSBT_BASE43,
        PSBT_BASE58,
        PSBT_BASE64,
        [
            (b"", "", "", ""),
            (binascii.unhexlify("61"), "2B", "2g", "YQ=="),
            (binascii.unhexlify("626262"), "1+45$", "a3gV", "YmJi"),
            (binascii.unhexlify("636363"), "1+-U-", "aPEr", "Y2Nj"),
            (
                binascii.unhexlify("73696d706c792061206c6f6e6720737472696e67"),
                "2YT--DWX-2WS5L5VEX1E:6E7C8VJ:E",
                "2cFupjhnEsSn59qHXstmK2ffpLv2",
                "c2ltcGx5IGEgbG9uZyBzdHJpbmc=",
            ),
            (
                binascii.unhexlify(
                    "00eb15231dfceb60925886b67d065299925915aeb172c06647"
                ),
                "03+1P14XU-QM.WJNJV$OBH4XOF5+E9OUY4E-2",
                "1NS17iag9jJgTHD1VXjvLCEnZuQ3rJDE9L",
                "AOsVIx3862CSWIa2fQZSmZJZFa6xcsBmRw==",
            ),
            (binascii.unhexlify("516b6fcd0f"), "1CDVY/HG", "ABnLTmg", "UWtvzQ8="),
            (
                binascii.unhexlify("bf4f89001e670274dd"),
                "22DOOE00VVRUHY",
                "3SEo3LWLoPntC",
                "v0+JAB5nAnTd",
            ),
            (binascii.unhexlify("572e4794"), "9.ZLRA", "3EFU7m", "Vy5HlA=="),
            (
                binascii.unhexlify("ecac89cad93923c02321"),
                "F5JWS5AJ:FL5YV0",
                "EJDM8drfXA6uyA",
                "7KyJytk5I8AjIQ==",
            ),
            (binascii.unhexlify("10c8511e"), "1-FFWO", "Rt5zm", "EMhRHg=="),
            (
                binascii.unhexlify("00000000000000000000"),
                "0000000000",
                "1111111111",
                "AAAAAAAAAAAAAA==",
            ),
            (
                binascii.unhexlify(
                    "000111d38e5fc9071ffcd20b4a763cc9ae4f252bb4e48fd66a835e252ada93ff480d6dd43dc62a641155a5"
                ),
                "05V$PS0ZWYH7M1RH-$2L71TF23XQ*HQKJXQ96L5E9PPMWXXHT3G1IP.HT-540H",
                "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz",
                "AAER045fyQcf/NILSnY8ya5PJSu05I/WaoNeJSrak/9IDW3UPcYqZBFVpQ==",
            ),
            (
                binascii.unhexlify(
                    "000102030405060708090a0b0c0d0e0f101112131415161718191a1b1c1d1e1f202122232425262728292a2b2c2d2e2f303132333435363738393a3b3c3d3e3f404142434445464748494a4b4c4d4e4f505152535455565758595a5b5c5d5e5f606162636465666768696a6b6c6d6e6f707172737475767778797a7b7c7d7e7f808182838485868788898a8b8c8d8e8f909192939495969798999a9b9c9d9e9fa0a1a2a3a4a5a6a7a8a9aaabacadaeafb0b1b2b3b4b5b6b7b8b9babbbcbdbebfc0c1c2c3c4c5c6c7c8c9cacbcccdcecfd0d1d2d3d4d5d6d7d8d9dadbdcdddedfe0e1e2e3e4e5e6e7e8e9eaebecedeeeff0f1f2f3f4f5f6f7f8f9fafbfcfdfeff"
                ),
                "060PLMRVA3TFF18/LY/QMLZT76BH2EO*BDNG7S93KP5BBBLO2BW0YQXFWP8O$/XBSLCYPAIOZLD2O$:XX+XMI79BSZP-B7U8U*$/A3ML:P+RISP4I-NQ./-B4.DWOKMZKT4:5+M3GS/5L0GWXIW0ES5J-J$BX$FIWARF.L2S/J1V9SHLKBSUUOTZYLE7O8765J**C0U23SXMU$.-T9+0/8VMFU*+0KIF5:5W:/O:DPGOJ1DW2L-/LU4DEBBCRIFI*497XHHS0.-+P-2S98B/8MBY+NKI2UP-GVKWN2EJ4CWC3UX8K3AW:MR0RT07G7OTWJV$RG2DG41AGNIXWVYHUBHY8.+5/B35O*-Z1J3$H8DB5NMK6F2L5M/1",
                "1cWB5HCBdLjAuqGGReWE3R3CguuwSjw6RHn39s2yuDRTS5NsBgNiFpWgAnEx6VQi8csexkgYw3mdYrMHr8x9i7aEwP8kZ7vccXWqKDvGv3u1GxFKPuAkn8JCPPGDMf3vMMnbzm6Nh9zh1gcNsMvH3ZNLmP5fSG6DGbbi2tuwMWPthr4boWwCxf7ewSgNQeacyozhKDDQQ1qL5fQFUW52QKUZDZ5fw3KXNQJMcNTcaB723LchjeKun7MuGW5qyCBZYzA1KjofN1gYBV3NqyhQJ3Ns746GNuf9N2pQPmHz4xpnSrrfCvy6TVVz5d4PdrjeshsWQwpZsZGzvbdAdN8MKV5QsBDY",
                "AAECAwQFBgcICQoLDA0ODxAREhMUFRYXGBkaGxwdHh8gISIjJCUmJygpKissLS4vMDEyMzQ1Njc4OTo7PD0+P0BBQkNERUZHSElKS0xNTk9QUVJTVFVWV1hZWltcXV5fYGFiY2RlZmdoaWprbG1ub3BxcnN0dXZ3eHl6e3x9fn+AgYKDhIWGh4iJiouMjY6PkJGSk5SVlpeYmZqbnJ2en6ChoqOkpaanqKmqq6ytrq+wsbKztLW2t7i5uru8vb6/wMHCw8TFxsfIycrLzM3Oz9DR0tPU1dbX2Nna29zd3t/g4eLj5OXm5+jp6uvs7e7v8PHy8/T19vf4+fr7/P3+/w==",
            ),
            (PSBT, PSBT_BASE43, PSBT_BASE58, PSBT_BASE64),
        ],
    )


def test_base_decode(mocker, m5stickv, tdata):
    from krux.baseconv import base_decode

    for data, data_base43, data_base58, data_base64 in tdata.TEST_CASES:
        assert base_decode(data_base43.encode(), 43) == data
        assert base_decode(data_base58.encode(), 58) == data
        assert base_decode(data_base64.encode(), 64) == data


def test_base_encode(mocker, m5stickv, tdata):
    from krux.baseconv import base_encode

    for data, data_base43, data_base58, data_base64 in tdata.TEST_CASES:
        assert base_encode(data, 43) == data_base43.encode()
        assert base_encode(data, 58) == data_base58.encode()
        assert base_encode(data, 64) == data_base64.encode()


def test_base_decode_from_unsupported_base(mocker, m5stickv):
    from krux.baseconv import base_decode

    with pytest.raises(ValueError):
        base_decode(b"", 21)


def test_base_decode_from_wrong_base(mocker, m5stickv):
    from krux.baseconv import base_decode

    with pytest.raises(ValueError):
        base_decode("abc".encode(), 43)


def test_base_encode_to_unsupported_base(mocker, m5stickv):
    from krux.baseconv import base_encode

    with pytest.raises(ValueError):
        base_encode(b"", 21)
