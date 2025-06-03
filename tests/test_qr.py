import pytest


@pytest.fixture
def tdata(mocker):
    from collections import namedtuple
    from ur.ur import UR
    from urtypes.crypto.psbt import PSBT

    TEST_DATA_BYTES = b'psbt\xff\x01\x00q\x02\x00\x00\x00\x01\xcf<X\xc3)\x82\xae P\x88\xd9\xbdI\xeb\x9b\x02\xac\xdfM=\xaev\xa5\x16\xc6\xb3\x06\xb1]\xe3\xa1N\x00\x00\x00\x00\x00\xfd\xff\xff\xff\x02|?]\x05\x00\x00\x00\x00\x16\x00\x14/4\xaa\x1c\xf0\nS\xb0U\xa2\x91\xa0:}E\xf0\xa6\x98\x8bR\x80\x96\x98\x00\x00\x00\x00\x00\x16\x00\x14\xe6j\xfe\xff\xc3\x83\x8eq\xf0\xa2{\x07\xe3\xb0\x0e\xdej\xe8\xe1`\x00\x00\x00\x00\x00\x01\x01\x1f\x00\xe1\xf5\x05\x00\x00\x00\x00\x16\x00\x14\xd0\xc4\xa3\xef\t\xe9\x97\xb6\xe9\x9e9~Q\x8f\xe3\xe4\x1a\x11\x8c\xa1"\x06\x02\xe7\xab%7\xb5\xd4\x9e\x97\x03\t\xaa\xe0n\x9eI\xf3l\xe1\xc9\xfe\xbb\xd4N\xc8\xe0\xd1\xcc\xa0\xb4\xf9\xc3\x19\x18s\xc5\xda\nT\x00\x00\x80\x01\x00\x00\x80\x00\x00\x00\x80\x00\x00\x00\x00\x00\x00\x00\x00\x00"\x02\x03]I\xec\xcdT\xd0\t\x9eCgbw\xc7\xa6\xd4b]a\x1d\xa8\x8a]\xf4\x9b\xf9Qzw\x91\xa7w\xa5\x18s\xc5\xda\nT\x00\x00\x80\x01\x00\x00\x80\x00\x00\x00\x80\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00'
    TEST_DATA_B58 = "UUucvki6KWyS35DhetbWPw1DiaccbHKywScF96E8VUwEnN1gss947UasRfkNxtrkzCeHziHyMCuoiQ2mSYsbYXuV3YwYBZwFh1c6xtBAEK1aDgPwMgqf74xTzf3m4KH4iUU5nHTqroDpoRZR59meafTCUBChZ5NJ8MoUdKE6avyYdSm5kUb4npmFpMpJ9S3qd2RedHMoQFRiXK3jwdH81emAEsFYSW3Kb7caPcWjkza4S4EEWWbaggofGFmxE5gNNg4A4LNC2ZUGLsALZffNvg3yh3qg6rFxhkiyzWc44kx9Khp6Evm1j4Njh8kjifkngLTPFtX3uWNLAB1XrvpPMx6kkkhr7RnFVrA4JsDp5BwVGAXBoSBLTqweFevZ5"
    TEST_DATA_UR = UR("crypto-psbt", PSBT(TEST_DATA_BYTES).to_cbor())
    TEST_DATA_BBQR = b'psbt\xff\x01\x00R\x02\x00\x00\x00\x01\x9a\x9b\xe1\xca)\x10\\\x97t<\x0f\xd1\xeey\xc0\xe6\r"\x8aa\xc8\xec\xbft\xf9\xe7\xcf\xfa\x01\x19\x0c{\x01\x00\x00\x00\x00\xfd\xff\xff\xff\x01!&\x00\x00\x00\x00\x00\x00\x16\x00\x14\xae\xcd\x1e\xdc>\xffe\xaa \x9d\x02\x15\xe7=p\x90]\xc1hlX\x0b+\x00O\x01\x045\x87\xcf\x03\xdb\xde\xe7\x1b\x80\x00\x00\x00\xb3*S\x0b\x7f\xb7\xf7\xdb\x7fB\x9fcO\xa6\xf4%-P\xc6L\xea\xbd\xb5\xeaB\x97\xe4\x1e\x94\xf8\xae\x16\x02`\x9c%\xeaeN\x82\xec=\xf7\xd8wV\xb3\xc9"A\xe7i\xa7U\xfeoaw\x1e$Y\x00\xbb\x18\xa1\x10e\xfbC\xfeT\x00\x00\x80\x01\x00\x00\x80\x00\x00\x00\x80\x00\x01\x01\x1f\x10\'\x00\x00\x00\x00\x00\x00\x16\x00\x14I\x8cM\xa5\x8c\xbb\x9cZi\x88\xb82\xde\xb33l\xf4BT\xa0\x01\x03\x04\x01\x00\x00\x00"\x06\x03\xed\x17\xfd\x05\xafk\xcdQ\xf8\xddl\xf77\xac\x13j\xfa\x00h\x1f\xb2\xa9\xc3\xf5||\xad\xe8J\xf8\x1fa\x18e\xfbC\xfeT\x00\x00\x80\x01\x00\x00\x80\x00\x00\x00\x80\x00\x00\x00\x00\x08\x00\x00\x00\x00\x00'
    TEST_DATA_BBQR_MULTI = b"psbt\xff\x01\x00\xc3\x02\x00\x00\x00\x03/#\xc5\xf6C##\xcb\x1b\x1e\x8e\x11-E\x00 \xdb*\xfa\x10\x1e\xd1N\xdea'm\x99J\xba\x96*\n\x00\x00\x00\x00\xfd\xff\xff\xff\xd2h\x80v\xf6<\x08\xa0k\x16\xce\x9f\xd9\n1\xbfF\x06\x81\x01\x0c\xae]\x0b\x11\x8a\xb5\xdfZ\xa6\xd3\xcf\x00\x00\x00\x00\x00\xfd\xff\xff\xff\xe9E\x99\x03\x1a\xf2\xe0n\xd7c7\xd3\xccx\xe5\xcc\x80\xbfu\xc2y\x19\x80\xfaK\x00\xaa\xdb\xd4\x00C\x9e\x00\x00\x00\x00\x00\xfd\xff\xff\xff\x02\x10'\x00\x00\x00\x00\x00\x00\x16\x00\x14N,\x8f\xf4\xae\xcc*/S\x03\x94\x8f\xdb~\xc9\xb7\xc1\x94\xeb\x97x\x00\x00\x00\x00\x00\x00\x00\x16\x00\x14\xfd\xfe\xbf\xcf\x13\xa7 \n\xe0\xa5\xca\x05\xad\xb0fSOphq\x00\x00\x00\x00O\x01\x045\x87\xcf\x03\xdb\xde\xe7\x1b\x80\x00\x00\x00\xb3*S\x0b\x7f\xb7\xf7\xdb\x7fB\x9fcO\xa6\xf4%-P\xc6L\xea\xbd\xb5\xeaB\x97\xe4\x1e\x94\xf8\xae\x16\x02`\x9c%\xeaeN\x82\xec=\xf7\xd8wV\xb3\xc9\"A\xe7i\xa7U\xfeoaw\x1e$Y\x00\xbb\x18\xa1\x10e\xfbC\xfeT\x00\x00\x80\x01\x00\x00\x80\x00\x00\x00\x80\x00\x01\x00\xfd\x88\x01\x02\x00\x00\x00\x01p\x89X\xbbU\x81\xa0\xc1(\xb1B\xb7\x02\x14\x17\xfa\\\xfe\x9e\xf6\xca\xb3\xe3T{$\xc0\xa1\xd1\x1c!\xc4\x08\x00\x00\x00\x00\xfd\xff\xff\xff\x0b\x10'\x00\x00\x00\x00\x00\x00\x16\x00\x14k\x0b\xa3\x1eb\x97\xcd\xe9=\x01\x86}{)\xd1\xb2\x05\xaf\x91l\x10'\x00\x00\x00\x00\x00\x00\x16\x00\x1441\xdf\xbby\x91\x95\x98=(\xa8\xc7\x13\x8b1\xd7\x88\x15\x12\xe1\x10'\x00\x00\x00\x00\x00\x00\x16\x00\x14`7c\xbaI\xd36\xc5\x92\t)\xbc\xb4\xbfe6({\xee'\xe8\x03\x00\x00\x00\x00\x00\x00\x16\x00\x14y\xb9\x0cf\x17\xc2\xeb\xf1n\x18\xa3\xc7_9\x00+\xe8\xc2\xeb\x83\x10'\x00\x00\x00\x00\x00\x00\x16\x00\x14R\xf02\x18\xb2z|Mxp\xfcaS\x07\xac\xc9\xc0N\xc2\xdb\x10'\x00\x00\x00\x00\x00\x00\x16\x00\x14\xde\xa6\xb0\x1a\xd4]#\xa6\xf8\xb9\xd7\xb1\xe7=\xb6\r\x1bu\xc47\x10'\x00\x00\x00\x00\x00\x00\x16\x00\x14\x15'\xf3fl\xef\xb8\xbd\x00\xf9\x9e\xadeI\xac\xb6\xae\xdfJ3\x9c3+\x00\x00\x00\x00\x00\x16\x00\x14\x91[/\x02-\xe7z9\xe9=fnk\x8d\xc6\x98z\x94\x14O\x10'\x00\x00\x00\x00\x00\x00\x16\x00\x14\xee\x86\xfc\x98C\x97,32\x1a\x97\x9b78\x8fu\xc8\xb7q\x8b\x10'\x00\x00\x00\x00\x00\x00\x16\x00\x14\xf8\x9c.\x16\xfb{\xba\xacO\x9dN\xf9a\xf7\xe2!\x0f\xc9@\x86\x10'\x00\x00\x00\x00\x00\x00\x16\x00\x14\xd9`;\xfe\xa1\xd0\xf7\x13\x15\xe7\xe5\x19_\xd3\xdcrG\xe7\xd9\x88;W'\x00\x01\x01\x1f\x10'\x00\x00\x00\x00\x00\x00\x16\x00\x14\xd9`;\xfe\xa1\xd0\xf7\x13\x15\xe7\xe5\x19_\xd3\xdcrG\xe7\xd9\x88\"\x06\x03\xa4\"z%\xc1F\xf2\xb3\x07\xa3\xe7G;\x9e\xe3v\x95\x1d\xcb\x0e\xadU\xf0\xed\x16\n\xc36e\xcb\x05\x98\x18e\xfbC\xfeT\x00\x00\x80\x01\x00\x00\x80\x00\x00\x00\x80\x00\x00\x00\x00,\x00\x00\x00\x00\x01\x00q\x02\x00\x00\x00\x01\xb0f\x7f\xd1\xe3\nN>\xa7\xb2\x9d\xfa0\x93S>&\x0b\x125\xce\xbc\x85E\x94\xeb\xff\xc8\xcca\x80\x8b\x01\x00\x00\x00\x00\xfd\xff\xff\xff\x02\xe8\x03\x00\x00\x00\x00\x00\x00\x16\x00\x14u<\x0b0e\x14\xc0I\x18+\xfa\xa7\xe8\x9b\xaf\x93\x7f\x10\t\x88\xbf\xac/\x00\x00\x00\x00\x00\x16\x00\x14J\xad3#:\xe1\x81\xea\x90\xa8\xc4\xb6T\x84qc\xc5\x92\x01\xbf\xe8\xcd%\x00\x01\x01\x1f\xe8\x03\x00\x00\x00\x00\x00\x00\x16\x00\x14u<\x0b0e\x14\xc0I\x18+\xfa\xa7\xe8\x9b\xaf\x93\x7f\x10\t\x88\"\x06\x02\xd7\xb1PI\x10\xbbq'\x14Js\t\xde\xee\xde2\xe8\x8a\x06W\r\x96\xdbh1\x9e\xb7V\x05\xd5D\x12\x18e\xfbC\xfeT\x00\x00\x80\x01\x00\x00\x80\x00\x00\x00\x80\x00\x00\x00\x00\x04\x00\x00\x00\x00\x01\x00R\x02\x00\x00\x00\x01\xfc\x11\xe3_\x96\xf5;\xb2\xe3\xccy\xfe2\xc8\xffh\x99\xdbM\x06\xf4iz[\xcd\x17\x87;tb\x1e\xb7\x00\x00\x00\x00\x00\xfd\xff\xff\xff\x01b\x07\x00\x00\x00\x00\x00\x00\x16\x00\x14\xbcZ\xe6\x1b+\xe5\xb6D\x05\xbf\x0e\xf6\x7fQ\xe2\xc5v\xd4\x97z}V'\x00\x01\x01\x1fb\x07\x00\x00\x00\x00\x00\x00\x16\x00\x14\xbcZ\xe6\x1b+\xe5\xb6D\x05\xbf\x0e\xf6\x7fQ\xe2\xc5v\xd4\x97z\"\x06\x02\xdf]\x7f\xd4t\x8b\x0e\x1b\nC\xa2X\x8as3\xa4'\x84I\xfc,R\xafJ\xe5\x05\x91\x83_\xc3\xab\x03\x18e\xfbC\xfeT\x00\x00\x80\x01\x00\x00\x80\x00\x00\x00\x80\x00\x00\x00\x00\x1e\x00\x00\x00\x00\"\x02\x03\xaa\xe4r \x02Tb\xff53D\xb3_\x83\x028\xe21\x11\xd4oH\xd8B\x07\xfc\x8f(\x0b,5\xac\x18e\xfbC\xfeT\x00\x00\x80\x01\x00\x00\x80\x00\x00\x00\x80\x00\x00\x00\x005\x00\x00\x00\x00\"\x02\x0246\xfb\xba\x95\x14\rX\x9c\x94\xc9\x05FW\x9d%\xe8\x1ebA\"ik\xf5\x01\x8f \x10\x1cN\xfd\x91\x18e\xfbC\xfeT\x00\x00\x80\x01\x00\x00\x80\x00\x00\x00\x80\x01\x00\x00\x00\x11\x00\x00\x00\x00"

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
    TEST_PARTS_FORMAT_SINGLEPART_BBQR = [
        "B$ZP0100FMUE4KXZZ7EBBRGEYDAMAODL63BVHGQCGHJUW3HYF67KWPHQRRL2SK7RYSN72JJ7T6P77RJIZFJ42CCUYTYPP77776GIU2QMMAQMMIFS52WNYHN376U2WFHGGKET5NZNTAIHWMBDE6BFXG6BT6I4LNH5HTZ6266PUUNYAKRXNMCXHV3P757LXXTJP2ZP7MRPVK5ADR34L3W536WKNH5BHOJJH7LISMJFZRIX3FPK272MN5X3RXZLBTJHSUOJ6ZZOB76ZPH2YF2TRFSNQLNRKCQHKN7TX6IIMBQGUAV4ABRWGAYDESQLVBB53YOZ4O53JZ7XDSUMZDU5YZ3TNG3HPTYQUWKAJDGIF4RTCKNXGW7RH6WOXM6PQ37DRG7T3X6I24GWF6DAZ6KNVMHX6LJJ3H5UF24H7SRAJBTJYDAADNQ3AA"
    ]
    TEST_PARTS_FORMAT_MULTIPART_BBQR = [
        "B$ZP0500FMUE4KXZZ7EHBGEJQGAYCWK77HUDOZ3F4XJ5E4T5QK5K4DAKW62X4COILX2LXF5ITY55G26XGQWS5IBCQ2777777X6KNCUHWZWDGGQNW3C47SN5ZBT33XMJVGLZKZC7FC3WNU6R7NLM6L4YMGCCS6XLHGJFX26UQO465T7HSTGFKOZY262LR5KUUNT4OLTNQ5L3BKBXHPFYIKTAC5JQDNAYYQOEJ6TX7S52WPNHUQOM2P5G7VY53T7PASTL5GKYY4DJH777NH4X3YXEB5PA5EU5MNM32IBP3C5SBJAVE7QMVSTG3Z4Z57PXXLS5ADSG5",
        "B$ZP0501VQK4YXN77X5626VH7HE75S56VDVAMHHTPG2XP2ZLU7UU7ZFG7RMCPRUUGBD7KVNKL7JRXW7PG7FMGNU7KRZHZHVZHT2F67TCXGOEUJGDN2EYKAVJX6O77BJQGA2DAARRAMEDGMX45VQAJBIUMNAWPRHO2DDAKBZVGY5G2ZYSCH7RL43P323VHGY7Q5KKWHCYPBIUN4IIA7GF7XCI73FOMXRMS42P33CLLPDLNWTKZWFZWWGXJ7GEDERWGG6L7O3S4LKBTNQ2FOHAW5Y3L3XRAFL2RASJ2YE6XTF7HMWZ2FEZZGT3W3WE6NOTVB7KP7UC",
        "B$ZP0502DEXF3OMTE5G7ZUHLR54RFC4PY5NTE2F7HD2LUGKJO7IAOI4JJVKTLPQVAV7RFA6Z26ODZYDX5A3JF5F5MUN2JLWEFIX7XMPT7LDOPNW3PCSUXD4YENEYXKT7J3FXTP3DF7B466LLKM65O3C3O7P4W6EOWE3EY6TCWQ7JH3XTFLFZPNTJPHM33R3GKRGRD4KH2L6253OPBTT6SOWGIZJNGZ43LP2JPHWYL3MI2JH5MOHJ5WHP5JOWX7HH7L6UZ7H6JCI77JCDDOJPJTIE5N7QWL34C4LH37SUGL7PFHJC67TTOO5MYPKRSGAZ4UE2QUTC",
        "B$ZP0503MNPKEVFFPLIO3U3G63C47XNN446S5GZKPONG63PIQ63WEXEHZVJE7M6OSDAIQYZA2AARDDAMQXQJRXUQKZ77CMMXT7O7ETLTP4MUYDVWKPRRMMR5W6T5K5OK5P7SPTREGZ2DHQSTGBJGJFG2OAN2JCQ46CKNB7VV7TC6Z5MT5MCTQO7WV7IYOSL3VU2VNNT23D4GVQUKEPNUEWQKSOHU4YW477RKYKWIJMCAYULCMO5L4MOAKNQHPIN2RBLTDZ55O73YYXTUWGC7GTV3TVQTQ333DDVVKFZBVRPGFALYFEEOZJJ7QKH6HJ35WXPPJ6CM",
        "B$ZP05044U72GE77GNTN55TF7OJFSFL5K26N3OREJFXDWA6MJOGET3DQ27WIS6RGVX6XJGYL5N7L437VQGHY5FS5TFPFKGYGRYDAFKUAN27B6W37UWSJWT42ZN4VCRCXWHYRF5IWZ47TUQPLXWPLETTMRY73ZGQZVON6KQEECIJ7HKRHIUFEYIKJ75GY2XJWY43TGWJ4GIKLZEXPOHBYT7KPX4DLPDXJDKWJUTJBTKMUZTD656NCVQQ3GFT4USKWW7YLTKRP4SJBZFJSWO7TF5RLBDEPR7M5RCQRSFE7QIQM2AA",
    ]

    return namedtuple(
        "TestData",
        [
            "TEST_DATA_BYTES",
            "TEST_DATA_B58",
            "TEST_DATA_UR",
            "TEST_DATA_BBQR",
            "TEST_DATA_BBQR_MULTI",
            "TEST_PARTS_FORMAT_NONE",
            "TEST_PARTS_FORMAT_PMOFN",
            "TEST_PARTS_FORMAT_SINGLEPART_UR",
            "TEST_PARTS_FORMAT_MULTIPART_UR",
            "TEST_PARTS_FORMAT_SINGLEPART_BBQR",
            "TEST_PARTS_FORMAT_MULTIPART_BBQR",
        ],
    )(
        TEST_DATA_BYTES,
        TEST_DATA_B58,
        TEST_DATA_UR,
        TEST_DATA_BBQR,
        TEST_DATA_BBQR_MULTI,
        TEST_PARTS_FORMAT_NONE,
        TEST_PARTS_FORMAT_PMOFN,
        TEST_PARTS_FORMAT_SINGLEPART_UR,
        TEST_PARTS_FORMAT_MULTIPART_UR,
        TEST_PARTS_FORMAT_SINGLEPART_BBQR,
        TEST_PARTS_FORMAT_MULTIPART_BBQR,
    )


def test_init(mocker, m5stickv):
    from ur.ur_decoder import URDecoder
    from krux.qr import QRPartParser

    parser = QRPartParser()

    assert isinstance(parser, QRPartParser)
    assert parser.parts == {}
    assert parser.total == -1
    assert parser.format is None


def test_parser(mocker, m5stickv, tdata):
    from ur.ur import UR
    from urtypes.crypto.psbt import PSBT
    from krux.qr import QRPartParser, FORMAT_NONE, FORMAT_PMOFN, FORMAT_UR, FORMAT_BBQR

    cases = [
        (FORMAT_NONE, tdata.TEST_PARTS_FORMAT_NONE),
        (FORMAT_PMOFN, tdata.TEST_PARTS_FORMAT_PMOFN),
        (FORMAT_UR, tdata.TEST_PARTS_FORMAT_SINGLEPART_UR),
        (FORMAT_UR, tdata.TEST_PARTS_FORMAT_MULTIPART_UR),
        (FORMAT_BBQR, tdata.TEST_PARTS_FORMAT_SINGLEPART_BBQR),
        (FORMAT_BBQR, tdata.TEST_PARTS_FORMAT_MULTIPART_BBQR),
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
                # Multi-part UR
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
        elif fmt == FORMAT_BBQR:
            assert isinstance(res, bytes)
            if parser.total_count() > 1:
                assert res == tdata.TEST_DATA_BBQR_MULTI
            else:
                assert res == tdata.TEST_DATA_BBQR
        else:
            assert isinstance(res, str)
            assert res == tdata.TEST_DATA_B58


def test_to_qr_codes(mocker, m5stickv, tdata):
    from krux.qr import to_qr_codes, FORMAT_NONE, FORMAT_PMOFN, FORMAT_UR, FORMAT_BBQR
    from krux.display import Display
    from krux.bbqr import BBQrCode
    import base32

    BBQR_CODE_DATA = BBQrCode(base32.encode(tdata.TEST_DATA_BBQR), "Z", "P")
    cases = [
        # Test 135 pixels wide display
        (FORMAT_NONE, tdata.TEST_DATA_B58, 135, 1),
        (FORMAT_PMOFN, tdata.TEST_DATA_B58, 135, 9),
        (FORMAT_UR, tdata.TEST_DATA_UR, 135, 26),
        (FORMAT_BBQR, BBQR_CODE_DATA, 135, 8),
        # Test 320 pixels wide display
        (FORMAT_NONE, tdata.TEST_DATA_B58, 320, 1),
        (FORMAT_PMOFN, tdata.TEST_DATA_B58, 320, 3),
        (FORMAT_UR, tdata.TEST_DATA_UR, 320, 6),
        (FORMAT_BBQR, BBQR_CODE_DATA, 320, 2),
    ]
    for case in cases:
        mocker.patch(
            "krux.display.lcd",
            new=mocker.MagicMock(width=mocker.MagicMock(return_value=case[2])),
        )
        display = Display()
        display.to_portrait()
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
