import pytest


@pytest.fixture
def tdata(mocker):
    import binascii
    from collections import namedtuple

    PSBT = b"\xefN\xf7\xebn\xf8}\xfd5\xd3Ny\xd3m4\xd3M4\xd3]\xbb\xf5\xad\xb7\xdbv\xb9u\xf6\xf9\xd5\xf78\xe5\xfd\xb6\xd1\xf6\xb9\xf1\xbd\x1fs]\xde\xd5\xed\xf7\xe3n\xfd\xd9\xaf9w\xb7\xb7\xe9\xc7z\xdf}\xdb\xe5\xc6\xdc\xdf\xdd4\xd3M4\xd3M4}\xf7\xdf}\xf7\xdf\xd3V\xb4\xe5\xa7\x9a\xd1\xbd4\xd3M4\xd3M}\xef\xa6\xbd\xd7\x87\xdf{\xd74\xd3\xadt\xf7\xb7\x1c\xdd\xbe\xb7\xe9\xfd\x9coN:\xd1\xf6\xb8}\xce6\xed\xdd\x9b\xe3\x9f<i\xcd4\xd3M4\xd3M4\xd3]5\xdbOy\xe5\xe7\x9a\xd1\xbd4\xd3M4\xd3M{k\xddx\xeb~9\xdbM\x1f\xeb\xc7u\xf3\xd7\xb5i\xd74u\xfd\\\xe1\xddzy\xaf\x1f\xd7\x874u\xb7\x9b\xf3\xbd\xb6\xd3m7o]\xf8\xd5\xc7\x1bk\xbe\xbc\xdd\xbe\x9a\x7f\x87\xf5\xdb\x7f\x1cw\xa7\xbd\xed\xee\xf5\xeb\xb7y\xeb\xd7\xdas\x8e\xdf\xd5\xee<w\x8e\xf9\xe3_8\xe3~ym\xde:\xe3\xad\xf4\xe3}6\xdbM8\xdb\x86\xf9\xf1\xe7\xdfi\xa6\xba\xf7\x87\xb5\xe7\x9f^k\x97=\xdd\xb6\xdfw\x86\xbc\xf7N\xb8\xdbn4\xe7\x97\x1d\x7fN\xf4o\xae\xfb\xd7\x8e\xbd\xe3\x8d\x9d\xd3\xbd6\xd5\xfe\\\xf1\xe6\xf4}\xe6\xba\xe7^\x9d\xebF\xfci\xc6\xf7\xdd\xa7z\xe1\xe7^\xebG\xbc\xef\xce[}\xbd\xdak\xde\x1b\xf7\xd6\xdd\x7f\xce\xb5\xe7W[\xf5\xafZ\xd3]5\xd3\x8d\xb6\xd3M\xb4\xef\xbd_w_\x1aw\x8e}\xeb\xae\x9dw\x8f_\xdd\xdez\xe1\xed\xddm\xce6\x7f\x87<\xe3\xbe\xf8{~\xb4i\xd6\xb5\xeb\xcdzk\xc7\x9d\xe3\xcf\x1d\xe7\xaf5\xd3]9\xe3\xbev\xdb]7o]\xf8\xd5\xc7\x1bk\xbe\xbc\xdd\xbe\x9a\x7f\x87\xf5\xdb\x7f\x1cw\xa7\xbd\xed\xee\xf5\xeb\xb7y\xeb\xd7\xdas\x8e\xdf\xd5\xee<w\x8e\xf9\xe3_8\xe3~ym\xde:\xdb]7u\xeeywW\xb5u\xa7<\xd3\x97\xb7\x7f\xc6\xb9\xf1\xcd_m\xff[\xf7\x874\xd9\xfd\xddm\xa6\x9f{]\xbb}\xe7\xdck\x8f}\xe5\xfd\xba\x7f\xcd\xb4\xf3v\xdd\xe7f\x9e\xdbm:\xd3v\xf5\xdf\x8d\\q\xb6\xbb\xeb\xcd\xdb\xe9\xa7\xf8\x7f]\xb7\xf1\xc7z{\xde\xde\xef^\xbbw\x9e\xbd}\xa78\xed\xfd^\xe3\xc7x\xef\x9e5\xf3\x8e7\xe7\x96\xdd\xe3\xadto\x86\xbam\xae\xbb\xd3M4\xd3O4\xd3M4\xd3O4\xd3\x8d4\xd3O4\xdbm:\xd3w^\xe7\x97u{WZs\xcd9{w\xfck\x9f\x1c\xd5\xf6\xdf\xf5\xbfxsM\x9f\xdd\xd6\xdai\xf7\xb5\xdb\xb7\xde}\xc6\xb8\xf7\xde_\xdb\xa7\xfc\xdbO7m\xddto\x86\xbam\xae\xbb\xd3M4\xd3O4\xd3M4\xd3O4\xd3\x9d4\xd3O4\xd3M4"
    PSBT_BASE32 = "55HPP23O7B672NOTJZ45G3JU2NGTJU25XP223N63O24XL5XZ2X3TRZP5W3I7NOPRXUPXGXO62XW7PY3O7XM26OLXW636TR323565XZOG3TP52NGTJU2NGTJUPX3567PX37JVNNHFU6NNDPJU2NGTJU2NPXX2NPOXQ7PXXVZU2OWXJ55XDTO35N7J7WOG6TR22H3LQ7OOG3W53G7DT46GTTJU2NGTJU2NGTJV2NO3J546LZ422G6TJU2NGTJU263L3V4OW7RZ3NGR726HOXZ5PNLJ242HL7K44HOXU6NPD7LYONDVW6N7HPNW2NWTO3257DK4OG3LX26N3PU2P6D7LW37DR32PPPN5326XN3Z5PL5U44O37K64PDXR346GXZY4N7HS3O6HLR235HDPU3NWTJY3ODPT4PH35U2NOXXQ626PH26NOLT3XNW353YNPHXJ24NW3RU46LR272O6RX2566XR266HDM52O6TNVP6LTY6N5D5425OOXU55NDPY2OG67O2O6XB45POWR5457HFW7N53JV54G7X23OX7TVV45LVX5NPLLJV2NOTRW3NGTNU566V6527DJ3Y47PLV2OXPD273XPHVYPN3VW44NT7Q46OHPXYPN7LI2OWWXV426TLY6O6HTY546XTLU25HHR345W3LU3W6XPY2XDRW256XTO35GT7Q725W7Y4O6T333PO6XV3O6PL27NHHDW72XXDY54O7HRV6OHDPZ4W3XR23NOTO5POPF3VPNLVU46NHF5XP7DLT4ONL5W76W7XQ42NT7O5NWTJ6625XN66PXDLR566L7N2P7G3J43W3XTWNHW3NU5NG5XV36GVY4NWXPV43W7JU74H6XNX6HDXU66633XV5O3XT26X3JZY5X6V5Y6HPDXZ4NPTRY36PFW54OWXI34GXJW25O6TJU2NGTZU2NGTJU2PGTJY2NGTJ42NW3J22N3V5Z4XOV5VOWTTZU4XW574NOPRZVPW372366DTJWP53VW2NH33LW5X3Z64NOHX3ZP5XJ743NHTO3O5ORXYNOTNV255GTJU2NHTJU2NGTJU6NGTTU2NGTZU2NGTI"
    PSBT_BASE43 = "8FSM5IDB86G368O8AS/4F+-66::YUPT-8+DI8FX:YGXN1+.IWW0OS*AMDBWDU-MVA-DV7FCT44B3GG5.C74X5U54C9D8IQE0BG0G*367ULCKVA*X6RK0RW:0V9C543WK5J9G2+4XXLV:YPH9IPEQ:3Y56N098RD-CCT6EFVHV14UN*5YWV1YB5.+99989PBAKWSDFN*/36EZG0K0M31L0NMXD*3.3.G9:M*8VXT.EYFJQVZQ.X:DQ9Z*PDGL1+P*6QB0C/SPF74B37$HBPWLI2GBLVTH/:VJ-RDFGXJ1-ZPY-/VRV3LI2TV5E96I/QIP6I-/V12W4FZJK:JRJ.GAQS-K6BJW$1QEDF6FYH*NGO*QGYCF/VCZV2.FPWB/+-:W/1U6/AYFI3.5JWB$1AKLLDDD21$1KM1WY+8DUIV8FJWCALZ80G7R+QU$9VJH$*YLOU83LJ86T7.NEG.0J:IJIPJHB.BKII$1YKIUOX7IFMOB4WQSKE6/VG*.CTK9538PEKO$GJ*FO/+O40.6K-G8$QB*7XOH3.T7:E6U7:F1:P++DNT6.YX*D6-+374PBB$F60KQV9$Y*$KQ7T0.GWRMQVOCD:47WFZFCR9JZU:1VYW1D2URACQ9KFWXK3D4-JMI7EEP2:5C/9W03ZES:$Z:8BZ68E*O*PLSEHI2XFXLJYI.*4ONU/FQ78APS55$CQO8BZPD-NQ9KCHKPQ49WH0M8IFE*AP47PZ2-Q23T83O9K0IKX6XO20:VP3LP/2JSVAND*JK8DSTQYO9-*REXRMR8:*P-Q-4-WRL2GOWH4$$BC1+Z75EI9F-4RY:S6USAXPUNXPXN2++R1DXYNLV4C17JQN7VK*VHWFC/YGP1Q2QO0VSVZ:E.G1TFG.RC8SFQN3AO0MYPIPW6TM8A/BB1T+T.-6FLLGB$7A7V.AX9$+UFDRCWV302LQVEQBDEXZIPSRY6.ZH/PO3.9$T.WQCOJYOA7+QRIRDRZ0NQPT6+:K0"
    PSBT_BASE58 = "fbTSWjBRdizz5iPG78MHuK5tBpDcesUFdMUdm31xFAarazYQ7q1GFNezcB1mR8bwrh6yNxyo7MmsatJ33QPBaTBqQAdjW6nK4oPBdeHyzgoh9mHAqyWJoWvZ6j2fYubfzyvqU1Aj57cvSDmoaGZiZrUwp3Wfp1FPpMrr1NisiZ3jXChxDienPhMYgLkUbpTeoxf8S8kGefFFcSi9R7MU4H2kNiVRXSURW4sMh6LtN9F6x9C8s5qxHrQjgx7E3ssrPCvp6RpJPg2SfrsGrEKXgcuKtzmFWomUtnu4RUxetXxXYRAtwc8DhWUHch6Ydxpq6jkEB37pzFmVGUxfK7NgrN4dzfeCtTj1MTiVx1Kb7E9UiHbcE3ChopSr8zqWVdRDzfr1zDyYpEJMvAK5bsFea1cg6sKSWo9xZTKScrQrgZAzbRokDdaoLqB2vonrfzjuAzndSroSD7uRa26EzgWBQN7AkSPyjEgUwKziWww8BbGb4SyACqnGESbci6jehqL95H4oVhcRjLrfvwZFwyUYHHmhsLrBRAH5VNAyud1H358JbD9h5Pj63wQX1fbcas1Mb7Sk5Qfa7MAK7Kw9gpnECnm3rTqHj5mtLY3gg74dfU9DRVyGs7sP74uBsdxYvtxQzyTkxfDysCkzzmNgYQNdH2FyN2TNbzgfVuwhbWwkapFb9SdetNNrRL7crSXH9QEkQxq7j7NDJLsBExmARwXTJn8V9ZZDxeTQHzEt2csmbNxuQMT9dCiAP5oWPPg1ASw1xCx6pZ5X2E2dtgHJB3QxZLTGyy94NBUQJAynvxLPNzCYaEAe2RZGwyZyBY3udTDgboFy9owLFQWTAcdZCVYfBder8sXeVUR67iHvU7wWjES5aWFSNnQndaUD8aNVBx27d5gaVmJ1ngpF7CTxNCHXoJzyD1VQRh"
    PSBT_BASE64 = "70736274ff0100550200000001279a2323a5dfb51fc45f220fa58b0fc13e1e3342792a85d7e36cd6333b5cbc390000000000ffffffff01a05aea0b000000001976a914ffe9c0061097cc3b636f2cb0460fa4fc427d2b4588ac0000000000010120955eea0b0000000017a9146345200f68d189e1adc0df1c4d16ea8f14c0dbeb87220203b1341ccba7683b6af4f1238cd6e97e7167d569fac47f1e48d47541844355bd4646304302200424b58effaaa694e1559ea5c93bbfd4a89064224055cdf070b6771469442d07021f5c8eb0fea6516d60b8acb33ad64ede60e8785bfb3aa94b99bdf86151db9a9a010104220020771fd18ad459666dd49f3d564e3dbc42f4c84774e360ada16816a8ed488d5681010547522103b1341ccba7683b6af4f1238cd6e97e7167d569fac47f1e48d47541844355bd462103de55d1e1dac805e3f8a58c1fbf9b94c02f3dbaafe127fefca4995f26f82083bd52ae220603b1341ccba7683b6af4f1238cd6e97e7167d569fac47f1e48d47541844355bd4610b4a6ba67000000800000008004000080220603de55d1e1dac805e3f8a58c1fbf9b94c02f3dbaafe127fefca4995f26f82083bd10b4a6ba670000008000000080050000800000"

    # Adapted from https://github.com/bitcoin/bitcoin/blob/master/src/test/data/base58_encode_decode.json
    return namedtuple(
        "TestData",
        [
            "PSBT",
            "PSBT_BASE32",
            "PSBT_BASE43",
            "PSBT_BASE58",
            "PSBT_BASE64",
            "TEST_CASES",
        ],
    )(
        PSBT,
        PSBT_BASE32,
        PSBT_BASE43,
        PSBT_BASE58,
        PSBT_BASE64,
        [
            (b"", "", "", "", ""),
            (binascii.unhexlify("61"), "ME", "2B", "2g", "YQ=="),
            (binascii.unhexlify("626262"), "MJRGE", "1+45$", "a3gV", "YmJi"),
            (binascii.unhexlify("636363"), "MNRWG", "1+-U-", "aPEr", "Y2Nj"),
            (
                binascii.unhexlify("73696d706c792061206c6f6e6720737472696e67"),
                "ONUW24DMPEQGCIDMN5XGOIDTORZGS3TH",
                "2YT--DWX-2WS5L5VEX1E:6E7C8VJ:E",
                "2cFupjhnEsSn59qHXstmK2ffpLv2",
                "c2ltcGx5IGEgbG9uZyBzdHJpbmc=",
            ),
            (
                binascii.unhexlify(
                    "00eb15231dfceb60925886b67d065299925915aeb172c06647"
                ),
                "ADVRKIY57TVWBESYQ23H2BSSTGJFSFNOWFZMAZSH",
                "03+1P14XU-QM.WJNJV$OBH4XOF5+E9OUY4E-2",
                "1NS17iag9jJgTHD1VXjvLCEnZuQ3rJDE9L",
                "AOsVIx3862CSWIa2fQZSmZJZFa6xcsBmRw==",
            ),
            (
                binascii.unhexlify("516b6fcd0f"),
                "KFVW7TIP",
                "1CDVY/HG",
                "ABnLTmg",
                "UWtvzQ8=",
            ),
            (
                binascii.unhexlify("bf4f89001e670274dd"),
                "X5HYSAA6M4BHJXI",
                "22DOOE00VVRUHY",
                "3SEo3LWLoPntC",
                "v0+JAB5nAnTd",
            ),
            (binascii.unhexlify("572e4794"), "K4XEPFA", "9.ZLRA", "3EFU7m", "Vy5HlA=="),
            (
                binascii.unhexlify("ecac89cad93923c02321"),
                "5SWITSWZHER4AIZB",
                "F5JWS5AJ:FL5YV0",
                "EJDM8drfXA6uyA",
                "7KyJytk5I8AjIQ==",
            ),
            (binascii.unhexlify("10c8511e"), "CDEFCHQ", "1-FFWO", "Rt5zm", "EMhRHg=="),
            (
                binascii.unhexlify("00000000000000000000"),
                "AAAAAAAAAAAAAAAA",
                "0000000000",
                "1111111111",
                "AAAAAAAAAAAAAA==",
            ),
            (
                binascii.unhexlify(
                    "000111d38e5fc9071ffcd20b4a763cc9ae4f252bb4e48fd66a835e252ada93ff480d6dd43dc62a641155a5"
                ),
                "AAARDU4OL7EQOH742IFUU5R4ZGXE6JJLWTSI7VTKQNPCKKW2SP7UQDLN2Q64MKTECFK2K",
                "05V$PS0ZWYH7M1RH-$2L71TF23XQ*HQKJXQ96L5E9PPMWXXHT3G1IP.HT-540H",
                "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz",
                "AAER045fyQcf/NILSnY8ya5PJSu05I/WaoNeJSrak/9IDW3UPcYqZBFVpQ==",
            ),
            (
                binascii.unhexlify(
                    "000102030405060708090a0b0c0d0e0f101112131415161718191a1b1c1d1e1f202122232425262728292a2b2c2d2e2f303132333435363738393a3b3c3d3e3f404142434445464748494a4b4c4d4e4f505152535455565758595a5b5c5d5e5f606162636465666768696a6b6c6d6e6f707172737475767778797a7b7c7d7e7f808182838485868788898a8b8c8d8e8f909192939495969798999a9b9c9d9e9fa0a1a2a3a4a5a6a7a8a9aaabacadaeafb0b1b2b3b4b5b6b7b8b9babbbcbdbebfc0c1c2c3c4c5c6c7c8c9cacbcccdcecfd0d1d2d3d4d5d6d7d8d9dadbdcdddedfe0e1e2e3e4e5e6e7e8e9eaebecedeeeff0f1f2f3f4f5f6f7f8f9fafbfcfdfeff"
                ),
                "AAAQEAYEAUDAOCAJBIFQYDIOB4IBCEQTCQKRMFYYDENBWHA5DYPSAIJCEMSCKJRHFAUSUKZMFUXC6MBRGIZTINJWG44DSOR3HQ6T4P2AIFBEGRCFIZDUQSKKJNGE2TSPKBIVEU2UKVLFOWCZLJNVYXK6L5QGCYTDMRSWMZ3INFVGW3DNNZXXA4LSON2HK5TXPB4XU634PV7H7AEBQKBYJBMGQ6EITCULRSGY5D4QSGJJHFEVS2LZRGM2TOOJ3HU7UCQ2FI5EUWTKPKFJVKV2ZLNOV6YLDMVTWS23NN5YXG5LXPF5X274BQOCYPCMLRWHZDE4VS6MZXHM7UGR2LJ5JVOW27MNTWW33TO55X7A4HROHZHF43T6R2PK5PWO33XP6DY7F47U6X3PP6HZ7L57Z7P674",
                "060PLMRVA3TFF18/LY/QMLZT76BH2EO*BDNG7S93KP5BBBLO2BW0YQXFWP8O$/XBSLCYPAIOZLD2O$:XX+XMI79BSZP-B7U8U*$/A3ML:P+RISP4I-NQ./-B4.DWOKMZKT4:5+M3GS/5L0GWXIW0ES5J-J$BX$FIWARF.L2S/J1V9SHLKBSUUOTZYLE7O8765J**C0U23SXMU$.-T9+0/8VMFU*+0KIF5:5W:/O:DPGOJ1DW2L-/LU4DEBBCRIFI*497XHHS0.-+P-2S98B/8MBY+NKI2UP-GVKWN2EJ4CWC3UX8K3AW:MR0RT07G7OTWJV$RG2DG41AGNIXWVYHUBHY8.+5/B35O*-Z1J3$H8DB5NMK6F2L5M/1",
                "1cWB5HCBdLjAuqGGReWE3R3CguuwSjw6RHn39s2yuDRTS5NsBgNiFpWgAnEx6VQi8csexkgYw3mdYrMHr8x9i7aEwP8kZ7vccXWqKDvGv3u1GxFKPuAkn8JCPPGDMf3vMMnbzm6Nh9zh1gcNsMvH3ZNLmP5fSG6DGbbi2tuwMWPthr4boWwCxf7ewSgNQeacyozhKDDQQ1qL5fQFUW52QKUZDZ5fw3KXNQJMcNTcaB723LchjeKun7MuGW5qyCBZYzA1KjofN1gYBV3NqyhQJ3Ns746GNuf9N2pQPmHz4xpnSrrfCvy6TVVz5d4PdrjeshsWQwpZsZGzvbdAdN8MKV5QsBDY",
                "AAECAwQFBgcICQoLDA0ODxAREhMUFRYXGBkaGxwdHh8gISIjJCUmJygpKissLS4vMDEyMzQ1Njc4OTo7PD0+P0BBQkNERUZHSElKS0xNTk9QUVJTVFVWV1hZWltcXV5fYGFiY2RlZmdoaWprbG1ub3BxcnN0dXZ3eHl6e3x9fn+AgYKDhIWGh4iJiouMjY6PkJGSk5SVlpeYmZqbnJ2en6ChoqOkpaanqKmqq6ytrq+wsbKztLW2t7i5uru8vb6/wMHCw8TFxsfIycrLzM3Oz9DR0tPU1dbX2Nna29zd3t/g4eLj5OXm5+jp6uvs7e7v8PHy8/T19vf4+fr7/P3+/w==",
            ),
            (PSBT, PSBT_BASE32, PSBT_BASE43, PSBT_BASE58, PSBT_BASE64),
        ],
    )


def test_base_decode(mocker, m5stickv, tdata):
    from krux.baseconv import base_decode

    for data, data_base32, data_base43, data_base58, data_base64 in tdata.TEST_CASES:
        assert base_decode(data_base32, 32) == data
        assert base_decode(data_base43, 43) == data
        assert base_decode(data_base58, 58) == data
        assert base_decode(data_base64, 64) == data


def test_base_encode(mocker, m5stickv, tdata):
    from krux.baseconv import base_encode

    for data, data_base32, data_base43, data_base58, data_base64 in tdata.TEST_CASES:
        assert base_encode(data, 32) == data_base32
        assert base_encode(data, 43) == data_base43
        assert base_encode(data, 58) == data_base58
        assert base_encode(data, 64) == data_base64


def test_base_decode_from_unsupported_base(mocker, m5stickv):
    from krux.baseconv import base_decode

    with pytest.raises(ValueError):
        base_decode("not-empty", 21)


def test_base_decode_from_wrong_base(mocker, m5stickv):
    from krux.baseconv import base_decode

    with pytest.raises(ValueError):
        base_decode("abc", 43)


def test_base_encode_to_unsupported_base(mocker, m5stickv):
    from krux.baseconv import base_encode

    with pytest.raises(ValueError):
        base_encode(b"not-empty", 21)


def test_base_encode_from_wrong_type(mocker, m5stickv):
    from krux.baseconv import base_encode

    err = "Invalid value, expected bytes"
    for base in (43, 58, 64):
        with pytest.raises(TypeError, match=err):
            base_encode("", base)


def test_base_decode_from_wrong_type(mocker, m5stickv):
    from krux.baseconv import base_decode

    err = "Invalid value, expected str"
    for base in (43, 58, 64):
        with pytest.raises(TypeError, match=err):
            base_decode(b"", base)


def test_base43_via_electrum_tests(mocker, m5stickv):
    from krux.baseconv import base_encode, base_decode
    from binascii import unhexlify

    hex_cases = [
        "020000000001021cd0e96f9ca202e017ca3465e3c13373c0df3a4cdd91c1fd02ea42a1a65d2a410000000000fdffffff757da7cf8322e5063785e2d8ada74702d2648fa2add2d533ba83c52eb110df690200000000fdffffff02d07e010000000000160014b544c86eaf95e3bb3b6d2cabb12ab40fc59cad9ca086010000000000232102ce0d066fbfcf150a5a1bbc4f312cd2eb080e8d8a47e5f2ce1a63b23215e54fb5ac02483045022100a9856bf10a950810abceeabc9a86e6ba533e130686e3d7863971b9377e7c658a0220288a69ef2b958a7c2ecfa376841d4a13817ed24fa9a0e0a6b9cb48e6439794c701210324e291735f83ff8de47301b12034950b80fa4724926a34d67e413d8ff8817c53024830450221008f885978f7af746679200ed55fe2e86c1303620824721f95cc41eb7965a3dfcf02207872082ac4a3c433d41a203e6d685a459e70e551904904711626ac899238c20a0121023d4c9deae1aacf3f822dd97a28deaec7d4e4ff97be746d124a63d20e582f5b290a971600",
        "020000000001012005273af813ba23b0c205e4b145e525c280dd876e061f35bff7db9b2e0043640100000000fdffffff02d885010000000000160014e73f444b8767c84afb46ef4125d8b81d2542a53d00e1f5050000000017a914052ed032f5c74a636ed5059611bb90012d40316c870247304402200c628917673d75f05db893cc377b0a69127f75e10949b35da52aa1b77a14c350022055187adf9a668fdf45fc09002726ba7160e713ed79dddcd20171308273f1a2f1012103cb3e00561c3439ccbacc033a72e0513bcfabff8826de0bc651d661991ade6171049e1600",
        "70736274ff01009a020000000258e87a21b56daf0c23be8e7070456c336f7cbaa5c8757924f545887bb2abdd750000000000ffffffff838d0427d0ec650a68aa46bb0b098aea4422c071b2ca78352a077959d07cea1d0100000000ffffffff0270aaf00800000000160014d85c2b71d0060b09c9886aeb815e50991dda124d00e1f5050000000016001400aea9a2e5f0f876a588df5546e8742d1d87008f00000000000100bb0200000001aad73931018bd25f84ae400b68848be09db706eac2ac18298babee71ab656f8b0000000048473044022058f6fc7c6a33e1b31548d481c826c015bd30135aad42cd67790dab66d2ad243b02204a1ced2604c6735b6393e5b41691dd78b00f0c5942fb9f751856faa938157dba01feffffff0280f0fa020000000017a9140fb9463421696b82c833af241c78c17ddbde493487d0f20a270100000017a91429ca74f8a08f81999428185c97b5d852e4063f6187650000000107da00473044022074018ad4180097b873323c0015720b3684cc8123891048e7dbcd9b55ad679c99022073d369b740e3eb53dcefa33823c8070514ca55a7dd9544f157c167913261118c01483045022100f61038b308dc1da865a34852746f015772934208c6d24454393cd99bdf2217770220056e675a675a6d0a02b85b14e5e29074d8a25a9b5760bea2816f661910a006ea01475221029583bf39ae0a609747ad199addd634fa6108559d6c5cd39b4c2183f1ab96e07f2102dab61ff49a14db6a7d02b0cd1fbb78fc4b18312b5b4e54dae4dba2fbfef536d752ae0001012000c2eb0b0000000017a914b7f5faf40e3d40a5a459b1db3535f2b72fa921e8870107232200208c2353173743b595dfb4a07b72ba8e42e3797da74e87fe7d9d7497e3b20289030108da0400473044022062eb7a556107a7c73f45ac4ab5a1dddf6f7075fb1275969a7f383efff784bcb202200c05dbb7470dbf2f08557dd356c7325c1ed30913e996cd3840945db12228da5f01473044022065f45ba5998b59a27ffe1a7bed016af1f1f90d54b3aa8f7450aa5f56a25103bd02207f724703ad1edb96680b284b56d4ffcb88f7fb759eabbe08aa30f29b851383d20147522103089dc10c7ac6db54f91329af617333db388cead0c231f723379d1b99030b02dc21023add904f3d6dcf59ddb906b0dee23529b7ffb9ed50e5e86151926860221f0e7352ae00220203a9a4c37f5996d3aa25dbac6b570af0650394492942460b354753ed9eeca5877110d90c6a4f000000800000008004000080002202027f6399757d2eff55a136ad02c684b1838b6556e5f1b6b34282a94b6b5005109610d90c6a4f00000080000000800500008000",
    ]

    b43_cases = [
        "3E2DH7.J3PKVZJ3RCOXQVS3Y./6-WE.75DDU0K58-0N1FRL565N8ZH-DG1Z.1IGWTE5HK8F7PWH5P8+V3XGZZ6GQBPHNDE+RD8CAQVV1/6PQEMJIZTGPMIJ93B8P$QX+Y2R:TGT9QW8S89U4N2.+FUT8VG+34USI/N/JJ3CE*KLSW:REE8T5Y*9:U6515JIUR$6TODLYHSDE3B5DAF:5TF7V*VAL3G40WBOM0DO2+CFKTTM$G-SO:8U0EW:M8V:4*R9ZDX$B1IRBP9PLMDK8H801PNTFB4$HL1+/U3F61P$4N:UAO88:N5D+J:HI4YR8IM:3A7K1YZ9VMRC/47$6GGW5JEL1N690TDQ4XW+TWHD:V.1.630QK*JN/.EITVU80YS3.8LWKO:2STLWZAVHUXFHQ..NZ0:.J/FTZM.KYDXIE1VBY7/:PHZMQ$.JZQ2.XT32440X/HM+UY/7QP4I+HTD9.DUSY-8R6HDR-B8/PF2NP7I2-MRW9VPW3U9.S0LQ.*221F8KVMD5ANJXZJ8WV4UFZ4R.$-NXVE+-FAL:WFERGU+WHJTHAP",
        "64XF-8+PM6*4IYN-QWW$B2QLNW+:C8-$I$-+T:L.6DKXTSWSFFONDP1J/MOS3SPK0-SYVW38U9.3+A1/*2HTHQTJGP79LVEK-IITQJ1H.C/X$NSOV$8DWR6JAFWXD*LX4-EN0.BDOF+PPYPH16$NM1H.-MAA$V1SCP0Q.6Y5FR822S6K-.5K5F.Z4Q:0SDRG-4GEBLAO4W9Z*H-$1-KDYAFOGF675W0:CK5M1LT92IG:3X60P3GKPM:X2$SP5A7*LT9$-TTEG0/DRZYV$7B4ADL9CVS5O7YG.J64HLZ24MVKO/-GV:V.T/L$D3VQ:MR8--44HK8W",
        "EFS+4WQ2R.5QWTVLQS.BWHG21Q-M0HVA+KKLG+9RYJ2B/GHJ$3OUOKH32U0NISGM$CI*KI24$PKQI0F*GA..*DW:UJ4FM-6S3B*VIJ0.M8M*DVCR9+TNG2R/IMZY0A72MS8+QMTO*:25V577L*DRC78WBK0BNAK7/8JQR-FA/L-KNBBKTQRZEU93T/Z/.7OBC6A7WWZ49DNHLG:X37ISM2+.ZT4ZC00.G8K8O6NM48GRR+N/-W/ASXT5VLPPHPRWR2PHMLZWDYAN8DMW$1EKD/EU4LHQWIKM0N42B*/32MQ1C:I17FMQVVQF6OA*X1RW8X.H17040FPH8/L5HBPFTTT0PMJGR9I0/J0+4PS5WJE/:W-Y.YA:SMFZMO36IMK0P/KUHVR.44OPT$TD*ZHSPZVULFWH75T+APO636*NYL19ZJIU3N37$KN7OY7*WOA498BWCPM$G6::C:YPDZ:PUISTZB-RL**B/QAX+HA*55O+:R/L8*J9B*G:QU6FS+HS+:OXPKOP-GDJK$NU72E4Y11BZENGIJWLWZ+C:01G$H-*LY5.LGC5I1A4G7$KT9BZ81LEPV5D09RAKI5BW1*O8QWMIIG17/8$J0X:W7F9FC7EMQRLESY2NNNVLZTHWB/FJVB-*.5JU0GQ*3JIBTQ$OR3AHTJ-U-C-8MWV$R::*VTRY-2+*H7U594$0JCN27R9*TY0+8:3Q7T/HES5OF*GLL::5Z8M$JNCLLKH6:J:GCT$E:27AXUA1L4ROJO3*-86C2QH.9TBNP0SS51XRL/J7:-+QES+37SOZIJCKG2XOUVPJR:F+MGS1L6-8/YA.6BKZ+FMF8F:OT2P4X:9M4P8IGM-/UUSS8S5*8YMZ$S+JKY.DHDCY$$+F53TGYK1.RHYA68-KO3O:$$IO/R9995TPAE6FF6$UOAUD5A2YLY.Q$VE$Q*0437K-DHKRFM$Q$3G:58+GER9D.6S$EW++HBBE0T62MAA/$-A2OV22QHY.JHK:6GNT.QQ*5YWZKCZI$+IQPU0UT/0H0PR9BYB1BB-Y+A.Q2HD$JP+:AT0CQR$R3PVHC9K/IPTVWJK0J4$J-B-CL6713L5PM-33-.CHXGJ$*ME.U-71V2JNX*W7JYC$V2VEEL:3GU3HGV84O.5PT+K*NB/2.-0.GCQNJ*ZOC$M2Y86V:URJ4/.ZVK6X1I--.B9NAWE54IDPLRN0FSWYGA/INDLPUBW7SZ/YADHWFLU*MWI121O2Y56QWG.EFNLSIVAVXYF$.:N/OU-PS7U/*Z94CR7T0+.F+RL9.-U5FQ1QL/A2$O2E0$TP-AX4*55QET9BPH6:K+CD$.+$*F0BUWSW.*$IF*WIC+UMJRZP5.50V1DMTIZ.D/2+$0T-GDBE7LHPGY0X0:G/*ZPTAMQABEC4HPML4UCLSAR-.5UT-X1.PMM60HUFAF",
    ]

    for hex_case, b43_case in zip(hex_cases, b43_cases):
        assert base_encode(unhexlify(hex_case), 43) == b43_case
        assert base_decode(b43_case, 43) == unhexlify(hex_case)


def test_base58_via_electrum_tests(mocker, m5stickv):
    from krux.baseconv import base_encode, base_decode
    from binascii import unhexlify

    hex_cases = [
        "0cd394bef396200774544c58a5be0189f3ceb6a41c8da023b099ce547dd4d8071ed6ed647259fba8c26382edbf5165dfd2404e7a8885d88437db16947a116e451a5d1325e3fd075f9d370120d2ab537af69f32e74fc0ba53aaaa637752964b3ac95cfea7",
    ]

    b58_cases = [
        "VuvZ2K5UEcXCVcogny7NH4Evd9UfeYipsTdWuU4jLDhyaESijKtrGWZTFzVZJPjaoC9jFBs3SFtarhDhQhAxkXosUD8PmUb5UXW1tafcoPiCp8jHy7Fe2CUPXAbYuMvAyrkocbe6",
    ]

    for hex_case, b58_case in zip(hex_cases, b58_cases):
        assert base_encode(unhexlify(hex_case), 58) == b58_case
        assert base_decode(b58_case, 58) == unhexlify(hex_case)


def test_hint_encodings_strict_on_input(mocker):
    from krux.baseconv import hint_encodings

    for input_type in (
        b"bytes is not str",
        ["list of str is not str"],
        ("tuple of str is not str",),
    ):
        with pytest.raises(TypeError, match="hint_encodings\\(\\) expected str"):
            hint_encodings(input_type)


def test_hint_encodings(mocker, m5stickv):
    from krux.baseconv import hint_encodings
    from krux.baseconv import base_encode
    from binascii import hexlify

    bytestring = bytes([i for i in range(256)])

    tests = {
        "hex": hexlify(bytestring).decode(),
        "HEX": hexlify(bytestring).decode().upper(),
        32: base_encode(bytestring, 32),
        43: base_encode(bytestring, 43),
        # 58: base_encode(bytestring, 58),
        64: base_encode(bytestring, 64),
        "latin-1": bytestring.decode("latin-1"),
        "utf8": bytestring[:127].decode()
        + bytestring[:127].decode("latin-1").encode().decode(),
    }

    for hint, input_str in tests.items():
        result = hint_encodings(input_str)
        assert isinstance(result, list)
        assert hint in result


def test_hint_encodings_does_not_validate(mocker, m5stickv):
    """
    hint_encodings is intended to quickly return a list of non-validated encodings.
    It is upon the caller to try/except decoding the input string.
    """
    from krux.baseconv import hint_encodings
    from krux.baseconv import base_decode
    from binascii import unhexlify, a2b_base64

    def get_range(min_chr, max_chr):
        return range(ord(min_chr), ord(max_chr) + 1)

    # "hex" starts at "0", finishes at "f" (invalid: >= ":" and <= "`")
    string = "".join(chr(i) for i in get_range("0", "f")) + "f"
    assert "hex" in hint_encodings(string)
    with pytest.raises(ValueError, match="Non-hexadecimal digit found"):
        unhexlify(string)

    # "HEX" starts at "0", finishes at "F" (invalid: >= ":" and <= "@")
    string = "".join(chr(i) for i in get_range("0", "F")) + "F"
    assert "HEX" in hint_encodings(string)
    with pytest.raises(ValueError, match="Non-hexadecimal digit found"):
        unhexlify(string)

    # base 32 starts at "2", finishes at "Z" (invalid: >= "8" and <= "@")
    string = "".join(chr(i) for i in get_range("2", "Z"))
    assert 32 in hint_encodings(string)
    with pytest.raises(
        ValueError, match="Invalid Base32 string: Non-base32 digit found"
    ):
        base_decode(string, 32)

    # base 43 starts at "$", finishes at "Z" (invalid: "%&'(),/", >= ":" and <= "@")
    string = "".join(chr(i) for i in get_range("$", "Z"))
    assert 43 in hint_encodings(string)
    with pytest.raises(ValueError, match="forbidden character *"):
        base_decode(string, 43)

    # base58 is not implemented in hint_encodings() at this time
    # base 58 starts at "1", finishes at "z"
    # (invalid: >= ":" and <= "@", >= "[" and <= "`", "I", "O", "l")
    # string = "".join(chr(i) for i in get_range("1", "z"))
    # assert 58 in hint_encodings(string)
    # with pytest.raises(ValueError, match="forbidden character *"):
    #     base_decode(string, 58)

    # base 64 starts at "0", finishes at "z" (invalid: >= ":" and <= "<", >= ">" and <= "@")
    string = "".join(chr(i) for i in get_range("0", "z")) + "=="
    assert 64 in hint_encodings(string)
    with pytest.raises(ValueError, match="Only base64 data is allowed"):
        a2b_base64(string, strict_mode=True)

    # no test for ascii, checking max(ord) <= 127 will always be correct
    # no test for latin-1, it doesn't exist in uPython, but range will be correct
    # no test for utf-8, yet; but some byte-combos are not allowed in utf-8
