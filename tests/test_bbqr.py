B32_TEST_BYTES = [
    b'psbt\xff\x01\x00{\x02\x00\x00\x00\x02\xd2h\x80v\xf6<\x08\xa0k\x16\xce\x9f\xd9\n1\xbfF\x06\x81\x01\x0c\xae]\x0b\x11\x8a\xb5\xdfZ\xa6\xd3\xcf\x00\x00\x00\x00\x00\xfd\xff\xff\xffX\xb8\x91\x7f\xcb\x166\xae\xcf\x9b\xa4\xec\x8f\x1d \xc9\xcfb\x82}\x16\x1d\xc0\xd7sb\xaf\x02\x7f\xcf\xa7}\x00\x00\x00\x00\x00\xfd\xff\xff\xff\x01\xe8\x03\x00\x00\x00\x00\x00\x00\x16\x00\x14\xae\xcd\x1e\xdc>\xffe\xaa \x9d\x02\x15\xe7=p\x90]\xc1hl\xb0\xfe*\x00\x00"\x02\x02\xd7\xb1PI\x10\xbbq\'\x14Js\t\xde\xee\xde2\xe8\x8a\x06W\r\x96\xdbh1\x9e\xb7V\x05\xd5D\x12G0D\x02 \x07\x8b\x9f\xe8y\xec_5\x12|\xbf;\xb5&2d\x07=x\x9f\xa2\xc8\x9b\x08\x9f\x12\xf1\xfeP\xea\xefV\x02 \x1a\xf3\xcc*\x97\x0e\x00\x9c\xcf\xa9\x83\xd1\xe4ph\x98\x9e\x8cML>\x03\xc4\x04\xb06\xa1+\xab\x1cs\x9c\x01\x00"\x02\x03\xc4\xc8\x06\xd0\xc1\x19\xb35\xe3\x9b\x14K\xc4\xba\xb1\xa5\x10\x06\xcf=\x97]\xbet\x07\xe3\x1e\xe7Y9\xe9\xe0G0D\x02 \x12\xeb\n\xf4\x95>3\xbdG\x07\xd5#\xf0z\x1d\xdaN\xcf0\xea\x157\x8c\xf5l\xb1:\x85#\x14\xd31\x02 x\x8aV;\xf1z\x17\x85\x80\xab\xc5\xae;\x96_\\\xfc\x02\xc3\xff\xd7N\xf8V&C\xe0\xcc<\x9e\xdb\xe0\x01\x00\x00',
    b"Hello World",
    b"Hello World.",
    b"1234567890" b"\x00",  # Single byte
    b"\x01\x02\x03\x04",  # Sequence of bytes
    b"\x00\xff\xfe\xfd\xfc\xfb",  # Mixed bytes
    b"\x00" * 10,  # All zeros
    b"\xff" * 10,  # All ones
    b"Hello, World!",  # ASCII text
    b"\x00\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0a\x0b\x0c\x0d\x0e\x0f",  # Full range of first 16 bytes
    b"The quick brown fox jumps over the lazy dog",  # Longer ASCII text
    b"\x12\x34\x56\x78\x9a\xbc\xde\xf0",  # Random hex sequence
    b"\x93\x83\xc1\x28\xd9\x8a\xea\xf4\xfa\xb1\xc8\xe0\x1c\xf7\xbf\x29",  # Random binary
]

BBQR_ENCODED_DESCRIPTORS = [
    # Nunchuk single
    [
        "B$ZU0100CXGMC3UCGAMABYD3T7RE65XAZCFIKABXUGZMK3AGQUE7GRVRTV2SXBOSB3T5HG35B7YD3QPGGZVGH6IZQTIQU5TO5AX64G7NHLCVHMD4WYB3PKGUH6ZP6SYBQMLIAUNBRXVGYCTF2BKK6CCRN3SG6Z5FDZJFA7SMHQPXX7VTQ6RFAMFSCL7472AYUU6GNB75WTGDQCHTJO3SKJ45IXJZCFIDTYZ4PJCUKH25SC2V3TR7MWENURU6J64VPSW53PN2NXFQGPJNOVROUJEIS66WVWRELHS6XCOU26WD35Z276YO4JOYMAOKUNY2EL2AA"
    ],
    # Nunchuk multi
    [
        "B$ZU0200PXHDTEVDGAAEBUM4KNIDLAKDG4QMAODDO6YRKZTJGCMRBCGFFVCGDVAYJY7R3TFEPWAP72754HW7OTEXWVWXRPCQYJDWYQR5PNZBCJHNSUT6Y2Y5LZB4PRPUNNAPXFIXPGFHTCLT5BBOA6XFMOYUQ3Y4M624X4AN26AU4P6JDFOE4Z7BOT7DRHOFCOT4ROAGCL7HTLJTVMWSOVGIGFABYYBP222XI5OY6HOZQ4V7RYYMYXU7GBHPL4IF7PHAMSBUYNRO5NG5Q47PA5QKRXY7HYPZXFJWU7VT24AHODTU6I52SIRXK6C3XMCVLU23RIPA",
        "B$ZU0201KJ2ZNNNI7BKXKANV63IYV5J7SWWVQ4XPRL3TZOC5JJSGYVISL4CGW5HMI77WZEWGS3WUN52KWTDE6BMZQVDY67SRDSMO5FGOPOXFSKA77QUV6KQBOQKWVAUEUUYNXLDY3YT6G2BQLGAWHE3WPJSHQWL7KUAVKQRSCLK77KW4MTXSOPWCRBSK4SXHYXB344BTNZGHFIQQJBLLQE353TMVMRTB6QDMKFQMWX5E4IJ24QR7IEYL5GDIORG2DZDDBNBYQBF4Y2DJJZ26NEMZNW2KSYZQEU2E7PBG4W4L6",
    ],
    # Sparrow single
    [
        "B$ZU0100AXA5WCUCGAAABUEP5GSXVGOTJU3IUQC5AZJJBF6URQPJZONGGEX2SGD6PXT4ZXKHVYPSMFQ4DGRAIBCJAAS5BZDT5QTM4WCJPDQPP4YAOXWMRXCDLFVZW7OM3UDA55WEVNFJTYN5CDFF2SA2Q4OUVEXKKKR3ONJN4HH3WBRMTMR7VDNIJZTF6JJJUWDGH5JIVLW7IVNUZZWZYTX2CFBKZTQMQO63NAYHWDO2ZGQ4NFCIZZAP"
    ],
    # Sparrow multi
    [
        "B$ZU0100GXG4XEVCGAAEBUJ5L6I2UXRYWOZMCIHCJYPNDYSVBDJCBO4QABDIKUBRGTBNP5ZMPL3PPVXZAA3H6UUCAUC6D6EU5TCVV4FK4U4IBBR5NPYIPCA2ZONIE2QG5GAILYGTL7SUHCLQK7XUD5Z3FAYX6MRS56AQM6ADG2FFGC7WRUS6H7N7MYGXPK5VXJNH7LWW3JFECXDULDXEDLHF5FEVDNR2WLQANOL3ECD3C4SQXDWRNBU3UDY6FA4ZJI2C5X6U2ZX7FDWDZPVQXR7J4H7MFN6WQVCLHQ34NDG5TRZ66RTI5LP327K7GM2UTA7J2K6YWQEKH3G4SXITCM6UWM5JK3OJR2QXVZGGUCNVDLSAMNR6XNTG7TFG4ZUP55D3HBCRO44RU7AQL3R2WJ7LGRXFAFGCRUJ45XPBH2HVGEMF2EN6MU6AFLRZ2YVS5BF6QJYOHFMB5ULYXVMADK43ACFXRZEF3VLRPLY3Y2E5GKUGPXBLHRFDVGZIHFXZ5FVNM73Z5PULPI3WZ2BNHLRA2ZKCN4KOOXXMRPO6DY2KDLXO2KBVOEAZH63MJTR5X3OMIFXBOTTHZGBT2MQRT473JSKCU3CLIKBWITHRMVZOEYPOVWCTNHMEZDW6V7T2NGCFI7QA"
    ],
]
BBQR_DECODED_DESCRIPTORS = [
    # Nunchuk single
    "# Exported from Nunchuk\nName: testnet\nPolicy: 1 of 1\nFormat: P2WSH\n\nDerivation: m/84'/1'/0'\n65fb43fe: tpubDDe8bRQqws125ChaJ4ZoB6qVbFn1sBubiim6SYcfmFz8XVSp4WWiMj4gAuzSxJPRDZwT9rT928wQmWX993CAq4TjBXdcoCUtuG2E115mLD5\n\n",
    # Nunchuk multi
    "# Exported from Nunchuk\nName: multisig\nPolicy: 2 of 3\nFormat: P2WSH\n\nDerivation: m/48'/1'/0'/2'\n65fb43fe: tpubDFM6mziafLfJPA9StFuzvdC5htjaMTsVaPSAjsahgE4c2CMWpg9yKaK4JyoaBjVYJKUFX9Kdyb4fgFaFUQmZNGU71Q1wZgZiGM1Go7p59NW\n\nDerivation: m/48'/1'/0'/2'\n84b90e2b: tpubDE6D5hG2QULH8XcBwZRP81DjFEYhkdRdE5EdAJXctPk6cCWJozhr6FaSyoopyU9DcUiKnUrZ14gZcdLRuSaTwDPpynBzdfmt4FEmenYTfrt\n\nDerivation: m/48'/1'/0'/2'\n473c5c27: tpubDEUCuxkfzMNmTG7oprJfK1HBHu3FNM43DMymAjyuwXNMNx4WwLib7xSacz5zMKRDcABJc2oezBLiefLarPuoXCnbTJmpuwodbP4nRoURJdS\n\n",
    # Sparrow single
    "wpkh([65fb43fe/84h/1h/0h]tpubDDe8bRQqws125ChaJ4ZoB6qVbFn1sBubiim6SYcfmFz8XVSp4WWiMj4gAuzSxJPRDZwT9rT928wQmWX993CAq4TjBXdcoCUtuG2E115mLD5/<0;1>/*)#na408ft8",
    # Sparrow multi (for Coldcard)
    "# Coldcard Multisig setup file (created by Sparrow)\n#\nName: multisig\nPolicy: 2 of 3\nDerivation: m/48'/1'/0'/2'\nFormat: P2WSH\n\n65FB43FE: tpubDFM6mziafLfJPA9StFuzvdC5htjaMTsVaPSAjsahgE4c2CMWpg9yKaK4JyoaBjVYJKUFX9Kdyb4fgFaFUQmZNGU71Q1wZgZiGM1Go7p59NW\n473C5C27: tpubDEUCuxkfzMNmTG7oprJfK1HBHu3FNM43DMymAjyuwXNMNx4WwLib7xSacz5zMKRDcABJc2oezBLiefLarPuoXCnbTJmpuwodbP4nRoURJdS\n84B90E2B: tpubDE6D5hG2QULH8XcBwZRP81DjFEYhkdRdE5EdAJXctPk6cCWJozhr6FaSyoopyU9DcUiKnUrZ14gZcdLRuSaTwDPpynBzdfmt4FEmenYTfrt\n",
]

BBQR_ENCODED_PSBTS = [
    # Nunchuk PSBT
    [
        "B$ZP0500FMUE4KXZZ7EHBGEJQGAYCWK77HUDOZ3F4XJ5E4T5QK5K4DAKW62X4COILX2LXF5ITY55G26XGQWS5IBCQ2777777X6KNCUHWZWDGGQNW3C47SN5ZBT33XMJVGLZKZC7FC3WNU6R7NLM6L4YMGCCS6XLHGJFX26UQO465T7HSTGFKOZY262LR5KUUNT4OLTNQ5L3BKBXHPFYIKTAC5JQDNAYYQOEJ6TX7S52WPNHUQOM2P5G7VY53T7PASTL5GKYY4DJH777NH4X3YXEB5PA5EU5MNM32IBP3C5SBJAVE7QMVSTG3Z4Z57PXXLS5ADSG5",
        "B$ZP0501VQK4YXN77X5626VH7HE75S56VDVAMHHTPG2XP2ZLU7UU7ZFG7RMCPRUUGBD7KVNKL7JRXW7PG7FMGNU7KRZHZHVZHT2F67TCXGOEUJGDN2EYKAVJX6O77BJQGA2DAARRAMEDGMX45VQAJBIUMNAWPRHO2DDAKBZVGY5G2ZYSCH7RL43P323VHGY7Q5KKWHCYPBIUN4IIA7GF7XCI73FOMXRMS42P33CLLPDLNWTKZWFZWWGXJ7GEDERWGG6L7O3S4LKBTNQ2FOHAW5Y3L3XRAFL2RASJ2YE6XTF7HMWZ2FEZZGT3W3WE6NOTVB7KP7UC",
        "B$ZP0502DEXF3OMTE5G7ZUHLR54RFC4PY5NTE2F7HD2LUGKJO7IAOI4JJVKTLPQVAV7RFA6Z26ODZYDX5A3JF5F5MUN2JLWEFIX7XMPT7LDOPNW3PCSUXD4YENEYXKT7J3FXTP3DF7B466LLKM65O3C3O7P4W6EOWE3EY6TCWQ7JH3XTFLFZPNTJPHM33R3GKRGRD4KH2L6253OPBTT6SOWGIZJNGZ43LP2JPHWYL3MI2JH5MOHJ5WHP5JOWX7HH7L6UZ7H6JCI77JCDDOJPJTIE5N7QWL34C4LH37SUGL7PFHJC67TTOO5MYPKRSGAZ4UE2QUTC",
        "B$ZP0503MNPKEVFFPLIO3U3G63C47XNN446S5GZKPONG63PIQ63WEXEHZVJE7M6OSDAIQYZA2AARDDAMQXQJRXUQKZ77CMMXT7O7ETLTP4MUYDVWKPRRMMR5W6T5K5OK5P7SPTREGZ2DHQSTGBJGJFG2OAN2JCQ46CKNB7VV7TC6Z5MT5MCTQO7WV7IYOSL3VU2VNNT23D4GVQUKEPNUEWQKSOHU4YW477RKYKWIJMCAYULCMO5L4MOAKNQHPIN2RBLTDZ55O73YYXTUWGC7GTV3TVQTQ333DDVVKFZBVRPGFALYFEEOZJJ7QKH6HJ35WXPPJ6CM",
        "B$ZP05044U72GE77GNTN55TF7OJFSFL5K26N3OREJFXDWA6MJOGET3DQ27WIS6RGVX6XJGYL5N7L437VQGHY5FS5TFPFKGYGRYDAFKUAN27B6W37UWSJWT42ZN4VCRCXWHYRF5IWZ47TUQPLXWPLETTMRY73ZGQZVON6KQEECIJ7HKRHIUFEYIKJ75GY2XJWY43TGWJ4GIKLZEXPOHBYT7KPX4DLPDXJDKWJUTJBTKMUZTD656NCVQQ3GFT4USKWW7YLTKRP4SJBZFJSWO7TF5RLBDEPR7M5RCQRSFE7QIQM2AA",
    ],
    # Sparrow PSBT
    [
        "B$ZP0100FMUE4KXZZ7EBBRGEYDAMAODL63BVHGQCGHJUW3HYF67KWPHQRRL2SK7RYSN72JJ7T6P77RJIZFJ42CCUYTYPP77776GIU2QMMAQMMIFS52WNYHN376U2WFHGGKET5NZNTAIHWMBDE6BFXG6BT6I4LNH5HTZ6266PUUNYAKRXNMCXHV3P757LXXTJP2ZP7MRPVK5ADR34L3W536WKNH5BHOJJH7LISMJFZRIX3FPK272MN5X3RXZLBTJHSUOJ6ZZOB76ZPH2YF2TRFSNQLNRKCQHKN7TX6IIMBQGUAV4ABRWGAYDESQLVBB53YOZ4O53JZ7XDSUMZDU5YZ3TNG3HPTYQUWKAJDGIF4RTCKNXGW7RH6WOXM6PQ37DRG7T3X6I24GWF6DAZ6KNVMHX6LJJ3H5UF24H7SRAJBTJYDAADNQ3AA"
    ],
]

BBQR_DECODED_PSBTS = [
    # Nunchuk PSBT
    b"psbt\xff\x01\x00\xc3\x02\x00\x00\x00\x03/#\xc5\xf6C##\xcb\x1b\x1e\x8e\x11-E\x00 \xdb*\xfa\x10\x1e\xd1N\xdea'm\x99J\xba\x96*\n\x00\x00\x00\x00\xfd\xff\xff\xff\xd2h\x80v\xf6<\x08\xa0k\x16\xce\x9f\xd9\n1\xbfF\x06\x81\x01\x0c\xae]\x0b\x11\x8a\xb5\xdfZ\xa6\xd3\xcf\x00\x00\x00\x00\x00\xfd\xff\xff\xff\xe9E\x99\x03\x1a\xf2\xe0n\xd7c7\xd3\xccx\xe5\xcc\x80\xbfu\xc2y\x19\x80\xfaK\x00\xaa\xdb\xd4\x00C\x9e\x00\x00\x00\x00\x00\xfd\xff\xff\xff\x02\x10'\x00\x00\x00\x00\x00\x00\x16\x00\x14N,\x8f\xf4\xae\xcc*/S\x03\x94\x8f\xdb~\xc9\xb7\xc1\x94\xeb\x97x\x00\x00\x00\x00\x00\x00\x00\x16\x00\x14\xfd\xfe\xbf\xcf\x13\xa7 \n\xe0\xa5\xca\x05\xad\xb0fSOphq\x00\x00\x00\x00O\x01\x045\x87\xcf\x03\xdb\xde\xe7\x1b\x80\x00\x00\x00\xb3*S\x0b\x7f\xb7\xf7\xdb\x7fB\x9fcO\xa6\xf4%-P\xc6L\xea\xbd\xb5\xeaB\x97\xe4\x1e\x94\xf8\xae\x16\x02`\x9c%\xeaeN\x82\xec=\xf7\xd8wV\xb3\xc9\"A\xe7i\xa7U\xfeoaw\x1e$Y\x00\xbb\x18\xa1\x10e\xfbC\xfeT\x00\x00\x80\x01\x00\x00\x80\x00\x00\x00\x80\x00\x01\x00\xfd\x88\x01\x02\x00\x00\x00\x01p\x89X\xbbU\x81\xa0\xc1(\xb1B\xb7\x02\x14\x17\xfa\\\xfe\x9e\xf6\xca\xb3\xe3T{$\xc0\xa1\xd1\x1c!\xc4\x08\x00\x00\x00\x00\xfd\xff\xff\xff\x0b\x10'\x00\x00\x00\x00\x00\x00\x16\x00\x14k\x0b\xa3\x1eb\x97\xcd\xe9=\x01\x86}{)\xd1\xb2\x05\xaf\x91l\x10'\x00\x00\x00\x00\x00\x00\x16\x00\x1441\xdf\xbby\x91\x95\x98=(\xa8\xc7\x13\x8b1\xd7\x88\x15\x12\xe1\x10'\x00\x00\x00\x00\x00\x00\x16\x00\x14`7c\xbaI\xd36\xc5\x92\t)\xbc\xb4\xbfe6({\xee'\xe8\x03\x00\x00\x00\x00\x00\x00\x16\x00\x14y\xb9\x0cf\x17\xc2\xeb\xf1n\x18\xa3\xc7_9\x00+\xe8\xc2\xeb\x83\x10'\x00\x00\x00\x00\x00\x00\x16\x00\x14R\xf02\x18\xb2z|Mxp\xfcaS\x07\xac\xc9\xc0N\xc2\xdb\x10'\x00\x00\x00\x00\x00\x00\x16\x00\x14\xde\xa6\xb0\x1a\xd4]#\xa6\xf8\xb9\xd7\xb1\xe7=\xb6\r\x1bu\xc47\x10'\x00\x00\x00\x00\x00\x00\x16\x00\x14\x15'\xf3fl\xef\xb8\xbd\x00\xf9\x9e\xadeI\xac\xb6\xae\xdfJ3\x9c3+\x00\x00\x00\x00\x00\x16\x00\x14\x91[/\x02-\xe7z9\xe9=fnk\x8d\xc6\x98z\x94\x14O\x10'\x00\x00\x00\x00\x00\x00\x16\x00\x14\xee\x86\xfc\x98C\x97,32\x1a\x97\x9b78\x8fu\xc8\xb7q\x8b\x10'\x00\x00\x00\x00\x00\x00\x16\x00\x14\xf8\x9c.\x16\xfb{\xba\xacO\x9dN\xf9a\xf7\xe2!\x0f\xc9@\x86\x10'\x00\x00\x00\x00\x00\x00\x16\x00\x14\xd9`;\xfe\xa1\xd0\xf7\x13\x15\xe7\xe5\x19_\xd3\xdcrG\xe7\xd9\x88;W'\x00\x01\x01\x1f\x10'\x00\x00\x00\x00\x00\x00\x16\x00\x14\xd9`;\xfe\xa1\xd0\xf7\x13\x15\xe7\xe5\x19_\xd3\xdcrG\xe7\xd9\x88\"\x06\x03\xa4\"z%\xc1F\xf2\xb3\x07\xa3\xe7G;\x9e\xe3v\x95\x1d\xcb\x0e\xadU\xf0\xed\x16\n\xc36e\xcb\x05\x98\x18e\xfbC\xfeT\x00\x00\x80\x01\x00\x00\x80\x00\x00\x00\x80\x00\x00\x00\x00,\x00\x00\x00\x00\x01\x00q\x02\x00\x00\x00\x01\xb0f\x7f\xd1\xe3\nN>\xa7\xb2\x9d\xfa0\x93S>&\x0b\x125\xce\xbc\x85E\x94\xeb\xff\xc8\xcca\x80\x8b\x01\x00\x00\x00\x00\xfd\xff\xff\xff\x02\xe8\x03\x00\x00\x00\x00\x00\x00\x16\x00\x14u<\x0b0e\x14\xc0I\x18+\xfa\xa7\xe8\x9b\xaf\x93\x7f\x10\t\x88\xbf\xac/\x00\x00\x00\x00\x00\x16\x00\x14J\xad3#:\xe1\x81\xea\x90\xa8\xc4\xb6T\x84qc\xc5\x92\x01\xbf\xe8\xcd%\x00\x01\x01\x1f\xe8\x03\x00\x00\x00\x00\x00\x00\x16\x00\x14u<\x0b0e\x14\xc0I\x18+\xfa\xa7\xe8\x9b\xaf\x93\x7f\x10\t\x88\"\x06\x02\xd7\xb1PI\x10\xbbq'\x14Js\t\xde\xee\xde2\xe8\x8a\x06W\r\x96\xdbh1\x9e\xb7V\x05\xd5D\x12\x18e\xfbC\xfeT\x00\x00\x80\x01\x00\x00\x80\x00\x00\x00\x80\x00\x00\x00\x00\x04\x00\x00\x00\x00\x01\x00R\x02\x00\x00\x00\x01\xfc\x11\xe3_\x96\xf5;\xb2\xe3\xccy\xfe2\xc8\xffh\x99\xdbM\x06\xf4iz[\xcd\x17\x87;tb\x1e\xb7\x00\x00\x00\x00\x00\xfd\xff\xff\xff\x01b\x07\x00\x00\x00\x00\x00\x00\x16\x00\x14\xbcZ\xe6\x1b+\xe5\xb6D\x05\xbf\x0e\xf6\x7fQ\xe2\xc5v\xd4\x97z}V'\x00\x01\x01\x1fb\x07\x00\x00\x00\x00\x00\x00\x16\x00\x14\xbcZ\xe6\x1b+\xe5\xb6D\x05\xbf\x0e\xf6\x7fQ\xe2\xc5v\xd4\x97z\"\x06\x02\xdf]\x7f\xd4t\x8b\x0e\x1b\nC\xa2X\x8as3\xa4'\x84I\xfc,R\xafJ\xe5\x05\x91\x83_\xc3\xab\x03\x18e\xfbC\xfeT\x00\x00\x80\x01\x00\x00\x80\x00\x00\x00\x80\x00\x00\x00\x00\x1e\x00\x00\x00\x00\"\x02\x03\xaa\xe4r \x02Tb\xff53D\xb3_\x83\x028\xe21\x11\xd4oH\xd8B\x07\xfc\x8f(\x0b,5\xac\x18e\xfbC\xfeT\x00\x00\x80\x01\x00\x00\x80\x00\x00\x00\x80\x00\x00\x00\x005\x00\x00\x00\x00\"\x02\x0246\xfb\xba\x95\x14\rX\x9c\x94\xc9\x05FW\x9d%\xe8\x1ebA\"ik\xf5\x01\x8f \x10\x1cN\xfd\x91\x18e\xfbC\xfeT\x00\x00\x80\x01\x00\x00\x80\x00\x00\x00\x80\x01\x00\x00\x00\x11\x00\x00\x00\x00",
    # Sparrow PSBT
    b'psbt\xff\x01\x00R\x02\x00\x00\x00\x01\x9a\x9b\xe1\xca)\x10\\\x97t<\x0f\xd1\xeey\xc0\xe6\r"\x8aa\xc8\xec\xbft\xf9\xe7\xcf\xfa\x01\x19\x0c{\x01\x00\x00\x00\x00\xfd\xff\xff\xff\x01!&\x00\x00\x00\x00\x00\x00\x16\x00\x14\xae\xcd\x1e\xdc>\xffe\xaa \x9d\x02\x15\xe7=p\x90]\xc1hlX\x0b+\x00O\x01\x045\x87\xcf\x03\xdb\xde\xe7\x1b\x80\x00\x00\x00\xb3*S\x0b\x7f\xb7\xf7\xdb\x7fB\x9fcO\xa6\xf4%-P\xc6L\xea\xbd\xb5\xeaB\x97\xe4\x1e\x94\xf8\xae\x16\x02`\x9c%\xeaeN\x82\xec=\xf7\xd8wV\xb3\xc9"A\xe7i\xa7U\xfeoaw\x1e$Y\x00\xbb\x18\xa1\x10e\xfbC\xfeT\x00\x00\x80\x01\x00\x00\x80\x00\x00\x00\x80\x00\x01\x01\x1f\x10\'\x00\x00\x00\x00\x00\x00\x16\x00\x14I\x8cM\xa5\x8c\xbb\x9cZi\x88\xb82\xde\xb33l\xf4BT\xa0\x01\x03\x04\x01\x00\x00\x00"\x06\x03\xed\x17\xfd\x05\xafk\xcdQ\xf8\xddl\xf77\xac\x13j\xfa\x00h\x1f\xb2\xa9\xc3\xf5||\xad\xe8J\xf8\x1fa\x18e\xfbC\xfeT\x00\x00\x80\x01\x00\x00\x80\x00\x00\x00\x80\x00\x00\x00\x00\x08\x00\x00\x00\x00\x00',
]


def test_base32_encoding(mocker):
    from krux.bbqr import base32_encode_stream
    from base64 import b32encode

    for test_bytes in B32_TEST_BYTES:
        expected = b32encode(test_bytes).decode("utf-8").rstrip("=")
        assert "".join(base32_encode_stream(test_bytes)) == expected


def test_base32_decoding(mocker):
    from krux.bbqr import base32_decode_stream
    from base64 import b32encode

    for test_bytes in B32_TEST_BYTES:
        encoded = b32encode(test_bytes).decode("utf-8")
        assert base32_decode_stream(encoded) == test_bytes


def test_decode_bbqr(mocker, m5stickv):
    from krux.qr import detect_format
    from krux.bbqr import decode_bbqr, parse_bbqr

    for encoded, decoded in zip(BBQR_ENCODED_DESCRIPTORS, BBQR_DECODED_DESCRIPTORS):
        parts = {}
        _, bbqr = detect_format(encoded[0])
        for encoded_part in encoded:
            part, index, total = parse_bbqr(encoded_part)
            parts[index] = part
        assert decode_bbqr(parts, bbqr.encoding, bbqr.file_type) == decoded

    for encoded, decoded in zip(BBQR_ENCODED_PSBTS, BBQR_DECODED_PSBTS):
        parts = {}
        _, bbqr = detect_format(encoded[0])
        for encoded_part in encoded:
            part, index, total = parse_bbqr(encoded_part)
            parts[index] = part
        assert decode_bbqr(parts, bbqr.encoding, bbqr.file_type) == decoded


def test_encode_bbqr(mocker, m5stickv):
    from krux.bbqr import encode_bbqr

    for encoded, decoded in zip(BBQR_ENCODED_DESCRIPTORS, BBQR_DECODED_DESCRIPTORS):
        bbqr_code = encode_bbqr(decoded.encode("utf-8"), file_type="U")
        encoded_payload = "".join([part[8:] for part in sorted(encoded)])
        assert encoded_payload == bbqr_code.payload

    for encoded, decoded in zip(BBQR_ENCODED_PSBTS, BBQR_DECODED_PSBTS):
        bbqr_code = encode_bbqr(decoded, file_type="P")
        encoded_payload = "".join([part[8:] for part in sorted(encoded)])
        assert encoded_payload == bbqr_code.payload
